<template>
  <div class="flex-grow-1 p-4">
    <div class="container-fluid">
      <div class="row mb-4">
        <div class="col-12">
          <div class="card bg-gradient-primary text-white">
            <div class="card-body">
              <h1 class="card-title mb-2">🛡️ Admin Dashboard</h1>
              <p class="card-text">Welcome back, Administrator! Monitor system analytics and user activities from here.</p>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-lg-2 col-md-4 mb-3">
          <div class="card bg-primary text-white">
            <div class="card-body text-center">
              <div class="card-icon">👥</div>
              <h3>{{ stats.total_users }}</h3>
              <p class="mb-0">Total Users</p>
            </div>
          </div>
        </div>
        <div class="col-lg-2 col-md-4 mb-3">
          <div class="card bg-success text-white">
            <div class="card-body text-center">
              <div class="card-icon">📝</div>
              <h3>{{ stats.total_quizzes }}</h3>
              <p class="mb-0">Total Quizzes</p>
            </div>
          </div>
        </div>
        <div class="col-lg-2 col-md-4 mb-3">
          <div class="card bg-info text-white">
            <div class="card-body text-center">
              <div class="card-icon">📚</div>
              <h3>{{ stats.total_subjects }}</h3>
              <p class="mb-0">Subjects</p>
            </div>
          </div>
        </div>
        <div class="col-lg-2 col-md-4 mb-3">
          <div class="card bg-warning text-white">
            <div class="card-body text-center">
              <div class="card-icon">📖</div>
              <h3>{{ stats.total_chapters }}</h3>
              <p class="mb-0">Chapters</p>
            </div>
          </div>
        </div>
        <div class="col-lg-2 col-md-4 mb-3">
          <div class="card bg-danger text-white">
            <div class="card-body text-center">
              <div class="card-icon">❓</div>
              <h3>{{ stats.total_questions }}</h3>
              <p class="mb-0">Questions</p>
            </div>
          </div>
        </div>
        <div class="col-lg-2 col-md-4 mb-3">
          <div class="card bg-dark text-white">
            <div class="card-body text-center">
              <div class="card-icon">🎯</div>
              <h3>{{ stats.average_quiz_score }}%</h3>
              <p class="mb-0">Avg Score</p>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-lg-3 col-md-6 mb-3">
          <div class="card bg-gradient-success text-white">
            <div class="card-body text-center">
              <h4>{{ stats.total_quiz_attempts }}</h4>
              <p class="mb-0">Total Attempts</p>
              <small>All time quiz attempts</small>
            </div>
          </div>
        </div>
        <div class="col-lg-3 col-md-6 mb-3">
          <div class="card bg-gradient-primary text-white">
            <div class="card-body text-center">
              <h4>{{ stats.completed_attempts }}</h4>
              <p class="mb-0">Completed</p>
              <small>{{ stats.completion_rate }}% completion rate</small>
            </div>
          </div>
        </div>
        <div class="col-lg-3 col-md-6 mb-3">
          <div class="card bg-gradient-info text-white">
            <div class="card-body text-center">
              <h4>{{ stats.active_users }}</h4>
              <p class="mb-0">Active Users</p>
              <small>{{ stats.user_engagement_rate }}% engagement</small>
            </div>
          </div>
        </div>
        <div class="col-lg-3 col-md-6 mb-3">
          <div class="card bg-gradient-warning text-white">
            <div class="card-body text-center">
              <h4>{{ stats.recent_attempts_7d }}</h4>
              <p class="mb-0">This Week</p>
              <small>{{ stats.recent_completions_7d }} completed</small>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-12 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">📈 User Registration & Quiz Attempts Trend</h5>
            </div>
            <div class="card-body">
              <div class="chart-container">
                <Line 
                  v-if="userTrendChartData.datasets.length > 0"
                  :data="userTrendChartData" 
                  :options="userTrendChartOptions" 
                />
                <div v-else class="chart-loading">
                  <span>Loading trend data...</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-lg-6 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">📊 Subject-wise Quiz Distribution</h5>
            </div>
            <div class="card-body">
              <div class="chart-container">
                <Bar 
                  v-if="subjectDistributionChartData.datasets.length > 0"
                  :data="subjectDistributionChartData" 
                  :options="subjectDistributionChartOptions" 
                />
                <div v-else class="chart-loading">
                  <span>Loading subject data...</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-lg-6 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">🎯 Score Distribution Analysis</h5>
            </div>
            <div class="card-body">
              <div class="chart-container">
                <Pie 
                  v-if="scoreDistributionChartData.datasets.length > 0"
                  :data="scoreDistributionChartData" 
                  :options="scoreDistributionChartOptions" 
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
        <div class="col-12 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">📚 Subject-wise Performance Analysis</h5>
            </div>
            <div class="card-body">
              <div class="chart-container">
                <Bar 
                  v-if="subjectPerformanceChartData.datasets.length > 0"
                  :data="subjectPerformanceChartData" 
                  :options="subjectPerformanceChartOptions" 
                />
                <div v-else class="chart-loading">
                  <span>Loading performance data...</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-lg-8 mb-4">
          <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="card-title mb-0">🔄 Recent Quiz Attempts</h5>
              <button class="btn btn-sm btn-outline-primary" @click="loadRecentActivity">
                🔄 Refresh
              </button>
            </div>
            <div class="card-body">
              <div v-if="recentActivity.recentAttempts.length === 0" class="text-center py-4">
                <p class="text-muted">No recent quiz attempts found.</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>User</th>
                      <th>Quiz</th>
                      <th>Subject</th>
                      <th>Score</th>
                      <th>Status</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="attempt in recentActivity.recentAttempts.slice(0, 10)" :key="attempt.id">
                      <td>{{ attempt.userName }}</td>
                      <td>{{ attempt.quizName }}</td>
                      <td>{{ attempt.subject }}</td>
                      <td>
                        <span class="badge" :class="getScoreBadgeClass(attempt.score)">
                          {{ attempt.score }}%
                        </span>
                      </td>
                      <td>
                        <span class="badge" :class="getStatusBadgeClass(attempt.status)">
                          {{ getStatusText(attempt.status) }}
                        </span>
                      </td>
                      <td>{{ formatDate(attempt.startTime) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
        <div class="col-lg-4 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">👥 Recent User Registrations</h5>
            </div>
            <div class="card-body">
              <div v-if="recentActivity.recentUsers.length === 0" class="text-center py-4">
                <p class="text-muted">No recent registrations.</p>
              </div>
              <div v-else>
                <div v-for="user in recentActivity.recentUsers.slice(0, 8)" :key="user.id" class="user-item mb-3">
                  <div class="d-flex align-items-center">
                    <div class="user-avatar me-3">
                      <div class="avatar-circle">{{ user.name.charAt(0).toUpperCase() }}</div>
                    </div>
                    <div class="user-info flex-grow-1">
                      <h6 class="mb-1">{{ user.name }}</h6>
                      <small class="text-muted">{{ formatDate(user.registrationDate) }}</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-12">
          <div class="card">
            <div class="card-header bg-primary text-white">
              <h5 class="card-title mb-0">📧 Manual Notification Controls</h5>
              <small>Send notifications immediately to all users</small>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <div class="d-flex align-items-center">
                    <div class="me-3">
                      <i class="fas fa-bell text-warning" style="font-size: 2rem;"></i>
                    </div>
                    <div class="flex-grow-1">
                      <h6 class="mb-1">Send Daily Reminders</h6>
                      <small class="text-muted">Send daily quiz reminders to all active users immediately</small>
                    </div>
                    <button 
                      class="btn btn-warning btn-sm"
                      @click="sendDailyReminders"
                      :disabled="loading"
                    >
                      <i class="fas fa-paper-plane"></i> Send Now
                    </button>
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <div class="d-flex align-items-center">
                    <div class="me-3">
                      <i class="fas fa-chart-bar text-info" style="font-size: 2rem;"></i>
                    </div>
                    <div class="flex-grow-1">
                      <h6 class="mb-1">Send Monthly Reports</h6>
                      <small class="text-muted">Generate and send monthly activity reports to all users</small>
                    </div>
                    <button 
                      class="btn btn-info btn-sm"
                      @click="sendMonthlyReports"
                      :disabled="loading"
                    >
                      <i class="fas fa-file-alt"></i> Generate & Send
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-12">
          <div class="card">
            <div class="card-header bg-info text-white">
              <h5 class="card-title mb-0">📧 Recent Reminder Logs (Last 24 Hours)</h5>
              <small>Total: {{ reminderLogs.total_count || 0 }} | Sent: {{ reminderLogs.sent_count || 0 }} | Failed: {{ reminderLogs.failed_count || 0 }}</small>
            </div>
            <div class="card-body p-0">
              <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
                <table class="table table-striped table-hover mb-0">
                  <thead class="table-dark sticky-top">
                    <tr>
                      <th style="width: 180px;">Sent At</th>
                      <th style="width: 200px;">User</th>
                      <th style="width: 100px;">Channel</th>
                      <th style="width: 80px;">Status</th>
                      <th>Message Preview</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="reminderLogs.logs && reminderLogs.logs.length === 0">
                      <td colspan="5" class="text-center text-muted py-4">
                        <i class="fas fa-info-circle"></i> No reminder logs found in the last 24 hours
                      </td>
                    </tr>
                    <tr 
                      v-for="(log, index) in reminderLogs.logs" 
                      :key="index"
                      :class="{
                        'table-success': log.status === 'sent',
                        'table-danger': log.status === 'failed'
                      }"
                    >
                      <td class="text-nowrap small">{{ log.sent_at }}</td>
                      <td class="small">
                        <strong>{{ log.user_name }}</strong><br>
                        <small class="text-muted">{{ log.user_email }}</small>
                      </td>
                      <td class="small">{{ log.channel }}</td>
                      <td>
                        <span 
                          class="badge"
                          :class="{
                            'bg-success': log.status === 'sent',
                            'bg-danger': log.status === 'failed'
                          }"
                        >
                          {{ log.status.toUpperCase() }}
                        </span>
                      </td>
                      <td class="small">{{ log.message_preview }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div class="card-footer text-center bg-light">
                <button 
                  class="btn btn-outline-info btn-sm" 
                  @click="loadReminderLogs"
                  :disabled="loading"
                >
                  <i class="fas fa-refresh"></i> Refresh Logs
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-12">
          <div class="card">
            <div class="card-header bg-success text-white">
              <h5 class="card-title mb-0">📊 Report History ({{ reportHistory.month_year || 'Current Month' }})</h5>
              <small>Total: {{ reportHistory.total_count || 0 }} | Monthly: {{ reportHistory.monthly_reports_count || 0 }} | CSV: {{ reportHistory.csv_exports_count || 0 }} | Failed: {{ reportHistory.failed_count || 0 }}</small>
            </div>
            <div class="card-body p-0">
              <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
                <table class="table table-striped table-hover mb-0">
                  <thead class="table-dark sticky-top">
                    <tr>
                      <th style="width: 180px;">Created At</th>
                      <th style="width: 200px;">User</th>
                      <th style="width: 120px;">Report Type</th>
                      <th style="width: 100px;">Month</th>
                      <th style="width: 100px;">Status</th>
                      <th>File Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="reportHistory.reports && reportHistory.reports.length === 0">
                      <td colspan="6" class="text-center text-muted py-4">
                        <i class="fas fa-info-circle"></i> No report history found for this month
                      </td>
                    </tr>
                    <tr 
                      v-for="(report, index) in reportHistory.reports" 
                      :key="index"
                      :class="{
                        'table-success': report.status === 'sent' || report.status === 'completed',
                        'table-danger': report.status === 'failed',
                        'table-warning': report.status === 'pending' || report.status === 'processing'
                      }"
                    >
                      <td class="text-nowrap small">{{ report.created_at }}</td>
                      <td class="small">
                        <strong>{{ report.user_name }}</strong><br>
                        <small class="text-muted">{{ report.user_email }}</small>
                      </td>
                      <td class="small">
                        <span class="badge bg-secondary">{{ report.report_type.replace('_', ' ').toUpperCase() }}</span>
                      </td>
                      <td class="small">{{ report.month || 'N/A' }}</td>
                      <td>
                        <span 
                          class="badge"
                          :class="{
                            'bg-success': report.status === 'sent' || report.status === 'completed',
                            'bg-danger': report.status === 'failed',
                            'bg-warning text-dark': report.status === 'pending' || report.status === 'processing'
                          }"
                        >
                          {{ report.status.toUpperCase() }}
                        </span>
                      </td>
                      <td class="small">
                        <div v-if="report.filename">
                          <strong>{{ report.filename }}</strong>
                        </div>
                        <div v-if="report.error_message" class="text-danger">
                          <small>{{ report.error_message }}</small>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div class="card-footer text-center bg-light">
                <button 
                  class="btn btn-outline-success btn-sm" 
                  @click="loadReportHistory"
                  :disabled="loading"
                >
                  <i class="fas fa-refresh"></i> Refresh History
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-12">
          <div class="card">
            <div class="card-header bg-danger text-white">
              <h5 class="card-title mb-0">🚨 System Logs (Last 100 Warnings & Errors)</h5>
              <small>Total: {{ systemLogs.total_count || 0 }} | Errors: {{ systemLogs.error_count || 0 }} | Warnings: {{ systemLogs.warning_count || 0 }}</small>
            </div>
            <div class="card-body p-0">
              <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
                <table class="table table-striped table-hover mb-0">
                  <thead class="table-dark sticky-top">
                    <tr>
                      <th style="width: 180px;">Timestamp</th>
                      <th style="width: 80px;">Level</th>
                      <th style="width: 100px;">Logger</th>
                      <th>Message</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="systemLogs.logs && systemLogs.logs.length === 0">
                      <td colspan="4" class="text-center text-muted py-4">
                        <i class="fas fa-info-circle"></i> No warning or error logs found
                      </td>
                    </tr>
                    <tr 
                      v-for="(log, index) in systemLogs.logs" 
                      :key="index"
                      :class="{
                        'table-danger': log.level === 'ERROR',
                        'table-warning': log.level === 'WARNING'
                      }"
                    >
                      <td class="text-nowrap small">{{ log.timestamp }}</td>
                      <td>
                        <span 
                          class="badge"
                          :class="{
                            'bg-danger': log.level === 'ERROR',
                            'bg-warning text-dark': log.level === 'WARNING'
                          }"
                        >
                          {{ log.level }}
                        </span>
                      </td>
                      <td class="small">{{ log.logger }}</td>
                      <td class="small">{{ log.message }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div class="card-footer text-center bg-light">
                <button 
                  class="btn btn-outline-secondary btn-sm" 
                  @click="loadSystemLogs"
                  :disabled="loading"
                >
                  <i class="fas fa-refresh"></i> Refresh Logs
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="toast-container position-fixed bottom-0 end-0 p-3">
        <div 
          id="liveToast" 
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
import { Line, Bar, Pie } from 'vue-chartjs'

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

interface AdminStats {
  total_users: number
  total_quizzes: number
  total_subjects: number
  total_chapters: number
  total_questions: number
  total_quiz_attempts: number
  completed_attempts: number
  active_users: number
  average_quiz_score: number
  recent_attempts_7d: number
  recent_completions_7d: number
  completion_rate: number
  user_engagement_rate: number
}

interface ChartData {
  userRegistrations: Array<{date: string, count: number}>
  quizAttempts: Array<{date: string, count: number}>
  subjectQuizDistribution: Array<{subject: string, count: number}>
  scoreDistribution: Array<{range: string, count: number}>
  topUsers: Array<{name: string, avgScore: number, attempts: number}>
  subjectPerformance: Array<{subject: string, avgScore: number, attempts: number}>
}

interface RecentActivity {
  recentAttempts: Array<{
    id: number
    userName: string
    quizName: string
    subject: string
    score: number
    startTime: string
    endTime: string | null
    status: string
  }>
  recentUsers: Array<{
    id: number
    name: string
    email: string
    registrationDate: string
  }>
}

interface SystemLogs {
  logs: Array<{
    timestamp: string
    level: 'ERROR' | 'WARNING'
    logger: string
    message: string
    severity: 'high' | 'medium'
  }>
  total_count: number
  error_count: number
  warning_count: number
}

interface ReminderLogs {
  logs: Array<{
    id: number
    user_id: number
    user_name: string
    user_email: string
    sent_at: string
    channel: string
    status: string
    message_preview: string
  }>
  total_count: number
  sent_count: number
  failed_count: number
  time_range: string
}

interface ReportHistory {
  reports: Array<{
    id: number
    user_id: number
    user_name: string
    user_email: string
    report_type: string
    month: string
    status: string
    created_at: string
    filename: string
    file_path: string
    task_id: string
    error_message: string
  }>
  total_count: number
  monthly_reports_count: number
  csv_exports_count: number
  completed_count: number
  failed_count: number
  pending_count: number
  month_year: string
}

const stats = ref<AdminStats>({
  total_users: 0,
  total_quizzes: 0,
  total_subjects: 0,
  total_chapters: 0,
  total_questions: 0,
  total_quiz_attempts: 0,
  completed_attempts: 0,
  active_users: 0,
  average_quiz_score: 0,
  recent_attempts_7d: 0,
  recent_completions_7d: 0,
  completion_rate: 0,
  user_engagement_rate: 0
})

const chartData = ref<ChartData>({
  userRegistrations: [],
  quizAttempts: [],
  subjectQuizDistribution: [],
  scoreDistribution: [],
  topUsers: [],
  subjectPerformance: []
})

const recentActivity = ref<RecentActivity>({
  recentAttempts: [],
  recentUsers: []
})

const systemLogs = ref<SystemLogs>({
  logs: [],
  total_count: 0,
  error_count: 0,
  warning_count: 0
})

const reminderLogs = ref<ReminderLogs>({
  logs: [],
  total_count: 0,
  sent_count: 0,
  failed_count: 0,
  time_range: '24 hours'
})

const reportHistory = ref<ReportHistory>({
  reports: [],
  total_count: 0,
  monthly_reports_count: 0,
  csv_exports_count: 0,
  completed_count: 0,
  failed_count: 0,
  pending_count: 0,
  month_year: ''
})

const statusToast = ref<HTMLElement | null>(null)
const toastMessage = ref('')
const toastType = ref<'success' | 'error'>('success')
const loading = ref(false)

// Chart.js data structures
const userTrendChartData = ref({
  labels: [] as string[],
  datasets: [] as any[]
})

const subjectDistributionChartData = ref({
  labels: [] as string[],
  datasets: [] as any[]
})

const scoreDistributionChartData = ref({
  labels: [] as string[],
  datasets: [] as any[]
})

const subjectPerformanceChartData = ref({
  labels: [] as string[],
  datasets: [] as any[]
})

// Chart options
const userTrendChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    title: {
      display: false
    },
    legend: {
      position: 'top' as const
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: 'Count'
      }
    }
  }
})

const subjectDistributionChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: 'Number of Quizzes'
      }
    }
  }
})

const scoreDistributionChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right' as const
    }
  }
})

const subjectPerformanceChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
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

if (auth.userIsLoggedIn && auth.user?.token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${auth.user.token}`
}

const loadAdminStats = async () => {
  try {
    const response = await axios.get('/api/admin/dashboard/stats')
    
    if (response.data && response.data.success) {
      stats.value = response.data.data
      console.log('Admin dashboard stats loaded:', response.data.data)
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
    const response = await axios.get('/api/admin/dashboard/chart-data')
    if (response.data && response.data.success) {
      chartData.value = response.data.data
    } else {
      generateSampleChartData()
    }
    
    await nextTick()
    prepareChartData()
  } catch (error) {
    console.error('Chart data loading error:', error)
    // Generate sample data as fallback
    generateSampleChartData()
    await nextTick()
    prepareChartData()
  }
}

const loadRecentActivity = async () => {
  try {
    const response = await axios.get('/api/admin/dashboard/recent-activity')
    if (response.data && response.data.success) {
      recentActivity.value = response.data.data
    }
  } catch (error) {
    console.error('Recent activity loading error:', error)
    showToast('Failed to load recent activity', 'error')
  }
}

const loadSystemLogs = async () => {
  try {
    const response = await axios.get('/api/admin/dashboard/system-logs')
    if (response.data && response.data.success) {
      systemLogs.value = response.data.data
    }
  } catch (error) {
    console.error('System logs loading error:', error)
    showToast('Failed to load system logs', 'error')
  }
}

const loadReminderLogs = async () => {
  try {
    const response = await axios.get('/api/admin/dashboard/reminder-logs')
    if (response.data && response.data.success) {
      reminderLogs.value = response.data.data
    }
  } catch (error) {
    console.error('Reminder logs loading error:', error)
    showToast('Failed to load reminder logs', 'error')
  }
}

const loadReportHistory = async () => {
  try {
    const response = await axios.get('/api/admin/dashboard/report-history')
    if (response.data && response.data.success) {
      reportHistory.value = response.data.data
    }
  } catch (error) {
    console.error('Report history loading error:', error)
    showToast('Failed to load report history', 'error')
  }
}

const generateSampleChartData = () => {
  chartData.value = {
    userRegistrations: [
      {date: '2025-07-20', count: 5},
      {date: '2025-07-21', count: 8},
      {date: '2025-07-22', count: 12},
      {date: '2025-07-23', count: 7},
      {date: '2025-07-24', count: 15},
      {date: '2025-07-25', count: 10},
      {date: '2025-07-26', count: 6}
    ],
    quizAttempts: [
      {date: '2025-07-20', count: 25},
      {date: '2025-07-21', count: 32},
      {date: '2025-07-22', count: 18},
      {date: '2025-07-23', count: 41},
      {date: '2025-07-24', count: 35},
      {date: '2025-07-25', count: 28},
      {date: '2025-07-26', count: 22}
    ],
    subjectQuizDistribution: [
      {subject: 'English I', count: 5},
      {subject: 'English II', count: 2},
      {subject: 'Computational Thinking', count: 1}
    ],
    scoreDistribution: [
      {range: '0-20', count: 2},
      {range: '21-40', count: 5},
      {range: '41-60', count: 12},
      {range: '61-80', count: 18},
      {range: '81-100', count: 15}
    ],
    topUsers: [
      {name: 'John Doe', avgScore: 92.5, attempts: 8},
      {name: 'Jane Smith', avgScore: 89.3, attempts: 6},
      {name: 'Bob Johnson', avgScore: 87.1, attempts: 5}
    ],
    subjectPerformance: [
      {subject: 'Mathematics', avgScore: 78.5, attempts: 45},
      {subject: 'Science', avgScore: 82.3, attempts: 38},
      {subject: 'History', avgScore: 75.8, attempts: 32},
      {subject: 'English', avgScore: 80.2, attempts: 28},
      {subject: 'Physics', avgScore: 85.1, attempts: 22}
    ]
  }
}

const prepareChartData = () => {
  prepareUserTrendChartData()
  prepareSubjectDistributionChartData() 
  prepareScoreDistributionChartData()
  prepareSubjectPerformanceChartData()
}

const prepareUserTrendChartData = () => {
  const registrations = chartData.value.userRegistrations
  const attempts = chartData.value.quizAttempts
  
  const allDates = [...new Set([
    ...registrations.map(r => r.date),
    ...attempts.map(a => a.date)
  ])].sort()
  
  userTrendChartData.value = {
    labels: allDates.map(date => new Date(date).toLocaleDateString()),
    datasets: [
      {
        label: 'User Registrations',
        data: allDates.map(date => {
          const reg = registrations.find(r => r.date === date)
          return reg ? reg.count : 0
        }),
        borderColor: '#10b981',
        backgroundColor: '#10b98120',
        fill: false,
        tension: 0.4
      },
      {
        label: 'Quiz Attempts',
        data: allDates.map(date => {
          const att = attempts.find(a => a.date === date)
          return att ? att.count : 0
        }),
        borderColor: '#3b82f6',
        backgroundColor: '#3b82f620',
        fill: false,
        tension: 0.4
      }
    ]
  }
}

const prepareSubjectDistributionChartData = () => {
  const data = chartData.value.subjectQuizDistribution
  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
  
  subjectDistributionChartData.value = {
    labels: data.map(item => item.subject),
    datasets: [{
      label: 'Number of Quizzes',
      data: data.map(item => item.count),
      backgroundColor: colors.slice(0, data.length),
      borderColor: '#ffffff',
      borderWidth: 1
    }]
  }
}

const prepareScoreDistributionChartData = () => {
  const data = chartData.value.scoreDistribution
  const colors = ['#ef4444', '#f59e0b', '#eab308', '#22c55e', '#10b981']
  
  scoreDistributionChartData.value = {
    labels: data.map(item => item.range),
    datasets: [{
      data: data.map(item => item.count),
      backgroundColor: colors.slice(0, data.length),
      borderColor: '#ffffff',
      borderWidth: 2
    }]
  }
}

const prepareSubjectPerformanceChartData = () => {
  const data = chartData.value.subjectPerformance
  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
  
  subjectPerformanceChartData.value = {
    labels: data.map(item => item.subject),
    datasets: [{
      label: 'Average Score (%)',
      data: data.map(item => item.avgScore),
      backgroundColor: colors.slice(0, data.length),
      borderColor: '#ffffff',
      borderWidth: 1
    }]
  }
}

const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const getScoreBadgeClass = (score: number) => {
  if (score >= 80) return 'bg-success'
  if (score >= 60) return 'bg-warning'
  return 'bg-danger'
}

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'completed': return 'bg-success'
    case 'in_progress': return 'bg-warning'
    default: return 'bg-secondary'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'completed': return '✅ Completed'
    case 'in_progress': return '⏳ In Progress'
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

const sendDailyReminders = async () => {
  loading.value = true
  try {
    const response = await axios.post('/api/admin/notifications/send-daily-reminders')
    if (response.data && response.data.success) {
      showToast(response.data.message || 'Daily reminders sent successfully!', 'success')
    } else {
      showToast(response.data.error_message || 'Failed to send daily reminders', 'error')
    }
  } catch (error: any) {
    console.error('Daily reminders error:', error)
    showToast('Failed to send daily reminders: ' + (error.response?.data?.message || error.message), 'error')
  } finally {
    loading.value = false
  }
}

const sendMonthlyReports = async () => {
  loading.value = true
  try {
    const response = await axios.post('/api/admin/notifications/send-monthly-reports')
    if (response.data && response.data.success) {
      showToast(response.data.message || 'Monthly reports generated and sent successfully!', 'success')
    } else {
      showToast(response.data.error_message || 'Failed to send monthly reports', 'error')
    }
  } catch (error: any) {
    console.error('Monthly reports error:', error)
    showToast('Failed to send monthly reports: ' + (error.response?.data?.message || error.message), 'error')
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(async () => {
  await loadAdminStats()
  await loadChartData()
  await loadRecentActivity()
  await loadReminderLogs()
  await loadReportHistory()
  await loadSystemLogs()
})
</script>

<style scoped>
.card {
  border: none;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
}

.bg-gradient-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.bg-gradient-success {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.bg-gradient-info {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.bg-gradient-warning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

/* Card icons */
.card-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  opacity: 0.8;
}

.card-body h3, .card-body h4 {
  font-weight: 700;
  margin: 0.5rem 0;
}

.card-body small {
  opacity: 0.8;
  font-size: 0.75rem;
}

.chart-container {
  position: relative;
  height: 350px;
  padding: 20px;
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
  width: 24px;
  height: 24px;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Enhanced card styling for charts */
.card:has(.chart-container) .card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom: none;
}

.card:has(.chart-container) .card-header h5 {
  margin: 0;
  font-weight: 600;
  font-size: 1rem;
}

.table {
  font-size: 0.9rem;
}

.table th {
  border-top: none;
  font-weight: 600;
  background-color: #f8f9fa;
  color: #495057;
}

.table td {
  vertical-align: middle;
}

.badge {
  font-size: 0.75rem;
  padding: 0.4rem 0.6rem;
}

.user-item {
  padding: 0.75rem 0;
  border-bottom: 1px solid #e9ecef;
}

.user-item:last-child {
  border-bottom: none;
}

.user-avatar {
  flex-shrink: 0;
}

.avatar-circle {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.1rem;
}

.user-info h6 {
  margin: 0;
  font-weight: 600;
  color: #495057;
}

.user-info small {
  font-size: 0.75rem;
  color: #6c757d;
}

@media (max-width: 768px) {
  .chart-container {
    height: 280px;
    padding: 15px;
  }
  
  .card-body h3, .card-body h4 {
    font-size: 1.5rem;
  }
  
  .card-icon {
    font-size: 1.5rem;
  }
}

@media (max-width: 576px) {
  .chart-container {
    height: 250px;
    padding: 10px;
  }
  
  .card-body {
    padding: 1rem;
  }
  
  .table {
    font-size: 0.8rem;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card {
  animation: fadeInUp 0.6s ease-out;
}

/* Chart animation */
.chart-container > * {
  animation: fadeInChart 0.8s ease-out;
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

.btn {
  transition: all 0.2s ease;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.toast {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.table-responsive::-webkit-scrollbar {
  height: 6px;
}

.table-responsive::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.table-responsive::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.table-responsive::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>