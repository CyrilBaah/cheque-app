<script setup>
import { ref, onMounted } from 'vue'

const API_URL = 'http://127.0.0.1:8000/api/cheques'

const chequeNo = ref('')
const approved = ref('yes')
const cheques = ref([])
const loading = ref(false)
const notificationMessage = ref('')
const notificationType = ref('')

async function loadCheques() {
  loading.value = true
  try {
    const response = await fetch(API_URL)
    const data = await response.json()
    cheques.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('Error loading cheques:', error)
    showNotification('Failed to load cheques', 'error')
  } finally {
    loading.value = false
  }
}

async function submitCheque() {
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        cheque_number: chequeNo.value,
        manager_approved: approved.value === 'yes',
      }),
    })

    if (response.ok) {
      showNotification('Cheque added successfully! ✓', 'success')
      chequeNo.value = ''
      approved.value = 'yes'
      await loadCheques()
    } else {
      showNotification('Failed to add cheque', 'error')
    }
  } catch (error) {
    console.error('Error submitting cheque:', error)
    showNotification('Failed to add cheque', 'error')
  }
}

async function clearCheque(id) {
  if (!confirm('Are you sure you want to clear this cheque?')) {
    return
  }

  try {
    const response = await fetch(`${API_URL}/${id}`, {
      method: 'DELETE',
    })

    if (response.ok) {
      showNotification('Cheque cleared successfully! ✓', 'success')
      await loadCheques()
    } else {
      showNotification('Failed to clear cheque', 'error')
    }
  } catch (error) {
    console.error('Error clearing cheque:', error)
    showNotification('Failed to clear cheque', 'error')
  }
}

function showNotification(message, type) {
  notificationMessage.value = message
  notificationType.value = type

  setTimeout(() => {
    notificationMessage.value = ''
    notificationType.value = ''
  }, 3000)
}

onMounted(() => {
  loadCheques()
})
</script>

<template>
  <div class="page">
    <header class="app-header">
      <h1>Cheque Clearance Department</h1>
    </header>

    <main class="content">
      <section class="form-section card">
        <h2>Create a new Cheque Entry</h2>
        <p class="info-box">
          Add cheque number and the associated branch manager approval status below.
        </p>

        <form class="cheque-form" @submit.prevent="submitCheque">
          <div class="form-row">
            <div class="form-group">
              <label class="label" for="chequeNo">Cheque No</label>
              <input
                id="chequeNo"
                v-model="chequeNo"
                type="text"
                placeholder="Cheque No"
                required
              />
            </div>

            <div class="form-group approval-group">
              <span class="label">Approved by Manager:</span>
              <div class="radio-buttons">
                <label class="radio-label">
                  <input v-model="approved" type="radio" value="yes" />
                  <span>Yes</span>
                </label>
                <label class="radio-label">
                  <input v-model="approved" type="radio" value="no" />
                  <span>No</span>
                </label>
              </div>
            </div>

            <button class="submit-btn" type="submit" :disabled="loading">
              {{ loading ? 'Submitting...' : 'Submit' }}
            </button>
          </div>
        </form>
      </section>

      <section class="cheques-section card">
        <h2>Cheques Pending Clearance</h2>
        <p class="pending-info">Cheques pending action listed below!</p>

        <div v-if="!cheques.length" class="empty-message">
          No cheques pending clearance. All caught up! 😊
        </div>

        <table v-else class="cheques-table">
          <thead>
            <tr>
              <th>Cheque No</th>
              <th>Approval Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cheque in cheques" :key="cheque.id">
              <td>{{ cheque.cheque_number }}</td>
              <td>{{ cheque.manager_approved ? 'Yes' : 'No' }}</td>
              <td>
                <button class="clear-btn" type="button" @click="clearCheque(cheque.id)">
                  Clear Cheque
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </main>

    <div v-if="notificationMessage" class="notification" :class="notificationType">
      {{ notificationMessage }}
    </div>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.app-header {
  background-color: #0d6efd;
  color: #ffffff;
  padding: 32px 40px;
  text-align: center;
}

.app-header h1 {
  font-size: 32px;
  font-weight: 600;
}

.content {
  max-width: 1200px;
  margin: 32px auto 48px;
  padding: 0 20px;
}

.card {
  background-color: #ffffff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  padding: 24px 28px;
  margin-bottom: 32px;
}

.form-section h2,
.cheques-section h2 {
  font-size: 24px;
  margin-bottom: 12px;
}

.info-box {
  background-color: #e3f7ff;
  border: 1px solid #c7ebff;
  border-radius: 4px;
  padding: 12px 16px;
  color: #1b4f72;
  margin-bottom: 20px;
}

.cheque-form {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-end;
}

.form-row {
  display: flex;
  flex-wrap: wrap;
  width: 100%;
  gap: 16px;
  align-items: flex-end;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group input[type='text'] {
  min-width: 260px;
}

.label {
  font-size: 14px;
  margin-bottom: 6px;
}

input[type='text'] {
  padding: 10px 12px;
  border-radius: 4px;
  border: 1px solid #ced4da;
  font-size: 14px;
}

.approval-group {
  flex: 1;
}

.radio-buttons {
  display: flex;
  gap: 16px;
  margin-top: 4px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 4px;
}

.submit-btn {
  padding: 10px 32px;
  background-color: #212529;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: default;
}

.submit-btn:hover:not(:disabled) {
  background-color: #141619;
}

.cheques-section {
  margin-top: 16px;
}

.pending-info {
  background-color: #e9ecef;
  border-radius: 4px;
  padding: 10px 14px;
  margin: 12px 0 18px;
}

.empty-message {
  padding: 16px;
  text-align: center;
  color: #6c757d;
}

.cheques-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
}

.cheques-table thead tr {
  background-color: #cfe2ff;
}

.cheques-table th,
.cheques-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid #dee2e6;
}

.cheques-table tbody tr:nth-child(even) {
  background-color: #f8f9fa;
}

.clear-btn {
  padding: 6px 16px;
  background-color: #dc3545;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.clear-btn:hover {
  background-color: #bb2d3b;
}

.notification {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 12px 18px;
  border-radius: 4px;
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.notification.success {
  background-color: #198754;
}

.notification.error {
  background-color: #dc3545;
}

@media (max-width: 768px) {
  .cheque-form {
    flex-direction: column;
    align-items: stretch;
  }

  .submit-btn {
    width: 100%;
  }
}
</style>
