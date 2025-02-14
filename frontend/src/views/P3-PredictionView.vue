<template>
    <div>
        <h2>预测</h2>
        <button @click="startInference">开始推理</button>
        <div v-for="(result, index) in results" :key="index">
            <p>Step {{ result.step }}: {{ result.result }}</p>
        </div>
    </div>
</template>

<script>
import { io } from 'socket.io-client';

export default {
    name: 'PredictionView',
    data() {
        return {
            socket: null,
            results: []
        };
    },
    methods: {
        startInference() {
            if (!this.socket) {
                this.socket = io('http://localhost:5000');  // 与后端建立连接
            }

            this.socket.on('connect', () => {
                console.log('Connected to server');
                this.socket.emit('start_prediction', {});  // 发送开始推理的信号
            });

            this.socket.on('connected', (data) => {
                console.log(data.message);  // 应该输出 "Connection established"
            });

            // 接收推理结果
            this.socket.on('inference_result', (data) => {
                console.log('Received result from backend:', data);
                this.results.push(data);  // 每次推理结果添加到 results 数组
            });
        }
    },
    unmounted() {
        if (this.socket) {
            this.socket.disconnect();  // 在组件销毁时断开连接
            console.log('Disconnected from server');
        }
    }
};
</script>
