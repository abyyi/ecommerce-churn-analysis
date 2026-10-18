"""Fixed-design temporal backtest. No tuning/calibration; original artifacts read-only.
Run: python validate_temporal.py --project-root /path/to/project --output-dir NEW_DIR
Requires the versions in ../requirements.txt. Output directory must not exist.
"""
import argparse, hashlib, json, platform
from pathlib import Path
import duckdb, numpy as np, pandas as pd, sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, f1_score, confusion_matrix

FEATURES = ['recency_days','purchase_sessions','total_spend','total_sessions','view_count','cart_count','purchase_count','cart_rate','purchase_rate','no_view_before','purchase_session_rate','recent_30d_views','recent_30d_carts','recent_30d_purchases','recent_30d_sessions']
PARAMS = dict(n_estimators=200,max_depth=5,min_samples_leaf=20,random_state=42,n_jobs=-1)

QUERY = "\n      WITH h AS (\n      SELECT user_id,\n       date_diff('second',max(event_time) FILTER (WHERE event_type='purchase'),TIMESTAMP '{cutoff}')/86400.0 recency_days,\n       count(DISTINCT rebuilt_session) FILTER (WHERE event_type='purchase') purchase_sessions,\n       sum(price) FILTER (WHERE event_type='purchase') total_spend,\n       count(DISTINCT rebuilt_session) total_sessions,\n       count(*) FILTER (WHERE event_type='view') view_count,\n       count(*) FILTER (WHERE event_type='cart') cart_count,\n       count(*) FILTER (WHERE event_type='purchase') purchase_count,\n       count(*) FILTER (WHERE event_time>='{recent}' AND event_type='view') recent_30d_views,\n       count(*) FILTER (WHERE event_time>='{recent}' AND event_type='cart') recent_30d_carts,\n       count(*) FILTER (WHERE event_time>='{recent}' AND event_type='purchase') recent_30d_purchases,\n       count(DISTINCT rebuilt_session) FILTER (WHERE event_time>='{recent}') recent_30d_sessions\n      FROM read_parquet(?) WHERE event_time>='{start}' AND event_time<'{cutoff}'\n      GROUP BY user_id HAVING purchase_count>0),\n      f AS (SELECT user_id,count(*) n FROM read_parquet(?)\n       WHERE event_time>='{cutoff}' AND event_time<'{end}' AND event_type='purchase' GROUP BY user_id)\n      SELECT h.*,CASE WHEN view_count>0 THEN cart_count::DOUBLE/view_count ELSE 0 END cart_rate,\n       CASE WHEN view_count>0 THEN purchase_count::DOUBLE/view_count ELSE 0 END purchase_rate,\n       (view_count=0)::INTEGER no_view_before,\n       purchase_sessions::DOUBLE/total_sessions purchase_session_rate,\n       CASE WHEN coalesce(f.n,0)>0 THEN 0 ELSE 1 END churn\n      FROM h LEFT JOIN f USING(user_id)\n    "

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()

def features(path, start, cutoff):
    # SQL below is feature aggregation only: no future labels in this function.
    recent=str((pd.Timestamp(cutoff)-pd.Timedelta(days=30)).date())
    q=QUERY.split(',\n      f AS')[0] + " SELECT h.*,CASE WHEN view_count>0 THEN cart_count::DOUBLE/view_count ELSE 0 END cart_rate,CASE WHEN view_count>0 THEN purchase_count::DOUBLE/view_count ELSE 0 END purchase_rate,(view_count=0)::INTEGER no_view_before,purchase_sessions::DOUBLE/total_sessions purchase_session_rate FROM h ORDER BY user_id"
    frame=duckdb.sql(q.format(start=start,cutoff=cutoff,recent=recent),params=[str(path)] if 'read_parquet(?)' in q else []).df()
    assert frame.user_id.is_unique and np.isfinite(frame[FEATURES]).all().all()
    assert (frame.recent_30d_sessions<=frame.total_sessions).all()
    return frame

