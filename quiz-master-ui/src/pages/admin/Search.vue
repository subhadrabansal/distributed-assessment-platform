<template>
  <div class="flex-grow-1 p-4">
    <h2 class="mb-4 text-center">Admin Search</h2>
    <div v-if="loading" class="text-center my-5">Loading...</div>
    <div v-else>
      <div v-if="results.subjects.length">
        <h3 class="mb-3 mt-4 text-primary">Subjects</h3>
        <div class="row g-3">
          <div v-for="subject in results.subjects" :key="subject.id" class="col-md-4">
            <div class="card h-100">
              <div class="card-body">
                <h5 class="card-title">{{ subject.name }}</h5>
                <p class="card-text">{{ subject.description }}</p>
                <hr/>
                <div class="d-flex justify-content-end gap-1">
                  <button class="btn btn-sm btn-info" @click="goToChapters(subject.id)">{{ subject.chapters }} Chapters</button>|
                  <button class="btn btn-sm btn-warning" @click="editSubject(subject)">Edit</button>
                  <button class="btn btn-sm btn-danger" @click="openDeleteSubjectDialog(subject.id)">Delete</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="results.chapters.length">
        <h3 class="mb-3 mt-4 text-primary">Chapters</h3>
        <div class="row g-3">
          <div v-for="chapter in results.chapters" :key="chapter.id" class="col-md-4">
            <div class="card h-100">
              <div class="card-body">
                <h5 class="card-title">{{ chapter.name }}</h5>
                <p class="card-text">{{ chapter.description }}</p>
                <p class="card-text"><strong>Subject:</strong> {{ chapter.subject_name }}</p>
                <hr/>
                <div class="d-flex justify-content-end gap-1">
                  <button class="btn btn-sm btn-info" @click="goToQuizzes(chapter.id)">{{ chapter.quizzes }} Quizzes</button>|
                  <button class="btn btn-sm btn-warning" @click="editChapter(chapter)">Edit</button>
                  <button class="btn btn-sm btn-danger" @click="openDeleteChapterDialog(chapter.id)">Delete</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="showAddChapter || showEditChapter" class="modal fade show d-block" tabindex="-1" style="background:rgba(0,0,0,0.3)">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">{{ showAddChapter ? 'Add Chapter' : 'Edit Chapter' }}</h5>
                <button type="button" class="btn-close" @click="closeChapterModal"></button>
              </div>
              <div class="modal-body">
                <form @submit.prevent="validateAndSubmitChapter">
                  <div class="mb-3">
                    <label class="form-label">Name</label>
                    <input v-model="chapterForm.name" class="form-control" :class="{'is-invalid': chapterNameError}" required />
                    <div v-if="chapterNameError" class="invalid-feedback">{{ chapterNameError }}</div>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Description</label>
                    <textarea v-model="chapterForm.description" class="form-control" :class="{'is-invalid': chapterDescError}" required></textarea>
                    <div v-if="chapterDescError" class="invalid-feedback">{{ chapterDescError }}</div>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Subject</label>
                    <select v-model="chapterForm.subject_id" class="form-control" :class="{'is-invalid': chapterSubjectError}" required>
                      <option value="" disabled>Select subject</option>
                      <option v-for="subject in subjectsList" :key="subject.id" :value="subject.id">{{ subject.name }}</option>
                    </select>
                    <div v-if="chapterSubjectError" class="invalid-feedback">{{ chapterSubjectError }}</div>
                  </div>
                  <div class="d-flex justify-content-end">
                    <button type="submit" class="btn btn-primary">{{ showAddChapter ? 'Add' : 'Update' }}</button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
        <div v-if="showDeleteChapterDialog" class="modal fade show d-block" tabindex="-1" style="background:rgba(0,0,0,0.3)">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">Confirm Delete</h5>
                <button type="button" class="btn-close" @click="closeDeleteChapterDialog"></button>
              </div>
              <div class="modal-body">
                <p>Are you sure you want to delete this chapter?</p>
              </div>
              <div class="modal-footer">
                <button class="btn btn-secondary" @click="closeDeleteChapterDialog">Cancel</button>
                <button class="btn btn-danger" @click="confirmDeleteChapter">Delete</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="results.quizzes.length">
        <h3 class="mb-3 mt-4 text-primary">Quizzes</h3>
        <div class="row g-3">
          <div v-for="quiz in results.quizzes" :key="quiz.id" class="col-md-4">
            <div class="card h-100 shadow-sm-lg">
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
                  <button class="btn btn-sm btn-danger" @click="openDeleteQuizDialog(quiz.id)">Delete</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="showAddQuiz || showEditQuiz" class="modal fade show d-block" tabindex="-1" style="background:rgba(0,0,0,0.3)">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">{{ showAddQuiz ? 'Add Quiz' : 'Edit Quiz' }}</h5>
                <button type="button" class="btn-close" @click="closeQuizModal"></button>
              </div>
              <div class="modal-body">
                <form @submit.prevent="validateAndSubmitQuiz">
                  <div class="mb-3">
                    <label class="form-label">Name</label>
                    <input v-model="quizForm.name" class="form-control" :class="{'is-invalid': quizNameError}" required />
                    <div v-if="quizNameError" class="invalid-feedback">{{ quizNameError }}</div>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Description</label>
                    <textarea v-model="quizForm.description" class="form-control" :class="{'is-invalid': quizDescError}" required></textarea>
                    <div v-if="quizDescError" class="invalid-feedback">{{ quizDescError }}</div>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Chapter</label>
                    <select v-model="quizForm.chapter_id" class="form-control" :class="{'is-invalid': quizChapterError}" required>
                      <option value="" disabled>Select chapter</option>
                      <option v-for="chapter in chaptersList" :key="chapter.id" :value="chapter.id">{{ chapter.name }}</option>
                    </select>
                    <div v-if="quizChapterError" class="invalid-feedback">{{ quizChapterError }}</div>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Start Date</label>
                    <input v-model="quizForm.start_date" class="form-control" :class="{'is-invalid': quizStartDateError}" required />
                    <div v-if="quizStartDateError" class="invalid-feedback">{{ quizStartDateError }}</div>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">End Date</label>
                    <input v-model="quizForm.end_date" class="form-control" :class="{'is-invalid': quizEndDateError}" required />
                    <div v-if="quizEndDateError" class="invalid-feedback">{{ quizEndDateError }}</div>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Duration (minutes)</label>
                    <input v-model.number="quizForm.duration" class="form-control" :class="{'is-invalid': quizDurationError}" required type="number" min="30" max="120" />
                    <div v-if="quizDurationError" class="invalid-feedback">{{ quizDurationError }}</div>
                  </div>
                  <div class="d-flex justify-content-end">
                    <button type="submit" class="btn btn-primary">{{ showAddQuiz ? 'Add' : 'Update' }}</button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
        <div v-if="showDeleteQuizDialog" class="modal fade show d-block" tabindex="-1" style="background:rgba(0,0,0,0.3)">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">Confirm Delete</h5>
                <button type="button" class="btn-close" @click="closeDeleteQuizDialog"></button>
              </div>
              <div class="modal-body">
                <p>Are you sure you want to delete this quiz?</p>
              </div>
              <div class="modal-footer">
                <button class="btn btn-secondary" @click="closeDeleteQuizDialog">Cancel</button>
                <button class="btn btn-danger" @click="confirmDeleteQuiz">Delete</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="results.users.length">
        <h3 class="mb-3 mt-4 text-primary">Users</h3>
        <div class="row g-3">
          <div v-for="user in results.users" :key="user.id" class="col-md-4">
            <UserCard :user="user" :currentUserId="auth.user?.id" @toggle-status="toggleUserStatus" />
          </div>
        </div>
      </div>
      <div v-if="!results.subjects.length && !results.chapters.length && !results.quizzes.length && !results.users.length && !loading" class="text-center my-5">
        <span>No results found.</span>
      </div>
    </div>
    <div v-if="showAddSubject || showEditSubject" class="modal fade show d-block" tabindex="-1" style="background:rgba(0,0,0,0.3)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ showAddSubject ? 'Add Subject' : 'Edit Subject' }}</h5>
            <button type="button" class="btn-close" @click="closeSubjectModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="validateAndSubmitSubject">
              <div class="mb-3">
                <label class="form-label">Name</label>
                <input v-model="subjectForm.name" class="form-control" :class="{'is-invalid': subjectNameError}" required />
                <div v-if="subjectNameError" class="invalid-feedback">{{ subjectNameError }}</div>
              </div>
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea v-model="subjectForm.description" class="form-control" :class="{'is-invalid': subjectDescError}" required></textarea>
                <div v-if="subjectDescError" class="invalid-feedback">{{ subjectDescError }}</div>
              </div>
              <div class="d-flex justify-content-end">
                <button type="submit" class="btn btn-primary">{{ showAddSubject ? 'Add' : 'Update' }}</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showDeleteSubjectDialog" class="modal fade show d-block" tabindex="-1" style="background:rgba(0,0,0,0.3)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Delete</h5>
            <button type="button" class="btn-close" @click="closeDeleteSubjectDialog"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete this subject?</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeDeleteSubjectDialog">Cancel</button>
            <button class="btn btn-danger" @click="confirmDeleteSubject">Delete</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from '@/axios'
