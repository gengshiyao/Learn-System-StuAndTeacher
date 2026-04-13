<template>
  <div class="card timeline-card">
    <div class="header">最近活动</div>
    <el-timeline>
      <el-timeline-item v-for="item in items" :key="item.ts" :timestamp="item.ts">
        {{ item.text }}
      </el-timeline-item>
    </el-timeline>
  </div>
</template>

<script setup lang="ts">
defineProps<{ items: { ts: string; text: string }[] }>();
</script>

<style scoped>
.timeline-card {
  padding: 14px;
  background: var(--color-surface);
}
.header {
  font-weight: 600;
  margin-bottom: 8px;
}
</style>
