# 🧼 Sistema Lavandería - Aplicación de Escritorio

Este proyecto es parte del sistema de punto de venta para una lavandería.

## 🔐 Módulo actual: Inicio de sesión (Login)

- Validación de usuarios desde base de datos MySQL (`usuarios`)
- Verificación de correo y contraseña
- Control por rol (`admin`, `cajero`)
- Conexión vía archivo `config.json`

---

## 🛠 Requisitos

- Python 3.12 (instalado desde [python.org](https://www.python.org))
- MySQL Server local
- `mysql-connector-python` instalado

Instalación del conector:

pip install mysql-connector-python

Se cambia contraseña del archivo config.json