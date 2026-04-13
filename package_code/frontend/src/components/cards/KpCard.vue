<template>
  <div class="card kp-card">
    <div class="header">
      <div class="title">{{ kp.name }}</div>
      <el-tag size="small" type="info">难度 {{ kp.difficulty }}</el-tag>
    </div>
    <div class="meta">预计 {{ kp.est_minutes }} 分钟</div>
    <div class="tags" v-if="kp.tags">
      <el-tag v-for="tag in kp.tags.split(',')" :key="tag" size="small" effect="plain">
        {{ tag }}
      </el-tag>
    </div>
    <el-button size="small" type="primary" @click="$emit('open', kp)">查看详情</el-button>
  </div>
</template>

<script setup lang="ts">
defineProps<{ kp: any }>();
defineEmits(["open"]);
</script>

<style scoped>
.kp-card {
  padding: 14px;
  background: var(--color-surface);
  display: grid;
  gap: 8px;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.title {
  font-weight: 600;
}
.meta {
  color: var(--color-text-muted);
  font-size: 12px;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
</style>
