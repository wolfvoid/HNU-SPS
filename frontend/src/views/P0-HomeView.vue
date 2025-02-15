<template>
    <div class="home">
    <!-- 欢迎标题 -->
    <h2>欢迎来到我们的平台</h2>
    <p>这是一个关于数据分析和预测的系统，我们提供实时的模型预测和数据可视化功能。</p>
    <p>在这里，您可以选择不同的时间数据库，管理数据库中的时间序列数据，进行多种操作。</p>
    <p>通过上传 CSV 文件，您还可以将本地数据导入到我们的 SQL 数据库中，进行进一步分析。</p>
    <p>我们还提供了一个预测功能，能够根据历史数据进行精准的时间序列预测。</p>

    <!-- 图片3 -->
    <img :src="require('@/assets/wencheng.png')" alt="欢迎图片3" class="image" />
    </div>
</template>

<script>
export default {
    name: 'HomeView',
};
</script>

<style scoped>
.home {
    padding: 20px;
    font-family: Arial, sans-serif;
}

h2 {
    color: #2C3E50;
    font-size: 28px;
    margin-bottom: 20px;
}

p {
    font-size: 18px;
    line-height: 1.6;
    color: #34495E;
    margin-bottom: 15px;
}

.image {
    width: 100%;
    max-width: 600px;
    height: auto;
    margin-bottom: 20px;
}
</style>
