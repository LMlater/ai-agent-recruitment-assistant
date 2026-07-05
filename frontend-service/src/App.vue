<template>
  <div class="app-shell">
    <header class="header">
      <div class="brand-block">
        <h1 class="brand-title">SmartCreditMultiAgent</h1>
        <div class="brand-subtitle">信贷审批辅助工作台</div>
      </div>

      <div class="capability-tags">
        <button
          v-for="item in capabilityItems"
          :key="item.id"
          class="capability-tag"
          type="button"
          :class="{ active: activeCapability === item.id }"
          @click="handleCapabilityClick(item)"
        >
          {{ item.label }}
        </button>
      </div>

      <div class="auth-status">
        <template v-if="loggedIn">
          <span>当前用户：admin</span>
          <el-button size="small" @click="handleLogout">退出登录</el-button>
        </template>
        <template v-else>
          <span>未登录</span>
          <el-button size="small" type="primary" @click="router.push('/login')">去登录</el-button>
        </template>
      </div>
    </header>

    <div class="layout">
      <aside v-if="loggedIn && route.path !== '/login'" class="sidebar">
        <button
          v-for="item in navItems"
          :key="item.id"
          class="nav-item"
          type="button"
          :class="{ active: activeNav === item.id }"
          @click="handleNavClick(item)"
        >
          <span class="nav-dot"></span>
          {{ item.label }}
        </button>
      </aside>

      <main class="main">
        <router-view @login-success="refreshAuth" />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { clearToken, hasToken } from "./api.js";

const LAST_BATCH_ROWS_KEY = "smartcredit.frontend.lastBatchRows";
const CURRENT_APPLICATION_ID_KEY = "smartcredit.frontend.currentApplicationId";

const router = useRouter();
const route = useRoute();
const loggedIn = ref(hasToken());

const navItems = [
  { id: "import", label: "文件导入", target: { path: "/workspace", hash: "#import" } },
  { id: "results", label: "批量检测结果", target: { path: "/workspace", hash: "#results" } },
  { id: "detail", label: "申请详情", requiresApplication: true, tab: "summary" },
  { id: "trace", label: "Agent Trace", requiresApplication: true, tab: "trace" },
  { id: "approval", label: "人工审批", requiresApplication: true, tab: "approval" }
];

const capabilityItems = [
  { id: "csv", label: "CSV批量导入", target: { path: "/workspace", hash: "#import" } },
  { id: "batch", label: "Batch AI Review", target: { path: "/workspace", hash: "#batch" } },
  { id: "tools", label: "Tool Trace", requiresApplication: true, tab: "tools" },
  { id: "policy", label: "Policy RAG", requiresApplication: true, tab: "policy" },
  { id: "approval", label: "Human-in-the-loop", requiresApplication: true, tab: "approval" },
  { id: "summary", label: "Real LLM Report", requiresApplication: true, tab: "summary" }
];

const activeNav = computed(() => {
  if (route.path === "/workspace") {
    return route.hash === "#results" ? "results" : "import";
  }
  if (route.path.startsWith("/applications/")) {
    return route.query.tab === "trace" ? "trace" : route.query.tab === "approval" ? "approval" : "detail";
  }
  return "";
});

const activeCapability = computed(() => {
  if (route.path === "/workspace") {
    return route.hash === "#batch" ? "batch" : "csv";
  }
  return route.query.tab || "";
});

watch(
  () => route.fullPath,
  () => {
    loggedIn.value = hasToken();
  }
);

function refreshAuth() {
  loggedIn.value = hasToken();
}

function currentApplicationId() {
  return localStorage.getItem(CURRENT_APPLICATION_ID_KEY) || "";
}

function clearLastBatchRows() {
  localStorage.removeItem(LAST_BATCH_ROWS_KEY);
  localStorage.removeItem(CURRENT_APPLICATION_ID_KEY);
}

async function handleLogout() {
  clearToken();
  clearLastBatchRows();
  loggedIn.value = false;
  await router.push("/login");
  ElMessage.success("已退出登录");
}

function handleNavClick(item) {
  if (item.requiresApplication) {
    navigateToCurrentApplication(item.tab);
    return;
  }
  navigateToWorkspace(item.target.hash);
}

function handleCapabilityClick(item) {
  if (item.requiresApplication) {
    navigateToCurrentApplication(item.tab);
    return;
  }
  navigateToWorkspace(item.target.hash);
}

function navigateToCurrentApplication(tab) {
  const applicationId = currentApplicationId();
  if (!applicationId) {
    ElMessage.warning("请先选择申请");
    return;
  }
  router.push({ path: `/applications/${applicationId}`, query: tab ? { tab } : {} });
}

function navigateToWorkspace(hash) {
  router.push({ path: "/workspace", hash });
  requestAnimationFrame(() => {
    document.getElementById(hash.replace("#", ""))?.scrollIntoView({ behavior: "smooth" });
  });
}
</script>