def labels(path, frame, cutoff, end):
    assert (pd.Timestamp(end)-pd.Timestamp(cutoff)).days==60
    buyers=duckdb.sql("SELECT DISTINCT user_id FROM read_parquet(?) WHERE event_time>=?::TIMESTAMP AND event_time<?::TIMESTAMP AND event_type='purchase'",params=[str(path),cutoff,end]).df().user_id
    return (~frame.user_id.isin(buyers)).astype(int).to_numpy()

def top_metrics(y, score, ascending=False):
    # Exact expected precision under uniform random resolution of boundary ties.
    out=[]; rng=np.random.default_rng(42)
    for fraction in [.1,.2,.3]:
        k=max(1,int(len(y)*fraction))
        s=np.asarray(score) if ascending else -np.asarray(score)
        boundary=np.sort(s)[k-1]; above=s<boundary; tied=s==boundary
        slots=k-int(above.sum()); hits=float(y[above].sum())
        expected=(hits+slots*y[tied].mean())/k
        row=dict(fraction=fraction,k=k,precision=expected,lift=expected/y.mean(),boundary_tie_n=int(tied.sum()))
        if ascending:
            # Equivalent to random tie order; sample tied positives without replacement.
            draws=rng.hypergeometric(int(y[tied].sum()),int(tied.sum()-y[tied].sum()),slots,size=1000)
            row['random_ties_1000_mean_precision']=float(((hits+draws)/k).mean())
        out.append(row)
    return out

