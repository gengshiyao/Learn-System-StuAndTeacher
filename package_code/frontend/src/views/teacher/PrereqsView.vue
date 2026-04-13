<template>
  <el-card class="card">
    <div class="header">
      <div class="title">先修关系</div>
      <el-button @click="loadPrereqs">刷新</el-button>
    </div>
    <div class="filters">
      <el-select v-model="courseId" placeholder="请选择课程" style="width: 220px">
        <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
    </div>

    <div class="split">
      <el-card class="card">
        <div class="section-title">依赖预览</div>
        <div ref="graphRef" class="graph"></div>
      </el-card>
      <el-card class="card">
        <div class="section-title">新增关系</div>
        <el-form inline>
          <el-form-item label="知识点">
            <el-select v-model="kpId">
              <el-option v-for="kp in kps" :key="kp.id" :label="kp.name" :value="kp.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="先修">
            <el-select v-model="prereqId">
              <el-option v-for="kp in kps" :key="kp.id" :label="kp.name" :value="kp.id" />
            </el-select>
          </el-form-item>
          <el-button type="primary" @click="add">新增</el-button>
        </el-form>

        <el-table :data="prereqs" style="margin-top: 12px">
          <el-table-column prop="id" label="编号" width="80" />
          <el-table-column prop="kp_id" label="知识点编号" width="120" />
          <el-table-column prop="prereq_kp_id" label="先修编号" width="120" />
          <el-table-column label="操作">
            <template #default="scope">
              <el-button size="small" @click="remove(scope.row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import * as echarts from "echarts";
import { api } from "../../api";

const courses = ref<any[]>([]);
const courseId = ref<number | null>(null);
const kps = ref<any[]>([]);
const prereqs = ref<any[]>([]);
const kpId = ref<number | null>(null);
const prereqId = ref<number | null>(null);
const graphRef = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

const loadCourses = async () => {
  const resp = await api.courses();
  courses.value = resp.data.data;
  if (courses.value.length && !courseId.value) {
    courseId.value = courses.value[0].id;
  }
};

const loadKps = async () => {
  if (!courseId.value) return;
  const resp = await api.kps(courseId.value);
  kps.value = resp.data.data;
};

const loadPrereqs = async () => {
  if (!courseId.value) return;
  const resp = await api.prereqs(courseId.value);
  prereqs.value = resp.data.data;
  renderGraph();
};

const renderGraph = () => {
  if (!graphRef.value) return;
  if (!chart) chart = echarts.init(graphRef.value);
  const nodes = kps.value.map((kp: any) => ({ name: kp.name }));
  const links = prereqs.value
    .map((edge: any) => {
      const source = kps.value.find((k: any) => k.id === edge.prereq_kp_id)?.name;
      const target = kps.value.find((k: any) => k.id === edge.kp_id)?.name;
      if (!source || !target) return null;
      return { source, target };
    })
    .filter(Boolean);
  chart.setOption({
    tooltip: {},
    series: [
      {
        type: "graph",
        layout: "force",
        roam: true,
        data: nodes,
        links,
        label: { show: true },
        force: { repulsion: 120, edgeLength: 80 }
      }
    ]
  });
};

const add = async () => {
  if (!kpId.value || !prereqId.value) return;
  await api.createPrereq({ kp_id: kpId.value, prereq_kp_id: prereqId.value });
  await loadPrereqs();
};

const remove = async (id: number) => {
  await api.deletePrereq(id);
  await loadPrereqs();
};

onMounted(async () => {
  await loadCourses();
  await loadKps();
  await loadPrereqs();
});

watch(courseId, async () => {
  await loadKps();
  await loadPrereqs();
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
.filters {
  margin: 12px 0;
}
.split {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 12px;
}
.section-title {
  font-weight: 600;
  margin-bottom: 10px;
}
.graph {
  height: 320px;
}
</style>
