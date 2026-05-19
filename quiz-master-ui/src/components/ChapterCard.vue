<template>
  <div class="card h-100">
    <div class="card-body">
      <h5 class="card-title">{{ chapter.name }}</h5>
      <p class="card-text">{{ chapter.description }}</p>
      <p class="card-text"><strong>Subject:</strong> {{ chapter.subject_name }}</p>
      <hr/>
      <div class="d-flex justify-content-end gap-1">
        <button class="btn btn-sm btn-info" @click="$emit('go-to-quizzes', chapter.id)">{{ chapter.quizzes }} Quizzes</button>|
        <button v-if="canEdit" class="btn btn-sm btn-warning" @click="$emit('edit', chapter)">Edit</button>
        <button v-if="canDelete" class="btn btn-sm btn-danger" @click="$emit('delete', chapter.id)">Delete</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  chapter: { type: Object, required: true },
  canEdit: { type: Boolean, default: true },
  canDelete: { type: Boolean, default: true }
})
</script>

<style scoped>
.card {
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
</style>
