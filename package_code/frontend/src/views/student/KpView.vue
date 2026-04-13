<template>
  <div class="page-grid three-cols">
    <div class="main">
      <el-card class="card">
        <div class="header">
          <div>
            <div class="title">{{ kpDetail?.name || '知识点详情' }}</div>
            <div class="meta">
              难度 {{ kpDetail?.difficulty || '-' }} · 预计 {{ kpDetail?.est_minutes || 0 }} 分钟
            </div>
          </div>
          <div class="progress">
            <el-progress :percentage="Math.round((masteryValue || 0.2) * 100)" />
          </div>
        </div>
      </el-card>

      <el-card class="card">
        <div class="section-title">资源列表</div>
        <div v-if="loading">
          <el-skeleton animated :rows="4" />
        </div>
        <div v-else class="resource-grid">
          <ResourceCard
            v-for="res in resources"
            :key="res.id"
            :resource="res"
            @use="selectResource"
          />
        </div>
      </el-card>

      <el-card class="card">
        <div class="section-title">学习操作</div>
        <div class="actions">
          <div class="timer">
            <div class="timer-value">{{ timerText }}</div>
            <div class="timer-actions">
              <el-button type="primary" @click="startTimer" :disabled="timerRunning">开始</el-button>
              <el-button @click="pauseTimer" :disabled="!timerRunning">暂停</el-button>
              <el-button type="success" @click="finishTimer">结束并提交</el-button>
            </div>
            <div class="hint muted">
              文档/视频类资源提交为「完成资源」；<strong>练习题</strong>在计时结束时记为「完成练习」，并解锁路径中的本节与下一节学习。
            </div>
          </div>
          <el-divider />
          <div class="quick-actions">
            <el-button type="warning" @click="completeExercise">完成练习题</el-button>
          </div>
          <div v-if="nextSectionId" class="next-section">
            <el-button type="primary" @click="goNextSection">下一节学习</el-button>
          </div>
          <el-divider />
          <div class="quiz">
            <div class="quiz-title">测验提交</div>
            <el-input-number v-model="score" :min="0" :max="100" />
            <el-button type="primary" @click="submitScore">提交测验</el-button>
          </div>
        </div>
      </el-card>
    </div>

    <div class="side">
      <el-card class="card">
        <div class="section-title">先修知识点</div>
        <div v-if="!prereqList.length" class="muted">暂无先修</div>
        <div class="chip-list">
          <el-tag v-for="kp in prereqList" :key="kp.id" @click="openKp(kp.id)">{{ kp.name }}</el-tag>
        </div>
      </el-card>
      <el-card class="card">
        <div class="section-title">后继知识点</div>
        <div v-if="!nextList.length" class="muted">暂无后继</div>
        <div class="chip-list">
          <el-tag v-for="kp in nextList" :key="kp.id" @click="openKp(kp.id)">{{ kp.name }}</el-tag>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onUnmounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { api } from "../../api";
import ResourceCard from "../../components/cards/ResourceCard.vue";

const route = useRoute();
const router = useRouter();
const kpId = ref(Number(route.params.id));
const kpDetail = ref<any>(null);
const resources = ref<any[]>([]);
const masteryValue = ref(0.2);
const prereqList = ref<any[]>([]);
const nextList = ref<any[]>([]);
const loading = ref(true);
const nextSectionId = ref<number | null>(null);

const score = ref(80);
const timerRunning = ref(false);
const elapsed = ref(0);
const activeResourceId = ref<number | null>(null);
let timer: number | null = null;

const currentResourceId = () => activeResourceId.value ?? resources.value[0]?.id;

const resourceMeta = (rid: number | undefined) =>
  rid != null ? resources.value.find((r: any) => r.id === rid) : undefined;

/** 与路径看板一致：记入本节完成，用于按周解锁 */
const markCurrentKpDoneOnPath = () => {
  const raw = JSON.parse(localStorage.getItem("path_done") || "[]");
  const set = new Set<number>(Array.isArray(raw) ? raw.map(Number) : []);
  set.add(kpId.value);
  localStorage.setItem("path_done", JSON.stringify([...set]));
};

const refreshNextSectionTarget = () => {
  const done = JSON.parse(localStorage.getItem("path_done") || "[]") as number[];
  if (!done.map(Number).includes(kpId.value)) {
    nextSectionId.value = null;
    return;
  }
  const items = JSON.parse(localStorage.getItem("latest_path_items") || "[]");
  const ids = items.map((i: any) => Number(i.kp_id));
  const idx = ids.indexOf(kpId.value);
  if (idx >= 0 && idx < ids.length - 1) {
    nextSectionId.value = ids[idx + 1];
    return;
  }
  nextSectionId.value = nextList.value[0]?.id ?? null;
};

const refreshMastery = async () => {
  const courses = await api.courses();
  const courseId = courses.data.data[0]?.id;
  if (!courseId) return;
  const masteryResp = await api.mastery(courseId);
  const row = masteryResp.data.data.find((m: any) => m.kp_id === kpId.value);
  if (row) masteryValue.value = row.mastery_value;
};

const timerText = ref("00:00");
const updateTimerText = () => {
  const minutes = Math.floor(elapsed.value / 60);
  const seconds = elapsed.value % 60;
  timerText.value = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
};

const startTimer = () => {
  timerRunning.value = true;
  if (timer) window.clearInterval(timer);
  timer = window.setInterval(() => {
    elapsed.value += 1;
    updateTimerText();
  }, 1000);
};

