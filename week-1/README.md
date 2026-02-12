# 🌿 Proyecto Semana 01: API de Gestión de Cultivos (AgroTech)

Este repositorio contiene la implementación de una API básica para el dominio de **Agricultura y AgroTech**, desarrollada como proyecto integrador de la primera semana del bootcamp.

---

## 🏛️ Información del Dominio

| Concepto | Detalle Adaptado |
| :--- | :--- |
| **Dominio** | Gestión de Cultivos |
| **Entidad Principal** | `Crop` (Cultivo) |
| **Actor Clave** | `Farmer` (Agricultor) |
| **Servicio** | `Schedule` (Calendario de Riego/Mantenimiento) |

---

## 📋 Descripción del Proyecto

El sistema permite gestionar la información técnica de los sembradíos, saludar al personal de campo en múltiples idiomas y verificar las tareas programadas según la hora del día, asegurando un monitoreo constante del estado de salud de la API.

### 🎯 Objetivos Cumplidos
* ✅ **Dockerización:** Implementación completa con Docker y Docker Compose.
* ✅ **Python Moderno:** Uso de *Type hints* y Python 3.14.
* ✅ **FastAPI:** Creación de endpoints asíncronos con validación de parámetros.
* ✅ **Documentación:** Integración automática con Swagger UI.

---

## 📦 Requisitos Funcionales Implementados

### RF-01: Endpoint de Información
**Ruta:** `GET /`  
Retorna los datos básicos del sistema AgroTech para confirmar la identidad de la API.

### RF-02: Bienvenida al Agricultor
**Ruta:** `GET /farmer/{name}`  
Recibe al personal de campo. Soporta parámetros de consulta para el idioma (`es`, `en`, `fr`).

### RF-03: Información Técnica del Cultivo
**Ruta:** `GET /crop/{identifier}/info`  
Permite consultar datos de un cultivo específico. El parámetro `detail_level` permite obtener:
* **Basic:** ID, tipo y salud general.
* **Full:** PH del suelo, última fecha de riego y sensores.

### RF-04: Gestión de Tareas por Horario
**Ruta:** `GET /service/schedule`  
Lógica de negocio aplicada:
* **06-11:** Fertilización.
* **12-17:** Mantenimiento.
* **18-05:** Riego automático.

### RF-05: Health Check
**Ruta:** `GET /health`  
Verifica el estado de conexión de los sistemas de monitoreo agrícola.

---

## 🏗️ Guía de Ejecución

Para levantar el proyecto en un entorno local aislado:

1. **Construir la imagen y arrancar el contenedor:**
   ```bash
   docker compose up --build
Acceder a la documentación interactiva:
2. **Visita [http://localhost:8000/docs](http://localhost:8000/docs) para probar todos los endpoints directamente desde el navegador.**
