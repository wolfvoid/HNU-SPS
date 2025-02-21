import numpy as np


class TimeSeriesForecaster:
    def __init__(self, data: np.ndarray, T: int, T_prime: int):
        """
        初始化预测器。
        :param data: 输入数据，形状为 (T+T', C, V)
        :param T: 过去时间步长
        :param T_prime: 预测时间步长
        :param reference: 向前参考时间步长，默认为 T
        """
        self.data = data
        self.T = T
        self.T_prime = T_prime
        self.C, self.V = data.shape[1], data.shape[2]
        self.reference = T

    def _compute_bounds(self):
        """
            计算每个时刻 T' 使用前 T 步的均值和上下界。
            :return: 下界 (T', C, V), 上界 (T', C, V)
            """
        lower_bound = np.zeros((self.T_prime, self.C, self.V))
        upper_bound = np.zeros((self.T_prime, self.C, self.V))
        for t in range(self.T_prime):
            past_data = self.data[t:t + self.reference, :, :]
            mean = np.mean(past_data, axis=0)
            std = np.std(past_data, axis=0)
            lower_bound[t, :, :] = mean - 2 * std
            upper_bound[t, :, :] = mean + 2 * std
        return lower_bound, upper_bound

    def history_weighted(self):
        """
        计算历史数据的加权和
        :return: (T, C)，表示加权后的历史数据
            """
        history_data = self.data[:self.T, :, :]
        valid_counts = np.sum(history_data != 0, axis=-1)
        valid_counts[valid_counts == 0] = 1
        weighted_history = np.sum(history_data, axis=-1) / valid_counts
        return weighted_history

    def _compute_weighted_sum(self, data: np.ndarray):
        """
        计算加权 V 维度并得到 T'*C 维度的数据。
        :param data: 输入数据，形状为 (T', C, V)
        :return: (T', C) 维度的加权数据
        """
        valid_mask = data != 0  # 计算非零项的掩码
        valid_counts = np.sum(valid_mask, axis=-1,
                              keepdims=True)  # 计算非零项个数 (T', C, 1)
        valid_counts[valid_counts == 0] = 1  # 避免除零

        weighted_data = np.sum(data * valid_mask, axis=-1) / \
            valid_counts.squeeze(-1)  # 对 V 维度求加权平均
        return weighted_data

    def forward(self):
        """
        执行前向预测
        输出:
        - weighted_result: 一个形状为 (T', C) 的 numpy 数组，表示加权后的预测数据
        - weighted_lower_bound: 一个形状为 (T', C) 的 numpy 数组，表示每个特征的下界
        - weighted_upper_bound: 一个形状为 (T', C) 的 numpy 数组，表示每个特征的上界
        """
        lower_bound, upper_bound = self._compute_bounds()
        future_data = self.data[self.T:, :, :]
        weighted_result = self._compute_weighted_sum(future_data)
        weighted_lower_bound = self._compute_weighted_sum(lower_bound)
        weighted_upper_bound = self._compute_weighted_sum(upper_bound)
        return weighted_result, weighted_lower_bound, weighted_upper_bound


if __name__ == '__main__':
    # 生成测试数据集
    T, T_prime, C, V = 10, 5, 3, 4  # 设定维度大小
    data = np.random.rand(T + T_prime, C, V)  # 生成随机数据

    # 实例化类
    forecaster = TimeSeriesForecaster(data, T, T_prime)
    result, lower_bound, upper_bound = forecaster.forward()
    history_weighted = forecaster.history_weighted()
    print("History Weighted Shape:", history_weighted.shape)  # 应该是(T, C)
    print("Weighted Result Shape:", result.shape)  # 应该是 (T', C)
    print("Lower Bound Shape:", lower_bound.shape)  # 应该是 (T', C)
    print("Upper Bound Shape:", upper_bound.shape)  # 应该是 (T', C)
