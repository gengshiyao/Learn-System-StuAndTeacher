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
          </div>
          <el-divider />
          <div class="quick-actions">
            <el-button type="warning" @click="completeExercise">快速完成练习</el-button>
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
import { onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api } from "../../api";
import ResourceCard from "../../components/cards/ResourceCard.vue";

const route = useRoute();
const router = useRouter();
const kpId = Number(route.params.id);
const kpDetail = ref<any>(null);
const resources = ref<any[]>([]);
const masteryValue = ref(0.2);
const prereqList = ref<any[]>([]);
const nextList = ref<any[]>([]);
const loading = ref(true);

const score = ref(80);
const timerRunning = ref(false);
const elapsed = ref(0);
const activeResourceId = ref<number | null>(null);
let timer: number | null = null;

const currentResourceId = () => activeResourceId.value ?? resources.value[0]?.id;

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
  await api.createEvent({
    kp_id: kpId,
    resource_id: currentResourceId(),
    event_type: "complete_resource",
    duration_sec: elapsed.value
  });
  cacheEvent("complete_resource", elapsed.value);
  elapsed.value = 0;
  updateTimerText();
  pauseTimer();
};

const completeExercise = async () => {
  await api.createEvent({
    kp_id: kpId,
    resource_id: currentResourceId(),
    event_type: "complete_exercise",
    duration_sec: 300
  });
  cacheEvent("complete_exercise", 300);
};

const submitScore = async () => {
  const assessments = await api.assessments(kpId);
  const assessmentId = assessments.data.data[0]?.id;
  if (!assessmentId) return;
  await api.createRecord({ assessment_id: assessmentId, score: score.value });
  const records = JSON.parse(localStorage.getItem("quiz_records") || "[]");
  records.unshift({ kp_id: kpId, score: score.value, ts: new Date().toISOString() });
  localStorage.setItem("quiz_records", JSON.stringify(records.slice(0, 50)));
  cacheEvent("quiz", 0);
};

const cacheEvent = (eventType: string, duration: number) => {
  const events = JSON.parse(localStorage.getItem("recent_events") || "[]");
  events.unshift({
    kp_id: kpId,
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

const loadData = async () => {
  loading.value = true;
  pauseTimer();
  elapsed.value = 0;
  activeResourceId.value = null;
  updateTimerText();
  const courses = await api.courses();
  const courseId = courses.data.data[0]?.id;
  if (!courseId) return;
  const [kpResp, masteryResp, prereqResp, resourceResp] = await Promise.all([
    api.kps(courseId),
    api.mastery(courseId),
    api.prereqs(courseId),
    api.resources(kpId)
  ]);
  const allKps = kpResp.data.data;
  kpDetail.value = allKps.find((kp: any) => kp.id === kpId);
  masteryValue.value = masteryResp.data.data.find((m: any) => m.kp_id === kpId)?.mastery_value || 0.2;
  const scopedResources = (resourceResp.data.data || []).filter((res: any) => res.kp_id === kpId);
  resources.value = scopedResources;
  const cache = JSON.parse(localStorage.getItem("resource_cache") || "[]");
  const merged = [...cache, ...scopedResources].reduce((acc: any[], item: any) => {
    if (!acc.find((i) => i.id === item.id)) acc.push(item);
    return acc;
  }, []);
  localStorage.setItem("resource_cache", JSON.stringify(merged));

  const edges = prereqResp.data.data;
  const prereqIds = edges.filter((e: any) => e.kp_id === kpId).map((e: any) => e.prereq_kp_id);
  const nextIds = edges.filter((e: any) => e.prereq_kp_id === kpId).map((e: any) => e.kp_id);
  prereqList.value = allKps.filter((kp: any) => prereqIds.includes(kp.id));
  nextList.value = allKps.filter((kp: any) => nextIds.includes(kp.id));
  loading.value = false;
};

onMounted(() => {
  updateTimerText();
  loadData();
});

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
}
.quick-actions {
  display: flex;
  gap: 8px;
}
.quiz {
  display: flex;
  align-items: center;
  gap: 8px;
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
