<template>
  <div class="auth">
    <el-card class="card auth-card">
      <div class="title">欢迎登录</div>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="70px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" />
        </el-form-item>
        <el-button type="primary" @click="onLogin">登录</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { api } from "../api";
import { useAuthStore } from "../store/auth";

const router = useRouter();
const auth = useAuthStore();
const formRef = ref();
const form = reactive({ username: "", password: "" });

const rules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }]
};

const onLogin = async () => {
  await formRef.value.validate();
  const resp = await api.login(form);
  const data = resp.data.data;
  auth.setAuth(data.token, data.user);
  if (data.user.role === "teacher") {
    router.push("/teacher/kps");
  } else if (data.user.role === "admin") {
    router.push("/admin/users");
  } else {
    router.push("/student/dashboard");
  }
};
</script>

<style scoped>
.auth {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
}
.auth-card {
  width: 360px;
  padding: 20px;
}
.title {
  font-weight: 600;
  font-size: 18px;
  margin-bottom: 12px;
}
</style>
