<template>
  <section class="login-page">
    <div class="login-panel">
      <div>
        <p class="eyebrow">Demo Admin</p>
        <h2>登录审批工作台</h2>
        <p class="page-subtitle">受保护页面需要先登录；如果浏览器仍保存上次 token，会显示为已登录状态。</p>
      </div>

      <el-form label-position="top" @submit.prevent>
        <el-form-item label="用户名">
          <el-input v-model="loginForm.username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="loginForm.password" type="password" show-password autocomplete="current-password" />
        </el-form-item>
        <div class="toolbar">
          <el-button @click="handleInitAdmin">初始化 demo admin</el-button>
          <el-button type="primary" :loading="loggingIn" @click="handleLogin">登录</el-button>
        </div>
      </el-form>
    </div>
  </section>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { initAdmin, login } from "../api.js";

const emit = defineEmits(["login-success"]);
const router = useRouter();
const loggingIn = ref(false);
const loginForm = ref({ username: "admin", password: "Admin@123456" });

async function handleInitAdmin() {
  try {
    await initAdmin();
    ElMessage.success("demo admin 已初始化");
  } catch (error) {
    ElMessage.info(`初始化返回：${error.message}`);
  }
}

async function handleLogin() {
  loggingIn.value = true;
  try {
    await login(loginForm.value.username, loginForm.value.password);
    emit("login-success");
    ElMessage.success("登录成功");
    await router.push("/workspace");
  } finally {
    loggingIn.value = false;
  }
}
</script>
