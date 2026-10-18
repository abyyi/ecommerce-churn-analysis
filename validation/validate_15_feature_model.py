"""Reproduce the saved local RF candidate; never use results as a fresh holdout.
Run in a pinned environment; the pickle must be a trusted project artifact.
"""
import argparse, hashlib, json, pickle, platform
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, f1_score, roc_auc_score,
    average_precision_score, confusion_matrix, classification_report, brier_score_loss)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate(y, prob, threshold):
    pred = (prob >= threshold).astype(int)
    return dict(threshold=threshold, accuracy=accuracy_score(y,pred),
        macro_f1=f1_score(y,pred,average='macro'), roc_auc=roc_auc_score(y,prob),
        average_precision_churn=average_precision_score(y,prob),
        brier_score=brier_score_loss(y,prob), predicted_churn_count=int(pred.sum()),
        confusion_matrix_rows_actual_columns_predicted=confusion_matrix(y,pred,labels=[0,1]).tolist(),
        classification_report=classification_report(y,pred,labels=[0,1],
            target_names=['retained','churned'],output_dict=True,zero_division=0))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,default=Path('validation_results'))
    args=parser.parse_args(); args.output_dir.mkdir(parents=True,exist_ok=True)
    root=args.project_root/'data/sample'
    model_path=root/'churn_model_v2.pkl'; feature_path=root/'user_features_v2.parquet'
    artifact=pickle.loads(model_path.read_bytes())
    model=artifact['model']; features=list(artifact['features'])
    assert len(features)==15 and list(model.feature_names_in_)==features
    assert list(model.classes_)==[0,1] and artifact['threshold']==0.7
    frame=duckdb.sql('SELECT * FROM read_parquet(?)',params=[str(feature_path)]).df()
    assert len(frame)==9428 and frame.user_id.is_unique and frame.churn.sum()==7658
    X=frame[features].copy(); y=frame.churn
    missing=X.isna().sum().to_dict()
    X[['cart_rate','purchase_rate']]=X[['cart_rate','purchase_rate']].fillna(0)
    assert np.isfinite(X.to_numpy()).all()
    train_idx,test_idx=train_test_split(np.arange(len(frame)),test_size=.2,random_state=42,stratify=y)
    assert not set(train_idx)&set(test_idx)
    fresh=RandomForestClassifier(**model.get_params()).fit(X.iloc[train_idx],y.iloc[train_idx])
    saved_p=model.predict_proba(X)[:,1]; fresh_p=fresh.predict_proba(X)[:,1]
    tree_match=all(np.array_equal(a.tree_.__getstate__()['nodes'],b.tree_.__getstate__()['nodes'])
        and np.array_equal(a.tree_.value,b.tree_.value)
        for a,b in zip(model.estimators_,fresh.estimators_))
    # Rebuild every model input and the target directly from session events.
    rebuilt=duckdb.sql("""
      WITH h AS (
      SELECT user_id,
       date_diff('second',max(event_time) FILTER (WHERE event_type='purchase'),TIMESTAMP '2020-03-01')/86400.0 recency_days,
       count(DISTINCT rebuilt_session) FILTER (WHERE event_type='purchase') purchase_sessions,
       sum(price) FILTER (WHERE event_type='purchase') total_spend,
       count(DISTINCT rebuilt_session) total_sessions,
       count(*) FILTER (WHERE event_type='view') view_count,
       count(*) FILTER (WHERE event_type='cart') cart_count,
       count(*) FILTER (WHERE event_type='purchase') purchase_count,
       count(*) FILTER (WHERE event_time>='2020-01-31' AND event_type='view') recent_30d_views,
       count(*) FILTER (WHERE event_time>='2020-01-31' AND event_type='cart') recent_30d_carts,
       count(*) FILTER (WHERE event_time>='2020-01-31' AND event_type='purchase') recent_30d_purchases,
       count(DISTINCT rebuilt_session) FILTER (WHERE event_time>='2020-01-31') recent_30d_sessions
      FROM read_parquet(?) WHERE event_time>='2019-10-01' AND event_time<'2020-03-01'
      GROUP BY user_id HAVING purchase_count>0),
      f AS (SELECT user_id,count(*) n FROM read_parquet(?)
       WHERE event_time>='2020-03-01' AND event_time<'2020-05-01' AND event_type='purchase' GROUP BY user_id)
      SELECT h.*,CASE WHEN view_count>0 THEN cart_count::DOUBLE/view_count ELSE 0 END cart_rate,
       CASE WHEN view_count>0 THEN purchase_count::DOUBLE/view_count ELSE 0 END purchase_rate,
       (view_count=0)::INTEGER no_view_before,
       purchase_sessions::DOUBLE/total_sessions purchase_session_rate,
       CASE WHEN coalesce(f.n,0)>0 THEN 0 ELSE 1 END churn
      FROM h LEFT JOIN f USING(user_id)
    """,params=[str(root/'session_events.parquet')]*2).df().set_index('user_id').loc[frame.user_id]
    rebuilt_X=rebuilt[features].reset_index(drop=True)
    checks={c:bool(np.allclose(X[c],rebuilt_X[c],rtol=1e-10,atol=1e-8)) for c in features}
    labels_match=bool(np.array_equal(y,rebuilt.churn))
    rebuilt_p=fresh.predict_proba(rebuilt_X)[:,1]
    result=dict(environment=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,
        sklearn=sklearn.__version__,duckdb=duckdb.__version__),
        source_sha256={p.name:sha(p) for p in [model_path,feature_path,root/'session_events.parquet']},
        features=features,model_params=model.get_params(),missing_before_fill=missing,
        preprocessing='Fill cart_rate and purchase_rate NaN with zero; no scaling or log transform.',
        split=dict(method='stratified random user split on original Parquet row order',test_size=.2,random_state=42,
         train_n=len(train_idx),test_n=len(test_idx),test_churn=int(y.iloc[test_idx].sum()),
         test_retained=int((y.iloc[test_idx]==0).sum()),
         train_user_ids_sha256=hashlib.sha256(frame.user_id.iloc[train_idx].to_numpy().tobytes()).hexdigest(),
         test_user_ids_sha256=hashlib.sha256(frame.user_id.iloc[test_idx].to_numpy().tobytes()).hexdigest()),
        saved_training_n=int(model._n_samples),saved_tree_states_equal_retrained=tree_match,
        max_abs_probability_difference_all_users=float(np.max(abs(saved_p-fresh_p))),
        feature_rebuild_matches=checks,label_rebuild_matches=labels_match,
        max_abs_probability_difference_rebuilt_features=float(np.max(abs(fresh_p-rebuilt_p))),
        evaluation={str(t):evaluate(y.iloc[test_idx],fresh_p[test_idx],t) for t in [.5,.7]},
        majority_baseline=evaluate(y.iloc[test_idx],np.ones(len(test_idx)),.7),
        limitations='Reconstructed historical split, already inspected during development; not an untouched or temporal holdout.')
    assert tree_match and np.allclose(saved_p,fresh_p,rtol=0,atol=1e-14)
    assert all(checks.values()) and labels_match
    assert np.array_equal(saved_p[test_idx]>=.7,fresh_p[test_idx]>=.7)
    (args.output_dir/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
