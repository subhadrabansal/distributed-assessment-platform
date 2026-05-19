<template>
    <!-- Navbar -->
    <nav class="navbar navbar-dark bg-dark fixed-top px-3 d-flex justify-content-between">
    <div>
        <button class="btn btn-outline-light d-md-none" @click="toggleSidebar">☰</button>
        <a class="navbar-brand ms-2" href="#">
        <img src="/src/assets/dap-logo.png" alt="Logo" style="width: 140px;">
        </a>
    </div>
        <div >
        <img :src="getProfilePicUrl(auth.user?.profile_picture)" alt="User" class="profile-pic me-2">
        <button class="btn btn-danger" @click="handleLogout">Logout</button>
    </div>
    </nav>

    <!-- Desktop Sidebar -->
    <div class="fixed-sidebar sidebar d-none d-md-block">
    <div class="d-flex justify-content-between align-items-center py-1">
        <input class="form-control me-1 " type="search" placeholder="Search" aria-label="Search"
          v-model="sidebarSearch" @keyup="onSidebarSearchKeyup" />
        <button class="py-1 fw-bold btn btn-outline-primary" @click="onSidebarSearch">&#128269;</button>
    </div>
    <div  class="sidebar-title text-center py-2 fw-bold">🎓 Admin Panel</div>  
    <RouterLink class="nav-link" to="/admin-dashboard"><strong>🏠 Dashboard</strong></RouterLink>
    <RouterLink class="nav-link" to="/subjects"><strong>📘 Subjects</strong></RouterLink>
    <RouterLink class="nav-link" to="/chapters"><strong>📖 Chapters</strong></RouterLink>
    <RouterLink class="nav-link" to="/quizzes"><strong>📝 Quizzes</strong></RouterLink>
    <RouterLink class="nav-link" to="/questions"><strong>❓ Questions</strong></RouterLink>
    <RouterLink class="nav-link" to="/users"><strong>👤 Users</strong></RouterLink>
    <RouterLink class="nav-link" to="/admin-settings"><strong>⚙️ Settings</strong></RouterLink>
    <hr class="my-2"  style="border-color:white;"/>
    <RouterLink class="nav-link" to="/profile"><strong>👤 Profile</strong></RouterLink>
    </div>

     <!-- Mobile Sidebar -->
    <div id="mobileSidebar" class="sidebar d-md-none">
    <div class="d-flex justify-content-between align-items-center py-1">
        <input class="form-control me-1 " type="search" placeholder="Search" aria-label="Search"
          v-model="sidebarSearch" @keyup="onSidebarSearchKeyup" />
        <button class="py-1 fw-bold btn btn-outline-primary" @click="onSidebarSearch">&#128269;</button>
    </div>
    <div  class="sidebar-title text-center py-2 fw-bold">🎓 Admin Panel</div>
    <RouterLink class="nav-link" to="/admin-dashboard" @click="handleSidebarSelect"><strong>🏠 Dashboard</strong></RouterLink>
    <RouterLink class="nav-link" to="/subjects" @click="handleSidebarSelect"><strong>📘 Subjects</strong></RouterLink>
    <RouterLink class="nav-link" to="/chapters" @click="handleSidebarSelect"><strong>📖 Chapters</strong></RouterLink>
    <RouterLink class="nav-link" to="/quizzes" @click="handleSidebarSelect"><strong>📝 Quizzes<</strong></RouterLink>
    <RouterLink class="nav-link" to="/questions" @click="handleSidebarSelect"><strong>❓ Questions</strong></RouterLink>
    <RouterLink class="nav-link" to="/users" @click="handleSidebarSelect"><strong>👤 Users</strong></RouterLink>
    <RouterLink class="nav-link" to="/admin-settings" @click="handleSidebarSelect"><strong>⚙️ Settings</strong></RouterLink>
    <hr class="my-2"  style="border-color:white;"/>
    <RouterLink class="nav-link" to="/profile"  @click="handleSidebarSelect"><strong>👤 Profile</strong></RouterLink>
    </div>
    <div id="sidebarOverlay" class="d-md-none" @click="toggleSidebar"></div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { toggleSidebar } from '@/utils/sidebar'
import axios from '@/axios'
import defaultPic from '@/assets/dummy-user.jpg'

const auth = useAuthStore()
const router = useRouter()

const sidebarSearch = ref('')
function onSidebarSearch() {
  if (sidebarSearch.value.trim()) {
    router.push({ name: 'AdminSearch', query: { q: sidebarSearch.value.trim() } })
  }
}
function onSidebarSearchKeyup(e: KeyboardEvent) {
  if (e.key === 'Enter') onSidebarSearch()
}

function getProfilePicUrl(pic: string | undefined) {
  if (!pic) return defaultPic
  if (pic.startsWith('http')) return pic
  const base = axios.defaults.baseURL || ''
  if (pic.startsWith('/static/')) return base + pic
  if (pic.startsWith('static/')) return base + '/' + pic
  if (pic.startsWith('profile_pics/')) return base + '/static/' + pic
  return base + '/static/profile_pics/' + pic
}

function handleSidebarSelect() {
  toggleSidebar();
}
function handleLogout() {
  auth.logout();
  router.push('/');
}
</script>

<style scoped>
.sidebar-title {
  color: #fff;
  background: #212529;
  font-size: 1.1rem;
  letter-spacing: 1px;
  border-bottom: 1px solid #444;
}
</style>



