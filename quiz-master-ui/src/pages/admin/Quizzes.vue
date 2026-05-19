<template>
  <div class="flex-grow-1 p-4">
      <div class="flex-grow-1 p-4">
        <div v-if="showDeleteDialog" class="modal fade show d-block" tabindex="-1" style="background:rgba(0,0,0,0.3)">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">Confirm Delete</h5>
                <button type="button" class="btn-close" @click="closeDeleteDialog"></button>
              </div>
              <div class="modal-body">
                <p>Are you sure you want to delete this quiz?</p>
              </div>
              <div class="modal-footer">
                <button class="btn btn-secondary" @click="closeDeleteDialog">Cancel</button>
                <button class="btn btn-danger" @click="confirmDeleteQuiz">Delete</button>
              </div>
            </div>
          </div>
        </div>
        <div>
          <h2 class="mb-4 text-center">Quizzes Management</h2>
          <div v-if="!isAdmin" class="alert alert-danger">You are not authorized to view this page.</div>
          <div v-else>
            <div class="mb-3 d-flex justify-content-between align-items-center">
              <div class="input-group w-90">
                <input v-model="search" class="form-control" placeholder="Search quizzes..." />
                <button class="btn btn-outline-primary" @click="handleSearch">&#128269;</button>
                <button class="btn btn-outline-secondary" @click="handleReset">❌</button>
                <button class="btn btn-outline-primary ms-2" @click="showAdd = true">➕Quiz</button>
              </div>
            </div>
            <div class="row g-3">
              <div v-for="quiz in filteredQuizzes" :key="quiz.id" class="col-md-4">
                <div class="card h-100 shadow-sm-lg" >
                  <div class="card-body">
                    <h5 class="card-title text-bg-light w-100">{{ quiz.name }}</h5>
                    <p class="card-text">{{ quiz.description }}</p>
                    <p class="card-text"><strong>Chapter:</strong> {{ quiz.chapter_name }}</p>
                    <p class="card-text"><strong>Subject:</strong> {{ quiz.subject_name }}</p>
                    <hr/>
                    <div class="d-flex justify-content-between flex-wrap w-100 mt-2 mb-2">
                      <span class="badge text-bg-success">Start: {{ quiz.start_date }} </span>
                      <span class="badge text-bg-danger">End:{{ quiz.end_date }}</span>
                      <span class="badge text-bg-warning">Duration: {{ quiz.duration }} min</span>
                      <span class="badge text-bg-warning">Status: {{ quiz.status }}</span>
                    </div>
                    <hr/>
                    <div class="d-flex justify-content-end gap-1 text-end mt-3">
                      <button class="btn btn-sm btn-info" @click="goToQuestions(quiz.id)">{{ quiz.questions }} Questions</button>|
                      <button class="btn btn-sm btn-warning" @click="editQuiz(quiz)">Edit</button>
                      <button class="btn btn-sm btn-danger" @click="openDeleteDialog(quiz.id)">Delete</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="showAdd || showEdit" class="modal fade show d-block" tabindex="-1" style="background:rgba(0,0,0,0.3)">
              <div class="modal-dialog">
                <div class="modal-content">
                  <div class="modal-header">
                    <h5 class="modal-title">{{ showAdd ? 'Add Quiz' : 'Edit Quiz' }}</h5>
                    <button type="button" class="btn-close" @click="closeModal"></button>
                  </div>
                  <div class="modal-body">
                    <form @submit.prevent="validateAndSubmit">
                      <div class="mb-3">
                        <label class="form-label">Name</label>
                        <input v-model="form.name" class="form-control" :class="{'is-invalid': nameError}" required />
                        <div v-if="nameError" class="invalid-feedback">{{ nameError }}</div>
                      </div>
                      <div class="mb-3">
                        <label class="form-label">Description</label>
                        <textarea v-model="form.description" class="form-control" :class="{'is-invalid': descError}" required></textarea>
                        <div v-if="descError" class="invalid-feedback">{{ descError }}</div>
                      </div>
                      <div class="mb-3">
                        <label class="form-label">Chapter</label>
                        <select v-model="form.chapter_id" class="form-control" :class="{'is-invalid': chapterError}" required>
                          <option value="" disabled>Select chapter</option>
                          <option v-for="chapter in chaptersList" :key="chapter.id" :value="chapter.id">{{ chapter.name }}</option>
                        </select>
                        <div v-if="chapterError" class="invalid-feedback">{{ chapterError }}</div>
                      </div>
                      <div class="mb-3">
                        <label class="form-label">Start Date</label>
                        <Datepicker v-model="startDateObj" :format="dateFormat" :input-class="['form-control', { 'is-invalid': startDateError }]" required />
                        <div v-if="startDateError" class="invalid-feedback">{{ startDateError }}</div>
                      </div>
                      <div class="mb-3">
                        <label class="form-label">End Date</label>
                        <Datepicker v-model="endDateObj" :format="dateFormat" :input-class="['form-control', { 'is-invalid': endDateError }]" required />
                        <div v-if="endDateError" class="invalid-feedback">{{ endDateError }}</div>
                      </div>
                      <div class="mb-3">
                        <label class="form-label">Duration (minutes)</label>
                        <input v-model.number="form.duration" class="form-control" :class="{'is-invalid': durationError}" required type="number" min="30" max="120" />
                        <div v-if="durationError" class="invalid-feedback">{{ durationError }}</div>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import Datepicker from 'vue3-datepicker'
