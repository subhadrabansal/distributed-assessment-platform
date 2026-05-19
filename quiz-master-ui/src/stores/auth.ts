import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const userIsLoggedIn = ref(false)
  const user = ref<any>(null)

  function setUser(loggedIn: boolean, userInfo: any = null) {
    userIsLoggedIn.value = loggedIn
    user.value = userInfo
  }

  // Optionally, add login/logout helpers
  function login(userInfo: any) {
    setUser(true, userInfo)
  }
  function logout() {
    setUser(false, { profile_picture: '/src/assets/dummy-user.jpg' })
  }

  return { userIsLoggedIn, user, setUser, login, logout }
}, {
  persist: true
})