<template>
  <div class="detail-root" v-if="movie">
    <!-- 高端大图虚化背景 -->
    <div
      class="blur-bg"
      :style="{ backgroundImage: `url(${getImg(movie.id)})` }"
    ></div>

    <div class="detail-content">
      <div class="movie-main-card">
        <img :src="getImg(movie.id)" class="main-poster" />
        <div class="main-info">
          <h1>{{ movie.title }}</h1>
          <div class="pills">
            <span class="score-p">⭐ {{ movie.score }} 分</span>
            <span class="year-p">{{ movie.release_date.split("-")[0] }}</span>
          </div>
          <div class="meta-data">
            <p><strong>导演：</strong>{{ movie.director }}</p>
            <p><strong>主演：</strong>{{ movie.actors }}</p>
            <p>
              <strong>类型：</strong
              ><span style="color: #e50914">{{ movie.tags }}</span>
            </p>
          </div>
          <div class="summary-section">
            <h3>影片简介</h3>
            <p>{{ movie.summary }}</p>
          </div>
          <div class="btn-group">
            <!-- 修改点：点击触发播放器 -->
            <button class="play-trigger" @click="showPlayer = true">
              <i class="fa fa-play"></i> 立即播放
            </button>
            <button class="back-trigger" @click="$router.push('/')">
              返回首页
            </button>
          </div>
        </div>
      </div>

      <!-- 详情页推荐 -->
      <section class="rel-section">
        <h3 class="section-title">相关影片推荐</h3>
        <div class="rel-list">
          <div
            class="mini-card"
            v-for="r in movie.related"
            :key="r.id"
            @click="reload(r.id)"
          >
            <img :src="getImg(r.id)" />
            <p>{{ r.title }}</p>
          </div>
        </div>
      </section>
    </div>

    <!-- 影院级视频播放弹窗 -->
    <div
      v-if="showPlayer"
      class="video-modal-overlay"
      @click.self="closePlayer"
    >
      <div class="video-box">
        <span class="close-video" @click="closePlayer">×</span>
        <video
          ref="videoPlayer"
          controls
          autoplay
          class="cinema-video"
          src="/trailer.mp4"
        >
          <!-- 这里对应 public/trailer.mp4 -->
          您的浏览器不支持视频播放。
        </video>
        <div class="video-info-bar">
          正在播放：{{ movie.title }} - 官方预告片
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";

const route = useRoute();
const router = useRouter();
const movie = ref(null);
const showPlayer = ref(false); // 控制播放器显示
const videoPlayer = ref(null);

const getImg = (id) => `/images/${((id * 17) % 300) + 1}.jpg`;

const loadData = async (id) => {
  const res = await api.get(`/movies/detail/${id}`);
  movie.value = res.data;
  window.scrollTo({ top: 0, behavior: "smooth" });
};

const closePlayer = () => {
  showPlayer.value = false;
};

onMounted(() => loadData(route.params.id));

const reload = (id) => {
  router.push(`/movie/${id}`);
  loadData(id);
};
</script>

<style scoped>
/* --- 保留原有高端样式 --- */
.detail-root {
  min-height: 100vh;
  background: #000;
  color: #fff;
  position: relative;
  overflow: hidden;
  padding-bottom: 100px;
}
.blur-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  filter: blur(70px) brightness(0.2);
  z-index: 0;
  transform: scale(1.1);
}
.detail-content {
  position: relative;
  z-index: 1;
  max-width: 1100px;
  margin: 0 auto;
  padding-top: 100px;
}
.movie-main-card {
  display: flex;
  gap: 60px;
  background: rgba(255, 255, 255, 0.05);
  padding: 50px;
  border-radius: 30px;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.main-poster {
  width: 300px;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8);
}
.main-info {
  flex: 1;
}
.main-info h1 {
  font-size: 45px;
  margin: 0 0 20px 0;
  font-weight: 800;
}
.pills {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}
.score-p {
  color: #ffc107;
  font-size: 22px;
  font-weight: bold;
}
.year-p {
  color: #888;
  font-size: 16px;
}
.meta-data {
  line-height: 2;
  margin-bottom: 30px;
  font-size: 15px;
}
.summary-section p {
  color: #ccc;
  line-height: 1.8;
  margin-bottom: 40px;
}

/* 按钮样式 */
.play-trigger {
  background: #e50914;
  color: white;
  border: none;
  padding: 15px 45px;
  border-radius: 30px;
  font-weight: bold;
  cursor: pointer;
  font-size: 16px;
  transition: 0.3s;
}
.play-trigger:hover {
  background: #ff1e2a;
  transform: scale(1.05);
}
.back-trigger {
  background: rgba(255, 255, 255, 0.05);
  color: white;
  border: 1px solid #444;
  padding: 15px 35px;
  border-radius: 30px;
  margin-left: 20px;
  cursor: pointer;
}

/* 🌟 视频播放器专有样式 🌟 */
.video-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  backdrop-filter: blur(10px);
}
.video-box {
  position: relative;
  width: 80%;
  max-width: 1000px;
  background: #000;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 0 50px rgba(229, 9, 20, 0.2);
}
.cinema-video {
  width: 100%;
  display: block;
  outline: none;
}
.close-video {
  position: absolute;
  top: 15px;
  right: 20px;
  font-size: 40px;
  color: #fff;
  cursor: pointer;
  z-index: 3001;
  opacity: 0.5;
  transition: 0.3s;
}
.close-video:hover {
  opacity: 1;
  color: #e50914;
}
.video-info-bar {
  background: #111;
  padding: 15px;
  text-align: center;
  font-size: 14px;
  color: #888;
  border-top: 1px solid #222;
}

/* 底部推荐 */
.rel-section {
  margin-top: 70px;
}
.section-title {
  border-left: 4px solid #e50914;
  padding-left: 15px;
  font-size: 24px;
  margin-bottom: 30px;
}
.rel-list {
  display: flex;
  gap: 25px;
  overflow-x: auto;
}
.mini-card {
  min-width: 160px;
  cursor: pointer;
}
.mini-card img {
  width: 100%;
  aspect-ratio: 2/3;
  border-radius: 8px;
  object-fit: cover;
}
.mini-card p {
  text-align: center;
  font-size: 13px;
  color: #888;
  margin-top: 10px;
}
</style>
