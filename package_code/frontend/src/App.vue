<template>
  <router-view v-if="isAuthRoute" />
  <AppShell v-else />
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import AppShell from "./components/layout/AppShell.vue";

const route = useRoute();
const isAuthRoute = computed(() => ["/login", "/register"].includes(route.path));
</script>
