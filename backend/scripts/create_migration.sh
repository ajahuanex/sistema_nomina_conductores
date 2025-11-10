#!/bin/bash
# Script para crear migración de base de datos

echo "Creando migración de base de datos..."
alembic revision --autogenerate -m "Add all models: infracciones, asignaciones, auditoria, notificaciones"

echo "Migración creada exitosamente"
