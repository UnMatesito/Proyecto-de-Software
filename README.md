# Histori.ar - Sistema de Gestión Histórica
**Proyecto académico** creado para la materia **Proyecto de Software** de la Universidad Nacional de La Plata (UNLP).

**Integrantes del equipo - Grupo 09**
- Carlos Benítez
- Tobias Palumbo
- Cielo Vega
- Mateo Suarez
- Neftalí Toledo

---

## Índice

- [Descripción del Proyecto](#descripción-del-proyecto)
- [Módulos Principales](#módulos-principales)
- [Instalación y Configuración](#instalación-y-configuración)
- [Accesos](#accesos)

---

## Descripción del Proyecto

**Histori.ar** es un sistema con una arquitectura MVC de gestión de sitios históricos diseñado para centralizar, administrar y consultar información y realizar reseñas de sitios históricos de manera eficiente. El proyecto implementa una arquitectura con:

- **Backend**: API REST desarrollada con Flask (Python)
- **Frontend**: Aplicación web interactiva con Vue.js
- **Base de Datos**: PostgreSQL para persistencia de datos
- **Almacenamiento**: MinIO para gestión de archivos
- **Administración**: Panel de control administrativo
---
## Módulos Principales

### [`admin/`](./admin/README.md) - Aplicación de Administración & API REST

**Stack**: Python, Flask, SQLAlchemy, PostgreSQL, MinIO (Almacenamiento de Imagenes)

Backend responsable de:
- **API REST** para todas las operaciones del sistema
- **CRUD** de usuarios
- **Autenticación** de usuarios Administradores
- **Gestión de Sitios Historicos** y evaluación de reseñas
- 
- **Validación** y procesamiento de datos

**Documentación completa**: Ver [`admin/README.md`](./admin/README.md)

---
### [`portal/`](./portal/README.md) - Frontend Web

**Stack**: Vue.js 3, Vite, HTML5, CSS3, JavaScript

Interfaz de usuario pública que proporciona:
- **Visualización** de contenido histórico
- **Búsqueda y Filtrado** avanzado
- **Interfaz Responsiva** para múltiples dispositivos
- **Consumo de API REST** del backend

**Documentación completa**: Ver [`portal/README.md`](./portal/README.md)

**Características**:
- Dashboard interactivo
- Galería de contenido
- Búsqueda de registros
- Perfil de usuario

---

### `calculator/` - Herramienta de Cálculo

**Módulo de prueba** para experimentar las funcionalidades de Gitflow.

---
## Instalación y Configuración

### 1️⃣ Clonar el Repositorio

```bash
git clone https://github.com/UnMatesito/Proyecto-de-Software.git
cd Proyecto-de-Software
```

### 2️⃣ Instalar Dependencias del Backend

```bash
# Instalar las dependencias de Python
poetry install

# Entrar al entorno virtual
cd admin
eval $(poetry env activate)
```

### 3️⃣ Instalar Dependencias del Frontend

```bash
# En una nueva terminal, desde la raíz del proyecto
cd portal
npm install
```

### 4️⃣ Configurar Variables de Entorno y Levantar las aplicaciones

Consulta el `README.md` de la carpeta admin para la configuración del proyecto y despliegue local.

---
## Accesos
- **Portal Web**: [http://localhost:3000](http://localhost:3000)
- **Panel de Administación**: [http://localhost:5000](http://localhost:5000)
- **PgAdmin**: [http://localhost:5050](http://localhost:5050)
- **MinIO**: [http://localhost:9001](http://localhost:9001)
