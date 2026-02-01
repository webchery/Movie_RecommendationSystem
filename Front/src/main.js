import { createApp } from 'vue'
import App from './App.vue'
import { createRouter, createWebHashHistory } from 'vue-router'

// 导入所有视图组件
import Home from './views/Home.vue'
import Detail from './views/Detail.vue'
import Admin from './views/Admin.vue'      
// import AdminLogin from './views/AdminLogin.vue' 
import AiChat from './views/AiChat.vue'
import TagSelection from './views/TagSelection.vue'

// 1. 定义路由映射
const routes = [
  { path: '/', component: Home },
  { path: '/movie/:id', component: Detail },
  //{ path: '/admin-login', component: AdminLogin },
  { path: '/admin', component: Admin },
   { path: '/ai-chat', component: AiChat },
   { path: '/tags', component: TagSelection }
]

// 2. 创建路由实例
const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 3. 创建并启动 Vue 应用
const app = createApp(App)
app.use(router) // 注入路由
app.mount('#app') // 挂载到 index.html 中的 #app 节点

