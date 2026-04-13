import axios from "axios";
import { ElMessage } from "element-plus";
import { useAuthStore } from "../store/auth";
import { useUiStore } from "../store/ui";

export const http = axios.create({
  baseURL: "/api"
});

http.interceptors.request.use((config) => {
  const store = useAuthStore();
  const ui = useUiStore();
  ui.startLoading();
  if (store.token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${store.token}`;
  }
  return config;
});

http.interceptors.response.use(
  (resp) => {
    const ui = useUiStore();
    ui.stopLoading();
    return resp;
  },
  (error) => {
    const ui = useUiStore();
    ui.stopLoading();
    const message = error?.response?.data?.message || "请求失败，请稍后重试";
    ElMessage.error(message);
    return Promise.reject(error);
  }
);
