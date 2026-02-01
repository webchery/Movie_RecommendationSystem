<template>
  <div class="admin-auth-container">
    <div class="login-box">
      <h1 class="logo">CINEMA<span>ADMIN</span></h1>
      <p class="subtitle">管理后台安全认证</p>
      <div class="form">
        <input
          v-model="form.username"
          placeholder="管理员账号"
          class="admin-input"
        />
        <input
          v-model="form.password"
          type="password"
          placeholder="认证密码"
          class="admin-input"
          @keyup.enter="handleLogin"
        />
        <button class="admin-btn" @click="handleLogin">认证并进入</button>
      </div>
      <p class="back-link" @click="$router.push('/')">← 返回普通用户首页</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "../api";
import { useRouter } from "vue-router";

const router = useRouter();
const form = ref({ username: "", password: "", role: "admin" });

const handleLogin = async () => {
  try {
    const res = await api.post("/auth/login", form.value);
    alert(res.data.msg);
    router.push("/admin");
  } catch (e) {
    alert("认证失败：非管理员账号或密码错误");
  }
};
</script>

<style scoped>
.admin-auth-container {
  height: 100vh;
  background: #001529;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: sans-serif;
}
.login-box {
  background: #fff;
  padding: 40px;
  border-radius: 8px;
  width: 320px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}
.logo {
  font-size: 28px;
  font-weight: 800;
  color: #333;
  margin-bottom: 5px;
}
.logo span {
  color: #e50914;
}
.subtitle {
  color: #888;
  font-size: 14px;
  margin-bottom: 30px;
}
.admin-input {
  width: 100%;
  padding: 12px;
  margin-bottom: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  outline: none;
}
.admin-btn {
  width: 100%;
  padding: 12px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  font-size: 16px;
}
.back-link {
  margin-top: 20px;
  color: #1890ff;
  font-size: 13px;
  cursor: pointer;
}
</style>
