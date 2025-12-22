import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const getProducts = async (page = 1, limit = 20) => {
  try {
    const response = await api.get('/products', {
      params: { page, limit }
    })
    return response.data
  } catch (error) {
    console.error('Error fetching products:', error)
    throw error
  }
}

export default api
