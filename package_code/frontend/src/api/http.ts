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
    const data = error?.response?.data as { message?: string; msg?: string } | undefined;
    let message =
      (typeof data?.message === "string" && data.message) ||
      (typeof data?.msg === "string" && data.msg) ||
      "";
    if (!message) {
      if (!error.response) {
        message = "无法连接服务器，请确认后端已启动（python run.py）且前端代理指向 http://127.0.0.1:5000";
      } else {
        message = "请求失败，请稍后重试";
      }
    }
    if (error.response?.status === 401) {
      const store = useAuthStore();
      store.clear();
      const path = `${window.location.pathname}${window.location.search}`;
      if (!path.startsWith("/login")) {
        window.location.assign("/login");
      }
    }
    ElMessage.error(message);
    return Promise.reject(error);
  }
);
