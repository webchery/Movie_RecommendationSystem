<template>
  <div class="movie-home">
    <!-- 1. 导航栏 -->
    <nav class="navbar">
      <div class="logo" @click="resetHome">CINEMA<span>MAX</span></div>

      <div class="search-bar">
        <select v-model="searchState.type" class="search-type">
          <option value="title">片名</option>
          <option value="director">导演</option>
          <option value="actors">演员</option>
          <option value="tags">标签</option>
        </select>
        <input
          v-model="searchState.keyword"
          placeholder="搜索百万电影..."
          @keyup.enter="handleSearch"
        />
        <button class="search-btn-transparent" @click="handleSearch">
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M11 19C15.4183 19 19 15.4183 19 11C19 6.58172 15.4183 3 11 3C6.58172 3 3 6.58172 3 11C3 15.4183 6.58172 19 11 19Z"
              stroke="#777"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <path
              d="M21 21L16.65 16.65"
              stroke="#777"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </button>
      </div>

      <div class="user-info">
        <div v-if="user.isLogin" class="user-status">
          <span>👤 {{ user.username }}</span>
          <button @click="handleLogout" class="logout-link">退出</button>
        </div>
        <button v-else class="btn-login" @click="showAuth = true">
          登录 / 注册
        </button>
      </div>
    </nav>

    <!-- 2. 登录注册弹窗 -->
    <div v-if="showAuth" class="auth-overlay" @click.self="closeAuthAndClear">
      <div class="auth-card">
        <h2>{{ isLoginMode ? "系统登录" : "会员注册" }}</h2>
        <div v-if="isLoginMode" class="role-selector">
          <label
            ><input type="radio" v-model="authForm.role" value="client" />
            用户</label
          >
          <label
            ><input type="radio" v-model="authForm.role" value="admin" />
            管理员</label
          >
        </div>
        <input v-model="authForm.username" placeholder="用户名" class="inp" />
        <input
          v-model="authForm.password"
          type="password"
          placeholder="密码"
          class="inp"
          @keyup.enter="handleAuth"
        />
        <button class="btn-submit" @click="handleAuth">确 认</button>
        <p
          v-if="authForm.role === 'client'"
          class="toggle"
          @click="toggleAuthMode"
        >
          {{ isLoginMode ? "没有账号？注册" : "已有账号？登录" }}
        </p>
        <span class="close-icon" @click="closeAuthAndClear">×</span>
      </div>
    </div>

    <!-- 3. AI 悬浮入口 -->
    <div class="ai-side-peek-wrapper" @click="$router.push('/ai-chat')">
      <div class="ai-bubble-hint">想知道电影最新资讯？问问我吧</div>
      <div class="ai-circle-core">
        <svg viewBox="0 0 24 24" class="ai-svg-icon">
          <path
            d="M19,8V7H17V5.5A2.5,2.5 0 0,0 14.5,3H9.5A2.5,2.5 0 0,0 7,5.5V7H5V8A2,2 0 0,0 3,10V18A2,2 0 0,0 5,20H19A2,2 0 0,0 21,18V10A2,2 0 0,0 19,8M9,7V5.5A0.5,0.5 0 0,1 9.5,5H14.5A0.5,0.5 0 0,1 15,5.5V7H9M19,18H5V10H19V18M17,13A1,1 0 0,1 16,14H14A1,1 0 0,1 13,13V12H11V13A1,1 0 0,1 10,14H8A1,1 0 0,1 7,13V11A1,1 0 0,1 8,10H16A1,1 0 0,1 17,11V13Z"
            fill="white"
          />
        </svg>
      </div>
    </div>

    <div class="container" v-if="recs.length > 0">
      <div v-if="searchState.isSearching" class="search-view">
        <h3 class="stitle">
          搜索结果: <span>"{{ searchState.keyword }}"</span>
        </h3>
        <div v-if="searchResults.length > 0" class="movie-grid-fixed">
          <div
            class="card"
            v-for="m in searchResults"
            :key="m.id"
            @click="$router.push('/movie/' + m.id)"
          >
            <img :src="getImg(m.id)" />
            <div class="info">
              <p>{{ m.title }}</p>
              <span>⭐ {{ m.score }}</span>
            </div>
          </div>
        </div>
        <button class="btn-back-home" @click="resetHome">返回首页</button>
      </div>

      <template v-else>
        <!--  Hero 巨幕扩展动画  -->
        <div
          class="hero"
          @click="$router.push('/movie/' + recs[0].id)"
          :style="{
            backgroundImage: `linear-gradient(to right, rgba(0,0,0,0.95) 20%, rgba(0,0,0,0.2) 80%), url(${getImg(recs[0].id)})`,
          }"
        >
          <div class="hero-text">
            <span class="hero-tag">今日热门</span>
            <h1>{{ recs[0].title }}</h1>
            <p>{{ recs[0].summary }}</p>
          </div>
        </div>

        <section class="section">
          <h3 class="stitle">为你推荐</h3>
          <div class="movie-scroll">
            <div
              class="card"
              v-for="m in recs"
              :key="m.id"
              @click="$router.push('/movie/' + m.id)"
            >
              <img :src="getImg(m.id)" />
              <div class="info">
                <p>{{ m.title }}</p>
                <span>⭐ {{ m.score }}</span>
              </div>
            </div>
          </div>
        </section>

        <section class="section ranking-module">
          <div class="rank-header">
            <div class="rank-tabs">
              <button
                :class="{ active: rankType === 'hot' }"
                @click="changeRankType('hot')"
              >
                今日热映榜
              </button>
              <button
                :class="{ active: rankType === 'new' }"
                @click="changeRankType('new')"
              >
                全球新片榜
              </button>
            </div>
          </div>
          <div class="rank-list">
            <div
              class="rank-item"
              v-for="(m, idx) in rankList"
              :key="m.id"
              @click="$router.push('/movie/' + m.id)"
            >
              <div class="rank-num" :class="{ 'top-3': idx < 3 }">
                {{ idx + 1 }}
              </div>
              <img :src="getImg(m.id)" class="rank-img" />
              <div class="rank-info">
                <p class="rank-title">{{ m.title }}</p>
                <div class="rank-meta">
                  <span v-if="rankType === 'new'">📅 {{ m.release_date }}</span>
                  <span v-else>🔥 {{ m.click_count }}</span>
                  <span class="rank-score">⭐ {{ m.score }}</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section v-if="footprints.length > 0" class="section">
          <h3 class="stitle">最近观看</h3>
          <div class="movie-scroll">
            <div
              class="card"
              v-for="m in footprints"
              :key="m.id"
              @click="$router.push('/movie/' + m.id)"
            >
              <img :src="getImg(m.id)" />
            </div>
          </div>
        </section>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch } from "vue";
