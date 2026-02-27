import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

function upsertProfile(list, profile) {
  const index = list.findIndex((item) => item.id === profile.id)
  if (index === -1) {
    list.unshift(profile)
  } else {
    list[index] = profile
  }
}

function extractFilename(contentDispositionHeader) {
  if (!contentDispositionHeader) {
    return 'consultant_profile.pdf'
  }

  const utf8Match = contentDispositionHeader.match(/filename\*=UTF-8''([^;]+)/i)
  if (utf8Match?.[1]) {
    try {
      return sanitizeDownloadFilename(decodeURIComponent(utf8Match[1]))
    } catch {
      return sanitizeDownloadFilename(utf8Match[1])
    }
  }

  const basicMatch = contentDispositionHeader.match(/filename="?([^";]+)"?/i)
  return sanitizeDownloadFilename(basicMatch?.[1] || 'consultant_profile.pdf')
}

function sanitizeDownloadFilename(filename) {
  const cleaned = String(filename).replace(/[\\/:"*?<>|]+/g, '').trim()
  if (!cleaned) {
    return 'consultant_profile.pdf'
  }
  if (cleaned.toLowerCase().endsWith('.pdf')) {
    return cleaned
  }
  return `${cleaned}.pdf`
}

export const useProfilesStore = defineStore('profiles', () => {
  const profiles = ref([])
  const currentProfile = ref(null)

  async function fetchProfiles() {
    try {
      const response = await api.get('/profiles')
      profiles.value = response.data
      return profiles.value
    } catch (error) {
      console.error('Error fetching profiles:', error)
      throw error
    }
  }

  async function fetchConsultantProfiles(consultantId) {
    try {
      const response = await api.get(`/profiles/consultant/${consultantId}`)
      return response.data
    } catch (error) {
      console.error('Error fetching consultant profiles:', error)
      throw error
    }
  }

  async function fetchProfile(id) {
    try {
      const response = await api.get(`/profiles/${id}`)
      currentProfile.value = response.data
      return currentProfile.value
    } catch (error) {
      console.error('Error fetching profile:', error)
      throw error
    }
  }

  async function createProfile(profileData) {
    try {
      const response = await api.post('/profiles', profileData)
      upsertProfile(profiles.value, response.data)
      return response.data
    } catch (error) {
      console.error('Error creating profile:', error)
      throw error
    }
  }

  async function deleteProfile(id) {
    try {
      await api.delete(`/profiles/${id}`)
      profiles.value = profiles.value.filter((p) => p.id !== id)
    } catch (error) {
      console.error('Error deleting profile:', error)
      throw error
    }
  }

  async function updateProfile(id, profileData) {
    try {
      const response = await api.put(`/profiles/${id}`, profileData)
      upsertProfile(profiles.value, response.data)
      if (currentProfile.value?.id === id) {
        currentProfile.value = response.data
      }
      return response.data
    } catch (error) {
      console.error('Error updating profile:', error)
      throw error
    }
  }

  async function duplicateProfile(id, newProfileName) {
    try {
      const response = await api.post(`/profiles/${id}/duplicate`, null, {
        params: { new_profile_name: newProfileName }
      })
      upsertProfile(profiles.value, response.data)
      return response.data
    } catch (error) {
      console.error('Error duplicating profile:', error)
      throw error
    }
  }

  async function exportProfilePdf(profileId, { companyName, accentColor }) {
    try {
      const formData = new FormData()

      if (companyName) {
        formData.append('company_name', companyName)
      }

      if (accentColor) {
        const isHexColor = /^#[0-9A-Fa-f]{6}$/.test(accentColor)
        if (!isHexColor) {
          throw new Error('Accent color must be a hex value like #0E4B8A')
        }
        formData.append('accent_color', accentColor)
      }

      formData.append('template', 'default')

      const response = await api.post(`/profiles/${profileId}/export/pdf`, formData, {
        responseType: 'blob',
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      const filename = extractFilename(response.headers['content-disposition'])

      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()

      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error exporting profile PDF:', error)
      throw error
    }
  }

  return {
    profiles,
    currentProfile,
    fetchProfiles,
    fetchConsultantProfiles,
    fetchProfile,
    createProfile,
    updateProfile,
    deleteProfile,
    duplicateProfile,
    exportProfilePdf
  }
})
