<template>
  <div class="flex-grow-1 p-4">
    <div class="card mx-auto p-4" style="max-width: 500px;">
      <div class="d-flex align-items-center mb-3 flex-wrap flex-md-nowrap">
        <img :src="getProfilePicUrl(auth.user?.profile_picture)" alt="Profile" class="rounded-circle me-3 mb-2 mb-md-0" width="80" height="80" />
        <div class="flex-grow-1">
          <h4 class="mb-0">{{ auth.user?.fullname }}</h4>
          <div class="text-muted small">{{ auth.user?.email }}</div>
        </div>
        <button class="btn btn-outline-secondary ms-auto mt-2 mt-md-0" @click="openPicDialog">Update</button>
      </div>
      <hr />
      <form @submit.prevent="validateAndUpdateProfile">
        <div class="mb-2">
          <label class="form-label">Full Name</label>
          <input v-model="profile.fullname" class="form-control" :class="{'is-invalid': fullnameError}" />
          <div v-if="fullnameError" class="invalid-feedback">{{ fullnameError }}</div>
        </div>
        <div class="mb-2">
          <label class="form-label">Qualification</label>
          <input v-model="profile.qualification" class="form-control" :class="{'is-invalid': qualificationError}" />
          <div v-if="qualificationError" class="invalid-feedback">{{ qualificationError }}</div>
        </div>
        <div class="mb-2">
          <label class="form-label">Subject</label>
          <input v-model="profile.subject" class="form-control" :class="{'is-invalid': subjectError}" />
          <div v-if="subjectError" class="invalid-feedback">{{ subjectError }}</div>
        </div>
        <div class="mb-2">
          <label class="form-label">Date of Birth</label>
          <input v-model="profile.date_of_birth" type="text" class="form-control" :class="{'is-invalid': dobError}" placeholder="DD-MM-YYYY" maxlength="10" />
          <div v-if="dobError" class="invalid-feedback">{{ dobError }}</div>
        </div>
        <div class="mb-2">
          <label class="form-label">Phone Number</label>
          <input v-model="profile.phone_number" class="form-control" :class="{'is-invalid': phoneError}" />
          <div v-if="phoneError" class="invalid-feedback">{{ phoneError }}</div>
        </div>
        <div class="d-flex justify-content-between mt-3">
          <button type="submit" class="btn btn-primary">Update</button>
          <button type="button" class="btn btn-outline-warning" @click="openPasswordDialog">Change Password</button>
        </div>
      </form>
    </div>

    <input ref="fileInput" type="file" accept="image/*" class="d-none" @change="uploadPicture" />

    <div v-if="showPasswordModal" class="modal fade show d-block" tabindex="-1" style="background:rgba(0,0,0,0.3)">
      <div class="modal-dialog custom-modal-width">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Change Password</h5>
            <button type="button" class="btn-close" @click="closePasswordDialog"></button>
          </div>
          <div class="modal-body">
            <div class="mb-2">
              <label class="form-label">New Password</label>
              <input v-model="password.new" type="password" class="form-control" :class="{'is-invalid': passwordError}" />
              <div v-if="passwordError" class="invalid-feedback">{{ passwordError }}</div>
            </div>
            <div class="mb-2">
              <label class="form-label">Retype Password</label>
              <input v-model="password.retype" type="password" class="form-control" :class="{'is-invalid': retypeError}" />
              <div v-if="retypeError" class="invalid-feedback">{{ retypeError }}</div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-primary" @click="validateAndUpdatePassword">Update</button>
            <button class="btn btn-secondary" @click="closePasswordDialog">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from '@/axios'
import defaultPic from '@/assets/dummy-user.jpg'
import { useFlashStore } from '@/stores/flash'

const auth = useAuthStore()
const flash = useFlashStore()
const profile = reactive({
  fullname: '',
  qualification: '',
  subject: '',
  date_of_birth: '',
  phone_number: '',
  profile_picture: ''
})
const fileInput = ref<HTMLInputElement | null>(null)
const showPasswordModal = ref(false)
const password = reactive({ new: '', retype: '' })
const fullnameError = ref('')
const qualificationError = ref('')
const subjectError = ref('')
const dobError = ref('')
const phoneError = ref('')
const passwordError = ref('')
const retypeError = ref('')

function getProfilePicUrl(pic: string | undefined) {
  if (!pic) return defaultPic
  if (pic.startsWith('http')) return pic
  const base = axios.defaults.baseURL || ''
  if (pic.startsWith('/static/')) return base + pic
  const filename = pic.replace(/^profile_pics[\\/]?/, '')
  return base + '/static/profile_pics/' + filename
}

async function fetchProfile() {
  try {
    const res = await axios.get('/auth/profile')
    if (res.data && res.data.data) {
      Object.assign(profile, res.data.data)
    }
  } catch (err) {}
}