import api from "../api";
import { useRouter } from "vue-router";

const router = useRouter();
const showAuth = ref(false);
const isLoginMode = ref(true);
const recs = ref([]);
const footprints = ref([]);
const rankList = ref([]);
const rankType = ref("hot");
const searchResults = ref([]);
const user = reactive({ isLogin: false, username: "", role: "" });
const authForm = reactive({ username: "", password: "", role: "client" });
const searchState = reactive({
  keyword: "",
  type: "title",
  isSearching: false,
});

const getImg = (id) => `/images/${((id * 17) % 300) + 1}.jpg`;

// 核心：清空逻辑 
const clearAuthForm = () => {
  authForm.username = "";
  authForm.password = "";
};
watch(() => authForm.role, clearAuthForm); // 切换角色清空
const toggleAuthMode = () => {
  isLoginMode.value = !isLoginMode.value;
  clearAuthForm();
}; // 切换登录注册清空
const closeAuthAndClear = () => {
  showAuth.value = false;
  clearAuthForm();
}; // 关闭弹窗清空

onMounted(async () => {
  initPage();
});

const initPage = async () => {
  const res = await api.get("/movies/home");
  recs.value = res.data.recs;
  fetchRankings();
  const userRes = await api.get("/auth/user_info");
  if (userRes.data.isLogin) {
    Object.assign(user, userRes.data);
    if (user.role === "client") {
      const fRes = await api.get("/user/footprints");
      footprints.value = fRes.data;
    }
  }
};

const handleSearch = async () => {
  if (!searchState.keyword) return;
  searchState.isSearching = true;
  const res = await api.get(
    `/movies/search?q=${searchState.keyword}&type=${searchState.type}`,
  );
  searchResults.value = res.data;
};

