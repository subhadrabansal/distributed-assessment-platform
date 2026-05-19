<template>
  <div class="flex-grow-1 p-4">
    <div class="user-score-main p-4">
      <div class="score-card-container bg-white shadow-sm-lg rounded-4 p-4">
        <h1 class="mb-4 text-center">All User Scores</h1>
        <div class="search-bar mb-3 d-flex justify-content-between align-items-center" v-if="!userId">
          <div class="input-group w-90">
            <input
              v-model="searchText"
              @keyup.enter="onSearch"
              type="text"
              placeholder="Search by user name, email, subject, chapter, or quiz name..."
              class="form-control search-input"
            />
            <button class="btn btn-outline-primary" @click="onSearch">&#128269;</button>
            <button class="btn btn-outline-secondary" @click="onReset">❌</button>
          </div>
        </div>
        <div v-if="loading" class="text-center my-5">Loading...</div>
        <div v-else>
          <template v-if="userId">
            <div v-if="userScores.length === 0" class="text-center">No scores found for this user.</div>
            <div v-else class="score-cards-row">
              <div v-for="score in userScores" :key="score.quiz_id" class="score-card">
                <div class="score-card-header">
                  <img :src="getProfilePicUrl(score.user_pic)" alt="User Pic" class="score-user-pic" />
                  <div class="score-user-name">{{ score.user_name }}</div>
                  <div class="score-user-email">{{ score.user_email }}</div>
                </div>
                <div class="score-card-body">
                  <div><b>Quiz:</b> {{ score.quiz_name }}</div>
                  <div><b>Quiz Start:</b> {{ score.quiz_start_date }}</div>
                  <div><b>Subject:</b> {{ score.subject_name }}</div>
                  <div><b>Chapter:</b> {{ score.chapter_name }}</div>
                  <div><b>Total Questions:</b> {{ score.total_questions }}</div>
                  <div><b>Attempted:</b> {{ score.attempted_questions }}</div>
                  <div><b>Unattempted:</b> {{ score.unattempted_questions }}</div>
                  <div><b>Total Marks:</b> {{ score.total_marks }}</div>
                  <div><b>Score:</b> {{ score.total_score }}</div>
                  <div><b>Date:</b> {{ score.date_stamp_of_attempt || '-' }}</div>
                  <div><b>Time:</b> {{ score.time_stamp_of_submited || '-' }}</div>
                  <div><b>Status:</b>
                    <span v-if="score.attempted_questions > 0 && !score.time_stamp_of_submited">Attempt and Not Submit</span>
                    <span v-else-if="score.attempted_questions > 0 && score.time_stamp_of_submited">Attempt and Submit</span>
                    <span v-else>Not Attempt</span>
                  </div>
                </div>
              </div>
            </div>
          </template>
          <template v-else>
            <div v-for="(chapters, subject) in allUserScores" :key="subject" class="mb-5">
              <h2 class="subject-title">Subject: {{ subject }}</h2>
              <div v-for="(scores, chapter) in chapters" :key="chapter" class="mb-4">
                <h3 class="chapter-title">Chapter: {{ chapter }}</h3>
                <div class="score-cards-row">
                  <div v-for="score in scores" :key="score.user_id + '-' + score.quiz_id" class="score-card">
                    <div class="score-card-header">
                      <img :src="getProfilePicUrl(score.user_pic)" alt="User Pic" class="score-user-pic" />
                      <div class="score-user-name">{{ score.user_name }}</div>
                      <div class="score-user-email">{{ score.user_email }}</div>
                    </div>
                    <div class="score-card-body">
                      <div><b>Quiz:</b> {{ score.quiz_name }}</div>
                      <div><b>Quiz Start:</b> {{ score.quiz_start_date }}</div>
                      <div><b>Total Questions:</b> {{ score.total_questions }}</div>
                      <div><b>Attempted:</b> {{ score.attempted_questions }}</div>
                      <div><b>Unattempted:</b> {{ score.unattempted_questions }}</div>
                      <div><b>Total Marks:</b> {{ score.total_marks }}</div>
                      <div><b>Score:</b> {{ score.total_score }}</div>
                      <div><b>Date:</b> {{ score.date_stamp_of_attempt || '-' }}</div>
                      <div><b>Time:</b> {{ score.time_stamp_of_submited || '-' }}</div>
                      <div><b>Status:</b>
                        <span v-if="score.attempted_questions > 0 && !score.time_stamp_of_submited">Attempt and Not Submit</span>
                        <span v-else-if="score.attempted_questions > 0 && score.time_stamp_of_submited">Attempt and Submit</span>
                        <span v-else>Not Attempt</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from '@/axios'
import dummyUserPic from '@/assets/dummy-user.jpg'

const route = useRoute()
const userId = computed(() => route.params.userId)

function getProfilePicUrl(pic: string | undefined) {
  if (!pic) return dummyUserPic
  if (pic.startsWith('http')) return pic
  const base = axios.defaults.baseURL || ''
  if (pic.startsWith('/static/')) return base + pic
  if (pic.startsWith('static/')) return base + '/' + pic
  if (pic.startsWith('profile_pics/')) return base + '/static/' + pic
  return base + '/static/profile_pics/' + pic
}

const userScores = ref<any[]>([])
const allUserScores = ref<Record<string, Record<string, any[]>>>({})
const loading = ref(true)
const searchText = ref('')

async function fetchScores(text = '') {
  loading.value = true
  try {
    let res
    if (userId.value) {
      res = await axios.get(`/admin/user-scores/${userId.value}`)
      userScores.value = res.data.data || []
    } else if (text) {
      res = await axios.get('/admin/user-scores/search', { params: { text } })
      allUserScores.value = res.data.data || {}
    } else {
      res = await axios.get('/admin/user-scores')
      allUserScores.value = res.data.data || {}
    }
  } catch (e) {
    userScores.value = []
    allUserScores.value = {}
  }
  loading.value = false
}

function onSearch() {
  fetchScores(searchText.value.trim())
}

function onReset() {
  searchText.value = ''
  fetchScores()
}

onMounted(() => {
  fetchScores()
})
</script>

<style scoped>
.user-score-main {
  min-height: 100vh;
  background: #f6f8fa;
  padding: 0;
}
.score-card-container {
  max-width: 100%;
  margin: 0 auto;
  background: #fff;
  box-shadow: 0 2px 16px rgba(0,0,0,0.08);
  border-radius: 1.5rem;
  padding: 2.5rem 2.5rem 2rem 2.5rem;
}
.search-bar {
  margin-bottom: 1.5rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}
.input-group.w-90 {
  width: 100%;
}
.search-input {

  font-size: 1.1em;
}
.subject-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1976d2;
  margin-bottom: 0.7rem;
  margin-top: 2rem;
}
.chapter-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
  margin-left: 1rem;
}
.score-cards-row {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem 2.5rem;
  margin-left: 0;
  margin-bottom: 2rem;
}
.score-card {
  background: #fff;
  border: 1.5px solid #e0e0e0;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  padding: 1.2rem 1.5rem;
  min-width: 260px;
  max-width: 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1.5rem;
}
.score-card-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 0.7rem;
}
.score-user-pic {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #1976d2;
  margin-bottom: 0.5rem;
}
.score-user-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #222;
}
.score-user-email {
  font-size: 0.95rem;
  color: #888;
  margin-bottom: 0.3rem;
}
.score-card-body {
  width: 100%;
  font-size: 0.98rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  align-items: flex-start;
}
</style>