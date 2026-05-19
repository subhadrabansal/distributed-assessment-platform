<template>
  <div class="card vcard p-2">
    <div class="d-flex align-items-start">
      <div class="me-3 text-center">
        <img :src="user.profile_picture ? getProfilePicUrl(user.profile_picture) : defaultPic" class="rounded-circle user-pic mb-2" width="80" height="80" alt="User Pic" />
        <span class="badge bg-secondary">{{ user.role || 'Student' }}</span>
      </div>
      <div class="flex-grow-1">
        <h5 class="mb-1">{{ user.fullname }}</h5>
        <p class="mb-1">{{ user.email }}</p>
      </div>
    </div>
    <hr class="my-2" />
    <div class="row mb-2 small">
      <div class="col-6 text-start"><strong>Date of Birth:</strong></div>
      <div class="col-6 text-end">{{ user.date_of_birth || '-' }}</div>
      <div class="col-6 text-start"><strong>Phone:</strong></div>
      <div class="col-6 text-end">{{ user.phone_number || '-' }}</div>
      <div class="col-6 text-start"><strong>Qualification:</strong></div>
      <div class="col-6 text-end">{{ user.qualification || '-' }}</div>
      <div class="col-6 text-start"><strong>Subject:</strong></div>
      <div class="col-6 text-end">{{ user.subject || '-' }}</div>
    </div>
    <div class="d-flex justify-content-between align-items-center mb-2">
      <button class="btn btn-outline-primary btn-sm" @click="goToUserScores">
        Quiz Count: <span class="fw-bold">{{ user.quiz_count ?? '-' }}</span>
      </button>
      <button
        :class="['btn btn-sm', user.status ? 'btn-success' : 'btn-danger']"
        @click="$emit('toggle-status', user)"
        :disabled="user.id === currentUserId"
      >
        {{ user.status ? 'Active' : 'Inactive' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'
import defaultPic from '@/assets/dummy-user.jpg'
import axios from '@/axios'
import { useRouter } from 'vue-router'

const props = defineProps({
  user: { type: Object, required: true },
  currentUserId: { type: [String, Number], required: true }
})
const emit = defineEmits(['toggle-status'])
const router = useRouter()

function getProfilePicUrl(pic: string | undefined) {
  if (!pic) return defaultPic
  if (pic.startsWith('http')) return pic
  const base = axios.defaults.baseURL || ''
  if (pic.startsWith('/static/')) return base + pic
  if (pic.startsWith('static/')) return base + '/' + pic
  if (pic.startsWith('profile_pics/')) return base + '/static/' + pic
  return base + '/static/profile_pics/' + pic
}

function goToUserScores() {
  router.push({ name: 'UserScore', params: { userId: props.user.id } })
}
</script>

<style scoped>
.vcard {
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  border-radius: 1rem;
  min-height: unset;
  height: auto;
  padding: 1rem 1rem 0.5rem 1rem !important;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}
.user-pic {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 50%;
  border: 2px solid #1976d2;
}
</style>
