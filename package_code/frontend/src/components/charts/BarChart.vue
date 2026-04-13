<template>
  <div ref="el" class="chart"></div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from "vue";
import * as echarts from "echarts";

const props = defineProps<{ option: any }>();
const el = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

const render = () => {
  if (!el.value) return;
  if (!chart) chart = echarts.init(el.value);
  chart.setOption(props.option || {}, true);
};

onMounted(() => {
  render();
  window.addEventListener("resize", render);
});

watch(() => props.option, render, { deep: true });

onUnmounted(() => {
  window.removeEventListener("resize", render);
  chart?.dispose();
});
</script>

<style scoped>
.chart {
  width: 100%;
  height: 280px;
}
</style>
