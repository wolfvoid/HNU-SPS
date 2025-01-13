import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import vuetify from './plugins/vuetify';
import { loadFonts } from './plugins/webfontloader';
import axios from 'axios';

loadFonts();

// 创建 app 实例
const app = createApp(App);

// 设置全局属性
app.config.globalProperties.$axios = axios;

// 使用插件
app
  .use(router)
  .use(vuetify)
  .mount('#app');