def evaluate(y,p,frame):
    return dict(n=len(y),churn_n=int(y.sum()),churn_rate=float(y.mean()),roc_auc=float(roc_auc_score(y,p)),macro_f1=float(f1_score(y,p>=.7,average='macro')),confusion_matrix=confusion_matrix(y,p>=.7,labels=[0,1]).tolist(),rf_top=top_metrics(y,p),rule_top=top_metrics(y,frame.recent_30d_views,True))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project-root',type=Path,required=True); ap.add_argument('--output-dir',type=Path,required=True); a=ap.parse_args()
    assert not a.output_dir.exists(), 'Use a NEW output directory to preserve results.'
    root=a.project_root; path=root/'data/sample/session_events.parquet'
    protected=[path,root/'data/sample/user_features_v2.parquet',root/'data/sample/churn_model_v2.pkl',root/'notebooks/01_data_quality.recovered.ipynb',root/'validation/validate_15_feature_model.py',root/'validation/metrics.json']
    before={str(p.relative_to(root)):sha(p) for p in protected}
    audit=duckdb.sql("SELECT min(event_time) first_event,max(event_time) last_event,count(*) events,count(distinct user_id) users FROM read_parquet(?)",params=[str(path)]).df().astype(str).to_dict('records')[0]
    monthly=duckdb.sql("SELECT strftime(event_time,'%Y-%m') AS event_month,count(*) events,count(distinct user_id) users,count(*) FILTER(WHERE event_type='purchase') purchases FROM read_parquet(?) GROUP BY 1 ORDER BY 1",params=[str(path)]).df().to_dict('records')
    session_check=duckdb.sql("WITH x AS (SELECT *,lag(event_time) OVER(PARTITION BY user_id ORDER BY event_time,rebuilt_session) prev,lag(rebuilt_session) OVER(PARTITION BY user_id ORDER BY event_time,rebuilt_session) sid FROM read_parquet(?)) SELECT count(*) FILTER(WHERE user_id IS NULL OR event_time IS NULL OR rebuilt_session IS NULL) null_keys,count(*) FILTER(WHERE (prev IS NULL AND rebuilt_session<>1) OR (prev IS NOT NULL AND rebuilt_session<>sid+CASE WHEN event_time-prev>INTERVAL '30 minutes' THEN 1 ELSE 0 END)) session_mismatches FROM x",params=[str(path)]).df().to_dict('records')[0]
    assert session_check['null_keys']==0
    windows=dict(train=dict(start='2019-10-01',cutoff='2020-01-01',end='2020-03-01'),test=dict(start='2019-11-30',cutoff='2020-03-01',end='2020-04-30'))
    for w in windows.values(): assert (pd.Timestamp(w['cutoff'])-pd.Timestamp(w['start'])).days==92
    assert windows['train']['end']<=windows['test']['cutoff']
    tr=features(path,'2019-10-01','2020-01-01'); yt=labels(path,tr,'2020-01-01','2020-03-01')
    model=RandomForestClassifier(**PARAMS).fit(tr[FEATURES],yt)
    te=features(path,'2019-11-30','2020-03-01'); prob=model.predict_proba(te[FEATURES])[:,1]
    # Late outcomes are first constructed AFTER training and prediction.
    y=labels(path,te,'2020-03-01','2020-04-30')
    overlap=te.user_id.isin(tr.user_id).to_numpy()
    groups={name:evaluate(y[m],prob[m],te.loc[m]) for name,m in [('all',np.ones(len(te),bool)),('seen_users',overlap),('unseen_users',~overlap)] if m.sum() and len(np.unique(y[m]))==2}
    # Causal, tie-invariant session definition: one boundary per user/timestamp.
    # A future event never changes a past event's session membership.
    duckdb.sql("""CREATE TEMP TABLE canonical_events AS WITH times AS (
      SELECT DISTINCT user_id,event_time FROM read_parquet(?)), gaps AS (
      SELECT *,lag(event_time) OVER(PARTITION BY user_id ORDER BY event_time) prev FROM times), ids AS (
      SELECT user_id,event_time,sum(CASE WHEN prev IS NULL OR event_time-prev>INTERVAL '30 minutes' THEN 1 ELSE 0 END)
      OVER(PARTITION BY user_id ORDER BY event_time ROWS UNBOUNDED PRECEDING) canonical_session FROM gaps)
      SELECT e.* EXCLUDE(rebuilt_session),ids.canonical_session AS rebuilt_session
      FROM read_parquet(?) e JOIN ids USING(user_id,event_time)""",params=[str(path),str(path)])
    global QUERY
    QUERY=QUERY.replace('read_parquet(?)','canonical_events')
    ctr=features(path,'2019-10-01','2020-01-01'); cte=features(path,'2019-11-30','2020-03-01')
    cm=RandomForestClassifier(**PARAMS).fit(ctr[FEATURES],yt)
    cp=cm.predict_proba(cte[FEATURES])[:,1]
    canonical=dict(results=evaluate(y,cp,cte),changed_train_users=int((tr[FEATURES]!=ctr[FEATURES]).any(axis=1).sum()),changed_test_users=int((te[FEATURES]!=cte[FEATURES]).any(axis=1).sum()))
    cache=duckdb.sql('SELECT count(*) n,count(distinct user_id) users,sum(churn) churn FROM read_parquet(?)',params=[str(root/'data/sample/user_features_v2.parquet')]).df().to_dict('records')[0]
    after={str(p.relative_to(root)):sha(p) for p in protected}; assert before==after
    result=dict(design='Fixed single temporal backtest; same users may recur. No tuning, calibration, or random-split refit.',windows=windows,observation_days=92,label_days=60,threshold=.7,features=FEATURES,params=PARAMS,train_n=len(tr),train_churn_rate=float(yt.mean()),test_seen_users=int(overlap.sum()),audit=audit,monthly=monthly,session_check=session_check,original_cache=cache,results=groups,canonical_session_sensitivity=canonical,source_sha256=before,protected_files_unchanged=True,script_sha256=sha(Path(__file__)),environment=dict(python=platform.python_version(),duckdb=duckdb.__version__,sklearn=sklearn.__version__,numpy=np.__version__,pandas=pd.__version__),ranking='K=floor(N*fraction); RF boundary ties use exact random-tie expectation; rule uses exact expectation plus seeded 1000-repeat mean.',limitations=['Historical sampled population selected using user IDs across all seven months: conditional backtest, not fully point-in-time population sampling.','Training label interval overlaps later feature interval, but all training labels mature at test cutoff; no late outcome enters fit.','Original observation period 152 days vs 92 here; original March-April target 61 days vs exact 60 here.','Single period, no untouched model-selection holdout; fixed parameters were previously chosen on related data.','Absence of recorded purchase means observed churn, not verified account closure; no data beyond April.'])
    a.output_dir.mkdir(parents=True); (a.output_dir/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
