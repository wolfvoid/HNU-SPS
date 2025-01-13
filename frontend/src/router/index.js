import { createRouter, createWebHistory } from 'vue-router';
import TimeDatabaseView from '../views/P1-TimeDatabaseView.vue';
import CsvImportView from '../views/P2-CsvImportView.vue';
import PredictionView from '../views/P3-PredictionView.vue';
import AlertView from '../views/P4-AlertView.vue';
import HomeView from '../views/P0-HomeView.vue';

const routes = [
  { path: '/', component: HomeView, name: 'Home', meta: { title: '主页面' } },
  { path: '/time-database', component: TimeDatabaseView, name: 'TimeDatabase', meta: { title: '时间数据库管理' } },
  { path: '/csv-import', component: CsvImportView, name: 'CsvImport', meta: { title: 'CSV 文件导入' } },
  { path: '/prediction', component: PredictionView, name: 'Prediction', meta: { title: '预测' } },
  { path: '/alert', component: AlertView, name: 'Alert', meta: { title: '预警功能' } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
