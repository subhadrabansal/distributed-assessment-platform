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
            <p>Are you sure you want to delete this chapter?</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeDeleteDialog">Cancel</button>
            <button class="btn btn-danger" @click="confirmDeleteChapter">Delete</button>
          </div>
        </div>
      </div>
    </div>
    <div>
      <h2 class="mb-4 text-center">Chapters Management</h2>
      <div v-if="!isAdmin" class="alert alert-danger">You are not authorized to view this page.</div>
      <div v-else>
        <div class="mb-3 d-flex justify-content-between align-items-center">
          <div class="input-group w-90">
            <input v-model="search" class="form-control" placeholder="Search chapters..." />
            <button class="btn btn-outline-primary" @click="handleSearch">&#128269;</button>
            <button class="btn btn-outline-secondary" @click="handleReset">❌</button>
            <button class="btn btn-outline-primary ms-2" @click="openAddModal">➕Chapter</button>
          </div>
        </div>
        <div class="row g-3">
          <div v-for="chapter in filteredChapters" :key="chapter.id" class="col-md-4">
            <div class="card h-100">
              <div class="card-body">
                <h5 class="card-title">{{ chapter.name }}</h5>
                <p class="card-text">{{ chapter.description }}</p>
                  <p class="card-text"><strong>Subject:</strong> {{ chapter.subject_name }}</p>
                  <hr/>
                <div class="d-flex justify-content-end gap-1">
                  <button class="btn btn-sm btn-info" @click="goToQuizzes(chapter.id)">{{ chapter.quizzes }} Quizzes</button>|
                  <button class="btn btn-sm btn-warning" @click="editChapter(chapter)">Edit</button>
                  <button class="btn btn-sm btn-danger" @click="openDeleteDialog(chapter.id)">Delete</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="showAdd || showEdit" class="modal fade show d-block" tabindex="-1" style="background:rgba(0,0,0,0.3)">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">{{ showAdd ? 'Add Chapter' : 'Edit Chapter' }}</h5>
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
                    <label class="form-label">Subject</label>
                    <select v-model="form.subject_id" class="form-control" :class="{'is-invalid': subjectError}" required>
                      <option value="" disabled>Select subject</option>
                      <option v-for="subject in subjectsList" :key="subject.id" :value="subject.id">{{ subject.name }}</option>
                    </select>
                    <div v-if="subjectError" class="invalid-feedback">{{ subjectError }}</div>
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
import { useRouter, useRoute } from 'vue-router'

const auth = useAuthStore()
const flash = useFlashStore()
const router = useRouter()

const isAdmin = computed(() => auth.userIsLoggedIn && auth.user?.isAdmin)
const chapters = ref<any[]>([])
const search = ref('')
const showAdd = ref(false)
const showEdit = ref(false)
const form = ref({ id: null, name: '', description: '', subject_id: null })
const filteredChapters = ref<any[]>([])
const showDeleteDialog = ref(false)
const chapterToDelete = ref<number|null>(null)
const nameError = ref('')
const descError = ref('')
const subjectError = ref('')
const subjectsList = ref<any[]>([])
const subjectId = ref<number | null>(null)

function closeModal() {
  showAdd.value = false
  showEdit.value = false
  form.value = { id: null, name: '', description: '', subject_id: null }
}

async function fetchChapters() {
  try {
    search.value = ''
    let res
    if (subjectId.value) {
      res = await axios.get(`/admin/subject/${subjectId.value}/chapters`)
    } else {
      res = await axios.get('/admin/chapter')
    }
    if (res.data && res.data.data) {
      chapters.value = res.data.data
      filteredChapters.value = res.data.data
    }
  } catch (err) {
    flash.setFlash('Failed to fetch chapters', 'error')
  }
}

async function addChapter() {
  try {
    await axios.post('/admin/chapter', {
      name: form.value.name,
      description: form.value.description,
      subject_id: form.value.subject_id
    })
    flash.setFlash('Chapter added successfully', 'success')
    closeModal()
    fetchChapters()
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to add chapter', 'error')
  }
}

async function openAddModal() {
  await fetchSubjectsList()
  showAdd.value = true
  form.value = { id: null, name: '', description: '', subject_id: null }
}

async function editChapter(chapter: any) {
  await fetchSubjectsList()
  form.value = { ...chapter }
  showEdit.value = true
}

async function updateChapter() {
  try {
    await axios.put(`/admin/chapter/${form.value.id}`, {
      name: form.value.name,
      description: form.value.description,
      subject_id: form.value.subject_id
    })
    flash.setFlash('Chapter updated successfully', 'success')
    closeModal()
    fetchChapters()
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to update chapter', 'error')
  }
}

function openDeleteDialog(id: number) {
  chapterToDelete.value = id
  showDeleteDialog.value = true
}
function closeDeleteDialog() {
  showDeleteDialog.value = false
  chapterToDelete.value = null
}
async function confirmDeleteChapter() {
  if (chapterToDelete.value !== null) {
    await deleteChapter(chapterToDelete.value)
  }
  closeDeleteDialog()
}

async function deleteChapter(id: number) {
  try {
    await axios.delete(`/admin/chapter/${id}`)
    flash.setFlash('Chapter deleted successfully', 'success')
    fetchChapters()
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to delete chapter', 'error')
  }
}

function handleSearch() {
  if (!search.value || search.value.trim().length < 3) {
    flash.setFlash('Please enter at least 3 characters to search.', 'error')
    return
  }
  axios.get(`/admin/chapter/search`, { params: { text: search.value } })
    .then(res => {
      if (res.data && res.data.data) {
        filteredChapters.value = res.data.data
      } else {
        filteredChapters.value = []
        flash.setFlash('No chapters found.', 'error')
      }
    })
    .catch(() => {
      filteredChapters.value = []
      flash.setFlash('No chapters found.', 'error')
    })
}

function handleReset() {
  search.value = ''
  subjectId.value = null 
  fetchChapters()
  filteredChapters.value = chapters.value
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

function validateAndSubmit() {
  nameError.value = ''
  descError.value = ''
  subjectError.value = ''
  const nameRegex = /^[A-Za-z\s']{2,512}$/
  const descRegex = /^[A-Za-z0-9 .,!?()'":;-]+$/
  let valid = true
  if (!form.value.name || !nameRegex.test(form.value.name)) {
    nameError.value = "Chapter name must be 2-512 letters, spaces, or ' only"
    valid = false
  }
  if (!form.value.description || !descRegex.test(form.value.description)) {
    descError.value = "Description can contain letters, numbers, spaces, and common punctuation (.,!?()'\":;-)."
    valid = false
  }
  if (!form.value.subject_id || isNaN(form.value.subject_id)) {
    subjectError.value = 'Please select a subject.'
    valid = false
  }
  if (!valid) return
  if (showAdd.value) {
    addChapter()
  } else {
    updateChapter()
  }
}

function goToQuizzes(chapterId: number) {
  sessionStorage.setItem('filter_chapter_id', String(chapterId))
  router.push('/quizzes')
}

onMounted(() => {
  const storedId = sessionStorage.getItem('filter_subject_id')
  if (storedId) {
    subjectId.value = Number(storedId)
    sessionStorage.removeItem('filter_subject_id')
  }
  if (auth.userIsLoggedIn && auth.user?.token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${auth.user.token}`
  }
  if (!isAdmin.value) {
    flash.setFlash('You are not authorized to view this page.', 'error')
    router.push('/')
    return
  }
  fetchChapters()
  filteredChapters.value = chapters.value
  fetchSubjectsList()
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
