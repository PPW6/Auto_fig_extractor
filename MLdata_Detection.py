import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler

# 1. 读取数据
df = pd.read_excel("test.xlsx")
df.replace('-', 0, inplace=True)
if 'SampleID' not in df.columns:
    df['SampleID'] = np.arange(len(df))

# 2. 构建特征向量
element_cols = ['Cu', 'Ag', 'Al', 'B', 'Ce', 'Co', 'Cr', 'Er', 'Fe', 'Hf',
                'Mg', 'Mn', 'Nb', 'Ni', 'Sc', 'Si', 'Sn', 'Ti', 'Y', 'Zn', 'Zr']
process_cols = ['homogenization temperature (℃)', 'homogenization time (h)',
                'solution temperature (℃)', 'solution time (h)', 'CR1', 'Temp1 (℃)', 'time1 (h)', 'CR2',
                'Temp2 (℃)', 'time2 (h)', 'CR3', 'Temp3 (℃)', 'time3 (h)']

X = df[element_cols + process_cols].values
scaler = StandardScaler()
X[:, len(element_cols):] = scaler.fit_transform(X[:, len(element_cols):])

# 3. 聚类
cos_sim = cosine_similarity(X)
distance_matrix = 1 - cos_sim
clustering = AgglomerativeClustering(
    n_clusters=None, metric='precomputed', linkage='complete', distance_threshold=0.15)
df['GroupID'] = clustering.fit_predict(distance_matrix)

# 4. 异常值检测
def robust_z_score(series):
    median = series.median()
    mad = np.median(np.abs(series - median))
    z = 0.6745 * (series - median) / mad if mad != 0 else pd.Series(0, index=series.index)
    return z

def detect_outliers(df, property_col='y_data', threshold=3.5):
    df['Outlier'] = False
    for group, group_df in df.groupby('GroupID'):
        z = robust_z_score(group_df[property_col])
        outlier_idx = group_df.index[np.abs(z) > threshold]
        df.loc[outlier_idx, 'Outlier'] = True
    return df

df = detect_outliers(df, property_col='y_data', threshold=3.5)

# 5. 加权融合（仅完全一致）
df['weight'] = df['source_reliability']
df.loc[df['Outlier'], 'weight'] *= 0.1

df['composition_process_key'] = df[element_cols + process_cols].astype(str).agg('-'.join, axis=1)

def weighted_stats_exact_match(group, value_col='y_data', weight_col='weight'):
    stats_list = []
    for key, sub_group in group.groupby('composition_process_key'):
        values = sub_group[value_col].values
        weights = sub_group[weight_col].values
        weighted_mean = np.sum(values * weights) / np.sum(weights)
        weighted_var = np.sum(weights * (values - weighted_mean)**2) / np.sum(weights)
        weighted_std = np.sqrt(weighted_var)
        stats_list.append(pd.DataFrame({
            'SampleID': sub_group['SampleID'],
            'Property_Fused': weighted_mean,
            'Property_Uncertainty': weighted_std,
            'Count': len(values)
        }))
    return pd.concat(stats_list)

group_stats = df.groupby('GroupID').apply(weighted_stats_exact_match).reset_index(drop=True)
df = df.merge(group_stats[['SampleID','Property_Fused','Property_Uncertainty']], on='SampleID', how='left')

df.to_excel("materials_data_fused_exact_match.xlsx", index=False)
print("融合后的性能数据已保存：materials_data_fused_exact_match.xlsx")
