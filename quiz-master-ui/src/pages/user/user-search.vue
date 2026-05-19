<template>
  <div class="flex-grow-1 p-4">
    <h2 class="mb-4 text-center">User Quiz Search Results</h2>
    <div v-if="loading" class="text-center py-8">
      <span>Loading quizzes...</span>
    </div>
    <div v-else>
      <div v-if="allEmpty" class="text-center py-8">
        <span>No quizzes found for your search.</span>
      </div>
      <div v-else>
        <div v-if="registeredQuizzes.length">
          <h3 class="mt-4 mb-2">Registered Quizzes</h3>
          <QuizList :quizzes="registeredQuizzes" type="registered" />
        </div>
        <div v-if="ongoingQuizzes.length">
          <h3 class="mt-4 mb-2">Ongoing Quizzes</h3>
          <QuizList :quizzes="ongoingQuizzes" type="ongoing" />
        </div>
        <div v-if="upcomingQuizzes.length">
          <h3 class="mt-4 mb-2">Upcoming Quizzes</h3>
          <QuizList :quizzes="upcomingQuizzes" type="upcoming" />
        </div>
        <div v-if="completedQuizzes.length">
          <h3 class="mt-4 mb-2">Completed Quizzes</h3>
          <QuizList :quizzes="completedQuizzes" type="completed" />
        </div>
        <div v-if="absentQuizzes.length">
          <h3 class="mt-4 mb-2">Absent Quizzes</h3>
          <QuizList :quizzes="absentQuizzes" type="absent" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from '@/axios'
import { useFlashStore } from '@/stores/flash'
import QuizList from '@/components/QuizList.vue'

const route = useRoute()
const flash = useFlashStore()
const loading = ref(true)
const searchText = ref(route.query.text || '')

const registeredQuizzes = ref([])
const ongoingQuizzes = ref([])
const upcomingQuizzes = ref([])
const completedQuizzes = ref([])
const absentQuizzes = ref([])

const allEmpty = computed(() =>
  !registeredQuizzes.value.length &&
  !ongoingQuizzes.value.length &&
  !upcomingQuizzes.value.length &&
  !completedQuizzes.value.length &&
  !absentQuizzes.value.length
)

async function fetchAll() {
  loading.value = true
  try {
    const [reg, ong, upc, com, abs] = await Promise.all([
      axios.get(`/user/quiz/registered/search?text=${encodeURIComponent(searchText.value)}`),
      axios.get(`/user/quiz/ongoing-unregistered/search?text=${encodeURIComponent(searchText.value)}`),
      axios.get(`/user/quiz/upcoming-unregistered/search?text=${encodeURIComponent(searchText.value)}`),
      axios.get(`/user/quiz/completed/search?text=${encodeURIComponent(searchText.value)}`),
      axios.get(`/user/quiz/absent/search?text=${encodeURIComponent(searchText.value)}`)
    ])
    registeredQuizzes.value = reg.data.data || []
    ongoingQuizzes.value = ong.data.data || []
    upcomingQuizzes.value = upc.data.data || []
    completedQuizzes.value = com.data.data || []
    absentQuizzes.value = abs.data.data || []
  } catch (e: any) {
    flash.setFlash('Some results could not be loaded', 'error')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchAll()
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
