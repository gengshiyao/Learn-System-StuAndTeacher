<template>
  <el-container :class="['app-shell', roleClass]" direction="vertical">
    <TopBar :collapsed="collapsed" @toggle="toggle" />
    <el-container class="shell-body">
      <SidebarNav :collapsed="collapsed" :role="role" @toggle="toggle" />
      <el-main :class="['main-content', roleClass]" v-loading="ui.loadingCount > 0">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";
import SidebarNav from "./SidebarNav.vue";
import TopBar from "./TopBar.vue";
import { useUiStore } from "../../store/ui";
import { useAuthStore } from "../../store/auth";

const ui = useUiStore();
const auth = useAuthStore();
const collapsed = ref(false);
const router = useRouter();
const role = computed(() => auth.user?.role || "guest");
const roleClass = computed(() => `role-${role.value}`);

const toggle = () => {
  collapsed.value = !collapsed.value;
};

let mediaQuery: MediaQueryList | null = null;
const syncCollapse = () => {
  if (!mediaQuery) return;
  collapsed.value = mediaQuery.matches;
};

onMounted(() => {
  mediaQuery = window.matchMedia("(max-width: 1024px)");
  syncCollapse();
  mediaQuery.addEventListener("change", syncCollapse);
  router.beforeEach(() => {
    ui.startLoading();
    return true;
  });
  router.afterEach(() => {
    ui.stopLoading();
  });
});

onUnmounted(() => {
  if (mediaQuery) mediaQuery.removeEventListener("change", syncCollapse);
});
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: var(--color-bg);
}

.shell-body {
  min-height: calc(100vh - 64px);
}

.main-content {
  padding: 18px 20px 32px;
  width: 100%;
}
</style>
