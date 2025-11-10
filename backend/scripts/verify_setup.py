#!/usr/bin/env python3
"""
Script para verificar que la configuración de base de datos está correcta
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

def verify_imports():
    """Verificar que todos los imports necesarios funcionan"""
    print("🔍 Verificando imports...")
    
    try:
        from app.core.config import settings
        print("  ✅ app.core.config")
    except ImportError as e:
        print(f"  ❌ app.core.config: {e}")
        return False
    
    try:
        from app.core.database import Base, engine, AsyncSessionLocal
        print("  ✅ app.core.database")
    except ImportError as e:
        print(f"  ❌ app.core.database: {e}")
        return False
    
    try:
        from app.models.base import BaseModel
        print("  ✅ app.models.base")
    except ImportError as e:
        print(f"  ❌ app.models.base: {e}")
        return False
    
    try:
        from app.models.user import Usuario
        print("  ✅ app.models.user")
    except ImportError as e:
        print(f"  ❌ app.models.user: {e}")
        return False
    
    return True


def verify_base_model():
    """Verificar que BaseModel tiene los campos requeridos"""
    print("\n🔍 Verificando BaseModel...")
    
    from app.models.base import BaseModel
    
    required_fields = ['id', 'created_at', 'updated_at']
    
    for field in required_fields:
        if hasattr(BaseModel, field):
            print(f"  ✅ Campo '{field}' presente")
        else:
            print(f"  ❌ Campo '{field}' faltante")
            return False
    
    return True


def verify_alembic_config():
    """Verificar configuración de Alembic"""
    print("\n🔍 Verificando configuración de Alembic...")
    
    alembic_ini = Path(__file__).resolve().parents[1] / "alembic.ini"
    if alembic_ini.exists():
        print("  ✅ alembic.ini existe")
    else:
        print("  ❌ alembic.ini no encontrado")
        return False
    
    alembic_dir = Path(__file__).resolve().parents[1] / "alembic"
    if alembic_dir.exists():
        print("  ✅ directorio alembic/ existe")
    else:
        print("  ❌ directorio alembic/ no encontrado")
        return False
    
    env_py = alembic_dir / "env.py"
    if env_py.exists():
        print("  ✅ alembic/env.py existe")
    else:
        print("  ❌ alembic/env.py no encontrado")
        return False
    
    versions_dir = alembic_dir / "versions"
    if versions_dir.exists():
        print("  ✅ alembic/versions/ existe")
    else:
        print("  ❌ alembic/versions/ no encontrado")
        return False
    
    return True


def verify_dependencies():
    """Verificar que las dependencias están instaladas"""
    print("\n🔍 Verificando dependencias...")
    
    dependencies = [
        'sqlalchemy',
        'alembic',
        'asyncpg',
        'pydantic',
        'fastapi'
    ]
    
    all_installed = True
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✅ {dep}")
        except ImportError:
            print(f"  ❌ {dep} no instalado")
            all_installed = False
    
    return all_installed


def main():
    """Ejecutar todas las verificaciones"""
    print("=" * 60)
    print("Verificación de Configuración de Base de Datos")
    print("=" * 60)
    
    checks = [
        ("Imports", verify_imports),
        ("BaseModel", verify_base_model),
        ("Alembic", verify_alembic_config),
        ("Dependencias", verify_dependencies)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error en verificación de {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Resumen de Verificación")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 ¡Todas las verificaciones pasaron exitosamente!")
        print("\n📝 Próximos pasos:")
        print("  1. Crear modelos adicionales en app/models/")
        print("  2. Importar modelos en alembic/env.py")
        print("  3. Crear migración: alembic revision --autogenerate -m 'mensaje'")
        print("  4. Aplicar migración: alembic upgrade head")
        return 0
    else:
        print("\n⚠️  Algunas verificaciones fallaron. Revisa los errores arriba.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
