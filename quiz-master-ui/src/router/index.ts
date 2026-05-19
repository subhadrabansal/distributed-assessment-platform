import type { RouteRecordRaw } from 'vue-router'
import { createRouter, createWebHistory} from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import NotFound from '@/pages/NotFound.vue'
// Importing pages
import Home from '@/pages/Home.vue'
import About from '@/pages/About.vue'
import SignUp from '@/pages/SignUp.vue'
import Login from '@/pages/Login.vue'
import Profile from '@/pages/Profile.vue'
// admin imports
import AdminDashboard from '@/pages/admin/Dashboard.vue'
import Subjects from '@/pages/admin/Subjects.vue'
import Chapters from '@/pages/admin/Chapters.vue'
import Questions from '@/pages/admin/Questions.vue'
import Quizzes from '@/pages/admin/Quizzes.vue'
import Users from '@/pages/admin/Users.vue'
import UserScore from '@/pages/admin/UserScore.vue'
import AdminSettings from '@/pages/admin/Settings.vue'
import Search from '@/pages/admin/Search.vue'
// user imports
import RegisteredQuiz from '@/pages/user/RegistredQuiz.vue'
import OnGoingQuiz from '@/pages/user/OnGoingQuiz.vue'
import UpcomingQuiz from '@/pages/user/UpcomingQuiz.vue'
import AbsentQuiz from '@/pages/user/AbsentQuiz.vue'
import UserDashboard from '@/pages/user/Dashboard.vue'
import CompletedQuiz from '@/pages/user/CompletedQuiz.vue'
import UserSettings from '@/pages/user/Settings.vue'
import QuizAttempt from '@/pages/user/QuizAttempt.vue'
import Score from '@/pages/user/Score.vue'


const routes: RouteRecordRaw[] = [
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound },

  {
    path: '/',
    component: DefaultLayout,
    children: [
      { path: '', name: 'Home', component: Home }
    ]
  },

  {
    path: '/about',
    component: DefaultLayout,
    children: [
      { path: '', name: 'About', component: About },
    ]
  },

  {
    path: '/signup',
    component: DefaultLayout,
    children: [
      { path: '', name: 'SignUp', component: SignUp },
    ]
  },

  {
    path: '/login',
    component: DefaultLayout,
    children: [
      { path: '', name: 'Login', component: Login },
    ]
  },
  {
    path: '/profile',
    component: DefaultLayout,
    children: [
      { path: '', name: 'Profile', component: Profile },
    ]
  },
  // Admin Routes
  {
    path: '/admin-dashboard',
    component: DefaultLayout,
    children: [
      { path: '', name: 'AdminDashboard', component: AdminDashboard }
    ]
  },
  {
    path: '/subjects',
    component: DefaultLayout,
    children: [
      { path: '', name: 'Subjects', component: Subjects },
    ]
  },
  {
    path: '/chapters',
    component: DefaultLayout,
    children: [
      { path: '', name: 'Chapters', component: Chapters },
    ]
  },
  {
    path: '/questions',
    component: DefaultLayout,
    children: [
      { path: '', name: 'Questions', component: Questions },
    ]
  },
  {
    path: '/quizzes',
    component: DefaultLayout,
    children: [
      { path: '', name: 'Quizzes', component: Quizzes }
    ]
  },
  {
    path: '/users',
    component: DefaultLayout,
    children: [
      { path: '', name: 'Users', component: Users }
    ]
  },
  {
    path: '/user-scores',
    component: DefaultLayout,
    children: [
      { path: '', name: 'UserScore', component: UserScore }
    ]
  },
  {
    path: '/user-scores/:userId',
    component: DefaultLayout,
    children: [
      { path: '', name: 'UserScore', component: UserScore }
    ]
  },
  {
    path: '/admin-settings',
    component: DefaultLayout,
    children: [
      { path: '', name: 'Settings', component: AdminSettings }
    ]
  },
  {
    path: '/admin-search',
    component: DefaultLayout,
    children: [
      { path: '', name: 'AdminSearch', component: Search }
    ]
  },
  // User Routes
  {
    path : '/user-dashboard',
    component: DefaultLayout,
    children: [
      { path: '', name: 'UserDashboard', component: UserDashboard }
    ]
  },
  {
    path: '/registered-quiz',
    component: DefaultLayout,
    children: [
      { path: '', name: 'RegisteredQuiz', component: RegisteredQuiz }
    ]
  },
  {
    path: '/ongoing-quiz',
    component: DefaultLayout,
    children: [
      { path: '', name: 'OnGoingQuiz', component: OnGoingQuiz }
    ]
  },
  {
    path: '/upcoming-quiz',
    component: DefaultLayout,
    children: [
      { path: '', name: 'UpcomingQuiz', component: UpcomingQuiz }
    ]
  },
  {
    path: '/completed-quiz',
    component: DefaultLayout,
    children: [
      { path: '', name: 'CompletedQuiz', component: CompletedQuiz }
    ]
  },
  {
    path: '/absent-quiz',
    component: DefaultLayout,
    children: [
      { path: '', name: 'AbsentQuiz', component: AbsentQuiz }
    ]
  },
  {
    path: '/user-settings',
    component: DefaultLayout,
    children: [
      { path: '', name: 'UserSettings', component: UserSettings }
    ]
  },
  {
    path: '/quiz-attempt',
    component: QuizAttempt,
    name: 'QuizAttempt',
  },
  {
    path: '/user/score',
    component: DefaultLayout,
    children: [
      { path: '', name: 'Score', component: Score }
    ]
  },
  {
    path: '/user-search',
    component: DefaultLayout,
    children: [
      { path: '', name: 'UserSearch', component: () => import('@/pages/user/user-search.vue') }
    ]
  },
  {
    path: '/forgot-password',
    component: DefaultLayout,
    children: [
      { path: '', name: 'ForgotPassword', component: () => import('@/pages/forgot-password.vue') },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
