<template>
  <div class="admin-wrapper">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="logo">ADMIN<span>SYSTEM</span></div>
      <nav>
        <div :class="{ active: tab === 'stats' }" @click="tab = 'stats'">
          📊 数据统计
        </div>
        <div :class="{ active: tab === 'movies' }" @click="tab = 'movies'">
          🎬 电影管理
        </div>
        <div :class="{ active: tab === 'users' }" @click="tab = 'users'">
          👥 会员审计
        </div>
      </nav>
      <button class="exit-btn" @click="handleLogout">退出回到首页</button>
    </aside>

    <!-- 主面板 -->
    <main class="main-panel">
      <!-- 1. 统计 -->
      <div v-if="tab === 'stats'">
        <h2>系统运行状态</h2>
        <div class="stats-grid">
          <div class="box">
            <h3>{{ stats.movie_count || 0 }}</h3>
            <p>电影总量</p>
          </div>
          <div class="box">
            <h3>{{ stats.client_count || 0 }}</h3>
            <p>注册会员</p>
          </div>
          <div class="box">
            <h3>{{ stats.total_clicks || 0 }}</h3>
            <p>累计播放</p>
          </div>
          <!-- 模型评估指标 -->
          <div class="box" style="border-bottom: 3px solid #52c41a">
            <h3 style="color: #52c41a">{{ stats.rmse || "计算中..." }}</h3>
            <p>模型 RMSE 指标</p>
          </div>
          <div class="box" style="border-bottom: 3px solid #1890ff">
            <h3 style="color: #1890ff">{{ stats.precision || "计算中..." }}</h3>
            <p>推荐预估准确率</p>
          </div>
        </div>
      </div>

      <!-- 2. 电影管理 -->
      <div v-if="tab === 'movies'">
        <div class="table-header">
          <h2>影片库管理</h2>
          <button class="add-btn" @click="openAdd">+ 新增影片</button>
        </div>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>标题</th>
              <th>导演</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in movies" :key="m.id">
              <td>{{ m.id }}</td>
              <td>{{ m.title }}</td>
              <td>{{ m.director }}</td>
              <td>
                <button class="btn-edit" @click="openEdit(m)">修改</button>
                <button class="btn-del" @click="doDelete(m.id)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!--  3. 增强版会员管理 -->
      <div v-if="tab === 'users'">
        <div class="table-header">
          <h2>系统会员账号审计</h2>
          <button class="add-user-btn" @click="openUserAdd">
            + 开设新账号
          </button>
        </div>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>用户名</th>
              <th style="color: #e50914">设置密码(明文)</th>
              <th>注册日期</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in clients" :key="c.id">
              <td>{{ c.id }}</td>
              <td>{{ c.username }}</td>
              <td style="font-weight: bold">{{ c.password }}</td>
              <td>{{ c.date }}</td>
              <td>
                <button class="btn-del" @click="deleteUser(c.id)">
                  删除会员
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

    <!-- 弹窗部分保持原样 -->
    <div v-if="showModal" class="modal-mask">
      <div class="modal-box">
        <h3>{{ form.id ? "编辑影片信息" : "录入新影片" }}</h3>
        <div class="form-item">
          <label>影片名称</label><input v-model="form.title" />
        </div>
        <div class="form-item">
          <label>导演名称</label><input v-model="form.director" />
        </div>
        <div class="form-item">
          <label>主演名单</label><input v-model="form.actors" />
        </div>
        <div class="form-item">
          <label>类型标签</label><input v-model="form.tags" />
        </div>
        <div class="form-item">
          <label>剧情简介</label
          ><textarea v-model="form.summary" rows="4"></textarea>
        </div>
        <div class="modal-btns">
          <button class="save" @click="saveMovie">确认提交</button>
          <button class="cancel" @click="showModal = false">取消</button>
        </div>
      </div>
    </div>
    <div v-if="showUserModal" class="modal-mask">
      <div class="modal-box user-form">
        <h3>开设新会员账号</h3>
        <div class="form-item">
          <label>设置用户名</label>
          <input v-model="userForm.username" placeholder="建议使用姓名拼音" />
        </div>
        <div class="form-item">
          <label>设置初始密码</label>
          <input v-model="userForm.password" placeholder="建议设为 123456" />
        </div>
        <div class="modal-btns">
          <button class="save" @click="submitUser">确认开户</button>
          <button class="cancel" @click="showUserModal = false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api";
import { useRouter } from "vue-router";

const router = useRouter();
const tab = ref("stats");
const stats = ref({});
const movies = ref([]);
const clients = ref([]);
const showModal = ref(false);
const form = ref({
  id: null,
  title: "",
  director: "",
  actors: "",
  tags: "",
  summary: "",
});

