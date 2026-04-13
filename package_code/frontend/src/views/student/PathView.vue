<template>
  <div class="page-grid">
    <el-card class="card">
      <div class="header">
        <div>
          <div class="title">路径看板</div>
          <div class="meta">版本 {{ pathMeta.version || '-' }} · 生成时间 {{ pathMeta.created_at || '-' }}</div>
        </div>
        <div class="filters">
          <el-checkbox v-model="filters.requiredOnly">仅看必修</el-checkbox>
          <el-checkbox v-model="filters.unmasteredOnly">仅看未达标</el-checkbox>
          <el-select v-model="filters.difficulty" placeholder="难度筛选" clearable>
            <el-option v-for="d in [1,2,3,4,5]" :key="d" :label="`难度 ${d}`" :value="d" />
          </el-select>
        </div>
      </div>
      <div class="snapshot" v-if="strategySummary">策略摘要：{{ strategySummary }}</div>

      <div v-if="loading">
        <el-skeleton animated :rows="6" />
      </div>
      <div v-else>
        <div v-if="!weeks.length">
          <EmptyState title="暂无路径" desc="请先生成学习路径" action-text="去生成" @action="goGenerate" />
        </div>
        <div v-else class="weeks">
          <PathWeekCard
            v-for="week in weeks"
            :key="week.week"
            :week="week"
            :done-ids="doneIds"
            :locked="week.weekLocked"
            :prev-week="week.prevWeek"
            @open="openKp"
            @toggle="toggleDone"
          />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { api } from "../../api";
import PathWeekCard from "../../components/cards/PathWeekCard.vue";
import EmptyState from "../../components/utils/EmptyState.vue";

const router = useRouter();
const loading = ref(true);
const pathMeta = ref<any>({});
const strategySummary = ref("");
const weeks = ref<any[]>([]);
const rawWeeks = ref<any[]>([]);
const masteryMap = ref<Map<number, number>>(new Map());
const doneIds = ref<number[]>([]);
const filters = ref({
  requiredOnly: false,
  unmasteredOnly: false,
  difficulty: null as null | number
});

const openKp = (kp: any) => {
  router.push(`/student/kp/${kp.id}`);
};

const goGenerate = () => {
  router.push("/student/dashboard");
};

const kpId = (kp: any) => kp.kp_id || kp.id;

const toggleDone = (kp: any) => {
  const id = kpId(kp);
  if (doneIds.value.includes(id)) {
    doneIds.value = doneIds.value.filter((x) => x !== id);
  } else {
    doneIds.value.push(id);
  }
  localStorage.setItem("path_done", JSON.stringify(doneIds.value));
  refreshWeeksDisplay();
};

const buildWeeks = (items: any[], kps: any[]) => {
  const kpMap = new Map(kps.map((k: any) => [k.id, k]));
  const sequence = items.map((i: any) => ({ ...i, ...kpMap.get(i.kp_id) }));
  const weekPlan = JSON.parse(localStorage.getItem("latest_weeks") || "[]");
  if (weekPlan.length) {
    return weekPlan.map((w: any) => ({
      week: w.week,
      kps: w.kp_ids.map((id: number) => sequence.find((s: any) => s.kp_id === id)).filter(Boolean)
    }));
  }
  const result: any[] = [];
  let current: any[] = [];
  let total = 0;
  let weekIndex = 1;
  sequence.forEach((kp: any) => {
    const minutes = kp.est_minutes || 0;
    if (current.length && total + minutes > 300) {
      result.push({ week: weekIndex, kps: current });
      weekIndex += 1;
      current = [];
      total = 0;
    }
    current.push(kp);
    total += minutes;
  });
  if (current.length) result.push({ week: weekIndex, kps: current });
  return result;
};

const applyFilters = (weeksData: any[], map: Map<number, number>) => {
  return weeksData
    .map((week) => {
      const filtered = week.kps.filter((kp: any) => {
        if (filters.value.requiredOnly && !kp.required_flag) return false;
        if (filters.value.unmasteredOnly && (map.get(kp.kp_id) || 0.2) >= 0.7) return false;
        if (filters.value.difficulty && kp.difficulty !== filters.value.difficulty) return false;
        return true;
      });
      return { ...week, kps: filtered };
    })
    .filter((w) => w.kps.length);
};

/** 按「完整周」知识点是否全部勾选完成，决定当周是否解锁（第一周始终解锁）。 */
const attachWeekProgressLocks = (sourceRaw: any[], filteredWeeks: any[]) => {
  const done = doneIds.value;
  return filteredWeeks.map((w) => {
    const idx = sourceRaw.findIndex((r: any) => r.week === w.week);
    if (idx <= 0) {
      return { ...w, weekLocked: false, prevWeek: undefined };
    }
    const prev = sourceRaw[idx - 1];
    const prevComplete = prev.kps.length === 0 || prev.kps.every((kp: any) => done.includes(kpId(kp)));
    return {
      ...w,
      weekLocked: !prevComplete,
      prevWeek: prev.week as number
    };
  });
};

const refreshWeeksDisplay = () => {
  if (!rawWeeks.value.length) {
    weeks.value = [];
    return;
  }
  const filtered = applyFilters(rawWeeks.value, masteryMap.value);
  weeks.value = attachWeekProgressLocks(rawWeeks.value, filtered);
};

const loadData = async () => {
  loading.value = true;
  doneIds.value = JSON.parse(localStorage.getItem("path_done") || "[]");
  const courses = await api.courses();
  const courseId = courses.data.data[0]?.id;
  if (!courseId) {
    rawWeeks.value = [];
    weeks.value = [];
    loading.value = false;
    return;
  }
  const [pathResp, kpResp, masteryResp] = await Promise.all([
    api.latestPath(courseId),
    api.kps(courseId),
    api.mastery(courseId)
  ]);
  const pathData = pathResp.data.data;
  if (!pathData) {
    pathMeta.value = {};
    rawWeeks.value = [];
    weeks.value = [];
    loading.value = false;
    return;
  }
  pathMeta.value = pathData.path;
  if (pathData.path?.strategy_snapshot) {
    try {
      const params = JSON.parse(pathData.path.strategy_snapshot);
      strategySummary.value = `阈值 ${params.mastery_threshold} · 测验权重 ${params.alpha_quiz}`;
    } catch {
      strategySummary.value = "-";
    }
  }
  rawWeeks.value = buildWeeks(pathData.items, kpResp.data.data);
  masteryMap.value = new Map(masteryResp.data.data.map((m: any) => [m.kp_id, m.mastery_value]));
  refreshWeeksDisplay();
  loading.value = false;
};

watch(filters, () => refreshWeeksDisplay(), { deep: true });

onMounted(loadData);
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 12px;
}
.title {
  font-weight: 600;
  font-size: 18px;
}
.meta {
  color: var(--color-text-muted);
  font-size: 12px;
}
.filters {
  display: flex;
  gap: 12px;
  align-items: center;
}
.snapshot {
  margin: 10px 0 12px;
  color: var(--color-text-muted);
}
.weeks {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}
@media (max-width: 1024px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
