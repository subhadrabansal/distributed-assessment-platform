<template>
  <div class="card h-100 shadow-sm-lg">
    <div class="card-body">
      <h5 class="card-title text-bg-light w-100">{{ quiz.name }}</h5>
      <p class="card-text">{{ quiz.description }}</p>
      <p class="card-text"><strong>Chapter:</strong> {{ quiz.chapter_name }}</p>
      <p class="card-text"><strong>Subject:</strong> {{ quiz.subject_name }}</p>
      <hr/>
      <div class="d-flex justify-content-between flex-wrap w-100 mt-2 mb-2">
        <span class="badge text-bg-success">Start: {{ quiz.start_date }}</span>
        <span class="badge text-bg-danger">End: {{ quiz.end_date }}</span>
        <span class="badge text-bg-warning">Duration: {{ quiz.duration }} min</span>
        <span class="badge text-bg-warning">Status: {{ quiz.status }}</span>
      </div>
      <hr/>
      <div class="d-flex justify-content-end gap-1 text-end mt-3">
        <button class="btn btn-sm btn-info" @click="goToQuestions">{{ quiz.questions }} Questions</button>|
        <button v-if="canEdit" class="btn btn-sm btn-warning" @click="editQuiz">Edit</button>
        <button v-if="canDelete" class="btn btn-sm btn-danger" @click="deleteQuiz">Delete</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
const props = defineProps({
  quiz: { type: Object, required: true },
  canEdit: { type: Boolean, default: true },
  canDelete: { type: Boolean, default: true }
})
const router = useRouter()
function goToQuestions() {
  router.push({ name: 'AdminQuestionManagement', query: { quizId: props.quiz.id } })
}
function editQuiz() {
  router.push({ name: 'AdminQuizEdit', params: { id: props.quiz.id } })
}
function deleteQuiz() {
  alert('Delete quiz: ' + props.quiz.name)
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
