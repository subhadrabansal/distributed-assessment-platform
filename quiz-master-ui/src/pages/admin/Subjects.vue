<template>
  <div class="flex-grow-1 p-4">
    <div>
      <h2 class="mb-4 text-center">Subjects Management</h2>
      <div v-if="!isAdmin" class="alert alert-danger">You are not authorized to view this page.</div>
      <div v-else>
        <div class="mb-3 d-flex justify-content-between align-items-center">
          <div class="input-group w-90">
            <input v-model="search" class="form-control" placeholder="Search subjects..." />
            <button class="btn btn-outline-primary" @click="handleSearch">&#128269;</button>
            <button class="btn btn-outline-secondary" @click="handleReset">❌</button>
            <button class="btn btn-outline-primary ms-2 " @click="showAdd = true">➕Subject</button>
          </div>
        </div>
        <div class="row g-3">
          <div v-for="subject in filteredSubjects" :key="subject.id" class="col-md-4">
            <div class="card h-100">
              <div class="card-body">
                <h5 class="card-title">{{ subject.name }}</h5>
                <p class="card-text">{{ subject.description }}</p>
                <hr/>
                <div class="d-flex justify-content-end gap-1">
                  <button class="btn btn-sm btn-info" @click="goToChapters(subject.id)"> {{ subject.chapters }} Chapters </button>|
                  <button class="btn btn-sm btn-warning" @click="editSubject(subject)">Edit</button>
                  <button class="btn btn-sm btn-danger" @click="openDeleteDialog(subject.id)">Delete</button>
                  
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="showAdd || showEdit" class="modal fade show d-block" tabindex="-1" style="background:rgba(0,0,0,0.3)">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">{{ showAdd ? 'Add Subject' : 'Edit Subject' }}</h5>
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
                  <div class="d-flex justify-content-end">
                    <button type="submit" class="btn btn-primary">{{ showAdd ? 'Add' : 'Update' }}</button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
        <div v-if="showDeleteDialog" class="modal fade show d-block" tabindex="-1" style="background:rgba(0,0,0,0.3)">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">Confirm Delete</h5>
                <button type="button" class="btn-close" @click="closeDeleteDialog"></button>
              </div>
              <div class="modal-body">
                <p>Are you sure you want to delete this subject?</p>
              </div>
              <div class="modal-footer">
                <button class="btn btn-secondary" @click="closeDeleteDialog">Cancel</button>
                <button class="btn btn-danger" @click="confirmDeleteSubject">Delete</button>
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
const subjects = ref<any[]>([])
const search = ref('')
const showAdd = ref(false)
const showEdit = ref(false)
const showDeleteDialog = ref(false)
const subjectToDelete = ref<number|null>(null)
const form = ref({ id: null, name: '', description: '' })
const filteredSubjects = ref<any[]>([])
const nameError = ref('')
const descError = ref('')

function closeModal() {
  showAdd.value = false
  showEdit.value = false
  form.value = { id: null, name: '', description: '' }
}

async function fetchSubjects() {
  try {
    search.value = ''
    const res = await axios.get('/admin/subject')
    if (res.data && res.data.data) {
      subjects.value = res.data.data
      filteredSubjects.value = res.data.data
    }
  } catch (err) {
    flash.setFlash('Failed to fetch subjects', 'error')
  }
}

async function addSubject() {
  try {
    await axios.post('/admin/subject', {
      name: form.value.name,
      description: form.value.description
    })
    flash.setFlash('Subject added successfully', 'success')
    closeModal()
    fetchSubjects()
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to add subject', 'error')
  }
}

function editSubject(subject: any) {
  form.value = { ...subject }
  showEdit.value = true
}

async function updateSubject() {
  try {
    await axios.put(`/admin/subject/${form.value.id}`, {
      name: form.value.name,
      description: form.value.description
    })
    flash.setFlash('Subject updated successfully', 'success')
    closeModal()
    fetchSubjects()
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to update subject', 'error')
  }
}

async function deleteSubject(id: number) {
  try {
    await axios.delete(`/admin/subject/${id}`)
    flash.setFlash('Subject deleted successfully', 'success')
    fetchSubjects()
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to delete subject', 'error')
  }
}

function openDeleteDialog(id: number) {
  subjectToDelete.value = id
  showDeleteDialog.value = true
}
function closeDeleteDialog() {
  showDeleteDialog.value = false
  subjectToDelete.value = null
}
async function confirmDeleteSubject() {
  if (subjectToDelete.value !== null) {
    await deleteSubject(subjectToDelete.value)
  }
  closeDeleteDialog()
}

function handleSearch() {
  if (!search.value || search.value.trim().length < 3) {
    flash.setFlash('Please enter at least 3 characters to search.', 'error')
    return
  }
  axios.get(`/admin/subject/search`, { params: { text: search.value } })
    .then(res => {
      if (res.data && res.data.data) {
        filteredSubjects.value = res.data.data
      } else {
        filteredSubjects.value = []
        flash.setFlash('No subjects found.', 'error')
      }
    })
    .catch(() => {
      filteredSubjects.value = []
      flash.setFlash('No subjects found.', 'error')
    })
}

function handleReset() {
  search.value = ''
  fetchSubjects()
  filteredSubjects.value = subjects.value
}

function validateAndSubmit() {
  nameError.value = ''
  descError.value = ''
  const nameRegex = /^[A-Za-z\s']+$/
  const descRegex = /^[A-Za-z0-9 .,!?()\'":;-]+$/
  let valid = true
  if (!form.value.name || !nameRegex.test(form.value.name)) {
    nameError.value = "Subject can only contain letters, spaces and ' (e.g., Mathematics, Computer Science)."
    valid = false
  }
  if (!form.value.description || !descRegex.test(form.value.description)) {
    descError.value = "Description can contain letters, numbers, spaces, and common punctuation (.,!?()'\":;-)."
    valid = false
  }
  if (!valid) return
  if (showAdd.value) {
    addSubject()
  } else {
    updateSubject()
  }
}

function goToChapters(subjectId: number) {
  sessionStorage.setItem('filter_subject_id', String(subjectId))
  router.push({ name: 'Chapters' })
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
  fetchSubjects()
  filteredSubjects.value = subjects.value
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
