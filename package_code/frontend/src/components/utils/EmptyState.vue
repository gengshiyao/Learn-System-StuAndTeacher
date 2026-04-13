<template>
  <div class="empty">
    <div class="title">{{ title }}</div>
    <div class="desc">{{ desc }}</div>
    <el-button v-if="actionText" type="primary" @click="$emit('action')">
      {{ actionText }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; desc: string; actionText?: string }>();
defineEmits(["action"]);
</script>

<style scoped>
.empty {
  padding: 24px;
  border: 1px dashed var(--color-border);
  border-radius: 14px;
  text-align: center;
  background: var(--color-surface);
}
.title {
  font-weight: 600;
  margin-bottom: 6px;
}
.desc {
  color: var(--color-text-muted);
  margin-bottom: 12px;
}
</style>
