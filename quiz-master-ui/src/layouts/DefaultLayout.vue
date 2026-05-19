<template>
  <!-- DefaultLayout.vue -->
  <div class="page">
    <Flash />
    <Header />
    <main :class="[mainContentClass]">
      <RouterView />
      <Footer />
    </main>
  </div>
</template>

<script setup lang="ts">
import Header from "@/components/Header.vue";
import Flash from "@/components/flash.vue";
import Footer from '@/components/Footer.vue';
import { RouterView } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { computed } from 'vue';

const auth = useAuthStore();
const mainContentClass = computed(() => auth.userIsLoggedIn ? 'main-content' : 'main-content-logoff');
</script>

