<template>
  <el-aside :width="collapsed ? '72px' : '240px'" class="sidebar">
    <div class="brand">
      <span v-if="!collapsed">学习路径系统</span>
      <span v-else>学</span>
    </div>
    <el-menu :default-active="active" router class="menu" :collapse="collapsed">
      <el-sub-menu v-if="isStudent" index="student">
        <template #title>
          <el-icon><HomeFilled /></el-icon>
          <span>学生端</span>
        </template>
        <el-menu-item index="/student/dashboard">学习仪表盘</el-menu-item>
        <el-menu-item index="/student/path">学习路径</el-menu-item>
        <el-menu-item index="/student/progress">学习分析</el-menu-item>
        <el-menu-item index="/student/profile">个人中心</el-menu-item>
      </el-sub-menu>
      <el-sub-menu v-if="isTeacher" index="teacher">
        <template #title>
          <el-icon><Reading /></el-icon>
          <span>教师端</span>
        </template>
        <el-menu-item index="/teacher/kps">知识点管理</el-menu-item>
        <el-menu-item index="/teacher/prereqs">先修关系</el-menu-item>
        <el-menu-item index="/teacher/resources">资源管理</el-menu-item>
        <el-menu-item index="/teacher/strategy">策略配置</el-menu-item>
        <el-menu-item index="/teacher/stats">统计概览</el-menu-item>
        <el-menu-item index="/teacher/profile">个人中心</el-menu-item>
      </el-sub-menu>
      <el-sub-menu v-if="isAdmin" index="admin">
        <template #title>
          <el-icon><User /></el-icon>
          <span>管理端</span>
        </template>
        <el-menu-item index="/admin/users">用户管理</el-menu-item>
        <el-menu-item index="/admin/export">数据导出</el-menu-item>
        <el-menu-item index="/admin/profile">个人中心</el-menu-item>
      </el-sub-menu>
    </el-menu>
  </el-aside>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import { HomeFilled, Notebook, PieChart, Reading, User } from "@element-plus/icons-vue";

const props = defineProps<{ collapsed: boolean; role: string }>();

const route = useRoute();
const active = computed(() => route.path);
const isStudent = computed(() => props.role === "student");
const isTeacher = computed(() => props.role === "teacher");
const isAdmin = computed(() => props.role === "admin");
</script>

<style scoped>
.sidebar {
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  min-height: 100vh;
}

.brand {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: var(--color-text);
  border-bottom: 1px solid var(--color-border);
}

.menu {
  border-right: none;
}
</style>