import defaultPic from '@/assets/dummy-user.jpg'
import { useAuthStore } from '@/stores/auth'
import { useFlashStore } from '@/stores/flash'
import UserCard from '@/components/UserCard.vue'

const search = ref('')
const loading = ref(false)
const results = ref<{ subjects: any[]; chapters: any[]; quizzes: any[]; users: any[] }>({ subjects: [], chapters: [], quizzes: [], users: [] })
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const flash = useFlashStore()

function getProfilePicUrl(pic: string | undefined) {
  if (!pic) return defaultPic
  if (pic.startsWith('http')) return pic
  const base = axios.defaults.baseURL || ''
  if (pic.startsWith('/static/')) return base + pic
  if (pic.startsWith('static/')) return base + '/' + pic
  if (pic.startsWith('profile_pics/')) return base + '/static/' + pic
  return base + '/static/profile_pics/' + pic
}

async function toggleUserStatus(user: any) {
  try {
    await axios.put(`/auth/user/${user.id}/status`)
    flash.setFlash('User status updated.', 'success')
    const found = results.value.users.find((u: any) => u.id === user.id)
    if (found) found.status = !user.status
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to update user status', 'error')
  }
}

onMounted(() => {
  const q = route.query.q as string
  if (q) {
    search.value = q
    onSearch()
  }
})

