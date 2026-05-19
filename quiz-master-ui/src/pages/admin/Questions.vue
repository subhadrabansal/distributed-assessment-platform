<template>
  <div class="flex-grow-1 p-4">
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteDialog" class="modal fade show d-block" tabindex="-1" style="background:rgba(0,0,0,0.3)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Delete</h5>
            <button type="button" class="btn-close" @click="closeDeleteDialog"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete this question?</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeDeleteDialog">Cancel</button>
            <button class="btn btn-danger" @click="confirmDeleteQuestion">Delete</button>
          </div>
        </div>
      </div>
    </div>
    <div>
      <h2 class="mb-4 text-center">Questions Management</h2>
      <div v-if="!isAdmin" class="alert alert-danger">You are not authorized to view this page.</div>
      <div v-else>
        <div class="mb-3 d-flex justify-content-between align-items-center">
          <div class="input-group w-90">
            <input v-model="search" class="form-control" placeholder="Search questions..." />
            <button class="btn btn-outline-primary" @click="handleSearch">&#128269;</button>
            <button class="btn btn-outline-secondary" @click="handleReset">❌</button>
            <button class="btn btn-outline-primary ms-2" @click="showAdd = true">➕Question</button>
          </div>
        </div>
        <div class="row g-3">
          <div v-for="question in filteredQuestions" :key="question.id" class="col-md-6">
            <div class="card h-100">
              <div class="card-body">
                <h5 class="card-title">{{ question.question }}</h5>
                <p class="card-text"><strong>Quiz:</strong> {{ question.quiz_name }}</p>
                <p class="card-text"><strong>Chapter:</strong> {{ question.chapter_name }}</p>
                <p class="card-text"><strong>Subject:</strong> {{ question.subject_name }}</p>
                <ul class="list-group mb-2">
                  <li class="list-group-item">A. {{ question.option1 }}</li>
                  <li class="list-group-item">B. {{ question.option2 }}</li>
                  <li class="list-group-item">C. {{ question.option3 }}</li>
                  <li class="list-group-item">D. {{ question.option4 }}</li>
                </ul>
                <p class="card-text"><strong>Answer:</strong> {{ question.answer }}</p>
                <p class="card-text"><strong>Marks:</strong> {{ question.marks }}</p>
                <div class="d-flex justify-content-end gap-1">
                  <button class="btn btn-sm btn-warning" @click="editQuestion(question)">Edit</button>
                  <button class="btn btn-sm btn-danger" @click="openDeleteDialog(question.id)">Delete</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="showAdd || showEdit" class="modal fade show d-block" tabindex="-1" style="background:rgba(0,0,0,0.3)">
          <div class="modal-dialog w-100 w-lg-50 mx-auto mt-10">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">{{ showAdd ? 'Add Question' : 'Edit Question' }}</h5>
                <button type="button" class="btn-close" @click="closeModal"></button>
              </div>
              <div class="modal-body">
                <form @submit.prevent="validateAndSubmit">
                  <div class="mb-3">
                    <label class="form-label">Quiz</label>
                    <select v-model="form.quiz_id" class="form-control" :class="{'is-invalid': quizError}" required>
                      <option value="" disabled>Select quiz</option>
                      <option v-for="quiz in quizzesList" :key="quiz.id" :value="quiz.id">{{ quiz.name }}</option>
                    </select>
                    <div v-if="quizError" class="invalid-feedback">{{ quizError }}</div>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Question</label>
                    <textarea v-model="form.question" class="form-control" :class="{'is-invalid': questionError}" required />
                    <div v-if="questionError" class="invalid-feedback">{{ questionError }}</div>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Option 1</label>
                    <textarea v-model="form.option1" class="form-control" :class="{'is-invalid': option1Error}" required />
                    <div v-if="option1Error" class="invalid-feedback">{{ option1Error }}</div>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Option 2</label>
                    <textarea v-model="form.option2" class="form-control" :class="{'is-invalid': option2Error}" required />
                    <div v-if="option2Error" class="invalid-feedback">{{ option2Error }}</div>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Option 3</label>
                    <textarea v-model="form.option3" class="form-control" :class="{'is-invalid': option3Error}" required />
                    <div v-if="option3Error" class="invalid-feedback">{{ option3Error }}</div>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Option 4</label>
                    <textarea v-model="form.option4" class="form-control" :class="{'is-invalid': option4Error}" required />
                    <div v-if="option4Error" class="invalid-feedback">{{ option4Error }}</div>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Answer</label>
                    <input v-model.number="form.answer" class="form-control" :class="{'is-invalid': answerError}" required type="number" min="1" max="4"/>
                    <div v-if="answerError" class="invalid-feedback">{{ answerError }}</div>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Marks</label>
                    <input v-model.number="form.marks" class="form-control" :class="{'is-invalid': marksError}" required type="number" min="1" max="5" />
                    <div v-if="marksError" class="invalid-feedback">{{ marksError }}</div>
                  </div>
                  <div class="d-flex justify-content-end">
                    <button type="submit" class="btn btn-primary">{{ showAdd ? 'Add' : 'Update' }}</button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from '@/axios'
