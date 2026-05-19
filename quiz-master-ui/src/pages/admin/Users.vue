<template>
  <div class="flex-grow-1 p-4">
    <div>
      <h2 class="mb-4 text-center">Users Management</h2>

      <div class="mb-3 d-flex justify-content-between align-items-center">
        <div class="input-group w-90">
          <input v-model="search" class="form-control" placeholder="Search users..." />
          <button class="btn btn-outline-primary" @click="searchUsers">&#128269;</button>
          <button class="btn btn-outline-secondary" @click="resetSearch">❌</button>
        </div>
      </div>

      <div class="row g-3">
        <div v-for="user in users" :key="user.id" class="col-md-6 col-lg-4">
          <UserCard :user="user" :currentUserId="auth.user?.id" @toggle-status="toggleUserStatus" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from '@/axios'
import defaultPic from '@/assets/dummy-user.jpg'
import { useAuthStore } from '@/stores/auth'
import { useFlashStore } from '@/stores/flash'
import UserCard from '@/components/UserCard.vue'

const auth = useAuthStore()
const flash = useFlashStore()
const users = ref<any[]>([])
const search = ref('')

function getProfilePicUrl(pic: string) {
  const apiRoot = axios.defaults.baseURL?.replace(/\/api$/, '') || ''
  if (pic.startsWith('http')) return pic
  return `${apiRoot}/static/profile_pics/${pic}`
}

async function fetchUsers() {
  try {
    const res = await axios.get('/auth/user')
    if (res.data && res.data.data) {
      users.value = res.data.data
    }
  } catch (err) {
  }
}

async function toggleUserStatus(user: any) {
  try {
    const res = await axios.put(`/auth/user/${user.id}/status`)
    if (res.data && res.data.success) {
      const isActive = res.data.data.status
      flash.setFlash(
        isActive ? 'User activated.' : 'User deactivated.',
        isActive ? 'error' : 'success' 
      )
      fetchUsers()
    } else {
      flash.setFlash(res.data.error_message || 'Failed to update user status', 'error')
    }
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to update user status', 'error')
  }
}

async function searchUsers() {
  if (!search.value || search.value.trim().length < 3) {
    flash.setFlash('Please enter at least 3 characters to search.', 'error')
    return
  }
  try {
    const res = await axios.get(`/auth/user/${encodeURIComponent(search.value)}/search`)
    if (res.data && res.data.data) {
      users.value = res.data.data
    } else {
      users.value = []
      flash.setFlash('No users found.', 'error')
    }
  } catch (err) {
    users.value = []
    flash.setFlash('No users found.', 'error')
  }
}

function resetSearch() {
  search.value = ''
  fetchUsers()
}

onMounted(() => {
  if (auth.userIsLoggedIn && auth.user?.token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${auth.user.token}`
  }
  fetchUsers()
})
</script>

<style scoped>
.vcard {
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  border-radius: 1rem;
  min-height: 180px;
}
.user-pic {
  object-fit: cover;
  border: 2px solid #eee;
}
</style>