watch(() => route.query.q, (newQ, oldQ) => {
  if (newQ !== oldQ) {
    search.value = newQ as string || ''
    if (search.value) onSearch()
    else onReset()
  }
})

async function onSearch() {
  if (route.name !== 'AdminSearch' || route.query.q !== search.value.trim()) {
    router.push({ name: 'AdminSearch', query: { q: search.value.trim() } })
    return
  }
  loading.value = true
  try {
    const q = search.value.trim()
    async function safeGet(url: string, params: any) {
      try {
        const res = await axios.get(url, params)
        return res.data.data || []
      } catch (err: any) {
        if (err.response && err.response.status === 404) return []
        throw err
      }
    }
    const [subjects, chapters, quizzes, users] = await Promise.all([
      safeGet('/admin/subject/search', { params: { text: q } }),
      safeGet('/admin/chapter/search', { params: { text: q } }),
      safeGet('/admin/quiz/search', { params: { text: q } }),
      safeGet(`/auth/user/${encodeURIComponent(q)}/search`, {})
    ])
    results.value = {
      subjects,
      chapters,
      quizzes: quizzes as any[],
      users
    }
  } catch (e) {
    results.value = { subjects: [], chapters: [], quizzes: [], users: [] }
  }
  loading.value = false
}

function onReset() {
  search.value = ''
  results.value = { subjects: [], chapters: [], quizzes: [], users: [] }
  if (route.query.q) {
    router.replace({ name: 'AdminSearch', query: {} })
  }
}

