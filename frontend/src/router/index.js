import { createRouter, createWebHistory } from 'vue-router';
import TimeDatabaseView from '../views/P1-TimeDatabaseView.vue';
import CsvImportView from '../views/P2-CsvImportView.vue';
import HomeView from '../views/P0-HomeView.vue';
import PredictionPage from '../views/PredictionPage.vue';

const routes = [
  { path: '/', component: HomeView, name: 'Home', meta: { title: '主页面' } },
  { path: '/time-database', component: TimeDatabaseView, name: 'TimeDatabase', meta: { title: '时间数据库管理' } },
  { path: '/csv-import', component: CsvImportView, name: 'CsvImport', meta: { title: 'CSV 文件导入' } },
  {
    path: '/prediction/:databaseName', // 加入 :databaseName 路由参数
    component: PredictionPage,
    name: 'Prediction',
    meta: { title: '预测' },
    props: true // 启用将路由参数作为 props 传递给组件
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
