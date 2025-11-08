import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AuthView from '../views/AuthView.vue'
import ProfileView from '../views/ProfileView.vue'
import { useAuthStore } from '../stores/auth'

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
      component: () => import('../views/DetailView.vue')
    },
    {
      path: "/sites/:site_id/review",
      name: "reviewEditor",
      component: () => import("../views/ReviewEditorView.vue"),
      path: '/auth/callback', 
      name: 'authCallback',
      component: AuthView,
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      beforeEnter: requireAuth,
    }
  ],
})

export default router