function goToChapters(subjectId: number) {
  sessionStorage.setItem('filter_subject_id', String(subjectId))
  router.push({ name: 'Chapters' })
}

function editSubject(subject: any) {
  showEditSubject.value = true
  showAddSubject.value = false
  subjectForm.value = { ...subject }
  subjectNameError.value = ''
  subjectDescError.value = ''
}

function openDeleteSubjectDialog(subjectId: number) {
  subjectToDelete.value = subjectId
  showDeleteSubjectDialog.value = true
}
function closeDeleteSubjectDialog() {
  showDeleteSubjectDialog.value = false
  subjectToDelete.value = null
}
async function confirmDeleteSubject() {
  if (subjectToDelete.value !== null) {
    await deleteSubject(subjectToDelete.value)
  }
  closeDeleteSubjectDialog()
}
async function deleteSubject(id: number) {
  try {
    await axios.delete(`/admin/subject/${id}`)
    flash.setFlash('Subject deleted successfully', 'success')
    await onSearch() 
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to delete subject', 'error')
  }
}

function goToQuizzes(chapterId: number) {
  sessionStorage.setItem('filter_chapter_id', String(chapterId))
  router.push('/quizzes')
}

function editChapter(chapter: any) {
  fetchSubjectsList()
  chapterForm.value = { ...chapter }
  showEditChapter.value = true
  showAddChapter.value = false
}

function openDeleteChapterDialog(id: number) {
  chapterToDelete.value = id
  showDeleteChapterDialog.value = true
}

function goToQuestions(quizId: number) {
  sessionStorage.setItem('filter_quiz_id', String(quizId))
  router.push('/questions')
}

function editQuiz(quiz: any) {
  fetchChaptersList()
  quizForm.value = { ...quiz }
  showEditQuiz.value = true
  showAddQuiz.value = false
}

function openDeleteQuizDialog(id: number) {
  quizToDelete.value = id
  showDeleteQuizDialog.value = true
}

const showAddChapter = ref(false)
const showEditChapter = ref(false)
const showDeleteChapterDialog = ref(false)
const chapterToDelete = ref<number|null>(null)
const chapterForm = ref({ id: null, name: '', description: '', subject_id: null })
const chapterNameError = ref('')
const chapterDescError = ref('')
const chapterSubjectError = ref('')
const subjectsList = ref<any[]>([])

const showAddQuiz = ref(false)
const showEditQuiz = ref(false)
const showDeleteQuizDialog = ref(false)
const quizToDelete = ref<number|null>(null)
const quizForm = ref({ id: null, name: '', description: '', chapter_id: '', start_date: '', end_date: '', duration: 30 })
const quizNameError = ref('')
const quizDescError = ref('')
const quizChapterError = ref('')
const quizStartDateError = ref('')
const quizEndDateError = ref('')
const quizDurationError = ref('')
const chaptersList = ref<any[]>([])

const showAddSubject = ref(false)
const showEditSubject = ref(false)
const showDeleteSubjectDialog = ref(false)
const subjectToDelete = ref<number|null>(null)
const subjectForm = ref({ id: null, name: '', description: '' })
const subjectNameError = ref('')
const subjectDescError = ref('')