import axios from '@/axios'
import { useAuthStore } from '@/stores/auth'
import { useFlashStore } from '@/stores/flash'
import { useRouter, useRoute } from 'vue-router'

const auth = useAuthStore()
const flash = useFlashStore()
const router = useRouter()
const route = useRoute()
const chapterId = ref<number | null>(null)

const isAdmin = computed(() => auth.userIsLoggedIn && auth.user?.isAdmin)
const quizzes = ref<any[]>([])
const search = ref('')
const showAdd = ref(false)
const showEdit = ref(false)
const showDeleteDialog = ref(false)
const quizToDelete = ref<number|null>(null)
const form = ref({ id: null, name: '', description: '', chapter_id: '', start_date: '', end_date: '', duration: 30 })
const filteredQuizzes = ref<any[]>([])
const chaptersList = ref<any[]>([])
const nameError = ref('')
const descError = ref('')
const chapterError = ref('')
const startDateError = ref('')
const endDateError = ref('')
const durationError = ref('')
const dateFormat = (date: Date) => {
  if (!date) return ''
  const dd = String(date.getDate()).padStart(2, '0')
  const mm = String(date.getMonth() + 1).padStart(2, '0')
  const yyyy = date.getFullYear()
  return `${dd}-${mm}-${yyyy}`
}
function parseDate(str: string): Date | undefined {
  if (!str) return undefined
  const [dd, mm, yyyy] = str.split('-')
  if (dd && mm && yyyy) return new Date(Number(yyyy), Number(mm) - 1, Number(dd))
  return undefined
}
function formatDate(date: Date | undefined): string {
  if (!date) return ''
  const dd = String(date.getDate()).padStart(2, '0')
  const mm = String(date.getMonth() + 1).padStart(2, '0')
  const yyyy = date.getFullYear()
  return `${dd}-${mm}-${yyyy}`
}
const startDateObj = ref<Date | undefined>(undefined)
const endDateObj = ref<Date | undefined>(undefined)

watch(
  () => form.value.start_date,
  (val) => {
    if (val && val.includes('-')) {
      const parts = val.split('-')
      if (parts[0].length === 4) {
        startDateObj.value = new Date(val)
      } else if (parts[2].length === 4) {
        startDateObj.value = parseDate(val as string)
      }
    }
  },
  { immediate: true }
)
watch(
  () => form.value.end_date,
  (val) => {
    if (val && val.includes('-')) {
      const parts = val.split('-')
      if (parts[0].length === 4) {
        endDateObj.value = new Date(val)
      } else if (parts[2].length === 4) {
        endDateObj.value = parseDate(val as string)
      }
    }
  },
  { immediate: true }
)
watch(startDateObj, (val) => {
  form.value.start_date = formatDate(val)
})
watch(endDateObj, (val) => {
  form.value.end_date = formatDate(val)
})

async function fetchChaptersList() {
  try {
    const res = await axios.get('/admin/chapter')
    if (res.data && res.data.data) {
      chaptersList.value = res.data.data
    }
  } catch (err) {
    flash.setFlash('Failed to fetch chapters for dropdown', 'error')
  }
}

function closeModal() {
  showAdd.value = false
  showEdit.value = false
  form.value = { id: null, name: '', description: '', chapter_id: '', start_date: '', end_date: '', duration: 30 }
  nameError.value = ''
  descError.value = ''
  chapterError.value = ''
  startDateError.value = ''
  endDateError.value = ''
  durationError.value = ''
}

onMounted(() => {
  const storedId = sessionStorage.getItem('filter_chapter_id')
  if (storedId) {
    chapterId.value = Number(storedId)
    sessionStorage.removeItem('filter_chapter_id')
  }
  if (isAdmin.value) {
    fetchQuizzes()
    fetchChaptersList()
  }
})

async function fetchQuizzes() {
  try {
    search.value = ''
    let res
    if (chapterId.value) {
      res = await axios.get(`/admin/chapter/${chapterId.value}/quiz`)
    } else {
      res = await axios.get('/admin/quiz')
    }
    if (res.data && res.data.data) {
      quizzes.value = res.data.data
      filteredQuizzes.value = res.data.data
    }
  } catch (err) {
    flash.setFlash('Failed to fetch quizzes', 'error')
  }
}

