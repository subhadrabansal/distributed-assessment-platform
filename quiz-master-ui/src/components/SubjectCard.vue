<template>
  <div class="card h-100">
    <div class="card-body">
      <h5 class="card-title">{{ subject.name }}</h5>
      <p class="card-text">{{ subject.description }}</p>
      <hr/>
      <div class="d-flex justify-content-end gap-1">
        <button class="btn btn-sm btn-info" @click="goToChapters">{{ subject.chapters }} Chapters</button>|
        <button v-if="canEdit" class="btn btn-sm btn-warning" @click="editSubject">Edit</button>
        <button v-if="canDelete" class="btn btn-sm btn-danger" @click="deleteSubject">Delete</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
const props = defineProps({
  subject: { type: Object, required: true },
  canEdit: { type: Boolean, default: true },
  canDelete: { type: Boolean, default: true }
})
const router = useRouter()
function goToChapters() {
  router.push({ name: 'Chapters', query: { subjectId: props.subject.id } })
}
function editSubject() {
  alert('Edit subject: ' + props.subject.name)
}
function deleteSubject() {
  alert('Delete subject: ' + props.subject.name)
}
</script>

<style scoped>
.card {
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
</style>
