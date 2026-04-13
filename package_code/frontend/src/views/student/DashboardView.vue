<template>
  <div class="page-grid three-cols">
    <div class="main">
      <el-card class="card">
        <div class="header-row">
          <div class="title">学习仪表盘</div>
          <div class="actions">
            <el-button type="primary" :disabled="!courseId" @click="generatePath">生成/刷新路径</el-button>
            <el-button :disabled="!canContinue" @click="continueLearning">继续学习</el-button>
          </div>
        </div>
        <div class="filters">
          <el-select v-model="courseId" placeholder="请选择课程" style="width: 220px">
            <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
          <el-input v-model="search" placeholder="搜索知识点或资源标题" clearable />
        </div>
        <div v-if="loading">
          <el-skeleton animated :rows="6" />
        </div>
        <div v-else>
          <div class="stats">
            <StatCard title="今日学习时长" :value="stats.todayMinutes + ' 分钟'" />
            <StatCard title="近7天学习次数" :value="stats.weekEvents" />
            <StatCard title="薄弱知识点数" :value="stats.weakCount" />
            <StatCard title="最近测验均分" :value="stats.quizAvg" />
          </div>
          <div class="charts">
            <el-card class="card chart-card">
              <div class="section-title">近14天学习时长</div>
              <LineChart :option="lineOption" />
            </el-card>
            <el-card class="card chart-card">
              <div class="section-title">掌握度分布</div>
              <BarChart :option="barOption" />
            </el-card>
          </div>
          <el-card class="card">
            <div class="section-title">推荐路径预览</div>
            <div v-if="!latestPathItems.length">
              <EmptyState title="暂无路径" desc="请先生成学习路径" action-text="生成路径" @action="generatePath" />
            </div>
            <div v-else class="path-preview">
              <el-tag v-for="kp in latestPathItems" :key="kp.id" class="chip">
                {{ kp.name }}
              </el-tag>
              <div class="week-summary">周计划：{{ weekSummary }}</div>
            </div>
          </el-card>
          <el-card class="card">
            <div class="section-title">知识点速览</div>
            <div class="kp-grid">
              <KpCard v-for="kp in kpPreview" :key="kp.id" :kp="kp" @open="openKp" />
            </div>
          </el-card>
        </div>
      </el-card>
    </div>
    <div class="side">
      <TimelineCard :items="timelineItems" />
      <el-card class="card search-card">
        <div class="section-title">搜索结果</div>
        <div v-if="!searchResults.length">
          <div class="muted">请输入关键词</div>
        </div>
        <div v-else class="search-list">
          <div v-for="item in searchResults" :key="item.key" class="search-item">
            {{ item.label }}
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { api } from "../../api";
import StatCard from "../../components/cards/StatCard.vue";
import KpCard from "../../components/cards/KpCard.vue";
import TimelineCard from "../../components/cards/TimelineCard.vue";
import LineChart from "../../components/charts/LineChart.vue";
import BarChart from "../../components/charts/BarChart.vue";
import EmptyState from "../../components/utils/EmptyState.vue";

const router = useRouter();
const courses = ref<any[]>([]);
const courseId = ref<number | null>(null);
const loading = ref(true);
const search = ref("");
const kps = ref<any[]>([]);
const mastery = ref<any[]>([]);
const latestPathItems = ref<any[]>([]);
const weekSummary = ref("");
const canContinue = ref(false);

const stats = ref({
  todayMinutes: 0,
  weekEvents: 0,
  weakCount: 0,
  quizAvg: 0
});

const timelineItems = ref<{ ts: string; text: string }[]>([]);

const lineOption = computed(() => {
  return {
    xAxis: { type: "category", data: statsLine.value.labels },
    yAxis: { type: "value" },
    series: [{ type: "line", data: statsLine.value.values, smooth: true }]
  };
});

const barOption = computed(() => {
  return {
    xAxis: { type: "category", data: ["0-0.3", "0.3-0.6", "0.6-0.8", "0.8-1"] },
    yAxis: { type: "value" },
    series: [{ type: "bar", data: statsBars.value }]
  };
});

const statsLine = ref({ labels: [] as string[], values: [] as number[] });
const statsBars = ref<number[]>([0, 0, 0, 0]);

const searchResults = computed(() => {
  if (!search.value) return [];
  const keyword = search.value.toLowerCase();
  const result: { key: string; label: string }[] = [];
  kps.value.forEach((kp: any) => {
    if (kp.name.toLowerCase().includes(keyword)) {
      result.push({ key: `kp-${kp.id}`, label: `知识点：${kp.name}` });
    }
  });
  const resources = JSON.parse(localStorage.getItem("resource_cache") || "[]");
  resources.forEach((res: any) => {
    if (res.title.toLowerCase().includes(keyword)) {
      result.push({ key: `res-${res.id}`, label: `资源：${res.title}` });
    }
  });
  return result.slice(0, 8);
});

const kpPreview = computed(() => kps.value.slice(0, 8));

const loadCourses = async () => {
  const resp = await api.courses();
  courses.value = resp.data.data;
  if (courses.value.length && !courseId.value) {
    courseId.value = courses.value[0].id;
  }
};

