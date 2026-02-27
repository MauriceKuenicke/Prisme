import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useBlocksStore = defineStore('blocks', () => {
  const blocks = ref([])

  const blocksByType = computed(() => {
    const grouped = {
      project: [],
      skill: [],
      misc: [],
      certification: []
    }

    for (const block of blocks.value) {
      if (grouped[block.block_type]) {
        grouped[block.block_type].push(block)
      }
    }

    return grouped
  })

  async function fetchBlocks(consultantId, viaToken = null) {
    try {
      const url = viaToken ? `/blocks/edit/${viaToken}` : `/blocks/consultant/${consultantId}`
      const response = await api.get(url)
      blocks.value = response.data
      return blocks.value
    } catch (error) {
      console.error('Error fetching blocks:', error)
      throw error
    }
  }

  async function createBlock(blockData, viaToken = null) {
    try {
      const url = viaToken ? `/blocks/edit/${viaToken}` : `/blocks`
      const response = await api.post(url, blockData)
      blocks.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('Error creating block:', error)
      throw error
    }
  }

  async function updateBlock(blockId, blockData, viaToken = null) {
    try {
      const url = viaToken ? `/blocks/edit/${viaToken}/${blockId}` : `/blocks/${blockId}`
      const response = await api.put(url, blockData)
      const index = blocks.value.findIndex((b) => b.id === blockId)
      if (index !== -1) {
        blocks.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('Error updating block:', error)
      throw error
    }
  }

  async function deleteBlock(blockId, viaToken = null) {
    try {
      const url = viaToken ? `/blocks/edit/${viaToken}/${blockId}` : `/blocks/${blockId}`
      await api.delete(url)
      blocks.value = blocks.value.filter((b) => b.id !== blockId)
    } catch (error) {
      console.error('Error deleting block:', error)
      throw error
    }
  }

  async function reorderBlocks(blockOrders, viaToken = null) {
    try {
      const url = viaToken ? `/blocks/edit/${viaToken}/reorder` : `/blocks/reorder`
      await api.post(url, { block_orders: blockOrders })
    } catch (error) {
      console.error('Error reordering blocks:', error)
      throw error
    }
  }

  return {
    blocks,
    blocksByType,
    fetchBlocks,
    createBlock,
    updateBlock,
    deleteBlock,
    reorderBlocks
  }
})
