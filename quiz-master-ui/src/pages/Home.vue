<template>
  <div class="flex-grow-1 p-4">
    
		    <div class="row mt-3 mb-3">
        <div class=" col p-2 bg-light text-dark rounded shadow-sm">
            <h2 class="fw-bold text-muted">Welcome to the Distributed Assessment Platform!</h2>
            <p class="mb-3 text-secondary">
                Challenge your knowledge, track your progress, and compete with others.  
                Start a quiz now and test your skills!
                <span v-if="!isLoggedIn">
                    <a href="#" class="btn btn-primary"><RouterLink class="nav-link" to="/login">Login</RouterLink></a> | 
                    <a href="#" class="btn btn-warning"><RouterLink class="nav-link" to="/signup">Register</RouterLink></a>
                </span>
            </p>
        </div>
    </div>

    <div class="row mb-2">
        <div class="col-md-4 mb-3">
            <div class="card h-100 shadow-sm">
                <div class="card-body text-center">
                    <div class="mb-3">🧠</div>
                    <h5 class="card-title text-primary">Smart Quizzes</h5>
                    <p class="card-text">Engage with carefully crafted questions designed to challenge your thinking and expand your knowledge across various subjects.</p>
                </div>
            </div>
        </div>
        <div class="col-md-4 mb-3">
            <div class="card h-100 shadow-sm">
                <div class="card-body text-center">
                    <div class="mb-3">📊</div>
                    <h5 class="card-title text-success">Track Progress</h5>
                    <p class="card-text">Monitor your learning journey with detailed analytics, performance metrics, and personalized insights to help you improve.</p>
                </div>
            </div>
        </div>
        <div class="col-md-4 mb-3">
            <div class="card h-100 shadow-sm">
                <div class="card-body text-center">
                    <div class="mb-3">🏆</div>
                    <h5 class="card-title text-warning">Compete & Achieve</h5>
                    <p class="card-text">Challenge yourself with leaderboards, achievements, and friendly competition to stay motivated and engaged.</p>
                </div>
            </div>
        </div>
    </div>

    <div class="row mb-2">
        <div class="col-lg-8 mx-auto">
            <div class="card border-0 bg-gradient" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <div class="card-body text-white text-center p-3">
                    <h3 class="mb-3">Why Choose Distributed Assessment Platform?</h3>
                    <p class="lead mb-3">
                        Distributed Assessment Platform is more than just a quiz platform – it's your personal learning companion. 
                        Whether you're a student preparing for exams, a professional looking to upskill, 
                        or simply someone who loves to learn, we've got you covered.
                    </p>
                    <div class="row text-center">
                        <div class="col-md-3 mb-3">
                            <h4 class="fw-bold">1000+</h4>
                            <small>Questions</small>
                        </div>
                        <div class="col-md-3 mb-3">
                            <h4 class="fw-bold">50+</h4>
                            <small>Categories</small>
                        </div>
                        <div class="col-md-3 mb-3">
                            <h4 class="fw-bold">500+</h4>
                            <small>Active Users</small>
                        </div>
                        <div class="col-md-3 mb-2">
                            <h4 class="fw-bold">95%</h4>
                            <small>Success Rate</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="row mb-2">
        <div class="col-12">
            <h3 class="text-center mb-3 text-muted">How It Works</h3>
        </div>
        <div class="col-md-3 mb-3">
            <div class="text-center">
                <div class="rounded-circle bg-primary text-white d-inline-flex align-items-center justify-content-center mb-3" style="width: 60px; height: 60px;">
                    <strong>1</strong>
                </div>
                <h6 class="fw-bold">Sign Up</h6>
                <p class="text-muted small">Create your free account and customize your learning preferences.</p>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="text-center">
                <div class="rounded-circle bg-success text-white d-inline-flex align-items-center justify-content-center mb-3" style="width: 60px; height: 60px;">
                    <strong>2</strong>
                </div>
                <h6 class="fw-bold">Choose Quiz</h6>
                <p class="text-muted small">Select from our extensive library of quizzes across multiple subjects.</p>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="text-center">
                <div class="rounded-circle bg-warning text-white d-inline-flex align-items-center justify-content-center mb-3" style="width: 60px; height: 60px;">
                    <strong>3</strong>
                </div>
                <h6 class="fw-bold">Take Quiz</h6>
                <p class="text-muted small">Answer questions at your own pace with instant feedback and explanations.</p>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="text-center">
                <div class="rounded-circle bg-info text-white d-inline-flex align-items-center justify-content-center mb-3" style="width: 60px; height: 60px;">
                    <strong>4</strong>
                </div>
                <h6 class="fw-bold">Track Progress</h6>
                <p class="text-muted small">Review your performance and get personalized recommendations.</p>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-lg-6 mx-auto text-center">
            <div class="card bg-light border-0">
                <div class="card-body p-4">
                    <h4 class="mb-3">Ready to Start Learning?</h4>
                    <p class="text-muted mb-3">
                        Join thousands of learners who are already improving their knowledge and skills with Distributed Assessment Platform.
                    </p>
                    <span v-if="!isLoggedIn">
                        <RouterLink to="/signup" class="btn btn-primary btn-lg me-3">Get Started Free</RouterLink>
                        <RouterLink to="/login" class="btn btn-outline-primary btn-lg">Sign In</RouterLink>
                    </span>
                    <span v-else>
                        <RouterLink to="/dashboard" class="btn btn-primary btn-lg me-3">Go to Dashboard</RouterLink>
                        <RouterLink to="/quiz" class="btn btn-outline-primary btn-lg">Start Quiz</RouterLink>
                    </span>
                </div>
            </div>
        </div>
    </div>
	  
    </div>
</template>

<script>
import { computed } from 'vue';
import { useAuthStore } from '../stores/auth';

export default {
  name: 'Home',
  setup() {
    const authStore = useAuthStore();
    
    const isLoggedIn = computed(() => authStore.isAuthenticated);
    
    return {
      isLoggedIn
    };
  }
};
</script>
