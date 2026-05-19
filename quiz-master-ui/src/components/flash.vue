<script setup lang="ts">
import { useFlashStore } from '@/stores/flash'
import { computed } from 'vue'

const flash = useFlashStore()
const isVisible = computed(() => !!flash.message)
</script>

<template>
  <div
    v-if="isVisible"
    :class="['flash-message', flash.type]"
    style="position:fixed;top:70px;right:20px;z-index:9999;min-width:200px;padding: 15px; border-radius: 4px; color: #fff; font-weight: 500;"
  >
    <li>{{ flash.message }}</li>
  </div>
</template>

<style scoped>
.flash-message.success {
  background: #198754;
  border-left: 5px solid #145c32;
}
.flash-message.error {
  background: #dc3545;
  border-left: 5px solid #a71d2a;
}
.flash-message.info {
  background: #0dcaf0;
  border-left: 5px solid #0a6b8a;
}
</style>