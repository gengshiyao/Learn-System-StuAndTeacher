<template>
  <el-card class="card">
    <div class="header">
      <div class="title">学习分析</div>
      <div class="filters">
        <el-select v-model="eventType" placeholder="事件类型" clearable>
          <el-option label="浏览" value="view" />
          <el-option label="完成资源" value="complete_resource" />
          <el-option label="完成练习" value="complete_exercise" />
          <el-option label="测验" value="quiz" />
        </el-select>
        <el-date-picker v-model="dateRange" type="daterange" range-separator="到" start-placeholder="开始日期" end-placeholder="结束日期" />
      </div>
    </div>

    <div v-if="loading">
      <el-skeleton animated :rows="6" />
    </div>
    <div v-else class="charts">
      <el-card class="card">
        <div class="section-title">掌握度雷达</div>
        <RadarChart :option="radarOption" />
      </el-card>
      <el-card class="card">
        <div class="section-title">薄弱知识点前10</div>
        <BarChart :option="weakOption" />
      </el-card>
      <el-card class="card">
        <div class="section-title">测验成绩趋势</div>
        <LineChart :option="quizOption" />
      </el-card>
    </div>

    <el-divider />
    <div class="section-title">学习记录</div>
    <el-table :data="filteredEvents">
      <el-table-column prop="kp_id" label="知识点编号" width="120" />
      <el-table-column label="类型" width="140">
        <template #default="scope">
          {{ eventTypeLabel(scope.row.event_type) }}
        </template>
      </el-table-column>
      <el-table-column prop="duration_sec" label="时长(秒)" width="120" />
      <el-table-column prop="ts" label="时间" />
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { api } from "../../api";
import RadarChart from "../../components/charts/RadarChart.vue";
import BarChart from "../../components/charts/BarChart.vue";
import LineChart from "../../components/charts/LineChart.vue";

const loading = ref(true);
const mastery = ref<any[]>([]);
const events = ref<any[]>([]);
const quizRecords = ref<any[]>([]);
const eventType = ref<string | null>(null);
const dateRange = ref<[Date, Date] | null>(null);

const radarOption = computed(() => {
  const indicators = mastery.value.slice(0, 6).map((m: any) => ({ name: `知识点${m.kp_id}`, max: 1 }));
  const values = mastery.value.slice(0, 6).map((m: any) => m.mastery_value || 0.2);
  return {
    radar: { indicator: indicators },
    series: [{ type: "radar", data: [{ value: values }] }]
  };
});

const weakOption = computed(() => {
  const sorted = [...mastery.value].sort((a, b) => a.mastery_value - b.mastery_value).slice(0, 10);
  return {
    xAxis: { type: "value" },
    yAxis: { type: "category", data: sorted.map((m) => `知识点${m.kp_id}`) },
    series: [{ type: "bar", data: sorted.map((m) => m.mastery_value) }]
  };
});

const quizOption = computed(() => {
  const labels = quizRecords.value.map((q: any) => q.ts.slice(5, 10));
  const values = quizRecords.value.map((q: any) => q.score);
  return {
    xAxis: { type: "category", data: labels },
    yAxis: { type: "value", max: 100 },
    series: [{ type: "line", data: values, smooth: true }]
  };
});

const filteredEvents = computed(() => {
  return events.value.filter((e: any) => {
    if (eventType.value && e.event_type !== eventType.value) return false;
    if (dateRange.value) {
      const ts = new Date(e.ts).getTime();
      const start = dateRange.value[0].getTime();
      const end = dateRange.value[1].getTime();
      if (ts < start || ts > end) return false;
    }
    return true;
  });
});

const eventTypeLabel = (value: string) => {
  if (value === "complete_resource") return "完成资源";
  if (value === "complete_exercise") return "完成练习";
  if (value === "view") return "浏览";
  if (value === "quiz") return "测验";
  return value;
};

const load = async () => {
  loading.value = true;
  const courses = await api.courses();
  const courseId = courses.data.data[0]?.id;
  if (!courseId) return;
  const masteryResp = await api.mastery(courseId);
  mastery.value = masteryResp.data.data;
  events.value = JSON.parse(localStorage.getItem("recent_events") || "[]");
  quizRecords.value = JSON.parse(localStorage.getItem("quiz_records") || "[]").slice(0, 14).reverse();
  loading.value = false;
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
.filters {
  display: flex;
  gap: 12px;
}
.section-title {
  font-weight: 600;
  margin-bottom: 10px;
}
.charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}
@media (max-width: 1024px) {
  .filters {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
