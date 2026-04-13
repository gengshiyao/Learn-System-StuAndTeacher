<template>
  <el-card class="card">
    <div class="header">
      <div class="title">资源管理</div>
      <div class="actions">
        <el-radio-group v-model="viewMode">
          <el-radio-button label="卡片" />
          <el-radio-button label="表格" />
        </el-radio-group>
      </div>
    </div>

    <div class="filters">
      <el-select v-model="courseId" placeholder="请选择课程" style="width: 220px">
        <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-select v-model="kpId" placeholder="请选择知识点" style="width: 220px">
        <el-option v-for="kp in kps" :key="kp.id" :label="kp.name" :value="kp.id" />
      </el-select>
    </div>

    <el-form inline class="create-form">
      <el-form-item label="标题">
        <el-input v-model="form.title" />
      </el-form-item>
      <el-form-item label="类型">
        <el-select v-model="form.type">
          <el-option label="文档" value="doc" />
          <el-option label="视频" value="video" />
          <el-option label="练习" value="exercise" />
          <el-option label="测验" value="quiz" />
        </el-select>
      </el-form-item>
      <el-form-item label="链接">
        <el-input v-model="form.url" />
      </el-form-item>
      <el-form-item label="难度">
        <el-input-number v-model="form.difficulty" :min="1" :max="5" />
      </el-form-item>
      <el-form-item label="预计分钟">
        <el-input-number v-model="form.est_minutes" :min="5" :max="240" />
      </el-form-item>
      <el-button type="primary" @click="add">新增</el-button>
    </el-form>

    <div v-if="viewMode === '卡片'" class="card-view">
      <ResourceCard v-for="res in resources" :key="res.id" :resource="res" @use="openResource" />
    </div>
    <el-table v-else :data="resources" style="margin-top: 12px">
      <el-table-column prop="id" label="编号" width="80" />
      <el-table-column prop="title" label="标题" />
      <el-table-column label="类型" width="120">
        <template #default="scope">
          {{ typeLabel(scope.row.type) }}
        </template>
      </el-table-column>
      <el-table-column prop="url" label="链接" />
      <el-table-column label="操作" width="120">
        <template #default="scope">
          <el-button size="small" @click="remove(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from "vue";
import { api } from "../../api";
import ResourceCard from "../../components/cards/ResourceCard.vue";

const courses = ref<any[]>([]);
const courseId = ref<number | null>(null);
const kps = ref<any[]>([]);
const kpId = ref<number | null>(null);
const resources = ref<any[]>([]);
const viewMode = ref("卡片");

const form = reactive({
  title: "",
  type: "doc",
  url: "",
  difficulty: 2,
  est_minutes: 20
});

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
  if (kps.value.length && !kpId.value) {
    kpId.value = kps.value[0].id;
  }
};

const loadResources = async () => {
  if (!kpId.value) return;
  const resp = await api.resources(kpId.value);
  resources.value = resp.data.data;
};

const add = async () => {
  if (!kpId.value) return;
  await api.createResource({ ...form, kp_id: kpId.value });
  form.title = "";
  await loadResources();
};

const remove = async (id: number) => {
  await api.deleteResource(id);
  await loadResources();
};

const openResource = (res: any) => {
  window.open(res.url, "_blank");
};

const typeLabel = (value: string) => {
  if (value === "video") return "视频";
  if (value === "exercise") return "练习";
  if (value === "quiz") return "测验";
  return "文档";
};

onMounted(async () => {
  await loadCourses();
  await loadKps();
  await loadResources();
});

watch(courseId, async () => {
  await loadKps();
  await loadResources();
});

watch(kpId, loadResources);
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
  display: flex;
  gap: 12px;
}
.create-form {
  margin-bottom: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.card-view {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 12px;
}
</style>