const pauseTimer = () => {
  timerRunning.value = false;
  if (timer) window.clearInterval(timer);
};

const finishTimer = async () => {
  if (!elapsed.value) return;
  const rid = currentResourceId();
  const meta = resourceMeta(rid);
  const isExercise = meta?.type === "exercise";
  await api.createEvent({
    kp_id: kpId.value,
    resource_id: rid,
    event_type: isExercise ? "complete_exercise" : "complete_resource",
    duration_sec: elapsed.value
  });
  cacheEvent(isExercise ? "complete_exercise" : "complete_resource", elapsed.value);
  if (isExercise) {
    markCurrentKpDoneOnPath();
    await refreshMastery();
    refreshNextSectionTarget();
    ElMessage.success("练习题已记录，路径中本节已勾选完成，可进入下一节学习");
  }
  elapsed.value = 0;
  updateTimerText();
  pauseTimer();
};

const completeExercise = async () => {
  await api.createEvent({
    kp_id: kpId.value,
    resource_id: currentResourceId(),
    event_type: "complete_exercise",
    duration_sec: 300
  });
  cacheEvent("complete_exercise", 300);
  markCurrentKpDoneOnPath();
  await refreshMastery();
  refreshNextSectionTarget();
  ElMessage.success("练习题已完成，可点击「下一节学习」或到路径看板继续");
};

const submitScore = async () => {
  const assessments = await api.assessments(kpId.value);
  const assessmentId = assessments.data.data[0]?.id;
  if (!assessmentId) return;
  await api.createRecord({ assessment_id: assessmentId, score: score.value });
  const records = JSON.parse(localStorage.getItem("quiz_records") || "[]");
  records.unshift({ kp_id: kpId.value, score: score.value, ts: new Date().toISOString() });
  localStorage.setItem("quiz_records", JSON.stringify(records.slice(0, 50)));
  cacheEvent("quiz", 0);
};

const cacheEvent = (eventType: string, duration: number) => {
  const events = JSON.parse(localStorage.getItem("recent_events") || "[]");
  events.unshift({
    kp_id: kpId.value,
    event_type: eventType,
    duration_sec: duration,
    ts: new Date().toISOString()
  });
  localStorage.setItem("recent_events", JSON.stringify(events.slice(0, 50)));
};

const selectResource = (res: any) => {
  window.open(res.url, "_blank");
  activeResourceId.value = res.id;
  if (!timerRunning.value) {
    startTimer();
  }
};

const openKp = (id: number) => {
  router.push(`/student/kp/${id}`);
};

const goNextSection = () => {
  if (nextSectionId.value != null) openKp(nextSectionId.value);
};

const loadData = async () => {
  loading.value = true;
  pauseTimer();
  elapsed.value = 0;
  activeResourceId.value = null;
  updateTimerText();
  const courses = await api.courses();
  const courseId = courses.data.data[0]?.id;
  if (!courseId) {
    loading.value = false;
    return;
  }
  const [kpResp, masteryResp, prereqResp, resourceResp] = await Promise.all([
    api.kps(courseId),
    api.mastery(courseId),
    api.prereqs(courseId),
    api.resources(kpId.value)
  ]);
  const allKps = kpResp.data.data;
  kpDetail.value = allKps.find((kp: any) => kp.id === kpId.value);
  masteryValue.value = masteryResp.data.data.find((m: any) => m.kp_id === kpId.value)?.mastery_value || 0.2;
  const scopedResources = (resourceResp.data.data || []).filter((res: any) => res.kp_id === kpId.value);
  resources.value = scopedResources;
  const cache = JSON.parse(localStorage.getItem("resource_cache") || "[]");
  const merged = [...cache, ...scopedResources].reduce((acc: any[], item: any) => {
    if (!acc.find((i) => i.id === item.id)) acc.push(item);
    return acc;
  }, []);
  localStorage.setItem("resource_cache", JSON.stringify(merged));

  const edges = prereqResp.data.data;
  const prereqIds = edges.filter((e: any) => e.kp_id === kpId.value).map((e: any) => e.prereq_kp_id);
  const nextIds = edges.filter((e: any) => e.prereq_kp_id === kpId.value).map((e: any) => e.kp_id);
  prereqList.value = allKps.filter((kp: any) => prereqIds.includes(kp.id));
  nextList.value = allKps.filter((kp: any) => nextIds.includes(kp.id));
  refreshNextSectionTarget();
  loading.value = false;
};

watch(
  () => route.params.id,
  (id) => {
    kpId.value = Number(id);
    updateTimerText();
    void loadData();
  },
  { immediate: true }
);

onUnmounted(() => {
  if (timer) window.clearInterval(timer);
});
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.title {
  font-size: 20px;
  font-weight: 600;
}
.meta {
  color: var(--color-text-muted);
  margin-top: 4px;
}
.progress {
  width: 240px;
}
.section-title {
  font-weight: 600;
  margin-bottom: 12px;
}
.resource-grid {
  display: grid;
  gap: 12px;
}
.actions {
  display: grid;
  gap: 12px;
}
.timer {
  display: grid;
  gap: 8px;
}
.timer-value {
  font-size: 24px;
  font-weight: 600;
}
.timer-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.hint {
  font-size: 12px;
  line-height: 1.5;
}
.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.next-section {
  margin-top: 4px;
}
.quiz {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.quiz-title {
  font-weight: 600;
}
.side {
  display: grid;
  gap: 16px;
}
.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.muted {
  color: var(--color-text-muted);
}
</style>
