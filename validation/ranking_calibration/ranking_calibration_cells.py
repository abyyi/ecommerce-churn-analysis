"""Notebook cells for churn-risk ranking, a tie-aware browsing baseline,
and probability-calibration diagnostics.

Run the cells in order from the project notebooks/ directory after loading
user_features_v2 with the exploratory notebook. Requires NumPy, pandas,
scikit-learn, Matplotlib and notebook display. This is a cell-oriented analysis,
not a standalone command-line program. Load only a trusted model pickle.
"""
# %% model_load
import pickle
import numpy as np
import pandas as pd

# 加载已保存的15特征模型
with open("../data/sample/churn_model_v2.pkl", "rb") as f:
    saved = pickle.load(f)

model = saved["model"]
features = saved["features"]

print("模型特征数量：", len(features))
print("预测阈值：", saved["threshold"])



# %% test_split
from sklearn.model_selection import train_test_split

# 使用模型原来的15个特征
X = user_features_v2[features].fillna(0)
y = user_features_v2["churn"]

# 复现原来的训练集和测试集划分
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# 预测测试用户的流失概率
y_prob = model.predict_proba(X_test)[:, 1]

print("测试用户数量：", len(X_test))
print("测试集流失率：", round(y_test.mean() * 100, 2), "%")



# %% ranking
# 整理测试集预测结果
risk_results = pd.DataFrame({
    "user_id": user_features_v2.loc[X_test.index, "user_id"].values,
    "actual_churn": y_test.values,
    "predicted_probability": y_prob
})

# 按预测流失概率从高到低排序
risk_results = risk_results.sort_values(
    "predicted_probability", ascending=False
).reset_index(drop=True)

# 测试集整体流失率
baseline_rate = risk_results["actual_churn"].mean()

# 计算不同筛选比例下的效果
results = []

for pct in [0.1, 0.2, 0.3]:
    k = int(len(risk_results) * pct)
    top_k = risk_results.head(k)

    precision = top_k["actual_churn"].mean()
    lift = precision / baseline_rate

    results.append({
        "Top %": f"{int(pct * 100)}%",
        "Users": k,
        "Precision@K": round(precision, 4),
        "Lift@K": round(lift, 4)
    })

lift_table = pd.DataFrame(results)
display(lift_table)



# %% rule_random_ties
# 对简单规则中的并列用户随机排序，重复1000次
rng = np.random.default_rng(42)

rule_views = X_test["recent_30d_views"].to_numpy()
actual = y_test.to_numpy()

rule_results_avg = []

for pct in [0.1, 0.2, 0.3]:
    k = int(len(actual) * pct)
    precisions = []

    for _ in range(1000):
        random_order = rng.permutation(len(actual))

        # 浏览次数少的排前面；相同时随机排序
        ranking = np.lexsort((
            random_order,
            rule_views
        ))

        selected = ranking[:k]
        precisions.append(actual[selected].mean())

    avg_precision = np.mean(precisions)

    rule_results_avg.append({
        "Top %": f"{int(pct * 100)}%",
        "RF Precision@K": round(
            risk_results.head(k)["actual_churn"].mean(), 4
        ),
        "Rule Avg Precision@K": round(avg_precision, 4),
        "Rule Avg Lift@K": round(
            avg_precision / baseline_rate, 4
        )
    })

fair_comparison = pd.DataFrame(rule_results_avg)
display(fair_comparison)



# %% calibration
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve
from sklearn.metrics import brier_score_loss

# 计算校准曲线
prob_true, prob_pred = calibration_curve(
    y_test,
    y_prob,
    n_bins=10,
    strategy="quantile"
)

plt.figure(figsize=(6, 5))

# 理想情况：预测概率 = 实际流失率
plt.plot([0, 1], [0, 1], "--", label="Perfect Calibration")

# 当前模型
plt.plot(prob_pred, prob_true, "o-", label="Random Forest")

plt.xlabel("Predicted Churn Probability")
plt.ylabel("Actual Churn Rate")
plt.title("Probability Calibration Curve")
plt.legend()
plt.grid(alpha=0.3)
plt.show()

# Brier Score：越低越好
print("Brier Score:", round(brier_score_loss(y_test, y_prob), 4))


