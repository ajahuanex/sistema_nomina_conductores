#!/bin/bash
# Script para ejecutar migraciones y poblar datos base

echo "=========================================="
echo "EJECUTANDO MIGRACIONES DE BASE DE DATOS"
echo "=========================================="

# Ejecutar migraciones
echo "Aplicando migraciones..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✓ Migraciones aplicadas exitosamente"
    
    echo ""
    echo "=========================================="
    echo "POBLANDO DATOS BASE"
    echo "=========================================="
    
    # Poblar datos base
    python scripts/seed_data.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Proceso completado exitosamente"
    else
        echo ""
        echo "✗ Error al poblar datos base"
        exit 1
    fi
else
    echo "✗ Error al aplicar migraciones"
    exit 1
fi
