<template>
  <el-card class="card">
    <div class="header">
      <div class="title">个人中心</div>
      <el-button type="danger" @click="logout">退出登录</el-button>
    </div>
    <div v-if="loading">
      <el-skeleton animated :rows="4" />
    </div>
    <div v-else class="info">
      <div class="item">
        <span class="label">用户编号</span>
        <span class="value">{{ userInfo.id }}</span>
      </div>
      <div class="item">
        <span class="label">用户名</span>
        <span class="value">{{ userInfo.username }}</span>
      </div>
      <div class="item">
        <span class="label">角色</span>
        <span class="value">{{ roleLabel }}</span>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { api } from "../../api";
import { useAuthStore } from "../../store/auth";

const router = useRouter();
const auth = useAuthStore();
const loading = ref(true);
const userInfo = ref({ id: "-", username: "-", role: "" });

const roleLabel = computed(() => {
  if (userInfo.value.role === "student") return "学生";
  if (userInfo.value.role === "teacher") return "教师";
  if (userInfo.value.role === "admin") return "管理员";
  return "未知";
});

const load = async () => {
  loading.value = true;
  const resp = await api.me();
  userInfo.value = resp.data.data;
  loading.value = false;
};

const logout = () => {
  auth.clear();
  router.push("/login");
};

onMounted(load);
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.title {
  font-weight: 600;
  font-size: 18px;
}
.info {
  display: grid;
  gap: 12px;
}
.item {
  display: flex;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 12px;
  background: var(--color-bg);
}
.label {
  color: var(--color-text-muted);
}
.value {
  font-weight: 600;
}
</style>
