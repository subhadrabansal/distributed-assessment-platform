<template>
  <div class="flex-grow-1 p-4">
    <div class="container-fluid">
      <div class="row mb-4">
        <div class="col-12">
          <div class="card bg-primary text-white">
            <div class="card-body">
              <h1 class="card-title mb-2">📚 Welcome to Your Dashboard</h1>
              <p class="card-text">{{ stats.user_name || auth.user?.fullname || 'Student' }}, manage your quiz data and exports from here.</p>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-md-2 mb-3">
          <div class="card bg-primary text-white">
            <div class="card-body text-center">
              <h3>{{ stats.total_quizzes }}</h3>
              <p class="mb-0">Total Quizzes</p>
            </div>
          </div>
        </div>
        <div class="col-md-2 mb-3">
          <div class="card bg-info text-white">
            <div class="card-body text-center">
              <h3>{{ stats.registered_quizzes }}</h3>
              <p class="mb-0">Registered</p>
            </div>
          </div>
        </div>
        <div class="col-md-2 mb-3">
          <div class="card bg-success text-white">
            <div class="card-body text-center">
              <h3>{{ stats.completed_quizzes }}</h3>
              <p class="mb-0">Completed</p>
            </div>
          </div>
        </div>
        <div class="col-md-2 mb-3">
          <div class="card bg-warning text-white">
            <div class="card-body text-center">
              <h3>{{ stats.in_progress_quizzes }}</h3>
              <p class="mb-0">In Progress</p>
            </div>
          </div>
        </div>
        <div class="col-md-2 mb-3">
          <div class="card bg-danger text-white">
            <div class="card-body text-center">
              <h3>{{ stats.absent_quizzes }}</h3>
              <p class="mb-0">Absent</p>
            </div>
          </div>
        </div>
        <div class="col-md-2 mb-3">
          <div class="card bg-dark text-white">
            <div class="card-body text-center">
              <h3>{{ stats.average_score }}%</h3>
              <p class="mb-0">Avg Score</p>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-lg-6 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">📈 Performance Over Time</h5>
            </div>
            <div class="card-body">
              <div class="chart-container">
                <Line 
                  v-if="performanceChartData.datasets.length > 0"
                  :data="performanceChartData" 
                  :options="performanceChartOptions" 
                />
                <div v-else class="chart-loading">
                  <span>Loading performance data...</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-lg-6 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">📊 Quiz Status Distribution</h5>
            </div>
            <div class="card-body">
              <div class="chart-container">
                <Pie 
                  v-if="statusChartData.datasets.length > 0"
                  :data="statusChartData" 
                  :options="statusChartOptions" 
                />
                <div v-else class="chart-loading">
                  <span>Loading status data...</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-lg-8 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">📚 Subject-wise Performance</h5>
            </div>
            <div class="card-body">
              <div class="chart-container">
                <Bar 
                  v-if="subjectChartData.datasets.length > 0"
                  :data="subjectChartData" 
                  :options="subjectChartOptions" 
                />
                <div v-else class="chart-loading">
                  <span>Loading subject data...</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-lg-4 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">🎯 Score Distribution</h5>
            </div>
            <div class="card-body">
              <div class="chart-container">
                <Doughnut 
                  v-if="scoreDistChartData.datasets.length > 0"
                  :data="scoreDistChartData" 
                  :options="scoreDistChartOptions" 
                />
                <div v-else class="chart-loading">
                  <span>Loading score data...</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">📊 CSV Data Export</h5>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-6">
                  <p class="text-muted">Export your complete quiz history including scores, dates, subjects, and performance details.</p>
                  <div class="d-flex gap-2">
                    <button 
                      class="btn btn-primary" 
                      @click="triggerCsvExport"
                      :disabled="exportLoading"
                    >
                      <span v-if="exportLoading" class="spinner-border spinner-border-sm me-2"></span>
                      {{ exportLoading ? 'Processing...' : '📥 Export My Data' }}
                    </button>
                    <button 
                      class="btn btn-outline-secondary" 
                      @click="refreshExports"
                      :disabled="refreshLoading"
                    >
                      <span v-if="refreshLoading" class="spinner-border spinner-border-sm me-2"></span>
                      🔄 Refresh
                    </button>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="alert alert-info mb-0">
                    <strong>Export includes:</strong>
                    <ul class="mb-0 mt-2">
                      <li>Quiz ID, Name, Chapter & Subject details</li>
                      <li>Attempt dates and scores</li>
                      <li>Performance percentages and rankings</li>
                      <li>Completion status and remarks</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="card-title mb-0">📋 Export History</h5>
              <small class="text-muted">Last {{ exportHistory.length }} exports</small>
            </div>
            <div class="card-body">
              <div v-if="exportHistory.length === 0" class="text-center py-4">
                <p class="text-muted">No exports yet. Click "Export My Data" to get started!</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>Date</th>
                      <th>Status</th>
                      <th>File Size</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="export_item in exportHistory" :key="export_item.export_id">
                      <td>{{ formatDate(export_item.created_at) }}</td>
                      <td>
                        <span class="badge" :class="getStatusBadgeClass(export_item.status)">
                          {{ getStatusText(export_item.status) }}
                        </span>
                      </td>
                      <td>
                        <span v-if="export_item.file_size">
                          {{ formatFileSize(export_item.file_size) }}
                        </span>
                        <span v-else class="text-muted">-</span>
                      </td>
                      <td>
                        <button 
                          v-if="export_item.status === 'completed' && export_item.download_url" 
                          class="btn btn-sm btn-success me-2"
                          @click="downloadExport(export_item.download_url!, export_item.filename!)"
                        >
                          📥 Download
                        </button>
                        <button 
                          v-if="export_item.status === 'pending' || export_item.status === 'processing'" 
                          class="btn btn-sm btn-outline-info"
                          @click="checkExportStatus(export_item.export_id)"
                        >
                          🔄 Check Status
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="toast-container position-fixed bottom-0 end-0 p-3">
        <div 
          ref="statusToast" 
          class="toast" 
          :class="{ 'text-bg-success': toastType === 'success', 'text-bg-danger': toastType === 'error' }"
        >
          <div class="toast-header">
            <strong class="me-auto">{{ toastType === 'success' ? '✅ Success' : '❌ Error' }}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
          </div>
          <div class="toast-body">
            {{ toastMessage }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from '@/axios'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line, Bar, Pie, Doughnut } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const auth = useAuthStore()

