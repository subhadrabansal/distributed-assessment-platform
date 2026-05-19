<template>
  <div class="quiz-attempt-main">
    <div class="quiz-attempt-left">
      <div class="quiz-title-main">Distributed Assessment Platform</div>
      <div class="user-info-block">
        <img :src="userPic" alt="User Pic" class="user-pic" />
        <div class="user-name-main">{{ userName }}</div>
      </div>
      <hr />
      <div class="quiz-meta-block">
        <div><b>Quiz:</b> {{ quizName }}</div>
        <div><b>Subject:</b> {{ subjectName }}</div>
        <div><b>Chapter:</b> {{ chapterName }}</div>
      </div>
      <hr />
      <div class="timer-main">
        <span :class="['timer-text', { 'timer-red': timeLeft < 60*5 }]">Time Left: {{ formattedTime }}</span>
      </div>
      <button class="btn btn-danger submit-btn" @click="submitQuiz">Submit Quiz</button>
      <hr />
      <div class="jump-label">Jump to Question:</div>
      <div class="jump-bar">
        <button v-for="(q, idx) in questions" :key="q.id" :class="['jump-btn', { active: idx === currentIndex, attempted: answers[q.id] }]" @click="goToQuestion(idx)">
          {{ idx + 1 }}
        </button>
      </div>
    </div>
    <div class="quiz-attempt-right">
      <div class="question-header">
        <span><b>Current Question:</b> {{ currentIndex + 1 }} / {{ questions.length }}</span>
        <span><b>Marks:</b> {{ totalMarks }}</span>
        <span><b>Answered:</b> {{ attemptedCount }}</span>
      </div>
      <div class="question-section" v-if="currentQuestion">
        <div class="question-text">{{ currentQuestion.text }}</div>
        <div class="options-list">
          <div v-for="option in currentQuestion.options" :key="option.id" class="option-item">
            <input type="radio" :id="'option-' + option.id" :name="'question-' + currentQuestion.id" :value="option.id" v-model="answers[currentQuestion.id]" />
            <label :for="'option-' + option.id">{{ option.text }}</label>
          </div>
        </div>
        <div class="action-buttons">
          <button class="btn btn-warning save-btn" @click="saveAnswer">Save & Next</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import axios from '@/axios'
import { useRouter } from 'vue-router'
import dummyUserPic from '@/assets/dummy-user.jpg'

const router = useRouter()

const quizId = Number(localStorage.getItem('current_quiz_id'))
function getProfilePicUrl(pic: string | undefined) {
  if (!pic) return dummyUserPic
  if (pic.startsWith('http')) return pic
  const base = axios.defaults.baseURL || ''
  if (pic.startsWith('/static/')) return base + pic
  if (pic.startsWith('static/')) return base + '/' + pic
  if (pic.startsWith('profile_pics/')) return base + '/static/' + pic
  return base + '/static/profile_pics/' + pic
}

const userPic = computed(() => getProfilePicUrl(userPicRaw.value))
const userPicRaw = ref('')

const userName = ref('')
const userEmail = ref('')
const questions = ref<any[]>([])
const totalMarks = ref(0)
const attemptedCount = computed(() => Object.keys(answers.value).length)
const answers = ref<Record<number, number>>({})
const currentIndex = ref(0)
const quizDuration = ref(0) // in minutes
const timeLeft = ref(0) // in seconds
let timerInterval: any = null

const currentQuestion = computed(() => questions.value[currentIndex.value])
const quizName = ref('')
const chapterName = ref('')
const subjectName = ref('')

