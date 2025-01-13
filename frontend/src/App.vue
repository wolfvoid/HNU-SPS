<template>
  <div id="app">
    <!-- 侧边栏 -->
    <div id="sidebar">
      <h2>功能选择</h2>
      <ul>
        <li><router-link to="/time-database">时间数据库管理</router-link></li>
        <li><router-link to="/csv-import">CSV 导入</router-link></li>
        <li><router-link to="/prediction">预测</router-link></li>
        <li><router-link to="/alert">预警功能</router-link></li>
      </ul>
    </div>

    <!-- 主内容区 -->
    <div id="main-content">
      <!-- 显示当前页面标题 -->
      <header>
        <h1>{{ currentPageTitle }}</h1>
      </header>

      <!-- 主要内容显示区域 -->
      <main>
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  computed: {
    // 获取当前页面的标题
    currentPageTitle() {
      const pageTitles = {
        '/': '主页面',
        '/time-database': '时间数据库管理',
        '/csv-import': 'CSV 文件导入',
        '/prediction': '预测',
        '/alert': '预警功能',
      };

      return pageTitles[this.$route.path] || '未知页面';
    },
  },
};
</script>

<style>
/* 基础字体和颜色设置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Arial', sans-serif;
  background-color: #f4f9fc;  /* 淡蓝色背景 */
  color: #333;
  line-height: 1.6;
}

a {
  text-decoration: none;
  color: inherit;
}

/* 侧边栏样式 */
#sidebar {
  width: 220px;
  position: fixed;
  top: 0;
  left: 0;
  height: 100%;
  background-color: #e0f7fa;  /* 淡蓝色 */
  padding: 20px;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
}

#sidebar h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #00796b;  /* 深绿色 */
  padding-bottom: 20px;
}

#sidebar ul {
  list-style-type: none;
  padding: 0;
}

#sidebar li {
  margin: 15px 0;
}

#sidebar a {
  font-size: 1rem;
  color: #00796b;  /* 深绿色 */
}

#sidebar a:hover {
  color: #004d40;  /* 更深的绿色 */
}

/* 主内容区样式 */
#main-content {
  margin-left: 240px;  /* 留出侧边栏位置 */
  padding: 20px;
}

header {
  background-color: #ffffff;  /* 白色背景 */
  padding: 10px;
  border-bottom: 1px solid #00796b;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

header h1 {
  margin: 0;
  font-size: 1.8rem;
  color: #00796b;  /* 深绿色 */
}

main {
  padding: 20px;
  background-color: #ffffff;  /* 白色背景 */
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  margin-top: 20px;
}

/* 首页样式 */
header h1 {
  font-size: 2rem;
  color: #00796b;
}

header p {
  font-size: 1.2rem;
  color: #555;
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  #sidebar {
    width: 100%;
    height: auto;
    position: static;
    padding: 10px;
  }

  #main-content {
    margin-left: 0;
  }

  header {
    padding: 15px;
  }
}
</style>
