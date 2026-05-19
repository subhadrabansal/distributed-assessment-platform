<template>
  <div class="flex-grow-1 p-4">
    <div class="container mt-5" style="max-width: 500px">
      <h2 class="mb-4 text-center">Login</h2>
      <div class="card mb-3 shadow-sm">
        <div class="card-body">
          <form @submit.prevent="login" class="form" novalidate>
            <div class="mb-3">
              <label for="email" class="form-label">Email</label>
              <input
                type="email"
                class="form-control"
                :class="{ 'is-invalid': errors.email }"
                id="email"
                v-model="user.email"
                required
              >
              <div class="invalid-feedback">{{ errors.email }}</div>
            </div>

            <div class="mb-3">
              <label for="password" class="form-label">Password</label>
              <input
                type="password"
                class="form-control"
                :class="{ 'is-invalid': errors.password }"
                id="password"
                v-model="user.password"
                required
              >
              <div class="invalid-feedback">{{ errors.password }}</div>
            </div>

            <button type="submit" class="btn btn-primary w-100 mb-2">Login</button>
            <div class="text-end">
              <small>
              Forgot your password?
              <RouterLink to="/forgot-password">Reset Password</RouterLink>
              </small>
            </div>
          </form>
          <div class="text-center mt-3">
            <p>Don't have an account? <RouterLink to="/signup">Sign Up</RouterLink></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { reactive } from 'vue'
import axios from '@/axios'
import { useFlashStore } from '@/stores/flash'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router';

const flash = useFlashStore()
const auth = useAuthStore()
const router = useRouter();

if (auth.userIsLoggedIn) {
  flash.setFlash('You are already logged in.', 'error')
  setTimeout(() => {
    router.push('/');
  }, 2000)
}

const user = reactive({
  email: '',
  password: ''
})

const errors = reactive({
  email: '',
  password: ''
})

const validate = () => {
  let valid = true
  errors.email = ''
  errors.password = ''

  if (!user.email) {
    errors.email = 'Email is required.'
    valid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(user.email)) {
    errors.email = 'Invalid email format.'
    valid = false
  }

  if (!user.password) {
    errors.password = 'Password is required.'
    valid = false
  } else if (user.password.length < 8) {
    errors.password = 'Password must be at least 8 characters.'
    valid = false
  }

  return valid
}

const login = async () => {
  if (!validate()) return
  try {
    const response = await axios.post('/auth/login', user)
    const data = response.data
    if (data && data.success && data.data && data.data.token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${data.data.token}`
      auth.login({
        id: data.data.id,
        fullname: data.data.username,
        email: data.data.email,
        token: data.data.token,
        roles: data.data.roles,
        isAdmin: data.data.isAdmin,
        profile_picture: data.data.profile_picture
      })

      if (data.data.isAdmin === true) {
        router.push('/admin-dashboard')
        flash.setFlash('Welcome Admin!', 'success')
      } else {
        router.push('/user-dashboard') 
        flash.setFlash('Welcome User!', 'success')
      }
 
    } else {
      flash.setFlash('Login failed. Please try again.', 'error')
    }
  } catch (error: any) {
    if (error.response && error.response.data) {
      const data = error.response.data
      if (typeof data === 'object') {
        if (data.email) errors.email = data.email
        if (data.password) errors.password = data.password
        if (data.message) flash.setFlash(data.message, 'error')
      } else if (typeof data === 'string') {
        flash.setFlash(data, 'error')
      }
    } else {
      flash.setFlash('Login failed. Please try again.', 'error')
    }
    console.error('Error logging in:', error)
  }
}
</script>
