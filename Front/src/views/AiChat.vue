<template>
  <div class="ai-page">
    <nav class="navbar">
      <div class="logo" @click="$router.push('/')">CINEMA<span>MAX</span></div>
      <button class="back-btn" @click="$router.push('/')">退出对话</button>
    </nav>

    <div class="chat-container">
      <div class="chat-window" id="chatBox">
        <!-- 消息列表 -->
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          :class="['msg-wrapper', msg.role]"
        >
          <div class="avatar">{{ msg.role === "user" ? "ME" : "AI" }}</div>
          <div class="bubble">{{ msg.content }}</div>
        </div>

        <!-- 加载中动画 -->
        <div v-if="loading" class="msg-wrapper assistant">
          <div class="avatar">AI</div>
          <div class="bubble loading-dots">
            正在思考<span>.</span><span>.</span><span>.</span>
          </div>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="input-area">
        <input
          v-model="userInput"
          @keyup.enter="sendMessage"
          placeholder="输入你想聊的电影话题..."
          :disabled="loading"
        />
        <button @click="sendMessage" :disabled="loading">发送</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from "vue";
import api from "../api";

const userInput = ref("");
const loading = ref(false);
const messages = reactive([
  {
    role: "assistant",
    content: "你好！我是你的私人电影助理，有什么我可以帮你的吗？",
  },
]);

const sendMessage = async () => {
  if (!userInput.value.trim() || loading.value) return;

  const msg = userInput.value;
  messages.push({ role: "user", content: msg });
  userInput.value = "";
  loading.value = true;

  scrollToBottom();

  try {
    const res = await api.post("/ai/chat", { message: msg });
    messages.push({ role: "assistant", content: res.data.reply });
  } catch (e) {
    messages.push({
      role: "assistant",
      content: "抱歉，我的大脑信号有点弱，请稍后再试。",
    });
  } finally {
    loading.value = false;
    scrollToBottom();
  }
};

const scrollToBottom = () => {
  nextTick(() => {
    const box = document.getElementById("chatBox");
    box.scrollTop = box.scrollHeight;
  });
};
</script>

<style scoped>
.ai-page {
  background: #0a0a0a;
  min-height: 100vh;
  color: white;
  display: flex;
  flex-direction: column;
}
.navbar {
  height: 70px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 50px;
  border-bottom: 1px solid #222;
}
.logo span {
  color: #e50914;
  font-weight: bold;
}
.back-btn {
  background: none;
  border: 1px solid #444;
  color: white;
  padding: 5px 15px;
  border-radius: 5px;
  cursor: pointer;
}

.chat-container {
  flex: 1;
  max-width: 900px;
  margin: 20px auto;
  width: 95%;
  display: flex;
  flex-direction: column;
  background: #141414;
  border-radius: 15px;
  overflow: hidden;
  border: 1px solid #222;
}
.chat-window {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  scroll-behavior: smooth;
}

.msg-wrapper {
  display: flex;
  margin-bottom: 25px;
  gap: 15px;
}
.msg-wrapper.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #333;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}
.user .avatar {
  background: #e50914;
}

.bubble {
  max-width: 70%;
  padding: 12px 18px;
  border-radius: 15px;
  line-height: 1.6;
  font-size: 15px;
}
.assistant .bubble {
  background: #262626;
  color: #eee;
  border-top-left-radius: 2px;
}
.user .bubble {
  background: #e50914;
  color: white;
  border-top-right-radius: 2px;
}

.input-area {
  padding: 20px;
  background: #1a1a1a;
  display: flex;
  gap: 15px;
}
.input-area input {
  flex: 1;
  background: #222;
  border: 1px solid #333;
  color: white;
  padding: 12px 20px;
  border-radius: 30px;
  outline: none;
}
.input-area input:focus {
  border-color: #e50914;
}
.input-area button {
  background: #e50914;
  color: white;
  border: none;
  padding: 0 25px;
  border-radius: 30px;
  font-weight: bold;
  cursor: pointer;
}

/* 动画效果 */
.loading-dots span {
  animation: blink 1.4s infinite;
  margin: 0 2px;
}
.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}
.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes blink {
  0% {
    opacity: 0.2;
  }
  20% {
    opacity: 1;
  }
  100% {
    opacity: 0.2;
  }
}
</style>
