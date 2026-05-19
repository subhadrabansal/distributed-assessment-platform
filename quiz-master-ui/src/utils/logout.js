// src/utils/logout.js
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

export function useLogout() {
  const auth = useAuthStore()
  const router = useRouter()

  function logout() {
    auth.logout()
    router.push('/')
  }

  return { logout }
}
