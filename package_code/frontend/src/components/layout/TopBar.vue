<template>
  <el-header class="topbar">
    <div class="left">
      <el-button text @click="$emit('toggle')">
        <el-icon><Menu /></el-icon>
      </el-button>
      <div class="title">
        <div class="page-title">{{ pageTitle }}</div>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item v-for="item in breadcrumbs" :key="item">{{ item }}</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
    </div>
    <div class="right">
      <el-switch
        v-model="darkMode"
        active-text="深色"
        inactive-text="浅色"
        @change="applyTheme"
      />
      <el-button text @click="goProfile">个人中心</el-button>
      <div class="user">
        <el-icon><UserFilled /></el-icon>
        <span>{{ username }}</span>
      </div>
    </div>
  </el-header>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Menu, UserFilled } from "@element-plus/icons-vue";
import { useAuthStore } from "../../store/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const darkMode = ref(false);

const pageTitle = computed(() => (route.meta.title as string) || "");
const breadcrumbs = computed(() => (route.meta.breadcrumbs as string[]) || []);
const username = computed(() => auth.user?.username || "未登录");
const role = computed(() => auth.user?.role || "");

const applyTheme = () => {
  const theme = darkMode.value ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
};

const goProfile = () => {
  if (role.value === "teacher") router.push("/teacher/profile");
  else if (role.value === "admin") router.push("/admin/profile");
  else router.push("/student/profile");
};

onMounted(() => {
  const stored = localStorage.getItem("theme") || "light";
  darkMode.value = stored === "dark";
  applyTheme();
});
</script>

<style scoped>
.topbar {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  padding: 0 16px;
}

.left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  font-weight: 600;
}

.right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text-muted);
}
</style>
