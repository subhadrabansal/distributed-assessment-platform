<template>
  <div class="flex-grow-1 p-4">
    <h2 class="mb-4 text-center">Registered Quizzes</h2>
    <div class="mb-3 d-flex justify-content-between align-items-center">
      <div class="input-group w-90">
        <input v-model="searchText" class="form-control" placeholder="Search quizzes..." @keyup.enter="onSearch" />
        <button class="btn btn-outline-primary" @click="onSearch">&#128269;</button>
        <button class="btn btn-outline-secondary" @click="onReset">❌</button>
      </div>
    </div>
    <div v-if="loading" class="text-center py-8">
      <span>Loading quizzes...</span>
    </div>
    <div v-else-if="sortedQuizzes.length === 0" class="text-center py-8">
      <span>No quiz registered</span>
      <br />
      <button class="btn btn-primary mt-3" @click="goToOngoing">Go to Ongoing Quizzes</button>
    </div>
    <div v-else>
      <div class="row g-3">
        <div v-for="quiz in sortedQuizzes" :key="quiz.id" class="col-md-4">
          <div class="card h-100 shadow-sm-lg">
            <div class="card-body d-flex flex-column justify-content-between">
              <div>
                <h5 class="card-title text-bg-light w-100">{{ quiz.name }}</h5>
                <p class="card-text"><strong>Chapter:</strong> {{ quiz.chapter_name }}</p>
                <p class="card-text"><strong>Subject:</strong> {{ quiz.subject_name }}</p>
                <hr/>
                <div class="d-flex justify-content-between flex-wrap w-100 mt-2 mb-2">
                  <span class="badge text-bg-success">Start: {{ quiz.start_date }}</span>
                  <span class="badge text-bg-danger">End: {{ quiz.end_date }}</span>
                  <span class="badge text-bg-warning">Duration: {{ quiz.duration }} min</span>
                </div>
                <div class="d-flex justify-content-between flex-wrap w-100 mt-2 mb-2">
                  <span class="badge text-bg-info">Questions: {{ quiz.questions }}</span>
                  <span class="badge text-bg-primary">Marks: {{ quiz.total_marks }}</span>
                </div>
              </div>
              <hr/>
              <button
                class="btn btn-primary w-100 mt-2"
                :disabled="isFutureQuiz(quiz.start_date)"
                @click="() => startQuiz(quiz.id)"
              >
                Start Quiz
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from '@/axios'
import { useFlashStore } from '@/stores/flash'
import { useRouter } from 'vue-router'

interface Quiz {
  id: number
  name: string
  subject_name: string
  chapter_name: string
  start_date: string
  end_date: string
  duration: number
  questions: number
  total_marks: number
}

const loading = ref(false)
const quizzes = ref<Quiz[]>([])
const searchText = ref('')
const flash = useFlashStore()
const router = useRouter()

const fetchQuizzes = async (search = '') => {
  loading.value = true
  try {
    const url = search
      ? `/user/quiz/registered/search?text=${encodeURIComponent(search)}`
      : '/user/quiz/registered'
    const res = await axios.get(url)
    quizzes.value = res.data.data || []
  } catch (e: any) {
    flash.setFlash('Failed to load quizzes', 'error')
  } finally {
    loading.value = false
  }
}

function onSearch() {
  fetchQuizzes(searchText.value.trim())
}
function onReset() {
  searchText.value = ''
  fetchQuizzes()
}

function goToOngoing() {
  router.push('/ongoing-quiz')
}

onMounted(() => {
  fetchQuizzes()
})

const sortedQuizzes = computed(() => {
  return [...quizzes.value].sort((a, b) => {
    if (a.subject_name !== b.subject_name) return a.subject_name.localeCompare(b.subject_name)
    if (a.chapter_name !== b.chapter_name) return a.chapter_name.localeCompare(b.chapter_name)
    return a.start_date.localeCompare(b.start_date)
  })
})

function isFutureQuiz(startDate: string): boolean {
  let d: Date | null = null
  if (startDate.includes('-')) {
    const parts = startDate.split('-')
    if (parts[0].length === 4) {
      d = new Date(startDate)
    } else if (parts[2].length === 4) {
      d = new Date(Number(parts[2]), Number(parts[1]) - 1, Number(parts[0]))
    }
  }
  if (!d) return false
  const today = new Date()
  today.setHours(0,0,0,0)
  d.setHours(0,0,0,0)
  return d > today
}

function startQuiz(quizId: number) {
  localStorage.setItem('current_quiz_id', quizId.toString())
  router.push({ path: '/quiz-attempt' })
}
</script>

<style scoped>
.card {
  cursor: pointer;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
</style>
