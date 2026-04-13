<template>
  <div class="card week-card" :class="{ 'week-card--locked': isLocked }">
    <div v-if="isLocked" class="lock-banner">{{ lockHint }}</div>
    <div class="header">
      <div class="title">第 {{ week.week }} 周</div>
      <div class="meta">预计 {{ totalMinutes }} 分钟</div>
    </div>
    <div class="chips">
      <div v-for="kp in week.kps" :key="kp.id" class="chip-item">
        <el-tag
          :type="kp.required_flag ? 'success' : 'info'"
          class="chip"
          :class="{ 'chip--disabled': isLocked }"
          @click="onOpen(kp)"
        >
          {{ kp.name }}
        </el-tag>
        <el-checkbox
          :disabled="isLocked"
          :model-value="doneIds.includes(kp.kp_id || kp.id)"
          @change="() => onToggle(kp)"
        >
          完成
        </el-checkbox>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const emit = defineEmits(["open", "toggle"]);
const props = defineProps<{
  week: { week: number; kps: any[] };
  doneIds: number[];
  locked?: boolean;
  prevWeek?: number;
}>();

const isLocked = computed(() => !!props.locked);

const lockHint = computed(() =>
  props.prevWeek != null
    ? `请先完成第 ${props.prevWeek} 周全部任务后再学习本周`
    : "请先完成上一周全部任务后再学习本周"
);

const onOpen = (kp: any) => {
  if (isLocked.value) return;
  emit("open", kp);
};

const onToggle = (kp: any) => {
  if (isLocked.value) return;
  emit("toggle", kp);
};

const totalMinutes = computed(() =>
  props.week.kps.reduce((sum, kp) => sum + (kp.est_minutes || 0), 0)
);
</script>

<style scoped>
.week-card {
  padding: 14px;
  background: var(--color-surface);
  display: grid;
  gap: 10px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-weight: 600;
}
.meta {
  color: var(--color-text-muted);
  font-size: 12px;
}
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.chip-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.chip {
  cursor: pointer;
}
.chip--disabled {
  cursor: not-allowed;
  opacity: 0.55;
}
.week-card--locked {
  position: relative;
  opacity: 0.92;
}
.lock-banner {
  font-size: 12px;
  color: var(--el-color-warning);
  background: color-mix(in srgb, var(--el-color-warning) 12%, transparent);
  border-radius: 6px;
  padding: 8px 10px;
  margin-bottom: 4px;
}
</style>