function openAddChapterModal() {
  fetchSubjectsList()
  showAddChapter.value = true
  showEditChapter.value = false
  chapterForm.value = { id: null, name: '', description: '', subject_id: null }
}
function closeChapterModal() {
  showAddChapter.value = false
  showEditChapter.value = false
  chapterForm.value = { id: null, name: '', description: '', subject_id: null }
  chapterNameError.value = ''
  chapterDescError.value = ''
  chapterSubjectError.value = ''
}
function closeDeleteChapterDialog() {
  showDeleteChapterDialog.value = false
  chapterToDelete.value = null
}
async function confirmDeleteChapter() {
  if (chapterToDelete.value !== null) {
    await deleteChapter(chapterToDelete.value)
  }
  closeDeleteChapterDialog()
}
async function deleteChapter(id: number) {
  try {
    await axios.delete(`/admin/chapter/${id}`)
    flash.setFlash('Chapter deleted successfully', 'success')
    results.value.chapters = results.value.chapters.filter((c: any) => c.id !== id)
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to delete chapter', 'error')
  }
}
async function fetchSubjectsList() {
  try {
    const res = await axios.get('/admin/subject')
    if (res.data && res.data.data) {
      subjectsList.value = res.data.data
    }
  } catch (err) {
    flash.setFlash('Failed to fetch subjects for dropdown', 'error')
  }
}
function validateAndSubmitChapter() {
  chapterNameError.value = ''
  chapterDescError.value = ''
  chapterSubjectError.value = ''
  const nameRegex = /^[A-Za-z\s']{2,512}$/;
  const descRegex = /^[A-Za-z0-9 .,!?()'":;-]+$/;
  let valid = true
  if (!chapterForm.value.name || !nameRegex.test(chapterForm.value.name)) {
    chapterNameError.value = "Chapter name must be 2-512 letters, spaces, or ' only"
    valid = false
  }
  if (!chapterForm.value.description || !descRegex.test(chapterForm.value.description)) {
    chapterDescError.value = "Description can contain letters, numbers, spaces, and common punctuation (.,!?()'\":;-)."
    valid = false
  }
  if (!chapterForm.value.subject_id || isNaN(chapterForm.value.subject_id)) {
    chapterSubjectError.value = 'Please select a subject.'
    valid = false
  }
  if (!valid) return
  if (showAddChapter.value) {
    addChapter()
  } else {
    updateChapter()
  }
}
async function addChapter() {
  try {
    const res = await axios.post('/admin/chapter', {
      name: chapterForm.value.name,
      description: chapterForm.value.description,
      subject_id: chapterForm.value.subject_id
    })
    flash.setFlash('Chapter added successfully', 'success')
    closeChapterModal()
    // Add to results
    results.value.chapters.push(res.data.data)
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to add chapter', 'error')
  }
}
async function updateChapter() {
  try {
    await axios.put(`/admin/chapter/${chapterForm.value.id}`, {
      name: chapterForm.value.name,
      description: chapterForm.value.description,
      subject_id: chapterForm.value.subject_id
    })
    flash.setFlash('Chapter updated successfully', 'success')
    closeChapterModal()
    await onSearch() 
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to update chapter', 'error')
  }
}

function openAddQuizModal() {
  fetchChaptersList()
  showAddQuiz.value = true
  showEditQuiz.value = false
  quizForm.value = { id: null, name: '', description: '', chapter_id: '', start_date: '', end_date: '', duration: 30 }
}
function closeQuizModal() {
  showAddQuiz.value = false
  showEditQuiz.value = false
  quizForm.value = { id: null, name: '', description: '', chapter_id: '', start_date: '', end_date: '', duration: 30 }
  quizNameError.value = ''
  quizDescError.value = ''
  quizChapterError.value = ''
  quizStartDateError.value = ''
  quizEndDateError.value = ''
  quizDurationError.value = ''
}
function closeDeleteQuizDialog() {
  showDeleteQuizDialog.value = false
  quizToDelete.value = null
}
async function confirmDeleteQuiz() {
  if (quizToDelete.value !== null) {
    await deleteQuiz(quizToDelete.value)
  }
  closeDeleteQuizDialog()
}
async function deleteQuiz(id: number) {
  try {
    await axios.delete(`/admin/quiz/${id}`)
    flash.setFlash('Quiz deleted successfully', 'success')
    results.value.quizzes = results.value.quizzes.filter((q: any) => q.id !== id)
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to delete quiz', 'error')
  }
}
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
function validateAndSubmitQuiz() {
  quizNameError.value = ''
  quizDescError.value = ''
  quizChapterError.value = ''
  quizStartDateError.value = ''
  quizEndDateError.value = ''
  quizDurationError.value = ''
  const nameRegex = /^[A-Za-z\s']{2,512}$/;
  const descRegex = /^[A-Za-z0-9 .,!?()'":;-]+$/;
  let valid = true
  if (!quizForm.value.name || !nameRegex.test(quizForm.value.name)) {
    quizNameError.value = "Quiz name must be 2-512 letters, spaces, or ' only"
    valid = false
  }
  if (!quizForm.value.description || !descRegex.test(quizForm.value.description)) {
    quizDescError.value = "Description can contain letters, numbers, spaces, and common punctuation (.,!?()'\":;-)."
    valid = false
  }
  if (!quizForm.value.chapter_id || isNaN(Number(quizForm.value.chapter_id))) {
    quizChapterError.value = 'Please select a chapter.'
    valid = false
  }
  if (!quizForm.value.start_date) {
    quizStartDateError.value = 'Start date is required.'
    valid = false
  }
  if (!quizForm.value.end_date) {
    quizEndDateError.value = 'End date is required.'
    valid = false
  }
  if (quizForm.value.duration < 30 || quizForm.value.duration > 120) {
    quizDurationError.value = 'Duration must be between 30 and 120 minutes.'
    valid = false
  }
  if (!valid) return
  if (showAddQuiz.value) {
    addQuiz()
  } else {
    updateQuiz()
  }
}
async function addQuiz() {
  try {
    const res = await axios.post('/admin/quiz', {
      name: quizForm.value.name,
      description: quizForm.value.description,
      chapter_id: quizForm.value.chapter_id,
      start_date: quizForm.value.start_date,
      end_date: quizForm.value.end_date,
      duration: quizForm.value.duration
    })
    flash.setFlash('Quiz added successfully', 'success')
    closeQuizModal()
    results.value.quizzes.push(res.data.data)
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to add quiz', 'error')
  }
}
async function updateQuiz() {
  try {
    await axios.put(`/admin/quiz/${quizForm.value.id}`, {
      name: quizForm.value.name,
      description: quizForm.value.description,
      chapter_id: quizForm.value.chapter_id,
      start_date: quizForm.value.start_date,
      end_date: quizForm.value.end_date,
      duration: quizForm.value.duration
    })
    flash.setFlash('Quiz updated successfully', 'success')
    closeQuizModal()
    await onSearch() 
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to update quiz', 'error')
  }
}

function openAddSubjectModal() {
  showAddSubject.value = true
  showEditSubject.value = false
  subjectForm.value = { id: null, name: '', description: '' }
  subjectNameError.value = ''
  subjectDescError.value = ''
}
function closeSubjectModal() {
  showAddSubject.value = false
  showEditSubject.value = false
  subjectForm.value = { id: null, name: '', description: '' }
  subjectNameError.value = ''
  subjectDescError.value = ''
}
function validateAndSubmitSubject() {
  subjectNameError.value = ''
  subjectDescError.value = ''
  const nameRegex = /^[A-Za-z\s']{2,512}$/;
  const descRegex = /^[A-Za-z0-9 .,!?()'":;-]+$/;
  let valid = true
  if (!subjectForm.value.name || !nameRegex.test(subjectForm.value.name)) {
    subjectNameError.value = "Subject name must be 2-512 letters, spaces, or ' only"
    valid = false
  }
  if (!subjectForm.value.description || !descRegex.test(subjectForm.value.description)) {
    subjectDescError.value = "Description can contain letters, numbers, spaces, and common punctuation (.,!?()'\":;-)."
    valid = false
  }
  if (!valid) return
  if (showAddSubject.value) {
    addSubject()
  } else {
    updateSubject()
  }
}
async function addSubject() {
  try {
    const res = await axios.post('/admin/subject', {
      name: subjectForm.value.name,
      description: subjectForm.value.description
    })
    flash.setFlash('Subject added successfully', 'success')
    closeSubjectModal()
    // Add to results
    results.value.subjects.push(res.data.data)
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to add subject', 'error')
  }
}
async function updateSubject() {
  try {
    await axios.put(`/admin/subject/${subjectForm.value.id}`, {
      name: subjectForm.value.name,
      description: subjectForm.value.description
    })
    flash.setFlash('Subject updated successfully', 'success')
    closeSubjectModal()
    await onSearch() 
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to update subject', 'error')
  }
}
</script>

<style scoped>
.card {
  transition: transform 0.2s;
}
.card:hover {
  transform: scale(1.02);
}
</style>
