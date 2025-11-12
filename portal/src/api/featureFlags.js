import api from './axios'

export const getFeatureFlag = async (name) => {
  const response = await api.get(`/feature-flags/${name}`)
  return response.data
}