const formattedTime = computed(() => {
  const min = Math.floor(timeLeft.value / 60)
  const sec = timeLeft.value % 60
  return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`
})

function goToQuestion(idx: number) {
  currentIndex.value = idx
}

const saveAnswer = async () => {
  const q = currentQuestion.value
  if (!q) return
  const selected = answers.value[q.id]
  if (selected !== undefined) {
    await axios.post('/user/quiz/answer', {
      quiz_id: quizId,
      question_id: q.id,
      user_answer: selected
    })
  }
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++;
  }
}

watch(answers, async (newVal, oldVal) => {
  const q = currentQuestion.value
  if (!q) return
  const selected = newVal[q.id]
  if (selected !== undefined && selected !== oldVal[q.id]) {
    await axios.post('/user/quiz/answer', {
      quiz_id: quizId,
      question_id: q.id,
      user_answer: selected
    })
  }
})

function submitQuiz() {
  axios.post(`/user/quiz/submit`, {
    quiz_id: quizId
  }).then(() => {
    localStorage.setItem('last_quiz_id', quizId.toString())
    router.replace('/user/score')
  })
}

function startTimer() {
  timerInterval = setInterval(() => {
    if (timeLeft.value > 0) {
      timeLeft.value--
      localStorage.setItem(`quiz_time_${quizId}`, timeLeft.value.toString())
    } else {
      clearInterval(timerInterval)
      submitQuiz()
    }
  }, 1000)
}

onMounted(async () => {
  try {
    const quizRes = await axios.post(`/user/quiz/attempt`, { quiz_id: quizId })
    const { user, quiz, questions: qs, answers: prevAnswers, time_left } = quizRes.data.data
    userPicRaw.value = user.pic
    userName.value = user.name
    userEmail.value = user.email
    questions.value = qs
    totalMarks.value = quiz.total_marks
    quizDuration.value = quiz.duration
    answers.value = prevAnswers || {}
    quizName.value = quiz.name
    chapterName.value = quiz.chapter_name
    subjectName.value = quiz.subject_name
    if (time_left !== undefined && time_left !== null) {
      timeLeft.value = time_left
    } else {
      timeLeft.value = quiz.duration * 60
    }
    startTimer()
    history.pushState(null, '', location.href)
    window.onpopstate = function () {
      history.go(1)
    }
  } catch (e) {
    alert('Failed to load quiz data. Please try again.')
  }
})

watch(timeLeft, (val) => {
  if (val <= 0 && timerInterval) {
    clearInterval(timerInterval)
    submitQuiz()
  }
})
</script>

<style scoped>
.quiz-attempt-main {
  display: flex;
  max-width: 1200px;
  margin: 0 auto;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  min-height: 80vh;
}
.quiz-attempt-left {
  flex: 0 0 340px;
  background: #fafbfc;
  border-right: 1px solid #eee;
  padding: 2rem 1.5rem 1.5rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.quiz-title-main {
  font-size: 2rem;
  font-weight: bold;
  text-align: center;
  margin-bottom: 0.5rem;
}
.user-info-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1rem;
}
.user-pic {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  margin-bottom: 0.5rem;
}
.user-name-main {
  font-weight: 600;
  font-size: 1.1rem;
}
.quiz-meta-block {
  width: 100%;
  font-size: 1.05em;
  margin-bottom: 1rem;
}
.timer-main {
  margin: 1rem 0 0.5rem 0;
  text-align: center;
}
.timer-text {
  font-size: 1.2em;
  font-weight: bold;
}
.timer-red {
  color: #e53935;
}
.submit-btn {
  width: 100%;
  margin: 0.5rem 0 1rem 0;
  font-size: 1.1em;
}
.jump-label {
  font-size: 1em;
  margin-bottom: 0.3rem;
  text-align: left;
  width: 100%;
}
.jump-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: flex-start;
  width: 100%;
}
.jump-btn {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  border: 1px solid #bbb;
  background: #f5f5f5;
  font-weight: bold;
  color: #333;
  cursor: pointer;
  font-size: 1.1em;
  transition: background 0.2s, color 0.2s;
}
.jump-btn.active {
  background: #1976d2;
  color: #fff;
  border-color: #1976d2;
}
.jump-btn.attempted {
  background: #43a047;
  color: #fff;
  border-color: #43a047;
}
.quiz-attempt-right {
  flex: 1;
  padding: 2.5rem 2.5rem 2rem 2.5rem;
  display: flex;
  flex-direction: column;
}
.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.1em;
  margin-bottom: 1.5rem;
}
.question-section {
  background: #fafbfc;
  border-radius: 10px;
  padding: 2rem 1.5rem 1.5rem 1.5rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.question-text {
  font-size: 1.15em;
  font-weight: 500;
  margin-bottom: 1.2rem;
}
.options-list {
  margin-bottom: 1.5rem;
}
.option-item {
  margin-bottom: 1rem;
  font-size: 1.08em;
  display: flex;
  align-items: center;
}
.option-item input[type="radio"] {
  margin-right: 0.7em;
}
.action-buttons {
  display: flex;
  justify-content: flex-end;
}
.save-btn {
  background: #ffc107;
  color: #222;
  border: none;
  font-weight: 600;
  padding: 0.5em 1.5em;
  border-radius: 6px;
  font-size: 1.1em;
}
.save-btn:hover {
  background: #ffb300;
}
@media (max-width: 900px) {
  .quiz-attempt-main {
    flex-direction: column;
  }
  .quiz-attempt-left, .quiz-attempt-right {
    padding: 1rem;
    border-radius: 0;
  }
  .quiz-attempt-left {
    border-right: none;
    border-bottom: 1px solid #eee;
    flex: unset;
  }
}
</style>