const resetHome = () => {
  searchState.isSearching = false;
  searchState.keyword = "";
};
const fetchRankings = async () => {
  const res = await api.get(`/movies/rankings?type=${rankType.value}`);
  rankList.value = res.data;
};
const changeRankType = (t) => {
  rankType.value = t;
  fetchRankings();
};

// 核心：注册与登录逻辑修复 
const handleAuth = async () => {
  if (!authForm.username || !authForm.password) return alert("请填写完整");

  const path = isLoginMode.value ? "/auth/login" : "/auth/register";
  try {
    const res = await api.post(path, {
      username: authForm.username,
      password: authForm.password,
      role: authForm.role,
    });

    if (isLoginMode.value) {
      if (res.data.role === "admin") {
        alert("管理员认证成功");
        router.push("/admin");
      } else {
              alert("登录成功！请选择您的观影偏好");
        //  核心改动：不再直接刷新首页，而是跳转到独立的标签选择页面
        router.push("/tags"); 
      }
    } else {
      alert("注册成功，请登录");
      isLoginMode.value = true;
      clearAuthForm(); // 注册成功清空
    }
  } catch (e) {
    alert(e.response?.data?.msg || "账号或密码错误");
    clearAuthForm(); //  输错后清空逻辑 
  }
};

const handleLogout = async () => {
  await api.get("/auth/logout");
  location.reload();
};
</script>

<style scoped>
.movie-home {
  background: #080808;
  color: white;
  min-height: 100vh;
  font-family: sans-serif;
}
.navbar {
  position: fixed;
  top: 0;
  width: 99.135%;
  height: 70px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 50px;
  background: rgba(0, 0, 0, 0.9);
  backdrop-filter: blur(10px);
  z-index: 1000;
  box-sizing: border-box;
  border-bottom: 1px solid #222;
}
.logo {
  font-size: 22px;
  font-weight: 800;
  cursor: pointer;
  flex-shrink: 0;
  color: white;
}
.logo span {
  color: #e50914;
}
.search-bar {
  display: flex;
  align-items: center;
  background: #1a1a1a;
  padding: 2px 15px;
  border-radius: 20px;
  border: 1px solid #333;
  margin: 0 30px;
}
.search-type {
  background: none;
  color: #777;
  border: none;
  font-size: 13px;
  border-right: 1px solid #333;
  padding-right: 10px;
  outline: none;
}
.search-bar input {
  background: none;
  border: none;
  color: white;
  padding: 8px 10px;
  width: 250px;
  outline: none;
}
.search-bar input::placeholder {
  color: #777;
}
.search-btn-transparent {
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
  outline: none;
}
.btn-login {
  background: #e50914;
  color: white;
  border: none;
  padding: 10px 25px;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
}
.logout-link {
  color: #e50914;
  font-size: 13px;
  text-decoration: underline;
  background: none;
  border: none;
  cursor: pointer;
  margin-left: 10px;
}
.container {
  padding: 90px 50px 50px;
}
.hero {
  height: 45vh;
  background-size: cover;
  background-position: center top;
  border-radius: 15px;
  display: flex;
  align-items: center;
  padding: 0 50px;
  margin-bottom: 50px;
  border: 1px solid #222;
  cursor: pointer;
  transition: all 0.8s cubic-bezier(0.165, 0.84, 0.44, 1);
  position: relative;
  overflow: hidden;
}
.hero:hover {
  height: 75vh;
  border-color: #e50914;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
}
.hero-text {
  max-width: 600px;
  position: relative;
  z-index: 2;
}
.hero-tag {
  background: #e50914;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 15px;
  display: inline-block;
}
.hero-text h1 {
  font-size: 46px;
  margin: 0 0 10px 0;
  text-shadow: 0 2px 10px #000;
}
.hero-text p {
  color: #ccc;
  line-height: 1.6;
  text-shadow: 0 1px 5px #000;
  font-size: 16px;
}

