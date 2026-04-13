<template>
  <el-card class="card">
    <div class="header">
      <div class="title">知识点管理</div>
      <el-button type="primary" @click="refresh">刷新</el-button>
    </div>
    <div class="filters">
      <el-select v-model="courseId" placeholder="请选择课程" style="width: 220px">
        <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
    </div>

    <el-form :model="form" inline class="create-form">
      <el-form-item label="名称">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="难度">
        <el-input-number v-model="form.difficulty" :min="1" :max="5" />
      </el-form-item>
      <el-form-item label="预计分钟">
        <el-input-number v-model="form.est_minutes" :min="5" :max="240" />
      </el-form-item>
      <el-form-item label="标签">
        <el-input v-model="form.tags" />
      </el-form-item>
      <el-button type="primary" @click="create">新增</el-button>
    </el-form>

    <el-table :data="kps" @row-click="openDrawer">
      <el-table-column type="index" label="编号" width="80" :index="courseLocalIndex" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="difficulty" label="难度" width="120" />
      <el-table-column prop="est_minutes" label="预计分钟" width="120" />
      <el-table-column label="操作" width="160">
        <template #default="scope">
          <el-button size="small" @click.stop="remove(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-drawer v-model="drawerVisible" title="知识点详情" size="30%">
    <el-form :model="editForm" label-width="90px">
      <el-form-item label="名称">
        <el-input v-model="editForm.name" />
      </el-form-item>
      <el-form-item label="难度">
        <el-input-number v-model="editForm.difficulty" :min="1" :max="5" />
      </el-form-item>
      <el-form-item label="预计分钟">
        <el-input-number v-model="editForm.est_minutes" :min="5" :max="240" />
      </el-form-item>
      <el-form-item label="标签">
        <el-input v-model="editForm.tags" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="editForm.description" type="textarea" />
      </el-form-item>
      <el-button type="primary" @click="save">保存</el-button>
    </el-form>
  </el-drawer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { api } from "../../api";

const courses = ref<any[]>([]);
const courseId = ref<number | null>(null);
const kps = ref<any[]>([]);
const drawerVisible = ref(false);

const form = reactive({
  name: "",
  difficulty: 2,
  est_minutes: 30,
  tags: ""
});

const editForm = reactive({
  id: 0,
  name: "",
  difficulty: 2,
  est_minutes: 30,
  tags: "",
  description: ""
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
};

const create = async () => {
  if (!courseId.value) return;
  await api.createKp({ ...form, course_id: courseId.value });
  form.name = "";
  await loadKps();
};

const remove = async (id: number) => {
  await api.deleteKp(id);
  await loadKps();
};

const openDrawer = (row: any) => {
  Object.assign(editForm, row);
  drawerVisible.value = true;
};

const save = async () => {
  await api.updateKp(editForm.id, { ...editForm });
  drawerVisible.value = false;
  await loadKps();
};

const refresh = async () => {
  await loadKps();
};

/** 与种子数据一致：Python基础 1–15，Python进阶 16–30，Python拓展 31–36 */
const globalKpIndexOffset = computed(() => {
  const c = courses.value.find((x) => x.id === courseId.value);
  const name = c?.name || "";
  if (name === "Python进阶") return 15;
  if (name === "Python拓展") return 30;
  return 0;
});

const courseLocalIndex = (index: number) => index + 1 + globalKpIndexOffset.value;

onMounted(async () => {
  await loadCourses();
  await loadKps();
});

watch(courseId, loadKps);
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
.create-form {
  margin-bottom: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
