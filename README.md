# Sistema de Facturación — API

Backend en FastAPI (Python) para el sistema de facturación. Arquitectura por capas (router → service → repository) organizada por features. Base de datos PostgreSQL (Supabase).

## Requisitos técnicos

- Python 3.11 o superior
- Cuenta de Supabase (base de datos PostgreSQL + Storage para fotos de productos)
- pip

## Arquitectura de carpetas

sistema_facturacion_api/
├── app/
│ ├── main.py # Punto de entrada: CORS, routers, exception handlers
│ ├── core/
│ │ ├── config.py # Configuración (variables de entorno)
│ │ ├── db.py # Pool de conexiones a PostgreSQL
│ │ ├── security.py # Hash de contraseñas, JWT
│ │ ├── deps.py # Dependencias de FastAPI (auth, permisos)
│ │ ├── permissions.py # Mapeo rol -> permisos
│ │ └── storage.py # Cliente de Supabase Storage (fotos)
│ └── features/
│ ├── auth/ # Login, /auth/me
│ ├── roles/ # CRUD de roles
│ ├── empleados/ # CRUD de empleados (retiro/reactivación)
│ ├── usuarios/ # Asignación de credenciales (tblseguridad)
│ ├── categorias/ # CRUD de categorías de producto
│ ├── productos/ # CRUD de productos + fotos
│ ├── clientes/ # CRUD de clientes
│ ├── facturas/ # Facturación (cálculo de totales, stock, estados)
│ └── dashboard/ # Indicadores generales
│ # cada feature contiene:
│ # router.py -> define los endpoints HTTP
│ # service.py -> reglas de negocio
│ # repository.py -> SQL parametrizado (sin ORM)
│ # schemas.py -> modelos Pydantic (entrada/salida, camelCase)
├── requirements.txt
├── .env.example
└── .env # (no versionado)


## Variables de entorno

Copia `.env.example` a `.env` y completa:

DATABASE_URL=postgresql://postgres.xxxx:TU_PASSWORD@aws-0-<region>.pooler.supabase.com:6543/postgres
JWT_SECRET=<cadena aleatoria de al menos 32 caracteres>
PASSWORD_PEPPER=<cadena aleatoria de al menos 16 caracteres>
JWT_EXPIRE_MINUTES=480
CORS_ORIGINS=http://localhost:5173
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=<service_role key de Supabase>
SUPABASE_STORAGE_BUCKET=<nombre del bucket para fotos de productos>


- `DATABASE_URL`: en Supabase → Settings → Database → Connection string → URI (usa el pooler en modo transacción, puerto 6543).
- `JWT_SECRET` y `PASSWORD_PEPPER`: generar con `python -c "import secrets; print(secrets.token_hex(32))"`.
- `SUPABASE_SERVICE_KEY`: en Supabase → Settings → API → **service_role** (nunca la `anon`).
- `SUPABASE_STORAGE_BUCKET`: bucket creado en Supabase → Storage.

**Nunca subas `.env` al repositorio.**

## Pasos para levantar el proyecto localmente

```bash
# 1. Clonar el repositorio
git clone https://github.com/soypadierna/sistema-facturacion-api.git
cd sistema-facturacion-api

# 2. Crear entorno virtual (opcional pero recomendado)
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
copy .env.example .env       # Windows
cp .env.example .env         # Linux/Mac
# Editar .env con tus credenciales reales

# 5. Ejecutar el servidor
uvicorn app.main:app --reload
```

La API queda disponible en `http://localhost:8000`. Documentación interactiva automática en `http://localhost:8000/docs`.

## Notas de seguridad y diseño

- Contraseñas nunca se guardan en texto plano: se hashean con scrypt + pepper (`s1$<hash>`), formato de 47 caracteres.
- Autenticación vía JWT (Bearer token), expira según `JWT_EXPIRE_MINUTES`.
- Autorización basada en roles: cada endpoint exige uno o más permisos (`core/permissions.py`).
- Los empleados no se eliminan físicamente; se "retiran" (`dtmretiro`), preservando el historial.
- Los totales de facturación siempre se calculan en el servidor (nunca se confía en el precio/total enviado por el cliente).
- Todo el acceso a datos usa SQL parametrizado (sin ORM), evitando inyección SQL.
