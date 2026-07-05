import { createRouter, createWebHistory } from "vue-router";
import { hasToken } from "./api.js";
import LoginPage from "./pages/LoginPage.vue";
import WorkspacePage from "./pages/WorkspacePage.vue";
import ApplicationDetail from "./pages/ApplicationDetail.vue";

const routes = [
  { path: "/", redirect: "/workspace" },
  { path: "/login", component: LoginPage, meta: { public: true } },
  { path: "/workspace", component: WorkspacePage },
  { path: "/applications/:applicationId", component: ApplicationDetail }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to) {
    if (to.hash) {
      return { el: to.hash, behavior: "smooth", top: 88 };
    }
    return { top: 0 };
  }
});

router.beforeEach((to, _from, next) => {
  if (!to.meta.public && !hasToken()) {
    next("/login");
    return;
  }
  if (to.path === "/login" && hasToken()) {
    next("/workspace");
    return;
  }
  next();
});

export default router;
