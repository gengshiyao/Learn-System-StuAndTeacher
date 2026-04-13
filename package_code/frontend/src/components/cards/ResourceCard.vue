<template>
  <div class="card resource-card">
    <div class="cover" :style="{ backgroundImage: `url(${cover})` }"></div>
    <div class="body">
      <div class="title">{{ resource.title }}</div>
      <div class="meta">{{ typeLabel }} · 难度 {{ resource.difficulty }} · {{ resource.est_minutes }} 分钟</div>
      <div class="link">{{ resource.url }}</div>
      <el-button size="small" type="primary" @click="$emit('use', resource)">开始使用</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import docCover from "../../assets/covers/doc.svg";
import videoCover from "../../assets/covers/video.svg";
import exerciseCover from "../../assets/covers/exercise.svg";
import quizCover from "../../assets/covers/quiz.svg";

const props = defineProps<{ resource: any }>();
defineEmits(["use"]);

const cover = computed(() => {
  if (props.resource.type === "video") return videoCover;
  if (props.resource.type === "exercise") return exerciseCover;
  if (props.resource.type === "quiz") return quizCover;
  return docCover;
});

const typeLabel = computed(() => {
  if (props.resource.type === "video") return "视频";
  if (props.resource.type === "exercise") return "练习";
  if (props.resource.type === "quiz") return "测验";
  return "文档";
});
</script>

<style scoped>
.resource-card {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 12px;
  padding: 12px;
  background: var(--color-surface);
}
.cover {
  border-radius: 12px;
  background-size: cover;
  background-position: center;
  min-height: 100px;
}
.title {
  font-weight: 600;
}
.meta {
  color: var(--color-text-muted);
  font-size: 12px;
  margin: 4px 0 6px;
}
.link {
  color: var(--color-text-muted);
  font-size: 12px;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
