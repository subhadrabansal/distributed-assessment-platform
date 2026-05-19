<template>
      <div class="flex-grow-1 p-4">
    <div class="card mx-auto p-4" style="max-width: 500px;">
  <div class="settings-page">
    <h2>Admin Notification Settings</h2>
    <form v-if="settings" @submit.prevent="updateAllSettings">
      <fieldset class="setting-block">
        <legend>Daily Reminder</legend>
        <label>Reminder Time:
          <input type="time" v-model="settings.daily_reminder.reminder_time" />
        </label>
        <label>Channel:
          <select v-model="settings.daily_reminder.reminder_channel">
            <option value="email">Email</option>
            
          </select>
        </label>
      </fieldset>
      <fieldset class="setting-block">
        <legend>Monthly Activity Report</legend>
        <label>Report Day of Month:
          <input type="number" min="1" max="31" v-model.number="settings.monthly_report.report_day_of_month" />
        </label>
        <label>Report Format:
          <select v-model="settings.monthly_report.report_format">
            <option value="html">HTML</option>

          </select>
        </label>
        <label>Channel:
          <select v-model="settings.monthly_report.report_channel">
            <option value="email">Email</option>

          </select>
        </label>
        <label>Report Time:
          <input type="time" v-model="settings.monthly_report.reminder_time" />
        </label>
      </fieldset>
      <button type="submit">Update All Settings</button>
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
  const res = await axios.get('/admin/settings')
  if (res.data.success && res.data.data) {
    settings.value = res.data.data
  }
}

const updateAllSettings = async () => {
  error.value = ''
  success.value = false
  try {

    const daily = axios.put(`/admin/settings/daily_reminder`, settings.value.daily_reminder)
    const monthly = axios.put(`/admin/settings/monthly_report`, settings.value.monthly_report)
    const [res1, res2] = await Promise.all([daily, monthly])
    if (res1.data.success && res2.data.success) {
      success.value = true
      setTimeout(() => (success.value = false), 2000)
    } else {
      error.value = (res1.data.error_message || res2.data.error_message || 'Update failed.')
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
.setting-block {
  border: 1px solid #ccc;
  padding: 1em;
  margin-bottom: 1em;
  border-radius: 8px;
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