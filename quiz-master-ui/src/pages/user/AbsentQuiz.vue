<template>
  <div class="flex-grow-1 p-4">
    <h2 class="mb-4 text-center">Absent Quizzes</h2>
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
    <div v-else-if="groupedQuizzes.length === 0" class="text-center py-8">
      <span>No absent quizzes found.</span>
      <br />
      <button class="btn btn-primary mt-3" @click="goToRegistered">Go to Registered Quizzes</button>
    </div>
    <div v-else>
      <div v-for="subject in groupedQuizzes" :key="subject.subjectName" class="mb-5">
        <h4 class="mb-3 text-primary">{{ subject.subjectName }}</h4>
        <div v-for="chapter in subject.chapters" :key="chapter.chapterName" class="mb-4">
          <h5 class="mb-2 text-secondary">{{ chapter.chapterName }}</h5>
          <div class="row g-3">
            <div v-for="quiz in chapter.quizzes" :key="quiz.id" class="col-md-4">
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
                </div>
              </div>
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
      ? `/user/quiz/absent/search?text=${encodeURIComponent(search)}`
      : '/user/quiz/absent'
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
function goToRegistered() {
  router.push('/registered-quiz')
}

onMounted(() => {
  fetchQuizzes()
})

const groupedQuizzes = computed(() => {
  const subjectMap: Record<string, Record<string, Quiz[]>> = {}
  quizzes.value.forEach(q => {
    if (!subjectMap[q.subject_name]) subjectMap[q.subject_name] = {}
    if (!subjectMap[q.subject_name][q.chapter_name]) subjectMap[q.subject_name][q.chapter_name] = []
    subjectMap[q.subject_name][q.chapter_name].push(q)
  })
  return Object.entries(subjectMap).map(([subjectName, chapters]) => ({
    subjectName,
    chapters: Object.entries(chapters).map(([chapterName, quizArr]) => ({
      chapterName,
      quizzes: quizArr.sort((a, b) => a.start_date.localeCompare(b.start_date))
    }))
  }))
})
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