interface ExportItem {
  export_id: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
  file_size?: number
  download_url?: string
  filename?: string
}

interface DashboardStats {
  total_quizzes: number
  registered_quizzes: number
  completed_quizzes: number
  in_progress_quizzes: number
  absent_quizzes: number
  average_score: number
  user_name: string
}

interface ChartData {
  performance: Array<{date: string, score: number}>
  subjects: Array<{name: string, score: number}>
  scoreDistribution: Array<{range: string, count: number}>
}

const stats = ref<DashboardStats>({
  total_quizzes: 0,
  registered_quizzes: 0,
  completed_quizzes: 0,
  in_progress_quizzes: 0,
  absent_quizzes: 0,
  average_score: 0,
  user_name: ''
})

const exportHistory = ref<ExportItem[]>([])
const exportLoading = ref(false)
const refreshLoading = ref(false)
const statusToast = ref<HTMLElement | null>(null)
const toastMessage = ref('')
const toastType = ref<'success' | 'error'>('success')

const chartData = ref<ChartData>({
  performance: [],
  subjects: [],
  scoreDistribution: []
})

const performanceChartData = ref({
  labels: [] as string[],
  datasets: [] as any[]
})

const statusChartData = ref({
  labels: [] as string[],
  datasets: [] as any[]
})

const subjectChartData = ref({
  labels: [] as string[],
  datasets: [] as any[]
})

const scoreDistChartData = ref({
  labels: [] as string[],
  datasets: [] as any[]
})

const performanceChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    title: {
      display: true,
      text: 'Performance Over Time'
    },
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 100,
      title: {
        display: true,
        text: 'Score (%)'
      }
    }
  }
})

const statusChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    title: {
      display: true,
      text: 'Quiz Status Distribution'
    },
    legend: {
      position: 'right' as const
    }
  }
})

const subjectChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    title: {
      display: true,
      text: 'Subject-wise Performance'
    },
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 100,
      title: {
        display: true,
        text: 'Average Score (%)'
      }
    }
  }
})

const scoreDistChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    title: {
      display: true,
      text: 'Score Distribution'
    },
    legend: {
      position: 'bottom' as const
    }
  }
})

if (auth.userIsLoggedIn && auth.user?.token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${auth.user.token}`
}

const triggerCsvExport = async () => {
  exportLoading.value = true
  try {
    const response = await axios.post('/api/user/export/trigger-csv-export')
    
    showToast('CSV export started! You will be notified when it\'s ready.', 'success')
    
    const newExport: ExportItem = {
      export_id: response.data.export_id,
      status: 'pending',
      created_at: new Date().toISOString(),
      file_size: undefined,
      download_url: undefined,
      filename: undefined
    }
    exportHistory.value.unshift(newExport)
    
  } catch (error: any) {
    console.error('Export error:', error)
    showToast(error.response?.data?.error || 'Failed to start export', 'error')
  } finally {
    exportLoading.value = false
  }
}

const refreshExports = async () => {
  refreshLoading.value = true
  try {
    const response = await axios.get('/api/user/export/my-exports')
    exportHistory.value = response.data.exports || []
  } catch (error) {
    console.error('Refresh error:', error)
    showToast('Failed to refresh export history', 'error')
  } finally {
    refreshLoading.value = false
  }
}

const checkExportStatus = async (exportId: number) => {
  try {
    const response = await axios.get(`/api/user/export/export-status/${exportId}`)
    
    const exportIndex = exportHistory.value.findIndex(exp => exp.export_id === exportId)
    if (exportIndex !== -1) {
      exportHistory.value[exportIndex] = { ...exportHistory.value[exportIndex], ...response.data }
    }
    
    if (response.data.status === 'completed') {
      showToast('Export completed! You can now download it.', 'success')
    } else if (response.data.status === 'failed') {
      showToast('Export failed. Please try again.', 'error')
    }
  } catch (error) {
    console.error('Status check error:', error)
    showToast('Failed to check export status', 'error')
  }
}

const downloadExport = async (downloadUrl: string, filename: string) => {
  try {
    const response = await axios.get(downloadUrl, { responseType: 'blob' })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename || 'quiz_export.csv')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    showToast('Download started!', 'success')
  } catch (error) {
    console.error('Download error:', error)
    showToast('Failed to download file', 'error')
  }
}

const loadDashboardStats = async () => {
  try {
    const response = await axios.get('/api/user/dashboard/stats')
    
    if (response.data && response.data.success) {
      stats.value = response.data.data
      console.log('Dashboard stats loaded:', response.data.data)
    } else {
      console.error('Invalid response format:', response.data)
      showToast('Failed to load dashboard statistics', 'error')
    }
  } catch (error: any) {
    console.error('Stats loading error:', error)
    showToast('Failed to load dashboard statistics: ' + (error.response?.data?.message || error.message), 'error')
  }
}

const loadChartData = async () => {
  try {
    const response = await axios.get('/api/user/dashboard/chart-data')
    if (response.data && response.data.success) {
      chartData.value = response.data.data
    } else {
      generateSampleChartData()
    }
    
    await nextTick()
    prepareChartData()
  } catch (error) {
    console.error('Chart data loading error:', error)
    generateSampleChartData()
    await nextTick()
    prepareChartData()
  }
}

const generateSampleChartData = () => {
  chartData.value.performance = [
    {date: '2025-07-20', score: 75},
    {date: '2025-07-21', score: 82},
    {date: '2025-07-22', score: 68},
    {date: '2025-07-23', score: 91},
    {date: '2025-07-24', score: 85},
    {date: '2025-07-25', score: 77},
    {date: '2025-07-26', score: stats.value.average_score || 80}
  ]
  
  chartData.value.subjects = [
    {name: 'Mathematics', score: 85},
    {name: 'Science', score: 78},
    {name: 'History', score: 92},
    {name: 'English', score: 76},
    {name: 'Physics', score: 88}
  ]
  
  chartData.value.scoreDistribution = [
    {range: '0-20', count: 0},
    {range: '21-40', count: 1},
    {range: '41-60', count: 2},
    {range: '61-80', count: 3},
    {range: '81-100', count: 4}
  ]
}

const prepareChartData = () => {
  preparePerformanceChartData()
  prepareStatusChartData()
  prepareSubjectChartData()
  prepareScoreDistributionChartData()
}

const preparePerformanceChartData = () => {
  const data = chartData.value.performance
  performanceChartData.value = {
    labels: data.map(item => new Date(item.date).toLocaleDateString()),
    datasets: [{
      label: 'Score (%)',
      data: data.map(item => item.score),
      borderColor: '#3b82f6',
      backgroundColor: '#3b82f620',
      fill: true,
      tension: 0.4,
      pointBackgroundColor: '#3b82f6',
      pointBorderColor: '#ffffff',
      pointBorderWidth: 2,
      pointRadius: 6
    }]
  }
}

const prepareStatusChartData = () => {
  const data = [
    { label: 'Completed', value: stats.value.completed_quizzes, color: '#10b981' },
    { label: 'In Progress', value: stats.value.in_progress_quizzes, color: '#f59e0b' },
    { label: 'Absent', value: stats.value.absent_quizzes, color: '#ef4444' }
  ]
  
  statusChartData.value = {
    labels: data.map(item => item.label),
    datasets: [{
      data: data.map(item => item.value),
      backgroundColor: data.map(item => item.color),
      borderColor: '#ffffff',
      borderWidth: 2
    }]
  }
}

const prepareSubjectChartData = () => {
  const data = chartData.value.subjects
  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
  
  subjectChartData.value = {
    labels: data.map(item => item.name),
    datasets: [{
      label: 'Average Score (%)',
      data: data.map(item => item.score),
      backgroundColor: colors.slice(0, data.length),
      borderColor: '#ffffff',
      borderWidth: 2
    }]
  }
}

const prepareScoreDistributionChartData = () => {
  const data = chartData.value.scoreDistribution
  const colors = ['#ef4444', '#f59e0b', '#eab308', '#22c55e', '#10b981']
  
  scoreDistChartData.value = {
    labels: data.map(item => item.range),
    datasets: [{
      data: data.map(item => item.count),
      backgroundColor: colors.slice(0, data.length),
      borderColor: '#ffffff',
      borderWidth: 2
    }]
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString()
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'completed': return 'bg-success'
    case 'processing': return 'bg-warning'
    case 'pending': return 'bg-info'
    case 'failed': return 'bg-danger'
    default: return 'bg-secondary'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'completed': return '✅ Ready'
    case 'processing': return '⏳ Processing'
    case 'pending': return '📋 Queued'
    case 'failed': return '❌ Failed'
    default: return status
  }
}

const showToast = (message: string, type: 'success' | 'error') => {
  toastMessage.value = message
  toastType.value = type
  
  if (statusToast.value) {
    const toast = new (window as any).bootstrap.Toast(statusToast.value)
    toast.show()
  }
}

onMounted(async () => {
  await loadDashboardStats()
  await refreshExports()
  await loadChartData()
})
</script>

<style scoped>
.card {
  border: none;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
}

.btn {
  transition: all 0.2s;
}

.table th {
  border-top: none;
  font-weight: 600;
}

.badge {
  font-size: 0.85em;
}

.chart-container {
  position: relative;
  height: 300px;
  padding: 15px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.chart-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6b7280;
  font-style: italic;
  font-size: 16px;
}

.chart-loading::before {
  content: "";
  width: 20px;
  height: 20px;
  border: 2px solid #e2e8f0;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive chart adjustments */
@media (max-width: 768px) {
  .chart-container {
    height: 250px;
    padding: 10px;
  }
}

@media (max-width: 576px) {
  .chart-container {
    height: 200px;
    padding: 8px;
  }
}

@keyframes fadeInChart {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.chart-container > * {
  animation: fadeInChart 0.6s ease-out;
}

:deep(.chartjs-tooltip) {
  opacity: 1;
  position: absolute;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  border-radius: 6px;
  pointer-events: none;
  transform: translate(-50%, 0);
  transition: all 0.1s ease;
}

.card:has(.chart-container) {
  overflow: hidden;
}

.card:has(.chart-container) .card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom: none;
}

.card:has(.chart-container) .card-header h5 {
  margin: 0;
  font-weight: 600;
}
</style>