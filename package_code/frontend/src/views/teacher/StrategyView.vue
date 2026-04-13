<template>
  <div class="page-grid three-cols">
    <el-card class="card">
      <div class="title">策略配置</div>
      <div class="filters">
        <el-select v-model="courseId" placeholder="请选择课程" style="width: 220px">
          <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </div>

      <el-form :model="form" label-width="140px" class="form">
        <el-form-item label="掌握度阈值">
          <el-input-number v-model="form.mastery_threshold" :min="0" :max="1" :step="0.05" />
        </el-form-item>
        <el-form-item label="测验权重">
          <el-input-number v-model="form.alpha_quiz" :min="0" :max="1" :step="0.05" />
        </el-form-item>
        <el-form-item label="练习权重">
          <el-input-number v-model="form.beta_exercise" :min="0" :max="1" :step="0.05" />
        </el-form-item>
        <el-form-item label="时长权重">
          <el-input-number v-model="form.gamma_time" :min="0" :max="1" :step="0.05" />
        </el-form-item>
        <el-form-item label="时长上限(分钟)">
          <el-input-number v-model="form.time_cap_min" :min="10" :max="240" />
        </el-form-item>
        <el-form-item label="衰减开关">
          <el-switch v-model="form.decay_enabled" />
        </el-form-item>
        <el-button type="primary" @click="save">保存</el-button>
      </el-form>
    </el-card>

    <el-card class="card">
      <div class="title">参数说明</div>
      <ul class="tips">
        <li>掌握度阈值：低于该值视为薄弱知识点。</li>
        <li>测验/练习/时长权重：三者之和建议为 1。</li>
        <li>时长上限：学习时长超过该值后不再累加。</li>
        <li>衰减开关：开启后可扩展为随时间衰减（当前仅展示）。</li>
      </ul>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from "vue";
import { api } from "../../api";

const courses = ref<any[]>([]);
const courseId = ref<number | null>(null);

const form = reactive({
  mastery_threshold: 0.7,
  alpha_quiz: 0.5,
  beta_exercise: 0.3,
  gamma_time: 0.2,
  time_cap_min: 60,
  decay_enabled: false
});

const loadCourses = async () => {
  const resp = await api.courses();
  courses.value = resp.data.data;
  if (courses.value.length && !courseId.value) {
    courseId.value = courses.value[0].id;
  }
};

const loadStrategy = async () => {
  if (!courseId.value) return;
  const resp = await api.getStrategy(courseId.value);
  const data = resp.data.data;
  if (data && data.params_json) {
    const parsed = JSON.parse(data.params_json);
    Object.assign(form, parsed);
  }
};

const save = async () => {
  if (!courseId.value) return;
  await api.updateStrategy({
    course_id: courseId.value,
    params_json: { ...form }
  });
};

onMounted(async () => {
  await loadCourses();
  await loadStrategy();
});

watch(courseId, loadStrategy);
</script>

<style scoped>
.title {
  font-weight: 600;
  font-size: 18px;
}
.filters {
  margin: 12px 0;
}
.form {
  margin-top: 12px;
}
.tips {
  margin: 12px 0 0;
  padding-left: 18px;
  color: var(--color-text-muted);
  display: grid;
  gap: 8px;
}
</style>
