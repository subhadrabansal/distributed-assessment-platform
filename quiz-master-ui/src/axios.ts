// src/axios.ts
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useFlashStore } from '@/stores/flash'
import router from '@/router'

const instance = axios.create({
  baseURL: 'http://127.0.0.1:5000', // Removed /api prefix to match backend
  withCredentials: true
})

// Add global response interceptor for auth errors
instance.interceptors.response.use(
  response => response,
  error => {
    // Handle 401/422 errors globally
    if (error.response && (error.response.status === 401 || error.response.status === 422)) {
      const auth = useAuthStore()
      const flash = useFlashStore()
      auth.logout()
      flash.setFlash('Session expired or invalid. Please log in again.', 'error')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default instance
