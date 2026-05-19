<template>
  <div class="flex-grow-1 p-4">
    <div class="card mx-auto p-4" style="max-width: 500px;">
  <div class="settings-page">
    <h2>User Notification Settings</h2>
    <form v-if="settings" @submit.prevent="updateSettings">
      <label>Reminder Time:
        <input type="time" v-model="settings.reminder_time" />
      </label>
      <label>Channel:
        <select v-model="settings.reminder_channel">
          <option value="email">Email</option>
        </select>
      </label>
      <label>Report Format:
        <select v-model="settings.report_format">
          <option value="html">HTML</option>

        </select>
      </label>
      <!-- <label>
        <input type="checkbox" v-model="settings.receive_weekly" /> Receive Weekly Reports
      </label> -->
      <label>
        <input type="checkbox" v-model="settings.receive_monthly" /> Receive Monthly Reports
      </label>
      <button type="submit">Update Settings</button>
      <span v-if="success" class="success">Updated!</span>
      <span v-if="error" class="error">{{ error }}</span>
    </form>
    <div v-else>Loading...</div>
  </div>
  </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '../../axios'

const settings = ref(null)
const success = ref(false)
const error = ref('')

const fetchSettings = async () => {
  const res = await axios.get('/user/settings')
  if (res.data.success && res.data.data) {
    settings.value = res.data.data
  }
}

const updateSettings = async () => {
  error.value = ''
  success.value = false
  try {
    const res = await axios.put('/user/settings', settings.value)
    if (res.data.success) {
      success.value = true
      setTimeout(() => (success.value = false), 2000)
    } else {
      error.value = res.data.error_message || 'Update failed.'
    }
  } catch (e) {
    error.value = 'Update failed.'
  }
}

onMounted(fetchSettings)
</script>

<style scoped>
.settings-page {
  max-width: 600px;
  margin: 0 auto;
}
label {
  display: block;
  margin-bottom: 0.5em;
}
button {
  margin-top: 0.5em;
}
.success {
  color: green;
  margin-left: 1em;
}
.error {
  color: red;
  margin-left: 1em;
}
</style>