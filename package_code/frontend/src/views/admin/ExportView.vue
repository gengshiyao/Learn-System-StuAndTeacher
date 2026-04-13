<template>
  <el-card class="card">
    <div class="header">
      <div class="title">数据导出</div>
      <el-select v-model="courseId" placeholder="请选择课程" style="width: 220px">
        <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
    </div>

    <div class="grid">
      <div v-for="item in exportItems" :key="item.type" class="card export-card">
        <div class="item-title">{{ item.title }}</div>
        <div class="item-desc">{{ item.desc }}</div>
        <div class="item-time">最近导出：{{ lastExport[item.type] || '暂无' }}</div>
        <el-button type="primary" @click="download(item.type)">下载 CSV</el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api } from "../../api";

const courses = ref<any[]>([]);
const courseId = ref<number | null>(null);
const lastExport = ref<Record<string, string>>({});

const exportItems = [
  {
    type: "events",
    title: "学习事件",
    desc: "字段：user_id、kp_id、event_type、duration_sec、ts"
  },
  {
    type: "records",
    title: "测验记录",
    desc: "字段：user_id、assessment_id、score、submit_time"
  },
  {
    type: "mastery",
    title: "掌握度",
    desc: "字段：user_id、kp_id、mastery_value、updated_at"
  },
  {
    type: "paths",
    title: "学习路径",
    desc: "字段：user_id、course_id、version、kp_id、seq、required_flag"
  }
];

const loadCourses = async () => {
  const resp = await api.courses();
  courses.value = resp.data.data;
  if (courses.value.length && !courseId.value) {
    courseId.value = courses.value[0].id;
  }
};

const download = async (type: string) => {
  if (!courseId.value) return;
  let resp;
  if (type === "events") resp = await api.exportEvents(courseId.value);
  if (type === "records") resp = await api.exportRecords(courseId.value);
  if (type === "mastery") resp = await api.exportMastery(courseId.value);
  if (type === "paths") resp = await api.exportPaths(courseId.value);
  if (!resp) return;
  const blob = new Blob([resp.data], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${type}.csv`;
  link.click();
  URL.revokeObjectURL(url);
  const record = { ...(JSON.parse(localStorage.getItem("export_times") || "{}")) };
  record[type] = new Date().toLocaleString();
  localStorage.setItem("export_times", JSON.stringify(record));
  lastExport.value = record;
};

onMounted(() => {
  loadCourses();
  lastExport.value = JSON.parse(localStorage.getItem("export_times") || "{}" );
});
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
.grid {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}
.export-card {
  padding: 16px;
  display: grid;
  gap: 8px;
  background: var(--color-surface);
}
.item-title {
  font-weight: 600;
}
.item-desc,
.item-time {
  color: var(--color-text-muted);
  font-size: 12px;
}
</style>
