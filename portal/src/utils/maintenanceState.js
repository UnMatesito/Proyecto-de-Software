import { reactive } from 'vue'

export const maintenanceState = reactive({
  isActive: false,
  message: '',
  lastChecked: 0,
})
