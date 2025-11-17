"""
Tests de integración para endpoints de pagos
"""
import pytest
from httpx import AsyncClient
from datetime import date, timedelta
from decimal import Decimal
from app.models.habilitacion import EstadoPago


@pytest.mark.asyncio
class TestPagosEndpoints:
    """Tests para endpoints de pagos"""
    
    async def test_get_pagos(
        self,
        client: AsyncClient,
        auth_headers,
        habilitacion_factory,
        concepto_tupa_factory,
        pago_factory
    ):
        """Test obtener lista de pagos"""
        # Arrange
        concepto = await concepto_tupa_factory.create()
        for i in range(3):
            habilitacion = await habilitacion_factory.create()
            await pago_factory.create(
                habilitacion_id=habilitacion.id,
                concepto_tupa_id=concepto.id
            )
        
        # Act
        response = await client.get("/api/v1/pagos", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
    
    async def test_registrar_pago(
        self,
        client: AsyncClient,
        auth_headers,
        habilitacion_factory,
        concepto_tupa_factory
    ):
        """Test registrar un nuevo pago"""
        # Arrange
        habilitacion = await habilitacion_factory.create()
        concepto = await concepto_tupa_factory.create(monto=Decimal("50.00"))
        
        pago_data = {
            "habilitacion_id": str(habilitacion.id),
            "concepto_tupa_id": str(concepto.id),
            "numero_recibo": "REC-TEST-001",
            "monto": 50.00,
            "fecha_pago": date.today().isoformat(),
            "entidad_bancaria": "Banco de la Nación"
        }
        
        # Act
        response = await client.post(
            "/api/v1/pagos",
            json=pago_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["numero_recibo"] == "REC-TEST-001"
        assert data["estado"] == "pendiente"
    
    async def test_get_pago_by_id(
        self,
        client: AsyncClient,
        auth_headers,
        habilitacion_factory,
        concepto_tupa_factory,
        pago_factory
    ):
        """Test obtener pago por ID"""
        # Arrange
        habilitacion = await habilitacion_factory.create()
        concepto = await concepto_tupa_factory.create()
        pago = await pago_factory.create(
            habilitacion_id=habilitacion.id,
            concepto_tupa_id=concepto.id
        )
        
        # Act
        response = await client.get(
            f"/api/v1/pagos/{pago.id}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(pago.id)
    
    async def test_get_pago_by_habilitacion(
        self,
        client: AsyncClient,
        auth_headers,
        habilitacion_factory,
        concepto_tupa_factory,
        pago_factory
    ):
        """Test obtener pago por habilitación"""
        # Arrange
        habilitacion = await habilitacion_factory.create()
        concepto = await concepto_tupa_factory.create()
        pago = await pago_factory.create(
            habilitacion_id=habilitacion.id,
            concepto_tupa_id=concepto.id
        )
        
        # Act
        response = await client.get(
            f"/api/v1/pagos/habilitacion/{habilitacion.id}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["habilitacion_id"] == str(habilitacion.id)
    
    async def test_confirmar_pago(
        self,
        client: AsyncClient,
        auth_headers,
        habilitacion_factory,
        concepto_tupa_factory,
        pago_factory
    ):
        """Test confirmar un pago"""
        # Arrange
        habilitacion = await habilitacion_factory.create()
        concepto = await concepto_tupa_factory.create()
        pago = await pago_factory.create(
            habilitacion_id=habilitacion.id,
            concepto_tupa_id=concepto.id,
            estado=EstadoPago.PENDIENTE
        )
        
        # Act
        response = await client.post(
            f"/api/v1/pagos/{pago.id}/confirmar",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "confirmado"
    
    async def test_rechazar_pago(
        self,
        client: AsyncClient,
        auth_headers,
        habilitacion_factory,
        concepto_tupa_factory,
        pago_factory
    ):
        """Test rechazar un pago"""
        # Arrange
        habilitacion = await habilitacion_factory.create()
        concepto = await concepto_tupa_factory.create()
        pago = await pago_factory.create(
            habilitacion_id=habilitacion.id,
            concepto_tupa_id=concepto.id,
            estado=EstadoPago.PENDIENTE
        )
        
        # Act
        response = await client.post(
            f"/api/v1/pagos/{pago.id}/rechazar?motivo=Monto incorrecto",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "rechazado"
        assert "Monto incorrecto" in data["observaciones"]
    
    async def test_generar_orden_pago(
        self,
        client: AsyncClient,
        auth_headers,
        habilitacion_factory,
        concepto_tupa_factory
    ):
        """Test generar orden de pago"""
        # Arrange
        habilitacion = await habilitacion_factory.create()
        await concepto_tupa_factory.create(
            codigo="HAB-CONDUCTOR",
            monto=Decimal("50.00")
        )
        
        # Act
        response = await client.post(
            f"/api/v1/pagos/habilitacion/{habilitacion.id}/generar-orden",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "codigo_orden" in data
        assert data["habilitacion_id"] == str(habilitacion.id)
    
    async def test_generar_reporte_ingresos(
        self,
        client: AsyncClient,
        auth_headers,
        habilitacion_factory,
        concepto_tupa_factory,
        pago_factory
    ):
        """Test generar reporte de ingresos"""
        # Arrange
        concepto = await concepto_tupa_factory.create(monto=Decimal("50.00"))
        for i in range(3):
            habilitacion = await habilitacion_factory.create()
            await pago_factory.create(
                habilitacion_id=habilitacion.id,
                concepto_tupa_id=concepto.id,
                estado=EstadoPago.CONFIRMADO,
                monto=Decimal("50.00"),
                fecha_pago=date.today()
            )
        
        fecha_inicio = (date.today() - timedelta(days=1)).isoformat()
        fecha_fin = date.today().isoformat()
        
        # Act
        response = await client.get(
            f"/api/v1/pagos/reportes/ingresos?fecha_inicio={fecha_inicio}&fecha_fin={fecha_fin}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "total_pagos" in data
        assert "monto_total" in data
        assert data["total_pagos"] >= 3
