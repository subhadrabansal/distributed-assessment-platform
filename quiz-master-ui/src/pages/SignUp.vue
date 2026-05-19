<template>
  <div class="flex-grow-1 p-4">
    <div class="container mt-5" style="max-width: 500px">
      <h2 class="mb-4 text-center">Sign Up</h2>
      <div class="card mb-3 shadow-sm">
        <div class="card-body">
      <form @submit.prevent="register" class="form" novalidate>
        <div class="mb-3">
          <label for="name" class="form-label">Full Name</label>
          <input
            type="text"
            class="form-control"
            :class="{ 'is-invalid': errors.fullname }"
            id="fullname"
            v-model="user.fullname"
            required
          >
          <div class="invalid-feedback">{{ errors.fullname }}</div>
        </div>
  
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
  
        <div class="mb-3">
          <label for="confirm_password" class="form-label">Confirm Password</label>
          <input
            type="password"
            class="form-control"
            :class="{ 'is-invalid': errors.confirm_password }"
            id="confirm_password"
            v-model="user.confirm_password"
            required
          >
          <div class="invalid-feedback">{{ errors.confirm_password }}</div>
        </div>
  
        <button type="submit" class="btn btn-primary w-100">Register</button>
        
      </form>
      <div class="text-center mt-3">
          <p>Already have an account? <RouterLink to="/login">Login</RouterLink></p>
        </div>
      </div>
    </div>
    </div>
  </div>
  </template>
  
  <script lang="ts" setup>
  import { reactive } from 'vue'
  import axios  from '@/axios'
  import { useFlashStore } from '@/stores/flash'
  import { useAuthStore } from '@/stores/auth'
  import { useRouter } from 'vue-router';

  const router = useRouter()
  const flash = useFlashStore()
  const auth = useAuthStore()

  if (auth.userIsLoggedIn) {
  flash.setFlash('You are already logged in.', 'error')
  setTimeout(() => {
    router.push('/');
  }, 2000)
}


  
  
  const user = reactive({
    fullname: '',
    email: '',
    password: '',
    confirm_password: ''
  })

  const errors = reactive({
    fullname: '',
    email: '',
    password: '',
    confirm_password: ''
  })

  const validate = () => {
  let valid = true

  errors.fullname = ''
  errors.email = ''
  errors.password = ''
  errors.confirm_password = ''

  if (user.fullname.length < 2 || user.fullname.length > 80) {
    errors.fullname = 'Full name must be between 2 and 80 characters.'
    valid = false
  } else if (!/^[A-Za-z\s']+$/.test(user.fullname)) {
    errors.fullname = 'Full name can only contain letters, spaces, and apostrophes.'
    valid = false
  }

  if (!user.email) {
    errors.email = 'Email is required.'
    valid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(user.email)) {
    errors.email = 'Invalid email format.'
    valid = false
  }
  
  if (user.password.length < 8 || user.password.length > 20) {
    errors.password = 'Password must be between 8 and 20 characters.'
    valid = false
  } else if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]+$/.test(user.password)) {
    errors.password = 'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character.'
    valid = false
  }

  if (user.confirm_password !== user.password) {
    errors.confirm_password = 'Passwords do not match.'
    valid = false
  }

  return valid
}



  const register = async () => {
    if (!validate()) return
    try {
      const response = await axios.post('/auth/register', user)
      console.log('User registered:', response.data)
      router.push('/login')
      flash.setFlash('Registration successful! Please log in.', 'success')
      
    } catch (error: any) {
      if (error.response && error.response.data) {
        const data = error.response.data
        if (typeof data === 'object') {
          if (data.fullname) errors.fullname = data.fullname
          if (data.email) errors.email = data.email
          if (data.password) errors.password = data.password
          if (data.confirm_password) errors.confirm_password = data.confirm_password
          if (data.error_message) flash.setFlash(data.error_message, 'error')
          else if (data.message) flash.setFlash(data.message, 'error')
          if (data.errors == "EmailError") {
            errors.email = data.message
          }
        } else if (typeof data === 'string') {
          flash.setFlash(data, 'error')
        }
      } else {
        flash.setFlash('Registration failed. Please try again.', 'error')
      }
      console.error('Error registering user:', error)
    }
  }


  </script>
