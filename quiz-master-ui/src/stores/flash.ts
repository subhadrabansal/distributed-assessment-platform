import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useFlashStore = defineStore('flash', () => {
  const message = ref('')
  const type = ref<'success' | 'error' | 'info'>('info')

  function setFlash(msg: string, msgType: 'success' | 'error' | 'info' = 'info') {
    message.value = msg
    type.value = msgType
    // Optionally auto-hide after a few seconds
    setTimeout(() => {
      message.value = ''
    }, 4000)
  }

  return { message, type, setFlash }
})