import { useAuthStore } from '@/stores/auth'
import { useFlashStore } from '@/stores/flash'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const flash = useFlashStore()
const router = useRouter()

const isAdmin = computed(() => auth.userIsLoggedIn && auth.user?.isAdmin)
const questions = ref<any[]>([])
const search = ref('')
const showAdd = ref(false)
const showEdit = ref(false)
const showDeleteDialog = ref(false)
const questionToDelete = ref<number|null>(null)
const form = ref({ id: null, quiz_id: '', question: '', option1: '', option2: '', option3: '', option4: '', answer: '', marks: 1 })
const filteredQuestions = ref<any[]>([])
const quizzesList = ref<any[]>([])
const quizError = ref('')
const questionError = ref('')
const option1Error = ref('')
const option2Error = ref('')
const option3Error = ref('')
const option4Error = ref('')
const answerError = ref('')
const marksError = ref('')

const quizId = ref<number | null>(null)

async function fetchQuizzesList() {
  try {
    const res = await axios.get('/admin/quiz')
    if (res.data && res.data.data) {
      quizzesList.value = res.data.data
    }
  } catch (err) {
    flash.setFlash('Failed to fetch quizzes for dropdown', 'error')
  }
}

function closeModal() {
  showAdd.value = false
  showEdit.value = false
  form.value = { id: null, quiz_id: '', question: '', option1: '', option2: '', option3: '', option4: '', answer: 1, marks: 1 }
  quizError.value = ''
  questionError.value = ''
  option1Error.value = ''
  option2Error.value = ''
  option3Error.value = ''
  option4Error.value = ''
  answerError.value = ''
  marksError.value = ''
}

async function fetchQuestions() {
  search.value = ''
  let res
  try {
    if (quizId.value) {
      res = await axios.get(`/admin/quiz/${quizId.value}/question`)
      if (res.data && res.data.data && res.data.data.length === 0) {
        quizId.value = null
        try {
          res = await axios.get('/admin/question')
        } catch (err) {
          questions.value = []
          filteredQuestions.value = []
          flash.setFlash('Failed to fetch questions', 'error')
          return
        }
      }
    } else {
      res = await axios.get('/admin/question')
    }
    if (res.data && res.data.data) {
      questions.value = res.data.data
    } else {
      questions.value = []
    }
    filteredQuestions.value = [...questions.value] 
  } catch (err) {
    questions.value = []
    filteredQuestions.value = []
    flash.setFlash('Failed to fetch questions', 'error')
  }
}

async function addQuestion() {
  try {
    await axios.post('/admin/question', {
      quiz_id: form.value.quiz_id,
      question: form.value.question,
      option1: form.value.option1,
      option2: form.value.option2,
      option3: form.value.option3,
      option4: form.value.option4,
      answer: form.value.answer,
      marks: form.value.marks
    })
    flash.setFlash('Question added successfully', 'success')
    closeModal()
    fetchQuestions()
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to add question', 'error')
  }
}

function editQuestion(question: any) {
  form.value = {
    id: question.id,
    quiz_id: question.quiz_id,
    question: question.question,
    option1: question.option1,
    option2: question.option2,
    option3: question.option3,
    option4: question.option4,
    answer: question.answer,
    marks: question.marks
  }
  showEdit.value = true
}

async function updateQuestion() {
  try {
    await axios.put(`/admin/question/${form.value.id}`, {
      quiz_id: form.value.quiz_id,
      question: form.value.question,
      option1: form.value.option1,
      option2: form.value.option2,
      option3: form.value.option3,
      option4: form.value.option4,
      answer: form.value.answer,
      marks: form.value.marks
    })
    flash.setFlash('Question updated successfully', 'success')
    closeModal()
    fetchQuestions()
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to update question', 'error')
  }
}

