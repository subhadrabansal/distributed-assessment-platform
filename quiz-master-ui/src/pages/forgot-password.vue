<template>
    <div class="flex-grow-1 p-4">
        <div class="container mt-5" style="max-width: 500px">
            <div class="forgot-password-container">
                <h2>Forgot Password</h2>
                <form @submit.prevent="submitEmail">
                <div class="mb-3">
                    <label>Email</label>
                    <input v-model="email" type="email" class="form-control" required />
                </div>
                <button class="btn btn-primary" :disabled="loading">Send OTP</button>
                </form>
                <div v-if="step === 2">
                <form @submit.prevent="submitOtp">
                    <div class="mb-3">
                    <label>OTP</label>
                    <input v-model="otp" type="text" class="form-control" required />
                    </div>
                    <div class="mb-3">
                    <label>New Password</label>
                    <input v-model="password" type="password" class="form-control" required />
                    </div>
                    <div class="mb-3">
                    <label>Retype Password</label>
                    <input v-model="confirmPassword" type="password" class="form-control" required />
                    </div>
                    <button class="btn btn-success" :disabled="loading">Reset Password</button>
                </form>
                </div>
                <div v-if="message" class="alert mt-3" :class="{'alert-success': success, 'alert-danger': !success}">{{ message }}</div>
                <div class="d-flex justify-content-between mt-4">
                    <router-link to="/login" class="btn btn-link">Back to Login</router-link>
                    <router-link to="/signup" class="btn btn-link">Sign Up</router-link>
                </div>
            </div>
        </div>
    </div>
    
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from '@/axios'
import { useRouter } from 'vue-router'

const email = ref('')
const otp = ref('')
const password = ref('')
const confirmPassword = ref('')
const message = ref('')
const success = ref(false)
const loading = ref(false)
const step = ref(1)
const router = useRouter()

async function submitEmail() {
  loading.value = true
  message.value = ''
  try {
    const res = await axios.post('/auth/forgot-password', { email: email.value })
    if (res.data && res.data.success) {
      step.value = 2
      message.value = 'OTP sent to your email.'
      success.value = true
    } else {
      message.value = res.data.error_message || 'Failed to send OTP.'
      success.value = false
    }
  } catch (err: any) {
    message.value = err.response?.data?.error_message || 'Failed to send OTP.'
    success.value = false
  } finally {
    loading.value = false
  }
}

async function submitOtp() {
  loading.value = true
  message.value = ''
  if (password.value !== confirmPassword.value) {
    message.value = 'Passwords do not match.'
    success.value = false
    loading.value = false
    return
  }
  try {
    const res = await axios.post('/auth/reset-password', {
      email: email.value,
      otp: otp.value,
      password: password.value
    })
    if (res.data && res.data.success) {
      message.value = 'Password reset successful. You can now login.'
      success.value = true
      setTimeout(() => router.push('/login'), 2000)
    } else {
      message.value = res.data.error_message || 'Failed to reset password.'
      success.value = false
    }
  } catch (err: any) {
    message.value = err.response?.data?.error_message || 'Failed to reset password.'
    success.value = false
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.forgot-password-container {
  max-width: 400px;
  margin: 40px auto;
  padding: 2rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
</style>
