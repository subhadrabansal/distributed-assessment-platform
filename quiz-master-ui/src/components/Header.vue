<template>
  <component :is="headerComponent" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import LoginHeader from './LoginHeader.vue'
import LogoutHeader from './LogoutHeader.vue'

const auth = useAuthStore()
const headerComponent = computed(() => {
  return auth.userIsLoggedIn ? LoginHeader : LogoutHeader
})
</script>