async function updateProfile() {
  try {
    const payload = {
      fullname: profile.fullname,
      qualification: profile.qualification,
      subject: profile.subject,
      phone_number: profile.phone_number,
      date_of_birth: profile.date_of_birth
    }
    const res = await axios.put('/auth/profile', payload)
    if (res.data.success) {
      flash.setFlash('Profile updated successfully.', 'success')
      auth.setUser(true, {
        ...auth.user,
        fullname: payload.fullname,
        profile_picture: profile.profile_picture
      })
      fetchProfile()
    } else {
      flash.setFlash(res.data.error_message || 'Failed to update profile.', 'error')
    }
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to update profile.', 'error')
  }
}

function openPicDialog() {
  fileInput.value?.click()
}

async function uploadPicture(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (!files || !files[0]) return
  const formData = new FormData()
  formData.append('file', files[0])
  try {
    const res = await axios.post('/auth/profile/upload_picture', formData)
    if (res.data.success) {
      const backendPic = res.data.data.profile_picture
      profile.profile_picture = backendPic
      flash.setFlash('Profile picture updated successfully.', 'success')
      auth.setUser(true, {
        ...auth.user,
        profile_picture: backendPic
      })
      fetchProfile()
    } else {
      flash.setFlash(res.data.error_message || 'Failed to update profile picture.', 'error')
    }
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to update profile picture.', 'error')
  }
}

function openPasswordDialog() {
  showPasswordModal.value = true
  password.new = ''
  password.retype = ''
}
function closePasswordDialog() {
  showPasswordModal.value = false
}
async function updatePassword() {
  if (!password.new || password.new !== password.retype) return
  try {
    const res = await axios.put('/auth/profile/upload_password', { new_password: password.new })
    if (res.data.success) {
      flash.setFlash('Password updated successfully.', 'success')
      closePasswordDialog()
    } else {
      flash.setFlash(res.data.error_message || 'Failed to update password.', 'error')
    }
  } catch (err: any) {
    flash.setFlash(err.response?.data?.error_message || 'Failed to update password.', 'error')
  }
}

function validateAndUpdatePassword() {
  passwordError.value = ''
  retypeError.value = ''
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]+$/
  let valid = true
  if (!password.new || password.new.length < 8 || password.new.length > 200 || !passwordRegex.test(password.new)) {
    passwordError.value = 'Password must be 8-200 chars, include uppercase, lowercase, number, and special character.'
    valid = false
  }
  if (!password.retype || password.retype !== password.new) {
    retypeError.value = 'Passwords must match.'
    valid = false
  }
  if (!valid) return
  updatePassword()
}

function validateAndUpdateProfile() {
  fullnameError.value = ''
  qualificationError.value = ''
  subjectError.value = ''
  dobError.value = ''
  phoneError.value = ''
  let valid = true

  const fullnameRegex = /^[A-Za-z\s']+$/
  if (!profile.fullname || profile.fullname.length < 2 || profile.fullname.length > 80 || !fullnameRegex.test(profile.fullname)) {
    fullnameError.value = "Full name is required and can only contain letters, spaces, and apostrophes (2-80 chars)."
    valid = false
  }
  const qualSubjRegex = /^[A-Za-z\s']+$/
  if (!profile.qualification || profile.qualification.length > 512 || !qualSubjRegex.test(profile.qualification)) {
    qualificationError.value = "Qualification is required and can only contain letters, spaces, and apostrophes (max 512 chars)."
    valid = false
  }
  if (!profile.subject || profile.subject.length > 512 || !qualSubjRegex.test(profile.subject)) {
    subjectError.value = "Subject is required and can only contain letters, spaces, and apostrophes (max 512 chars)."
    valid = false
  }
  const dobRegex = /^\d{2}-\d{2}-\d{4}$/
  if (!profile.date_of_birth || !dobRegex.test(profile.date_of_birth)) {
    dobError.value = "Date of birth is required and must be in DD-MM-YYYY format."
    valid = false
  }
  const phoneRegex = /^\+?[1-9]\d{1,14}$/
  if (!profile.phone_number || !phoneRegex.test(profile.phone_number) || profile.phone_number.length > 15) {
    phoneError.value = "Phone number is required and must be in E.164 format (e.g., +911234567890, max 15 digits)."
    valid = false
  }
  if (!valid) return
  updateProfile()
}

onMounted(() => {
  if (auth.userIsLoggedIn && auth.user?.token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${auth.user.token}`
  }
  fetchProfile()
})
</script>

<style scoped>
.card {
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  border-radius: 1rem;
}
.rounded-circle {
  object-fit: cover;
  border: 2px solid #eee;
}
.modal-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.15) !important;
  z-index: 1050;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 30vh;
}
.modal-dialog.custom-modal-width {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
}
@media (max-width: 600px) {
  .modal-dialog.custom-modal-width {
    max-width: 95vw;
    width: 95vw;
    margin: 0 2vw;
  }
}
@media (max-width: 300px) {
  .d-flex.align-items-center.mb-3.flex-wrap.flex-md-nowrap {
    flex-direction: column !important;
    align-items: stretch !important;
  }
  .btn.ms-auto.mt-2.mt-md-0 {
    width: 50%;
    margin-left: 0 !important;
  }
}
</style>