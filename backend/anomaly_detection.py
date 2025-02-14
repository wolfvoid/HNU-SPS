import numpy as np
import pandas as pd

class AnomalyDetection:
    def __init__(self, data, threshold=1.0, rate_threshold=1.0, k=2.0, batch_size=1):
        # 输入数据
        self.df = pd.DataFrame(data)
        self.threshold = threshold  # 用于判断是否发生异变的变化率阈值
        self.rate_threshold = rate_threshold  # 用于判断是否发生异变的变化率阈值
        self.k = k  # 用于计算上下界的标准差倍数
        self.batch_size = batch_size

    def calculate_rate_of_change(self):
        """
        计算每个特征的变化率
        """
        # 计算变化率 (差值)
        self.df['delta_feature_1'] = self.df['feature_1'].diff().abs()
        self.df['delta_feature_2'] = self.df['feature_2'].diff().abs()
        self.df['delta_feature_3'] = self.df['feature_3'].diff().abs()

    def calculate_multidimensional_change(self):
        """
        计算三维变化率的欧几里得范数（多维聚合变化）
        """
        self.df['delta_combined'] = np.sqrt(
            self.df['delta_feature_1']**2 +
            self.df['delta_feature_2']**2 +
            self.df['delta_feature_3']**2
        )

    def calculate_statistics(self):
        """
        计算历史数据的均值和标准差
        """
        self.mean_feature_1 = self.df['feature_1'].mean()
        self.std_feature_1 = self.df['feature_1'].std()

        self.mean_feature_2 = self.df['feature_2'].mean()
        self.std_feature_2 = self.df['feature_2'].std()

        self.mean_feature_3 = self.df['feature_3'].mean()
        self.std_feature_3 = self.df['feature_3'].std()

    def detect_anomalies(self):
        """
        检测每个特征的异常值，并返回结果。

        输入:
        - 无直接输入参数。函数使用类的实例变量（即历史数据和阈值）来计算异常。

        过程:
        - 对每个特征（`feature_1`, `feature_2`, `feature_3`）计算变化率（`delta_*`）。
        - 基于历史数据计算每个特征的均值和标准差。
        - 根据历史均值和标准差计算上下界，定义正常波动范围。
        - 如果特征值超出上下界，且变化率超过指定的阈值（`rate_threshold`），则认为发生异常。
        - 同时计算三维变化的欧几里得范数并判断整体异常。

        输出:
        - 返回一个列表，包含每个特征及整体的异常检测结果，格式如下：

        [
            [upper_bound_feature_1, lower_bound_feature_1, current_rate_of_change_feature_1, anomaly_detected_feature_1],
            [upper_bound_feature_2, lower_bound_feature_2, current_rate_of_change_feature_2, anomaly_detected_feature_2],
            [upper_bound_feature_3, lower_bound_feature_3, current_rate_of_change_feature_3, anomaly_detected_feature_3],
            [upper_bound_combined, lower_bound_combined, current_combined_rate_of_change, anomaly_detected_combined]
        ]

        其中：
        - `upper_bound_feature_x`：特征 `x` 的上界（基于历史均值和标准差计算）。
        - `lower_bound_feature_x`：特征 `x` 的下界（基于历史均值和标准差计算）。
        - `current_rate_of_change_feature_x`：特征 `x` 当前的变化率（即相邻时间点的差值）。
        - `anomaly_detected_feature_x`：布尔值，表示特征 `x` 是否发生异常（如果当前值超出上下界，且变化率超过阈值）。
        - `upper_bound_combined`：整体变化的上界（基于所有特征的变化率计算）。
        - `lower_bound_combined`：整体变化的下界（基于所有特征的变化率计算）。
        - `current_combined_rate_of_change`：整体变化的变化率（所有特征变化的欧几里得范数）。
        - `anomaly_detected_combined`：布尔值，表示是否发生整体异常（如果综合变化超过上下界，且变化率超过阈值）。
        """

        self.calculate_rate_of_change()
        self.calculate_multidimensional_change()
        self.calculate_statistics()

        results = []

        for feature in ['feature_1', 'feature_2', 'feature_3']:
            # 基于历史数据的均值和标准差来计算上下界
            if feature == 'feature_1':
                mean = self.mean_feature_1
                std = self.std_feature_1
            elif feature == 'feature_2':
                mean = self.mean_feature_2
                std = self.std_feature_2
            elif feature == 'feature_3':
                mean = self.mean_feature_3
                std = self.std_feature_3

            # 上下界基于历史的均值和标准差
            upper_bound = mean + self.k * std
            lower_bound = mean - self.k * std

            # 当前变化率
            delta_col = f'delta_{feature}'
            current_rate_of_change = self.df[delta_col].iloc[-1]

            # 异常检测：同时考虑数值和变化率
            last_value = self.df[feature].iloc[-1]
            anomaly_detected = (last_value > upper_bound or last_value < lower_bound) and \
                               (current_rate_of_change > self.rate_threshold)

            results.append([upper_bound, lower_bound, current_rate_of_change, anomaly_detected])

        # 计算整体的变化：欧几里得范数的上界、下界
        last_combined_change = self.df['delta_combined'].iloc[-1]
        upper_bound_combined = self.df['delta_combined'].max() + self.threshold
        lower_bound_combined = self.df['delta_combined'].min() - self.threshold

        # 整体变化的异常检测
        anomaly_detected_combined = (last_combined_change > self.rate_threshold) and \
                                     (last_combined_change > upper_bound_combined or last_combined_change < lower_bound_combined)

        # 最后一行是整体的上界、下界、当前变化率和是否异变
        results.append([upper_bound_combined, lower_bound_combined, last_combined_change, anomaly_detected_combined])

        return results

# 示例数据
data = {
    'date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06'],
    'feature_1': [10, 12, 15, 16, 18, 20],
    'feature_2': [5, 6, 7, 8, 9, 10],
    'feature_3': [3, 4, 5, 6, 7, 8]
}

# 创建AnomalyDetection实例，增加阈值和k值
anomaly_detector = AnomalyDetection(data, threshold=0.5, rate_threshold=0.05, k=2.0)

# 检测异常并获取结果
results = anomaly_detector.detect_anomalies()

# 打印结果
print("结果: 每个特征的上界、下界、当前变化率和是否发生异变")
for i, result in enumerate(results):
    print(f"特征 {i+1} -> 上界: {result[0]}, 下界: {result[1]}, 当前变化率: {result[2]}, 是否异变: {result[3]}")
