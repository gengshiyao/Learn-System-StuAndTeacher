<template>
  <el-card class="card">
    <div class="header">
      <div class="title">统计概览</div>
      <el-select v-model="courseId" placeholder="请选择课程" style="width: 220px">
        <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
    </div>

    <div class="stats">
      <StatCard title="学习事件数量" :value="stats.event_count" />
      <StatCard title="测验平均分" :value="stats.avg_score" />
      <StatCard title="达标率" :value="(stats.mastery_rate * 100).toFixed(1) + '%'" />
      <StatCard title="近7天活跃人数" :value="stats.active_users_7d" />
    </div>

    <div class="charts">
      <el-card class="card">
        <div class="section-title">活跃人数走势(近7天)</div>
        <LineChart :option="activeOption" />
      </el-card>
      <el-card class="card">
        <div class="section-title">测验均分与达标率</div>
        <BarChart :option="scoreOption" />
      </el-card>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { api } from "../../api";
import StatCard from "../../components/cards/StatCard.vue";
import LineChart from "../../components/charts/LineChart.vue";
import BarChart from "../../components/charts/BarChart.vue";

const courses = ref<any[]>([]);
const courseId = ref<number | null>(null);
const stats = ref<any>({
  event_count: 0,
  avg_score: 0,
  mastery_rate: 0,
  active_users_7d: 0
});

const activeOption = computed(() => {
  const labels = Array.from({ length: 7 }, (_, i) => `第${i + 1}天`);
  const values = labels.map(() => stats.value.active_users_7d || 0);
  return {
    xAxis: { type: "category", data: labels },
    yAxis: { type: "value" },
    series: [{ type: "line", data: values, smooth: true }]
  };
});

const scoreOption = computed(() => {
  return {
    xAxis: { type: "category", data: ["测验均分", "达标率"] },
    yAxis: { type: "value" },
    series: [
      {
        type: "bar",
        data: [stats.value.avg_score || 0, (stats.value.mastery_rate || 0) * 100]
      }
    ]
  };
});

const loadCourses = async () => {
  const resp = await api.courses();
  courses.value = resp.data.data;
  if (courses.value.length && !courseId.value) {
    courseId.value = courses.value[0].id;
  }
};

const load = async () => {
  if (!courseId.value) return;
  const resp = await api.stats(courseId.value);
  stats.value = resp.data.data;
};

onMounted(async () => {
  await loadCourses();
  await load();
});

watch(courseId, load);
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
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin: 16px 0;
}
.charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}
.section-title {
  font-weight: 600;
  margin-bottom: 8px;
}
</style>
