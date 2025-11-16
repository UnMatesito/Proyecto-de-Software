import { createRouter, createWebHistory } from 'vue-router'
import { getFeatureFlag } from '@/api/featureFlags'
import { maintenanceState } from '@/utils/maintenanceState'
import { useAuthStore } from '../stores/auth'

import HomeView from '../views/HomeView.vue'
import ProfileView from '../views/ProfileView.vue'

const requireAuth = (to, from, next) => {
  const authStore = useAuthStore();
  if (authStore.isAuthenticated) {
    next();
  } else {
    next('/');
  }
};


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/sites',
      name: 'sites',
      component: () => import('../views/SitesView.vue'),
    },
    {
      path: '/sites/:name/:description/:city/:province/:tags/:order_by/:lat/:long/:radius/:page/:per_page',
      name: 'sitesQuery',
      component: () => import('../views/SitesView.vue'),
    },
    {
      path: '/sites/:site_id',
      name: 'siteDetail',
      component: () => import('../views/SiteDetailsView.vue')
    },
    {
      path: "/sites/:site_id/review",
      name: "reviewEditor",
      component: () => import("../views/ReviewEditorView.vue"),
     },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      beforeEnter: requireAuth,
    }
  ],
})

const PORTAL_FLAG_NAME = 'portal_maintenance_mode'
const CACHE_WINDOW_MS = 15000
let ongoingRequest = null

const ensurePortalAvailability = async (forceRefresh = false) => {
  const now = Date.now()
  if (
    !forceRefresh &&
    maintenanceState.lastChecked &&
    now - maintenanceState.lastChecked < CACHE_WINDOW_MS
  ) {
    return maintenanceState.isActive
  }

  if (!ongoingRequest) {
    ongoingRequest = getFeatureFlag(PORTAL_FLAG_NAME)
      .then((data) => {
        maintenanceState.isActive = Boolean(data.is_enabled)
        maintenanceState.message = data.maintenance_message || ''
        maintenanceState.lastChecked = Date.now()

        return maintenanceState.isActive
      })
      .catch((error) => {
        console.error('No se pudo obtener el estado de mantenimiento del portal', error)
        maintenanceState.isActive = false
        maintenanceState.message = ''
        maintenanceState.lastChecked = Date.now()

        return false
      })
      .finally(() => {
        ongoingRequest = null
      })
  }

  return ongoingRequest
}

router.beforeEach(async (to, from, next) => {
  const forceRefresh = maintenanceState.isActive
  await ensurePortalAvailability(forceRefresh)
  return next()
})

router.beforeResolve(async (to, from, next) => {
  await ensurePortalAvailability(true)
  next()
})

export default router

export { ensurePortalAvailability }