async function addQuiz() {
  try {
    await axios.post('/admin/quiz', {
      name: form.value.name,
      description: form.value.description,
      chapter_id: form.value.chapter_id,
      start_date: form.value.start_date,
      end_date: form.value.end_date,
      duration: form.value.duration
    })
    flash.setFlash('Quiz added successfully', 'success')
    closeModal()
    fetchQuizzes()
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to add quiz', 'error')
  }
}

function editQuiz(quiz: any) {
  form.value = {
    id: quiz.id,
    name: quiz.name,
    description: quiz.description,
    chapter_id: quiz.chapter_id,
    start_date: quiz.start_date,
    end_date: quiz.end_date,
    duration: quiz.duration
  }
  showEdit.value = true
}

async function updateQuiz() {
  try {
    await axios.put(`/admin/quiz/${form.value.id}`,
      {
        name: form.value.name,
        description: form.value.description,
        chapter_id: form.value.chapter_id,
        start_date: form.value.start_date,
        end_date: form.value.end_date,
        duration: form.value.duration
      }
    )
    flash.setFlash('Quiz updated successfully', 'success')
    closeModal()
    fetchQuizzes()
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to update quiz', 'error')
  }
}

function openDeleteDialog(id: number) {
  quizToDelete.value = id
  showDeleteDialog.value = true
}
function closeDeleteDialog() {
  showDeleteDialog.value = false
  quizToDelete.value = null
}
async function confirmDeleteQuiz() {
  if (quizToDelete.value !== null) {
    await deleteQuiz(quizToDelete.value)
  }
  closeDeleteDialog()
}

async function deleteQuiz(id: number) {
  try {
    await axios.delete(`/admin/quiz/${id}`)
    flash.setFlash('Quiz deleted successfully', 'success')
    fetchQuizzes()
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to delete quiz', 'error')
  }
}

function handleSearch() {
  if (!search.value || search.value.trim().length < 3) {
    flash.setFlash('Please enter at least 3 characters to search.', 'error')
    return
  }
  axios.get(`/admin/quiz/search?text=${encodeURIComponent(search.value)}`)
    .then(res => {
      if (res.data && res.data.data) {
        filteredQuizzes.value = res.data.data
      } else {
        filteredQuizzes.value = []
        flash.setFlash('No quizzes found.', 'error')
      }
    })
    .catch(() => {
      filteredQuizzes.value = []
      flash.setFlash('No quizzes found.', 'error')
    })
}

function handleReset() {
  search.value = ''
  chapterId.value = null 
  fetchQuizzes()
  filteredQuizzes.value = quizzes.value
}

function formatDateToDDMMYYYY(dateStr: string): string {
  if (!dateStr) return ''
  const [yyyy, mm, dd] = dateStr.split('-')
  if (yyyy && mm && dd) return `${dd}-${mm}-${yyyy}`
  return dateStr
}
function formatDateToYYYYMMDD(dateStr: string): string {
  if (!dateStr) return ''
  const [dd, mm, yyyy] = dateStr.split('-')
  if (dd && mm && yyyy) return `${yyyy}-${mm}-${dd}`
  return dateStr
}
function onDateChange(field: 'start_date' | 'end_date') {
  if (form.value[field]) {
    form.value[field] = formatDateToDDMMYYYY(form.value[field])
  }
}

function validateAndSubmit() {
  nameError.value = '';
  descError.value = '';
  chapterError.value = '';
  startDateError.value = '';
  endDateError.value = '';
  durationError.value = '';
  const nameRegex = /^[A-Za-z\s']{2,512}$/;
  const descRegex = /^[A-Za-z0-9\s',-]{3,}$/;
  const chapterIdRegex = /^[0-9]+$/;
  const durationRegex = /^(30|60|90|120)$/;

  let isValid = true;

  if (!form.value.name || !nameRegex.test(form.value.name)) {
    nameError.value = 'Invalid name';
    isValid = false;
  }

  if (!form.value.description || !descRegex.test(form.value.description)) {
    descError.value = 'Invalid description';
    isValid = false;
  }

  if (!form.value.chapter_id || !chapterIdRegex.test(String(form.value.chapter_id))) {
    chapterError.value = 'Invalid chapter';
    isValid = false;
  }

  if (form.value.start_date === '' || !startDateObj.value) {
    startDateError.value = 'Start date is required';
    isValid = false;
  }

  if (form.value.end_date === '' || !endDateObj.value) {
    endDateError.value = 'End date is required';
    isValid = false;
  }

  if (form.value.duration === null || form.value.duration === undefined || !durationRegex.test(String(form.value.duration))) {
    durationError.value = 'Duration must be 30, 60, 90, or 120 minutes';
    isValid = false;
  }

  if (isValid) {
    if (showAdd.value) {
      addQuiz();
    } else if (showEdit.value) {
      updateQuiz();
    }
  }
}

function goToQuestions(quizId: number) {
  sessionStorage.setItem('filter_quiz_id', String(quizId))
  router.push('/questions')
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