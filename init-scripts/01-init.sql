-- Script de inicialización de base de datos
-- Se ejecuta automáticamente al crear el contenedor de PostgreSQL

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- Para búsquedas de texto

-- Configurar timezone
SET timezone = 'America/Lima';

-- Crear índices adicionales si es necesario
-- (Los índices principales se crean con Alembic)
