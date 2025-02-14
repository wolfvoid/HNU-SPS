import pandas as pd
import numpy as np

class myDataLoader:
    def __init__(self, file_path, batch_size=3, device_id=None):
        # 读取CSV文件
        self.df = pd.read_csv(file_path)
        # 确保数据按设备编号和时间排序
        self.df['时间'] = pd.to_datetime(self.df['时间'], errors='coerce')
        self.df = self.df.sort_values(by=['设备编号', '时间'])
        self.batch_size = batch_size
        self.device_id = device_id  # 可选的设备编号筛选

    def preprocess(self):
        # 提取我们关心的列：设备编号、时间、采集值x、y、z
        self.df_filtered = self.df[['设备编号', '时间', '采集值x', '采集值y', '采集值z']].dropna()

        # 如果指定了设备编号，则只筛选该设备的数据
        if self.device_id:
            self.df_filtered = self.df_filtered[self.df_filtered['设备编号'] == self.device_id]

    def generate_batches(self):
        batch_count = 0
        # 根据设备编号分组
        device_groups = self.df_filtered.groupby('设备编号')

        # 遍历每个设备编号的分组，生成连续时间的批次
        for device, group in device_groups:
            # 按时间排序
            group = group.sort_values(by='时间')
            # 将数据切割成多个批次
            for start in range(0, len(group), self.batch_size):
                batch = group.iloc[start:start + self.batch_size]
                # 检查每个批次是否足够大
                if len(batch) == self.batch_size:
                    batch_count += 1
                    # 返回设备编号、时间序列和采集值
                    yield batch[['设备编号', '时间', '采集值x', '采集值y', '采集值z']]

        print(f"Total batches generated: {batch_count}")  # 输出总共生成了多少组batch

# 测试该类
def test_data_loader(file_path, device_id=None):
    # 创建DataLoader实例
    data_loader = myDataLoader(file_path, batch_size=10)
    data_loader.preprocess()

    # 生成并打印每个批次数据
    temp = 0
    for batch in data_loader.generate_batches():
        print(batch)
        print("\n---\n")
        temp += 1
        if temp > 10:
            break

# 假设你已经上传了文件，可以测试：
file_path = r"E:\Code_files\时空\data\长寨社区市布鞋厂宿舍楼后滑坡.csv"
device_id = 431271010011010101  # 可修改为需要的设备编号
test_data_loader(file_path, device_id=device_id)
