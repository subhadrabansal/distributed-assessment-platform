<template>
  <div>
    <div v-if="type === 'registered' && quizzes.length === 0" class="text-center py-8">
      <span>No quiz registered</span>
    </div>
    <div v-else-if="type === 'ongoing' && quizzes.length === 0" class="text-center py-8">
      <span>No quizzes ongoing this time</span>
    </div>
    <div v-else-if="type === 'upcoming' && quizzes.length === 0" class="text-center py-8">
      <span>No upcoming quizzes this time</span>
    </div>
    <div v-else-if="type === 'completed' && quizzes.length === 0" class="text-center py-8">
      <span>No completed quizzes found.</span>
    </div>
    <div v-else-if="type === 'absent' && quizzes.length === 0" class="text-center py-8">
      <span>No absent quizzes found.</span>
    </div>
    <div v-else>
      <div class="row g-3">
        <div v-for="quiz in quizzes" :key="quiz.id" class="col-md-4">
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
              <button v-if="type === 'registered'" class="btn btn-primary w-100 mt-2" :disabled="isFutureQuiz(quiz.start_date)" @click="() => startQuiz(quiz.id)">Start Quiz</button>
              <button v-if="type === 'ongoing' || type === 'upcoming'" class="btn btn-primary w-100 mt-3" @click="() => joinQuiz(quiz.id)">Join</button>
              <button v-if="type === 'completed'" class="btn btn-success w-100 mt-2" @click="() => viewScore(quiz.id)">View</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  quizzes: { type: Array, required: true },
  type: { type: String, required: true }
})
const router = useRouter()

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
function joinQuiz(quizId: number) {
  router.push({ path: '/ongoing-quiz' })
}
function viewScore(quizId: number) {
  localStorage.setItem('last_quiz_id', quizId.toString())
  router.push('/user/score')
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
