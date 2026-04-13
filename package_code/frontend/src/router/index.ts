import { createRouter, createWebHistory } from "vue-router";

import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import StudentDashboard from "../views/student/DashboardView.vue";
import StudentPath from "../views/student/PathView.vue";
import StudentKp from "../views/student/KpView.vue";
import StudentProgress from "../views/student/ProgressView.vue";
import TeacherKps from "../views/teacher/KpsView.vue";
import TeacherPrereqs from "../views/teacher/PrereqsView.vue";
import TeacherResources from "../views/teacher/ResourcesView.vue";
import TeacherStrategy from "../views/teacher/StrategyView.vue";
import TeacherStats from "../views/teacher/StatsView.vue";
import AdminUsers from "../views/admin/UsersView.vue";
import AdminExport from "../views/admin/ExportView.vue";
import ProfileView from "../views/profile/ProfileView.vue";

const routes = [
  { path: "/", redirect: "/login" },
  {
    path: "/login",
    component: LoginView,
    meta: { title: "登录", breadcrumbs: ["登录"] }
  },
  {
    path: "/register",
    component: RegisterView,
    meta: { title: "注册", breadcrumbs: ["注册"] }
  },
  {
    path: "/student/dashboard",
    component: StudentDashboard,
    meta: { title: "学生仪表盘", breadcrumbs: ["学生端", "仪表盘"] }
  },
  {
    path: "/student/path",
    component: StudentPath,
    meta: { title: "学习路径", breadcrumbs: ["学生端", "学习路径"] }
  },
  {
    path: "/student/kp/:id",
    component: StudentKp,
    meta: { title: "知识点详情", breadcrumbs: ["学生端", "知识点详情"] }
  },
  {
    path: "/student/progress",
    component: StudentProgress,
    meta: { title: "学习分析", breadcrumbs: ["学生端", "学习分析"] }
  },
  {
    path: "/student/profile",
    component: ProfileView,
    meta: { title: "个人中心", breadcrumbs: ["学生端", "个人中心"] }
  },
  {
    path: "/teacher/kps",
    component: TeacherKps,
    meta: { title: "知识点管理", breadcrumbs: ["教师端", "知识点"] }
  },
  {
    path: "/teacher/prereqs",
    component: TeacherPrereqs,
    meta: { title: "先修关系", breadcrumbs: ["教师端", "先修关系"] }
  },
  {
    path: "/teacher/resources",
    component: TeacherResources,
    meta: { title: "资源管理", breadcrumbs: ["教师端", "资源管理"] }
  },
  {
    path: "/teacher/strategy",
    component: TeacherStrategy,
    meta: { title: "策略配置", breadcrumbs: ["教师端", "策略配置"] }
  },
  {
    path: "/teacher/stats",
    component: TeacherStats,
    meta: { title: "统计概览", breadcrumbs: ["教师端", "统计概览"] }
  },
  {
    path: "/teacher/profile",
    component: ProfileView,
    meta: { title: "个人中心", breadcrumbs: ["教师端", "个人中心"] }
  },
  {
    path: "/admin/users",
    component: AdminUsers,
    meta: { title: "用户管理", breadcrumbs: ["管理端", "用户管理"] }
  },
  {
    path: "/admin/export",
    component: AdminExport,
    meta: { title: "数据导出", breadcrumbs: ["管理端", "数据导出"] }
  },
  {
    path: "/admin/profile",
    component: ProfileView,
    meta: { title: "个人中心", breadcrumbs: ["管理端", "个人中心"] }
  }
];

export const router = createRouter({
  history: createWebHistory(),
  routes
});

const getRole = () => {
  try {
    const user = JSON.parse(localStorage.getItem("user") || "null");
    return user?.role || null;
  } catch {
    return null;
  }
};

router.beforeEach((to) => {
  const publicRoutes = ["/login", "/register"];
  if (publicRoutes.includes(to.path)) return true;
  const role = getRole();
  if (!role) return "/login";
  if (role === "student" && (to.path.startsWith("/teacher") || to.path.startsWith("/admin"))) {
    return "/student/dashboard";
  }
  if (role === "teacher" && (to.path.startsWith("/student") || to.path.startsWith("/admin"))) {
    return "/teacher/kps";
  }
  if (role === "admin" && (to.path.startsWith("/student") || to.path.startsWith("/teacher"))) {
    return "/admin/users";
  }
  return true;
});