const loadDashboard = async () => {
  if (!courseId.value) {
    loading.value = false;
    return;
  }
  loading.value = true;
  try {
    const [kpResp, masteryResp, pathResp] = await Promise.all([
      api.kps(courseId.value),
      api.mastery(courseId.value),
      api.latestPath(courseId.value)
    ]);
    kps.value = kpResp.data.data;
    mastery.value = masteryResp.data.data;
    const pathData = pathResp.data.data;
    if (pathData && pathData.items) {
      localStorage.setItem("latest_path_items", JSON.stringify(pathData.items));
      const kpMap = new Map(kps.value.map((k: any) => [k.id, k]));
      latestPathItems.value = pathData.items
        .slice(0, 6)
        .map((item: any) => kpMap.get(item.kp_id))
        .filter(Boolean);
      const weeks = JSON.parse(localStorage.getItem("latest_weeks") || "[]");
      weekSummary.value = weeks.length ? `${weeks.length} 周` : "未生成周计划";
      const masteryMap = new Map(mastery.value.map((m: any) => [m.kp_id, m.mastery_value]));
      const firstWeak = pathData.items.find((item: any) => (masteryMap.get(item.kp_id) || 0.2) < 0.7);
      canContinue.value = !!firstWeak;
    } else {
      latestPathItems.value = [];
      weekSummary.value = "未生成周计划";
      canContinue.value = false;
    }
    refreshStats();
  } finally {
    loading.value = false;
  }
};

const refreshStats = () => {
  const events = JSON.parse(localStorage.getItem("recent_events") || "[]");
  const quizRecords = JSON.parse(localStorage.getItem("quiz_records") || "[]");
  const today = new Date().toDateString();
  let todayMinutes = 0;
  let weekEvents = 0;
  const now = Date.now();

  events.forEach((e: any) => {
    const ts = new Date(e.ts).toDateString();
    if (ts === today) todayMinutes += (e.duration_sec || 0) / 60;
    if (now - new Date(e.ts).getTime() <= 7 * 24 * 3600 * 1000) weekEvents += 1;
  });

  const weakCount = mastery.value.filter((m: any) => m.mastery_value < 0.7).length;
  const quizAvg = quizRecords.length
    ? Math.round(quizRecords.reduce((sum: number, r: any) => sum + r.score, 0) / quizRecords.length)
    : 0;

  stats.value = {
    todayMinutes: Math.round(todayMinutes),
    weekEvents,
    weakCount,
    quizAvg
  };

  const labels: string[] = [];
  const values: number[] = [];
  for (let i = 13; i >= 0; i -= 1) {
    const day = new Date(now - i * 24 * 3600 * 1000);
    const key = day.toISOString().slice(5, 10);
    labels.push(key);
    const sum = events
      .filter((e: any) => new Date(e.ts).toDateString() === day.toDateString())
      .reduce((acc: number, e: any) => acc + (e.duration_sec || 0), 0);
    values.push(Math.round(sum / 60));
  }
  statsLine.value = { labels, values };

  const buckets = [0, 0, 0, 0];
  mastery.value.forEach((m: any) => {
    const val = m.mastery_value;
    if (val < 0.3) buckets[0] += 1;
    else if (val < 0.6) buckets[1] += 1;
    else if (val < 0.8) buckets[2] += 1;
    else buckets[3] += 1;
  });
  statsBars.value = buckets;

  timelineItems.value = events.slice(0, 10).map((e: any) => ({
    ts: new Date(e.ts).toLocaleString(),
    text: `${eventLabel(e.event_type)} · 知识点 ${e.kp_id}`
  }));
};

const generatePath = async () => {
  if (!courseId.value) return;
  const resp = await api.generatePath({ course_id: courseId.value, time_budget_per_week_minutes: 300 });
  localStorage.setItem("latest_weeks", JSON.stringify(resp.data.data.weeks || []));
  await loadDashboard();
};

const openKp = (kp: any) => {
  router.push(`/student/kp/${kp.id}`);
};

const continueLearning = () => {
  if (!courseId.value) return;
  const masteryMap = new Map(mastery.value.map((m: any) => [m.kp_id, m.mastery_value]));
  const pathItems = JSON.parse(localStorage.getItem("latest_path_items") || "[]");
  if (!pathItems.length) {
    router.push("/student/path");
    return;
  }
  const target = pathItems.find((item: any) => (masteryMap.get(item.kp_id) || 0.2) < 0.7);
  if (target) router.push(`/student/kp/${target.kp_id}`);
};

const eventLabel = (value: string) => {
  if (value === "complete_resource") return "完成资源";
  if (value === "complete_exercise") return "完成练习";
  if (value === "view") return "浏览";
  if (value === "quiz") return "测验";
  return value;
};

onMounted(async () => {
  try {
    await loadCourses();
    await loadDashboard();
  } catch {
    loading.value = false;
  }
});

watch(courseId, async () => {
  await loadDashboard();
});
</script>

<style scoped>
.page-grid {
  gap: 16px;
}

.main {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.title {
  font-weight: 600;
  font-size: 18px;
}

.actions {
  display: flex;
  gap: 8px;
}

.filters {
  display: flex;
  gap: 12px;
  margin: 12px 0;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.section-title {
  font-weight: 600;
  margin-bottom: 10px;
}

.path-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.chip {
  margin-right: 6px;
}

.week-summary {
  color: var(--color-text-muted);
  margin-left: 8px;
}

.side {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

.search-card {
  padding: 12px;
}

.search-list {
  display: grid;
  gap: 8px;
}

.search-item {
  padding: 8px 10px;
  border-radius: 10px;
  background: var(--color-bg);
}

.kp-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.muted {
  color: var(--color-text-muted);
}

@media (max-width: 1024px) {
  .filters {
    flex-direction: column;
  }
}
</style>