function openDeleteDialog(id: number) {
  questionToDelete.value = id
  showDeleteDialog.value = true
}
function closeDeleteDialog() {
  showDeleteDialog.value = false
  questionToDelete.value = null
}
async function confirmDeleteQuestion() {
  if (questionToDelete.value !== null) {
    await deleteQuestion(questionToDelete.value)
  }
  closeDeleteDialog()
}

async function deleteQuestion(id: number) {
  try {
    await axios.delete(`/admin/question/${id}`)
    flash.setFlash('Question deleted successfully', 'success')
    await fetchQuestions()
    filteredQuestions.value = [...questions.value] 
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to delete question', 'error')
  }
}

function handleSearch() {
  if (!search.value || search.value.trim().length < 3) {
    flash.setFlash('Please enter at least 3 characters to search.', 'error')
    return
  }
  axios.get(`/admin/question/search`, { params: { text: search.value } })
    .then(res => {
      if (res.data && res.data.data) {
        filteredQuestions.value = res.data.data
      } else {
        filteredQuestions.value = []
        flash.setFlash('No questions found.', 'error')
      }
    })
    .catch(() => {
      filteredQuestions.value = []
      flash.setFlash('No questions found.', 'error')
    })
}

function handleReset() {
  search.value = ''
  quizId.value = null 
  fetchQuestions()
  filteredQuestions.value = questions.value
}

function validateAndSubmit() {
  quizError.value = ''
  questionError.value = ''
  option1Error.value = ''
  option2Error.value = ''
  option3Error.value = ''
  option4Error.value = ''
  answerError.value = ''
  marksError.value = ''
  const textRegex = /^[A-Za-z0-9\s,.'"'_?-]{1,4096}$/
  let valid = true
  if (!form.value.quiz_id || isNaN(Number(form.value.quiz_id))) {
    quizError.value = 'Please select a quiz.'
    valid = false
  }
  if (!form.value.question || !textRegex.test(form.value.question)) {
    questionError.value = 'Question must be 1-4096 characters with letters, numbers, spaces, and basic punctuation.'
    valid = false
  }
  if (!form.value.option1 || !textRegex.test(form.value.option1)) {
    option1Error.value = 'Option 1 must be 1-4096 characters with letters, numbers, spaces, and basic punctuation.'
    valid = false
  }
  if (!form.value.option2 || !textRegex.test(form.value.option2)) {
    option2Error.value = 'Option 2 must be 1-4096 characters with letters, numbers, spaces, and basic punctuation.'
    valid = false
  }
  if (!form.value.option3 || !textRegex.test(form.value.option3)) {
    option3Error.value = 'Option 3 must be 1-4096 characters with letters, numbers, spaces, and basic punctuation.'
    valid = false
  }
  if (!form.value.option4 || !textRegex.test(form.value.option4)) {
    option4Error.value = 'Option 4 must be 1-4096 characters with letters, numbers, spaces, and basic punctuation.'
    valid = false
  }
  const answerNum = Number(form.value.answer)
  if (!answerNum || isNaN(answerNum) || answerNum < 1 || answerNum > 4) {
    answerError.value = 'Answer must be between 1 and 4.'
    valid = false
  }
  if (!form.value.marks || isNaN(form.value.marks) || form.value.marks < 1 || form.value.marks > 5) {
    marksError.value = 'Marks must be between 1 and 5.'
    valid = false
  }
  if (!valid) return
  if (showAdd.value) {
    addQuestion()
  } else {
    updateQuestion()
  }
}

onMounted(() => {
  if (auth.userIsLoggedIn && auth.user?.token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${auth.user.token}`
  }
  if (!isAdmin.value) {
    flash.setFlash('You are not authorized to view this page.', 'error')
    router.push('/')
    return
  }
  const storedQuizId = sessionStorage.getItem('filter_quiz_id')
  if (storedQuizId) {
    quizId.value = Number(storedQuizId)
    sessionStorage.removeItem('filter_quiz_id')
  }
  fetchQuestions()
  filteredQuestions.value = questions.value
  fetchQuizzesList()
})
</script>

<style scoped>
.card {
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.modal {
  display: block;
}
</style>
