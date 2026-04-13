<template>
  <div class="card stat-card">
    <div class="label">{{ title }}</div>
    <div class="value">{{ value }}</div>
    <div class="sub" v-if="subtext">{{ subtext }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; value: string | number; subtext?: string }>();
</script>

<style scoped>
.stat-card {
  padding: 16px;
  background: var(--color-surface);
}
.label {
  color: var(--color-text-muted);
  font-size: 13px;
}
.value {
  font-size: 24px;
  font-weight: 600;
  margin-top: 6px;
}
.sub {
  margin-top: 6px;
  color: var(--color-text-muted);
  font-size: 12px;
}
</style>
