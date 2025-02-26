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
                <div :id="'chart-' + index" class="chart"></div>
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
            alertButtonText: "开启预警",
            alertShow: false,
            chartsData: [],
            charts: [] // 存储 ECharts 实例
        };
    },
    methods: {
        // 开始推理请求
        startInference() {
            // 清空当前图表数据
            this.chartsData = [];
            this.charts = [];

            if (!this.socket) {
                this.socket = io("http://localhost:5000");
            }

            this.socket.on("connect", () => {
                console.log("Connected to server");
                this.socket.emit("start_prediction", { database: this.databaseName });
            });

            this.socket.on("connected", (data) => {
                console.log(data.message);
            });

            // 处理历史数据
            this.socket.on("inference_result", (data) => {
                console.log("Received result from backend:", data);

                if (data.history_weighted) {
                    this.processHistoryData(data.history_weighted);
                } else if (data.predicted_weighted) {
                    this.processPredictionData(data);
                }
            });
        },

        // 处理历史数据
        processHistoryData(history_weighted) {
            if (this.chartsData.length === 0) {
                Object.keys(history_weighted[0]).forEach((key, index) => {
                    this.chartsData.push({
                        title: `变量 ${index + 1}`,
                        historyData: [],
                        predictedData: [],
                        upperLimit: [],
                        lowerLimit: [],
                        rate: 0
                    });
                });
            }

            this.chartsData.forEach((chartData, index) => {
                const key = Object.keys(history_weighted[0])[index];
                chartData.historyData = history_weighted.map(item => item[key]);
            });

            this.$nextTick(() => {
                this.initCharts();
            });
        },

        // 处理预测数据
        processPredictionData({ predicted_weighted, upper_bound, lower_bound }) {
            this.chartsData.forEach((chartData, index) => {
                const key = Object.keys(predicted_weighted[0])[index];

                chartData.predictedData.push(...predicted_weighted.map(item => item[key]));
                chartData.upperLimit.push(...upper_bound.map(item => item[key]));
                chartData.lowerLimit.push(...lower_bound.map(item => item[key]));
            });

            this.$nextTick(() => {
                this.updateCharts();
            });
        },

        // 初始化图表
        initCharts() {
            this.chartsData.forEach((chartData, index) => {
                const chartDom = document.getElementById(`chart-${index}`);
                if (!chartDom) return;

                const myChart = echarts.init(chartDom);
                this.charts[index] = myChart;

                myChart.setOption({
                    title: {
                        text: chartData.title,
                    },
                    tooltip: {
                        trigger: "axis",
                        axisPointer: {
                            type: "line"
                        },
                    },
                    xAxis: {
                        type: "category",
                        data: chartData.historyData.map((_, i) => `Time ${i + 1}`)
                    },
                    yAxis: {
                        type: "value",
                        min: 0,
                    },
                    series: [
                        {
                            name: "历史数据",
                            type: "line",
                            data: chartData.historyData,
                            itemStyle: { color: "#000000" } // 历史数据改为黑色
                        }
                    ]
                });
            });
        },

        // 更新图表
        updateCharts() {
            this.chartsData.forEach((chartData, index) => {
                const myChart = this.charts[index];
                if (!myChart) return;

                const historyLength = chartData.historyData.length;
                const totalXData = [
                    ...chartData.historyData.map((_, i) => `Time ${i + 1}`),
                    ...chartData.predictedData.map((_, i) => `T' ${historyLength + i + 1}`)
                ];

                const lastHistoryValue = chartData.historyData[historyLength - 1];  //把预测数据添加一项，等于历史数据最后的值，这样就可以使预测值和历史值连续


                myChart.setOption({
                    tooltip: {
                        trigger: "axis",
                        axisPointer: {
                            type: "line"
                        },
                        formatter: function (params) {
                            let result = params[0].axisValue + "<br/>";
                            params.forEach(item => {
                                if (item.data !== null) {
                                    result += `${item.marker} ${item.seriesName}: ${item.data} <br/>`;
                                }
                            });
                            return result;
                        }
                    },
                    xAxis: {
                        type: "category",
                        data: totalXData
                    },
                    series: [
                        {
                            name: "历史数据",
                            type: "line",
                            data: chartData.historyData,
                            itemStyle: { color: "#000000" } // 确保历史数据颜色为黑色
                        },
                        {
                            name: "预测数据",
                            type: "line",
                            showSymbol: true,
                            symbolSize: 6,
                            data: [...new Array(historyLength - 1).fill(undefined), lastHistoryValue, ...chartData.predictedData],
                            itemStyle: { color: "#ff7f0e" }
                        },
                        {
                            name: "上界",
                            type: "line",
                            data: [...new Array(historyLength).fill(undefined), ...chartData.upperLimit],
                            lineStyle: {
                                color: "#e74c3c",
                                type: "dashed",
                                opacity: this.alertShow ? 1 : 0
                            },
                            symbol: this.alertShow ? 'circle' : 'none',
                            symbolSize: 6,
                            itemStyle: { color: this.alertShow ? "#e74c3c" : "transparent" }
                        },
                        {
                            name: "下界",
                            type: "line",
                            data: [...new Array(historyLength).fill(undefined), ...chartData.lowerLimit],
                            lineStyle: {
                                color: "#f1c40f",
                                type: "dashed",
                                opacity: this.alertShow ? 1 : 0
                            },
                            symbol: this.alertShow ? 'circle' : 'none',
                            symbolSize: 6,
                            itemStyle: { color: this.alertShow ? "#f1c40f" : "transparent" }
                        }
                    ]
                });
            });
        },

        // 切换警报状态
        toggleAlert() {
            this.alertShow = !this.alertShow;
            this.alertButtonText = this.alertShow ? "关闭预警" : "开启预警";
            this.updateCharts();
        },

        // 返回上一页面
        goBack() {
            this.$router.go(-1);
        }
    },

    unmounted() {
        if (this.socket) {
            this.socket.disconnect();
            console.log("Disconnected from server");
        }
    }
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