// 🌟 唯一的数据加载入口
const loadAll = async () => {
  try {
    // 加载统计和评估模型数据
    const sRes = await api.get("/admin/stats");
    stats.value = sRes.data;

    // 加载电影列表
    const mRes = await api.get("/admin/movies");
    movies.value = mRes.data.items;

    // 加载会员列表
    const cRes = await api.get("/admin/clients");
    clients.value = cRes.data;
  } catch (e) {
    console.error("加载数据失败", e);
    // 如果未登录，跳转回首页
    router.push("/");
  }
};
// 🌟 管理员删除用户 🌟
const deleteUser = async (id) => {
  if (
    confirm(
      "警告：删除会员将永久抹除其所有足迹和偏好数据，且不可恢复！确定吗？",
    )
  ) {
    await api.delete(`/admin/clients/${id}`);
    loadAll();
  }
};

// 🌟 管理员开户 🌟
const openUserAdd = () => {
  userForm.value = { username: "", password: "" };
  showUserModal.value = true;
};

const doDelete = async (id) => {
  if (confirm("确定永久删除这部电影吗？关联数据将同步清理。")) {
    await api.delete(`/admin/movies/${id}`);
    loadAll();
  }
};

const openAdd = () => {
  form.value = {
    id: null,
    title: "",
    director: "",
    actors: "",
    tags: "",
    summary: "",
  };
  showModal.value = true;
};

const openEdit = (m) => {
  form.value = { ...m };
  showModal.value = true;
};

const saveMovie = async () => {
  if (!form.value.title) return alert("标题必填");
  try {
    if (form.value.id) {
      await api.put(`/admin/movies/${form.value.id}`, form.value);
    } else {
      await api.post("/admin/movies", form.value);
    }
    showModal.value = false;
    loadAll();
  } catch (e) {
    alert("操作失败");
  }
};

const handleLogout = async () => {
  await api.get("/auth/logout");
  router.push("/");
};

onMounted(loadAll);
</script>

<style scoped>
.add-user-btn {
  background: #1890ff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}
.add-user-btn:hover {
  background: #40a9ff;
}
.user-form {
  width: 350px !important;
}
.btn-del {
  color: #f5222d;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 13px;
  text-decoration: underline;
}
.btn-del:hover {
  color: #ff4d4f;
}

.admin-wrapper {
  display: flex;
  height: 100vh;
  background: #f5f6fa;
  color: #333;
  font-family: sans-serif;
}
.sidebar {
  width: 260px;
  background: #2f3640;
  color: #fff;
  padding: 40px 0;
  display: flex;
  flex-direction: column;
}
.logo {
  text-align: center;
  font-size: 24px;
  font-weight: 800;
  margin-bottom: 50px;
}
.logo span {
  color: #e50914;
}
nav div {
  padding: 15px 35px;
  cursor: pointer;
  transition: 0.3s;
  font-size: 15px;
}
nav div.active {
  background: #e50914;
  color: #fff;
}
.exit-btn {
  margin: auto 30px 30px;
  padding: 10px;
  background: none;
  border: 1px solid #555;
  color: #fff;
  cursor: pointer;
  border-radius: 5px;
}
.main-panel {
  flex: 1;
  padding: 40px;
  overflow-y: auto;
}
.stats-grid {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}
.box {
  background: #fff;
  padding: 30px;
  min-width: 200px;
  flex: 1;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  text-align: center;
}
.box h3 {
  font-size: 32px;
  margin: 0;
  color: #e50914;
}
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.add-btn {
  background: #e50914;
  color: white;
  border: none;
  padding: 10px 25px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}
.table {
  width: 100%;
  background: #fff;
  border-collapse: collapse;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}
.table th,
.table td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}
.btn-edit {
  color: #1890ff;
  background: none;
  border: none;
  cursor: pointer;
  margin-right: 15px;
}
.btn-del {
  color: #f5222d;
  background: none;
  border: none;
  cursor: pointer;
}
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-box {
  background: white;
  padding: 40px;
  border-radius: 15px;
  width: 450px;
}
.form-item {
  margin-bottom: 15px;
}
.form-item label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  font-size: 14px;
}
.form-item input,
.form-item textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-sizing: border-box;
}
.modal-btns {
  display: flex;
  gap: 15px;
  margin-top: 25px;
}
.modal-btns button {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}
.modal-btns button.save {
  background: #e50914;
  color: white;
}
.modal-btns button.cancel {
  background: #eee;
  color: #333;
}
</style>
