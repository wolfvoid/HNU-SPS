<template>
    <div class="prediction-page">
        <h2>开始预测</h2>
        <p>当前选择的数据库：{{ databaseName }}</p>

        <!-- 按钮区域 -->
        <div class="button-container">
            <button class="start-btn" @click="startInference">开始预测</button>
            <button class="alert-btn" @click="toggleAlert">{{ alertButtonText }}</button>
            <button class="back-btn" @click="goBack">返回</button>
        </div>

        <!-- 显示推理结果 -->
        <div class="charts-container">
            <div v-for="(chartData, index) in chartsData" :key="index" class="chart-box">
                <div class="chart-title">{{ chartData.title }}</div>
                <div ref="chart" :id="'chart-' + index" class="chart"></div>
                <div class="rate">变化率：{{ chartData.rate }}</div>
            </div>
        </div>
    </div>
</template>

<script>
import { io } from "socket.io-client";
import * as echarts from "echarts";

export default {
    name: "PredictionPage",
    props: {
        databaseName: String, // 从路由传递的参数
    },
    data() {
        return {
            socket: null,
            alertButtonText: "开启预警", // 默认按钮文本
            alertShow: false,  // 控制警报线显示
            chartsData: [
                { title: "X 采集值", data: [], rate: 0, upperLimit: [], lowerLimit: [] },
                { title: "Y 采集值", data: [], rate: 0, upperLimit: [], lowerLimit: [] },
                { title: "Z 采集值", data: [], rate: 0, upperLimit: [], lowerLimit: [] },
                { title: "加权综合评判值", data: [], rate: 0, upperLimit: [], lowerLimit: [] },
            ],
        };
    },
    methods: {
        // 开始推理请求
        startInference() {
            // 清空当前图表数据
            this.chartsData.forEach(chartData => {
                chartData.data = [];
                chartData.upperLimit = [];
                chartData.lowerLimit = [];
                chartData.rate = 0;
            });

            if (!this.socket) {
                this.socket = io("http://localhost:5000"); // 与后端建立连接
            }

            this.socket.on("connect", () => {
                console.log("Connected to server");
                this.socket.emit("start_prediction", { database: this.databaseName }); // 发送数据库信息和推理开始信号
            });

            this.socket.on("connected", (data) => {
                console.log(data.message); // 连接成功的消息
            });

            this.socket.on("inference_result", (data) => {
                console.log("Received result from backend:", data);

                // 更新每个图表的数据
                this.chartsData.forEach((chartData, index) => {
                    const key = ["x", "y", "z", "weighted"][index]; // 获取图表数据的对应字段
                    const currentData = data[key];  // 获取当前字段的数据
                    if (currentData && currentData.length > 0) {
                        chartData.data.push(currentData[0]);  // 添加数据中的第一个值
                        chartData.upperLimit.push(currentData[1]); // 上界
                        chartData.lowerLimit.push(currentData[2]); // 下界
                        chartData.rate = currentData[3]; // 更新变化率
                    }
                });

                // 在图表渲染后更新显示
                this.$nextTick(() => {
                    this.updateCharts(); // 更新图表
                });
            });
        },

        // 更新图表
        updateCharts() {
            this.chartsData.forEach((chartData, index) => {
                const chart = this.$refs.chart[index]; // 获取每个图表的 DOM 引用
                if (chart) {
                    const myChart = echarts.getInstanceByDom(chart) || echarts.init(chart);
                    const option = {
                        title: {
                            text: chartData.title,
                        },
                        tooltip: {
                            trigger: "axis",
                        },
                        xAxis: {
                            type: "category",
                            data: this.chartsData[0].data.map((_, i) => `Time ${i + 1}`), // 用时间作为x轴标签
                        },
                        yAxis: {
                            type: "value",
                            min: 0,
                        },
                        series: [
                            {
                                name: "数据值",
                                type: "line",
                                data: chartData.data,
                                itemStyle: {
                                    color: "#1f77b4", // 蓝色数据值
                                },
                            },
                            {
                                name: "上界",
                                type: "line",
                                data: chartData.upperLimit,
                                lineStyle: {
                                    color: "#e74c3c", // 红色
                                    type: "dashed",
                                    opacity: this.alertShow ? 1 : 0, // 控制上界显示
                                },
                                symbol: this.alertShow ? 'circle' : 'none', // 控制上界点显示
                                symbolSize: 6,
                                itemStyle: {
                                    color: this.alertShow ? "#e74c3c" : "transparent", // 红色点
                                },
                            },
                            {
                                name: "下界",
                                type: "line",
                                data: chartData.lowerLimit,
                                lineStyle: {
                                    color: "#f1c40f", // 黄色
                                    type: "dashed",
                                    opacity: this.alertShow ? 1 : 0, // 控制下界显示
                                },
                                symbol: this.alertShow ? 'circle' : 'none', // 控制下界点显示
                                symbolSize: 6,
                                itemStyle: {
                                    color: this.alertShow ? "#f1c40f" : "transparent", // 黄色点
                                },
                            },
                        ],
                    };

                    // 设置选项并渲染图表
                    myChart.resize();
                    myChart.setOption(option);
                }
            });
        },

        // 切换警报状态
        toggleAlert() {
            this.alertShow = !this.alertShow;
            this.alertButtonText = this.alertShow ? "关闭预警" : "开启预警";
            this.updateCharts();// 立即更新图表状态
        },

        // 返回上一页面
        goBack() {
            this.$router.go(-1); // 返回上一页
        },
    },

    unmounted() {
        if (this.socket) {
            this.socket.disconnect(); // 在组件销毁时断开连接
            console.log("Disconnected from server");
        }
    },
};
</script>

<style scoped>
.prediction-page {
    padding: 20px;
    font-family: Arial, sans-serif;
}

h2 {
    color: #2c3e50;
    font-size: 28px;
    margin-bottom: 20px;
}

p {
    font-size: 18px;
    color: #555;
}

.button-container {
    margin-top: 30px;
}

button {
    padding: 10px 20px;
    font-size: 16px;
    margin: 10px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

.start-btn {
    background-color: #28a745;
    /* 绿色按钮 */
    color: white;
}

.alert-btn {
    background-color: #dc3545;
    /* 红色按钮 */
    color: white;
}

.back-btn {
    background-color: #fd7e14;
    /* 橙色按钮 */
    color: white;
}

.charts-container {
    display: flex;
    flex-wrap: wrap;
    margin-top: 40px;
}

.chart-box {
    width: 45%;
    margin: 20px 2%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 8px;
}

.chart-title {
    text-align: center;
    font-size: 20px;
    margin-bottom: 10px;
}

.chart {
    width: 100%;
    height: 300px;
}

.rate {
    margin-top: 10px;
    font-size: 16px;
    color: #888;
}
</style>
