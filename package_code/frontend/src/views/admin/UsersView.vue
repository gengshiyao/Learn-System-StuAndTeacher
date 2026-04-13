<template>
  <el-card class="card">
    <div class="header">
      <div class="title">用户管理</div>
      <el-button @click="load">刷新</el-button>
    </div>

    <div class="stats">
      <StatCard title="总用户数" :value="stats.total" />
      <StatCard title="学生数" :value="stats.student" />
      <StatCard title="教师数" :value="stats.teacher" />
      <StatCard title="管理员数" :value="stats.admin" />
    </div>

    <el-table :data="users">
      <el-table-column prop="id" label="编号" width="80" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column label="角色" width="120">
        <template #default="scope">
          {{ roleLabel(scope.row.role) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-select v-model="scope.row.role" size="small" style="width: 120px">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
            <el-option label="管理员" value="admin" />
          </el-select>
          <el-button size="small" @click="save(scope.row)">保存</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { api } from "../../api";
import StatCard from "../../components/cards/StatCard.vue";

const users = ref<any[]>([]);

const stats = computed(() => {
  const total = users.value.length;
  const student = users.value.filter((u) => u.role === "student").length;
  const teacher = users.value.filter((u) => u.role === "teacher").length;
  const admin = users.value.filter((u) => u.role === "admin").length;
  return { total, student, teacher, admin };
});

const load = async () => {
  const resp = await api.users();
  users.value = resp.data.data;
};

const save = async (user: any) => {
  await api.updateUser(user.id, { role: user.role });
  await load();
};

const roleLabel = (value: string) => {
  if (value === "student") return "学生";
  if (value === "teacher") return "教师";
  if (value === "admin") return "管理员";
  return value;
};

onMounted(load);
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-weight: 600;
  font-size: 18px;
}
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin: 16px 0;
}
</style>