/*  AI 侧边半露悬浮  */
.ai-side-peek-wrapper {
  position: fixed;
  top: 52vh;
  right: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 10px;
}
.ai-side-peek-wrapper:hover {
  transform: translate3d(-15px, 0, 0);
}
.ai-circle-core {
  width: 54px;
  height: 54px;
  background: linear-gradient(135deg, #e50914 0%, #b20710 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 5px 20px rgba(229, 9, 20, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
}
.ai-svg-icon {
  width: 28px;
  height: 28px;
}
.ai-bubble-hint {
  background: white;
  color: #111;
  padding: 10px 20px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  margin-right: 15px;
  white-space: nowrap;
  opacity: 0;
  transform: translate3d(15px, 0, 0);
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
  pointer-events: none;
}
.ai-side-peek-wrapper:hover .ai-bubble-hint {
  opacity: 1;
  transform: translate3d(0, 0, 0);
}

/* 列表排布 */
.search-view {
  min-height: 80vh;
}
.movie-grid-fixed {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 25px;
  margin-top: 30px;
}
.no-data {
  text-align: center;
  padding: 100px;
  color: #444;
  font-size: 18px;
}
.btn-back-home {
  display: block; /* 设为块级元素 */
  margin: 40px auto 0; /* 上边距40px，左右auto实现居中 */
  background: #222;
  color: #fff;
  border: 1px solid #444;
  padding: 12px 40px;
  border-radius: 4px;
  cursor: pointer;
}
.btn-back-home:hover {
  background: #333;
  border-color: #e50914;
}
.section {
  margin-top: 50px;
}
.stitle {
  border-left: 4px solid #e50914;
  padding-left: 15px;
  font-size: 22px;
  margin-bottom: 25px;
}
.movie-scroll {
  display: flex;
  gap: 20px;
  overflow-x: auto;
  padding-bottom: 15px;
  scrollbar-width: none;
}
.card {
  min-width: 180px;
  cursor: pointer;
  transition: 0.3s;
}
.card:hover {
  transform: scale(1.05);
}
.card img {
  width: 100%;
  aspect-ratio: 2/3;
  border-radius: 8px;
  object-fit: cover;
  background: #111;
}
.info {
  margin-top: 10px;
  font-size: 13px;
}
.info span {
  color: #ffc107;
}
.ranking-module {
  background: #111;
  padding: 30px;
  border-radius: 20px;
  border: 1px solid #222;
}
.rank-header {
  display: flex;
  gap: 10px;
  background: #000;
  padding: 5px;
  border-radius: 10px;
  width: fit-content;
  margin-bottom: 30px;
}
.rank-tabs button {
  background: none;
  border: none;
  color: #555;
  padding: 8px 20px;
  cursor: pointer;
  border-radius: 5px;
  font-weight: bold;
}
.rank-tabs button.active {
  background: #e50914;
  color: white;
}
.rank-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px 40px;
}
.rank-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px;
  border-radius: 10px;
  cursor: pointer;
}
.rank-num {
  font-size: 26px;
  font-weight: 900;
  font-style: italic;
  color: #333;
  width: 30px;
}
.rank-num.top-3 {
  color: #e50914;
}
.rank-img {
  width: 45px;
  height: 65px;
  object-fit: cover;
  border-radius: 4px;
}
.rank-info {
  flex: 1;
}
.rank-title {
  font-weight: bold;
  margin: 0 0 5px 0;
  font-size: 14px;
}
.rank-meta {
  font-size: 12px;
  color: #666;
  display: flex;
  justify-content: space-between;
}
.auth-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.auth-card {
  background: #141414;
  padding: 40px;
  border-radius: 15px;
  width: 320px;
  text-align: center;
  position: relative;
  border: 1px solid #333;
}
.role-selector {
  margin-bottom: 20px;
  color: #888;
  font-size: 14px;
}
.inp {
  width: 100%;
  padding: 12px;
  margin-bottom: 15px;
  background: #222;
  border: 1px solid #333;
  border-radius: 5px;
  color: white;
  box-sizing: border-box;
}
.btn-submit {
  width: 100%;
  padding: 12px;
  background: #e50914;
  color: white;
  border: none;
  font-weight: bold;
  cursor: pointer;
  border-radius: 4px;
}
.toggle {
  margin-top: 15px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
}
.close-icon {
  position: absolute;
  top: 10px;
  right: 20px;
  font-size: 30px;
  color: #444;
  cursor: pointer;
}
</style>
