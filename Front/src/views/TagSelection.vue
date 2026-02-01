<template>
  <div class="tag-selection-page">
    <div class="center-card">
      <h1>定制您的私人影院</h1>
      <p class="subtitle">选择 1-3 个感兴趣的题材，我们将为您优化模型权重</p>
      
      <div class="tag-grid">
        <div 
          v-for="t in tags" :key="t" 
          :class="['tag-box', { active: selected.includes(t) }]"
          @click="toggle(t)"
        >
          {{ t }}
        </div>
      </div>

      <div class="action-btns">
        <button class="btn-go" :disabled="selected.length === 0" @click="saveAndEnter">
          开启智能推荐
        </button>
        <button class="btn-skip" @click="$router.push('/')">直接进入首页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../api';
import { useRouter } from 'vue-router';

const router = useRouter();
const selected = ref([]);
const tags = ["Action", "Adventure", "Animation", "Comedy", "Crime", "Drama", "Fantasy", "Horror", "Romance", "Sci-Fi", "Thriller", "War"];

const toggle = (t) => {
    if(selected.value.includes(t)) selected.value = selected.value.filter(i => i !== t);
    else if(selected.value.length < 3) selected.value.push(t);
};

const saveAndEnter = async () => {
    await api.post('/auth/preferences', { tags: selected.value.join(',') });
    router.push('/');
};
</script>

<style scoped>
.tag-selection-page { height: 100vh; background: #0a0a0a; display: flex; align-items: center; justify-content: center; color: white; font-family: sans-serif; }
.center-card { max-width: 700px; text-align: center; }
h1 { font-size: 40px; margin-bottom: 10px; font-weight: 800; }
.subtitle { color: #666; margin-bottom: 50px; }
.tag-grid { display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; margin-bottom: 60px; }
.tag-box { padding: 12px 30px; border: 1px solid #333; border-radius: 30px; cursor: pointer; transition: 0.3s; color: #888; font-weight: bold; }
.tag-box:hover { border-color: #e50914; color: white; }
.tag-box.active { background: #e50914; border-color: #e50914; color: white; box-shadow: 0 0 20px rgba(229, 9, 20, 0.4); }
.action-btns { display: flex; flex-direction: column; align-items: center; gap: 20px; }
.btn-go { background: #e50914; border: none; color: white; padding: 15px 60px; border-radius: 40px; font-size: 18px; font-weight: bold; cursor: pointer; }
.btn-go:disabled { background: #222; color: #555; cursor: not-allowed; }
.btn-skip { background: none; border: none; color: #444; cursor: pointer; text-decoration: underline; }
</style>