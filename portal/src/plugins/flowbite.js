import { initFlowbite } from 'flowbite'

let initialized = false
let pending = false

export default {
  install(app) {
    app.mixin({
      mounted() {
        // Evita inicializar Flowbite antes de que el DOM esté listo
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', () => initFlowbite(), { once: true })
          return
        }

        // Evita múltiples ejecuciones seguidas durante el mismo ciclo de renderizado
        if (!pending) {
          pending = true
          setTimeout(() => {
            initFlowbite()
            pending = false
            initialized = true
          }, 0)
        }
      },
    })
  },
}
