<template>
  <component :is="headerComponent" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AdminLoginHeader from './AdminLoginHeader.vue'
import UserLoginHeader from './UserLoginHeader.vue'

const auth = useAuthStore()

const headerComponent = computed(() => {
  const user = auth.user;
  if (!auth.userIsLoggedIn || !user) {
    return null;
  }
  if (user.isAdmin === true) {
    return AdminLoginHeader;
  } else if (user.isAdmin === false) {
    return UserLoginHeader;
  }
  return UserLoginHeader;
})
</script>
