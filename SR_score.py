import pandas as pd
import numpy as np

# -------------------------
# 1. 读取数据
# -------------------------
df_main = pd.read_excel("Cu-Cr-X dataset.xlsx")
df_journal = pd.read_excel("期刊分区表.xlsx")

# -------------------------
# 2. 标准化期刊名称并匹配
# -------------------------
df_main["Journal_clean"] = df_main["journal"].str.strip().str.lower()
df_journal["Journal_clean"] = df_journal["journal"].str.strip().str.lower()

df_merged = pd.merge(
    df_main,
    df_journal[["Journal_clean", "IF", "JCR"]],
    on="Journal_clean",
    how="left"
)

# -------------------------
# 3. 计算 source_reliability
# -------------------------
def compute_source_reliability(df, IF_max=12, current_year=2025):
    def norm_if(x):
        if pd.isna(x):
            return 0.5
        return np.log1p(x) / np.log1p(IF_max)

    def score_q(q):
        mapping = {
            1: 1.0,
            2: 0.85,
            3: 0.7,
            4: 0.55,
            "not indexed": 0.3
        }
        if isinstance(q, str) and q.strip().isdigit():
            q = int(q)
        return mapping.get(q, 0.5)

    def score_year(y):
        if pd.isna(y):
            return 0.7
        return max(0.6, 1 - 0.03 * (current_year - y))

    def score_type(t):
        t = str(t).lower() if not pd.isna(t) else ""
        if t.startswith("exp"):
            return 1.0
        elif "review" in t:
            return 0.9
        else:
            return 0.7

    if "Type" not in df.columns:
        df["Type"] = "exp"

    df["S_IF"] = df["IF"].apply(norm_if)
    df["S_Q"] = df["JCR"].apply(score_q)
    df["S_Y"] = df["year"].apply(score_year)
    df["S_T"] = df["Type"].apply(score_type)

    reliability = (
        0.4 * df["S_IF"] +
        0.3 * df["S_Q"] +
        0.2 * df["S_Y"] +
        0.1 * df["S_T"]
    ).clip(0, 1)

    return reliability

# -------------------------
# 4. 计算并回写到 df_main
# -------------------------
df_main["source_reliability"] = compute_source_reliability(df_merged)

# -------------------------
# 5. 保存结果
# -------------------------
df_main.to_excel("Cu-Cr-X_dataset_with_reliability.xlsx", index=False)
print("✅ 已将 source_reliability 添加到原始数据表 Cu-Cr-X_dataset_with_reliability.xlsx")
