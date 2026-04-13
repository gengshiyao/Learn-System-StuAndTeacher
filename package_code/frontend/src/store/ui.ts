import { defineStore } from "pinia";

export const useUiStore = defineStore("ui", {
  state: () => ({
    loadingCount: 0
  }),
  actions: {
    startLoading() {
      this.loadingCount += 1;
    },
    stopLoading() {
      this.loadingCount = Math.max(0, this.loadingCount - 1);
    }
  }
});
