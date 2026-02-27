import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

function upsertConsultant(list, consultant) {
  const index = list.findIndex((item) => item.id === consultant.id)
  if (index === -1) {
    list.unshift(consultant)
  } else {
    list[index] = consultant
  }
}

export const useConsultantsStore = defineStore('consultants', () => {
  const consultants = ref([])
  const currentConsultant = ref(null)

  async function fetchConsultants() {
    try {
      const response = await api.get('/consultants')
      consultants.value = response.data
      return consultants.value
    } catch (error) {
      console.error('Error fetching consultants:', error)
      throw error
    }
  }

  async function fetchConsultant(id) {
    try {
      const response = await api.get(`/consultants/${id}`)
      currentConsultant.value = response.data
      return currentConsultant.value
    } catch (error) {
      console.error('Error fetching consultant:', error)
      throw error
    }
  }

  async function createConsultant(consultantData) {
    try {
      const response = await api.post('/consultants', consultantData)
      upsertConsultant(consultants.value, response.data)
      return response.data
    } catch (error) {
      console.error('Error creating consultant:', error)
      throw error
    }
  }

  async function updateConsultant(id, consultantData) {
    try {
      const response = await api.put(`/consultants/${id}`, consultantData)
      upsertConsultant(consultants.value, response.data)
      if (currentConsultant.value?.id === id) {
        currentConsultant.value = response.data
      }
      return response.data
    } catch (error) {
      console.error('Error updating consultant:', error)
      throw error
    }
  }

  async function deleteConsultant(id) {
    try {
      await api.delete(`/consultants/${id}`)
      consultants.value = consultants.value.filter((c) => c.id !== id)
      if (currentConsultant.value?.id === id) {
        currentConsultant.value = null
      }
    } catch (error) {
      console.error('Error deleting consultant:', error)
      throw error
    }
  }

  return {
    consultants,
    currentConsultant,
    fetchConsultants,
    fetchConsultant,
    createConsultant,
    updateConsultant,
    deleteConsultant
  }
})
