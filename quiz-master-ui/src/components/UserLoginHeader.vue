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
        <input class="form-control me-1 " type="search" v-model="searchText" placeholder="Search" aria-label="Search"/>
        <button class="py-1 fw-bold btn btn-outline-primary" @click="handleSearch">&#128269;</button>
        </div>
        <div class="sidebar-title text-center py-1 fw-bold">🎓 Student Panel</div>
        <RouterLink class="nav-link" to="/user-dashboard"><strong>🏠 Dashboard</strong></RouterLink>
        <RouterLink class="nav-link" to="/registered-quiz"><strong>📝 Registered Quiz</strong></RouterLink>
        <RouterLink class="nav-link" to="/ongoing-quiz"><strong>🏅 OnGoing Quiz</strong></RouterLink>
        <RouterLink class="nav-link" to="/upcoming-quiz"><strong>📅 Upcoming Quiz</strong></RouterLink>
        <RouterLink class="nav-link" to="/completed-quiz"><strong>🏆 Completed Quiz</strong></RouterLink>
        <RouterLink class="nav-link" to="/absent-quiz"><strong>❌ Absent Quiz</strong></RouterLink>
        <RouterLink class="nav-link" to="/user-settings"><strong>⚙️ Settings</strong></RouterLink>
        <hr class="my-2"  style="border-color:white;"/>
        <RouterLink class="nav-link" to="/profile"><strong>👤 Profile</strong></RouterLink>
    </div>

    <!-- Mobile Sidebar -->
    <div id="mobileSidebar" class="sidebar d-md-none">
    <div class="d-flex justify-content-between align-items-center py-1">
        <input class="form-control me-1 " type="search" v-model="searchText" placeholder="Search" aria-label="Search"/>
        <button class="py-1 fw-bold btn btn-outline-primary" @click="handleSearch">&#128269;</button>
    </div>
    <div class="sidebar-title text-center py-2 fw-bold">Student Panel</div>
    <RouterLink class="nav-link" to="/user-dashboard" @click="handleSidebarSelect"><strong>🏠 Dashboard</strong></RouterLink>
    <RouterLink class="nav-link" to="/registered-quiz" @click="handleSidebarSelect"><strong>📝 Registered Quiz</strong></RouterLink>
    <RouterLink class="nav-link" to="/ongoing-quiz" @click="handleSidebarSelect"><strong>🏅 OnGoing  Quiz</strong></RouterLink>
    <RouterLink class="nav-link" to="/upcoming-quiz" @click="handleSidebarSelect"><strong>📅 Upcoming Quiz</strong></RouterLink>
    <RouterLink class="nav-link" to="/completed-quiz" @click="handleSidebarSelect"><strong>🏆 Completed Quiz</strong></RouterLink>
    <RouterLink class="nav-link" to="/absent-quiz" @click="handleSidebarSelect"><strong>❌ Absent Quiz</strong></RouterLink>
    <RouterLink class="nav-link" to="/user-settings" @click="handleSidebarSelect"><strong>⚙️ Settings</strong></RouterLink>
    <hr class="my-2"  style="border-color:white;"/>
    <RouterLink class="nav-link" to="/profile"  @click="handleSidebarSelect"><strong>👤 Profile</strong></RouterLink>
    </div>
    <div id="sidebarOverlay" class="d-md-none" @click="toggleSidebar"></div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { toggleSidebar } from '@/utils/sidebar'
import axios from '@/axios'
import defaultPic from '@/assets/dummy-user.jpg'
import { ref } from 'vue'

const auth = useAuthStore()
const router = useRouter()
const searchText = ref('')

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

function handleSearch() {
  if (searchText.value.trim().length < 3) return;
  router.push({ path: '/user-search', query: { text: searchText.value.trim() } })
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



