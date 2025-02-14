import pandas as pd
import xgboost as xgb
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

class myXGBOOST:
    def __init__(self, lag=3, model_path='xgboost_model.pkl'):
        self.lag = lag
        self.model_path = model_path
        self.model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, max_depth=5)

    def create_lag_features(self, df):
        """
        根据滞后窗口大小创建滞后特征。
        """
        features = []
        for i in range(self.lag, len(df)):
            row = []
            for j in range(1, self.lag+1):
                row.append(df['feature_1'][i-j])  # feature_1_t-1, feature_1_t-2, ...
                row.append(df['feature_2'][i-j])  # feature_2_t-1, feature_2_t-2, ...
                row.append(df['feature_3'][i-j])  # feature_3_t-1, feature_3_t-2, ...
            row.append(df['target'][i])  # 目标值
            features.append(row)
        return pd.DataFrame(features, columns=[f'feature_1_t-{i}' for i in range(1, self.lag+1)] +
                            [f'feature_2_t-{i}' for i in range(1, self.lag+1)] +
                            [f'feature_3_t-{i}' for i in range(1, self.lag+1)] + ['target'])

    def train(self, df):
        """
        训练模型并保存到本地
        """
        # 创建滞后特征
        df_lag = self.create_lag_features(df)

        # 提取特征和目标变量
        X = df_lag.drop(columns=['target'])
        y = df_lag['target']

        # 划分数据集
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

        # 训练模型
        self.model.fit(X_train, y_train)

        # 预测并评估模型
        y_pred = self.model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        print(f'Training RMSE: {rmse}')
        print(f'Training MAE: {mae}')
        print(f'Training R²: {r2}')

        # 保存模型
        joblib.dump(self.model, self.model_path)
        print(f'Model saved to {self.model_path}')

    def test(self, df):
        """
        加载模型并进行测试
        """
        # 加载模型
        self.model = joblib.load(self.model_path)

        # 创建滞后特征
        df_lag = self.create_lag_features(df)

        # 提取特征和目标变量
        X = df_lag.drop(columns=['target'])
        y = df_lag['target']

        # 划分数据集
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

        # 预测并评估模型
        y_pred = self.model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        print(f'Test RMSE: {rmse}')
        print(f'Test MAE: {mae}')
        print(f'Test R²: {r2}')

def main():
    # 模拟一个示例数据集
    data = {
        'date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06'],
        'feature_1': [10, 12, 15, 16, 18, 20],
        'feature_2': [5, 6, 7, 8, 9, 10],
        'feature_3': [3, 4, 5, 6, 7, 8],
        'target': [20, 22, 25, 30, 35, 40]
    }

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])

    # 创建myXGBOOST对象
    model = myXGBOOST(lag=3, model_path='xgboost_model.pkl')

    # 训练模型
    print("Training the model...")
    model.train(df)

    # 测试模型
    print("\nTesting the model...")
    model.test(df)

if __name__ == "__main__":
    main()
