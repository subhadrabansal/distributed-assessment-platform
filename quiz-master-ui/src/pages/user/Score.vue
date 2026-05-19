<template>
  <div class="certificate-main">
    <div class="certificate-card" ref="certificateRef">
      <div class="certificate-header">
        <div class="certificate-title">Distributed Assessment Platform</div>
        <img :src="userPic" alt="User Pic" class="certificate-user-pic" />
        <div class="certificate-name">{{ user.name }}</div>
      </div>
      <div class="certificate-body">
        <div class="certificate-desc">
          You have finished the quiz <b>{{ quiz.name }}</b>. Your Performance Summary:
        </div>
        <div class="certificate-summary-row">
          <div class="certificate-summary-col">
            <div><b>Subject:</b> <span>{{ quiz.subject_name }}</span></div>
            <div><b>Total Questions:</b> <span>{{ score.total_questions }}</span></div>
            <div><b>Total Marks:</b> <span>{{ quiz.total_marks }}</span></div>
            <div><b>Date:</b> <span>{{ score.date }}</span></div>
          </div>
          <div class="certificate-summary-col">
            <div><b>Chapter:</b> <span>{{ quiz.chapter_name }}</span></div>
            <div><b>Attempted Questions:</b> <span>{{ score.attempted_questions }}</span></div>
            <div><b>Score:</b> <span>{{ score.total_score }}</span></div>
            <div><b>Time:</b> <span>{{ score.time }}</span></div>
          </div>
          <div class="certificate-summary-col">
            <div><b>Unattempted Questions:</b> <span>{{ score.unattempted_questions }}</span></div>
            <div><b>Grade:</b> <span>{{ grade }}</span></div>
          </div>
        </div>
      </div>
      <div class="certificate-footer">
        <div class="certificate-signature-block">
          <div class="certificate-signature-label">Authorized By</div>
          <div class="certificate-signature">Distributed Assessment Platform</div>
        </div>
        <button class="btn btn-primary certificate-download-btn" @click="downloadScore">Download Certificate</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/axios'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import dummyUserPic from '@/assets/dummy-user.jpg'

function getProfilePicUrl(pic: string | undefined) {
  if (!pic) return dummyUserPic
  if (pic.startsWith('http')) return pic
  const base = axios.defaults.baseURL || ''
  if (pic.startsWith('/static/')) return base + pic
  if (pic.startsWith('static/')) return base + '/' + pic
  if (pic.startsWith('profile_pics/')) return base + '/static/' + pic
  return base + '/static/profile_pics/' + pic
}

const router = useRouter()
const quizId = Number(localStorage.getItem('last_quiz_id'))
const user = ref({ name: '', pic: '', email: '' })
const userEmail = ref('')
const quiz = ref({ name: '', subject_name: '', chapter_name: '', total_marks: 0 })
const score = ref({ total_questions: 0, attempted_questions: 0, unattempted_questions: 0, total_score: 0, date: '', time: '' })
const grade = ref('')
const certificateRef = ref<HTMLElement | null>(null)

const userPic = computed(() => getProfilePicUrl(user.value.pic))

function calculateGrade(score: number, total: number) {
  if (total === 0) return 'F'
  const percent = (score / total) * 100
  if (percent >= 90) return 'A+'
  if (percent >= 80) return 'A'
  if (percent >= 70) return 'B'
  if (percent >= 60) return 'C'
  if (percent >= 50) return 'D'
  return 'F'
}

function downloadScore() {
  const cert = certificateRef.value
  if (!cert) return
  const img = cert.querySelector('.certificate-user-pic') as HTMLImageElement
  if (img && !img.complete) {
    img.onload = () => downloadScore()
    return
  }
  const downloadBtn = cert.querySelector('.certificate-download-btn') as HTMLElement
  if (downloadBtn) downloadBtn.style.display = 'none'
  html2canvas(cert, { scale: 2, useCORS: true, allowTaint: true }).then(canvas => {
    if (downloadBtn) downloadBtn.style.display = ''
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF({ unit: 'mm', format: [297, 210], orientation: 'landscape' })
    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    pdf.addImage(imgData, 'PNG', 0, 0, pageWidth, pageHeight)
    pdf.save('quiz_certificate.pdf')
  })
}

onMounted(async () => {
  if (!quizId) {
    router.replace('/')
    return
  }
  const res = await axios.post('/user/quiz/score', { quiz_id: quizId })
  const data = res.data.data
  user.value = {
    name: data.user.name || '',
    pic: data.user.pic || '',
    email: data.user.email || ''
  }
  userEmail.value = user.value.email || ''
  quiz.value = data.quiz
  score.value = data.score
  grade.value = calculateGrade(score.value.total_score, quiz.value.total_marks)
})
</script>

<style scoped>
.certificate-main {
  width: 100vw;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #fff;
}
.certificate-card {
  width: 90vw;
  max-width: 1000px;
  min-height: 500px;
  background: #fff;
  border: 2px solid #222;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.10);
  padding: 2.5rem 2.5rem 2rem 2.5rem;
  margin: 2rem auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.certificate-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1.2rem;
}
.certificate-title {
  font-size: 2.7rem;
  font-weight: 700;
  color: #222;
  margin-bottom: 0.7rem;
  letter-spacing: 1px;
}
.certificate-user-pic {
  width: 110px;
  height: 110px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 0.7rem;
  border: 3px solid #1976d2;
}
.certificate-name {
  font-size: 2rem;
  font-weight: 500;
  color: #222;
  margin-bottom: 1.2rem;
}
.certificate-body {
  width: 100%;
  text-align: center;
  margin-bottom: 1.5rem;
}
.certificate-desc {
  font-size: 1.15rem;
  margin-bottom: 1.2rem;
}
.certificate-summary-row {
  display: flex;
  justify-content: space-between;
  gap: 2.5rem;
  width: 100%;
  margin: 0 auto 1.2rem auto;
  font-size: 1.08em;
}
.certificate-summary-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  align-items: flex-start;
}
.certificate-summary-col b {
  color: #222;
}
.certificate-footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 1.5rem;
}
.certificate-signature-block {
  text-align: center;
  margin-bottom: 1.2rem;
}
.certificate-signature-label {
  font-size: 1em;
  color: #888;
}
.certificate-signature {
  font-size: 1.2em;
  font-weight: 600;
  color: #1976d2;
  margin-top: 0.2rem;
}
.certificate-download-btn {
  background: #1976d2;
  color: #fff;
  border: none;
  padding: 0.7em 2em;
  border-radius: 8px;
  font-size: 1.1em;
  font-weight: 600;
  cursor: pointer;
  margin-top: 1.2rem;
}
.certificate-download-btn:hover {
  background: #1256a3;
}
</style>
