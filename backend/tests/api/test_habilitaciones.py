"""
Tests para endpoints de habilitaciones
"""
import pytest
from datetime import date, datetime, timedelta
from httpx import AsyncClient
from app.models.habilitacion import EstadoHabilitacion
from app.models.user import RolUsuario


@pytest.mark.asyncio
class TestHabilitacionesEndpoints:
    """Tests para endpoints de habilitaciones"""
    
    async def test_descargar_certificado_exitoso(
        self,
        client: AsyncClient,
        db_session,
        habilitacion_factory,
        director_usuario
    ):
        """Test descargar certificado exitosamente"""
        # Arrange
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.HABILITADO,
            fecha_habilitacion=datetime.utcnow(),
            vigencia_hasta=date.today() + timedelta(days=365)
        )
        habilitacion.habilitado_por = director_usuario.id
        await db_session.commit()
        
        # Act
        response = await client.get(
            f"/api/v1/habilitaciones/{habilitacion.id}/certificado",
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers["content-disposition"]
        assert habilitacion.codigo_habilitacion in response.headers["content-disposition"]
        
        # Verificar que es un PDF válido
        pdf_content = response.content
        assert pdf_content[:4] == b'%PDF'
        assert len(pdf_content) > 0
    
    async def test_descargar_certificado_sin_autenticacion(
        self,
        client: AsyncClient,
        habilitacion_factory
    ):
        """Test descargar certificado sin autenticación"""
        # Arrange
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.HABILITADO
        )
        
        # Act
        response = await client.get(
            f"/api/v1/habilitaciones/{habilitacion.id}/certificado"
        )
        
        # Assert
        # Returns 403 because RBAC decorator runs before authentication
        assert response.status_code == 403
    
    async def test_descargar_certificado_habilitacion_no_existe(
        self,
        client: AsyncClient,
        director_usuario
    ):
        """Test descargar certificado de habilitación inexistente"""
        # Arrange
        from uuid import uuid4
        from app.core.security import create_access_token
        
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        habilitacion_id_falso = uuid4()
        
        # Act
        response = await client.get(
            f"/api/v1/habilitaciones/{habilitacion_id_falso}/certificado",
            headers=headers
        )
        
        # Assert
        assert response.status_code == 404
        assert "Habilitacion" in response.json()["detail"]
    
    async def test_descargar_certificado_estado_invalido(
        self,
        client: AsyncClient,
        db_session,
        habilitacion_factory,
        director_usuario
    ):
        """Test descargar certificado de habilitación no habilitada"""
        # Arrange
        from app.core.security import create_access_token
        
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.PENDIENTE
        )
        
        # Act
        response = await client.get(
            f"/api/v1/habilitaciones/{habilitacion.id}/certificado",
            headers=headers
        )
        
        # Assert
        assert response.status_code == 400
        assert "HABILITADAS" in response.json()["detail"]
    
    async def test_descargar_certificado_como_gerente(
        self,
        client: AsyncClient,
        db_session,
        habilitacion_factory,
        usuario_gerente
    ):
        """Test descargar certificado como gerente"""
        # Arrange
        from app.core.security import create_access_token
        
        token = create_access_token({
            "sub": str(usuario_gerente.id),
            "email": usuario_gerente.email,
            "rol": usuario_gerente.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.HABILITADO,
            fecha_habilitacion=datetime.utcnow(),
            vigencia_hasta=date.today() + timedelta(days=365)
        )
        habilitacion.habilitado_por = usuario_gerente.id
        await db_session.commit()
        
        # Act
        response = await client.get(
            f"/api/v1/habilitaciones/{habilitacion.id}/certificado",
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
    
    async def test_descargar_certificado_como_operario(
        self,
        client: AsyncClient,
        db_session,
        habilitacion_factory,
        operario_usuario
    ):
        """Test descargar certificado como operario"""
        # Arrange
        from app.core.security import create_access_token
        
        token = create_access_token({
            "sub": str(operario_usuario.id),
            "email": operario_usuario.email,
            "rol": operario_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.HABILITADO,
            fecha_habilitacion=datetime.utcnow(),
            vigencia_hasta=date.today() + timedelta(days=365)
        )
        habilitacion.habilitado_por = operario_usuario.id
        await db_session.commit()
        
        # Act
        response = await client.get(
            f"/api/v1/habilitaciones/{habilitacion.id}/certificado",
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
    
    async def test_descargar_certificado_multiples_veces(
        self,
        client: AsyncClient,
        db_session,
        habilitacion_factory,
        director_usuario
    ):
        """Test descargar certificado múltiples veces"""
        # Arrange
        from app.core.security import create_access_token
        
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.HABILITADO,
            fecha_habilitacion=datetime.utcnow(),
            vigencia_hasta=date.today() + timedelta(days=365)
        )
        habilitacion.habilitado_por = director_usuario.id
        await db_session.commit()
        
        # Act - Primera descarga
        response1 = await client.get(
            f"/api/v1/habilitaciones/{habilitacion.id}/certificado",
            headers=headers
        )
        
        # Act - Segunda descarga
        response2 = await client.get(
            f"/api/v1/habilitaciones/{habilitacion.id}/certificado",
            headers=headers
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.content[:4] == b'%PDF'
        assert response2.content[:4] == b'%PDF'
        # Los PDFs deben ser similares (pueden variar ligeramente por timestamp)
        assert len(response1.content) > 0
        assert len(response2.content) > 0


    # ========================================================================
    # Tests para GET /api/v1/habilitaciones
    # ========================================================================
    
    async def test_listar_habilitaciones_exitoso(
        self,
        client: AsyncClient,
        db_session,
        habilitacion_factory,
        director_usuario
    ):
        """Test listar habilitaciones exitosamente"""
        # Arrange
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        # Crear varias habilitaciones
        await habilitacion_factory(estado=EstadoHabilitacion.PENDIENTE)
        await habilitacion_factory(estado=EstadoHabilitacion.EN_REVISION)
        await habilitacion_factory(estado=EstadoHabilitacion.HABILITADO)
        
        # Act
        response = await client.get(
            "/api/v1/habilitaciones",
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3
    
    async def test_listar_habilitaciones_con_filtro_estado(
        self,
        client: AsyncClient,
        db_session,
        habilitacion_factory,
        director_usuario
    ):
        """Test listar habilitaciones filtradas por estado"""
        # Arrange
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        # Crear habilitaciones con diferentes estados
        await habilitacion_factory(estado=EstadoHabilitacion.PENDIENTE)
        await habilitacion_factory(estado=EstadoHabilitacion.PENDIENTE)
        await habilitacion_factory(estado=EstadoHabilitacion.EN_REVISION)
        
        # Act
        response = await client.get(
            "/api/v1/habilitaciones?estado=pendiente",
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        for hab in data:
            assert hab["estado"] == "pendiente"
    
    async def test_listar_habilitaciones_con_paginacion(
        self,
        client: AsyncClient,
        db_session,
        habilitacion_factory,
        director_usuario
    ):
        """Test listar habilitaciones con paginación"""
        # Arrange
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        # Crear varias habilitaciones
        for _ in range(5):
            await habilitacion_factory(estado=EstadoHabilitacion.PENDIENTE)
        
        # Act
        response = await client.get(
            "/api/v1/habilitaciones?skip=0&limit=2",
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 2
    
    async def test_listar_habilitaciones_sin_autorizacion(
        self,
        client: AsyncClient,
        usuario_gerente
    ):
        """Test listar habilitaciones sin autorización (gerente no puede)"""
        # Arrange
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(usuario_gerente.id),
            "email": usuario_gerente.email,
            "rol": usuario_gerente.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        # Act
        response = await client.get(
            "/api/v1/habilitaciones",
            headers=headers
        )
        
        # Assert
        assert response.status_code == 403
    
    # ========================================================================
    # Tests para GET /api/v1/habilitaciones/pendientes
    # ========================================================================
    
    async def test_listar_habilitaciones_pendientes_exitoso(
        self,
        client: AsyncClient,
        db_session,
        habilitacion_factory,
        operario_usuario
    ):
        """Test listar habilitaciones pendientes exitosamente"""
        # Arrange
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(operario_usuario.id),
            "email": operario_usuario.email,
            "rol": operario_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        # Crear habilitaciones pendientes
        await habilitacion_factory(estado=EstadoHabilitacion.PENDIENTE)
        await habilitacion_factory(estado=EstadoHabilitacion.PENDIENTE)
        await habilitacion_factory(estado=EstadoHabilitacion.EN_REVISION)
        
        # Act
        response = await client.get(
            "/api/v1/habilitaciones/pendientes",
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        for hab in data:
            assert hab["estado"] == "pendiente"
    
    # ========================================================================
    # Tests para GET /api/v1/habilitaciones/{id}
    # ========================================================================
    
    async def test_obtener_habilitacion_exitoso(
        self,
        client: AsyncClient,
        habilitacion_factory,
        director_usuario
    ):
        """Test obtener habilitación por ID exitosamente"""
        # Arrange
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        habilitacion = await habilitacion_factory(estado=EstadoHabilitacion.PENDIENTE)
        
        # Act
        response = await client.get(
            f"/api/v1/habilitaciones/{habilitacion.id}",
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(habilitacion.id)
        assert data["codigo_habilitacion"] == habilitacion.codigo_habilitacion
        assert data["estado"] == habilitacion.estado.value
    
    async def test_obtener_habilitacion_no_existe(
        self,
        client: AsyncClient,
        director_usuario
    ):
        """Test obtener habilitación inexistente"""
        # Arrange
        from uuid import uuid4
        from app.core.security import create_access_token
        
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        habilitacion_id_falso = uuid4()
        
        # Act
        response = await client.get(
            f"/api/v1/habilitaciones/{habilitacion_id_falso}",
            headers=headers
        )
        
        # Assert
        assert response.status_code == 404
    
    # ========================================================================
    # Tests para POST /api/v1/habilitaciones/{id}/revisar
    # ========================================================================
    
    async def test_revisar_solicitud_exitoso(
        self,
        client: AsyncClient,
        db_session,
        habilitacion_factory,
        operario_usuario
    ):
        """Test revisar solicitud exitosamente"""
        # Arrange
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(operario_usuario.id),
            "email": operario_usuario.email,
            "rol": operario_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        habilitacion = await habilitacion_factory(estado=EstadoHabilitacion.PENDIENTE)
        
        # Act
        response = await client.post(
            f"/api/v1/habilitaciones/{habilitacion.id}/revisar",
            headers=headers,
            json={"observaciones": "Iniciando revisión de documentos"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "en_revision"
        assert data["revisado_por"] == str(operario_usuario.id)
        assert data["fecha_revision"] is not None
    
    async def test_revisar_solicitud_estado_invalido(
        self,
        client: AsyncClient,
        habilitacion_factory,
        operario_usuario
    ):
        """Test revisar solicitud con estado inválido"""
        # Arrange
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(operario_usuario.id),
            "email": operario_usuario.email,
            "rol": operario_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        habilitacion = await habilitacion_factory(estado=EstadoHabilitacion.APROBADO)
        
        # Act
        response = await client.post(
            f"/api/v1/habilitaciones/{habilitacion.id}/revisar",
            headers=headers,
            json={}
        )
        
        # Assert
        assert response.status_code == 400
        assert "PENDIENTE" in response.json()["detail"]
    
    # ========================================================================
    # Tests para POST /api/v1/habilitaciones/{id}/aprobar
    # ========================================================================
    
    async def test_aprobar_solicitud_exitoso(
        self,
        client: AsyncClient,
        db_session,
        habilitacion_factory,
        director_usuario
    ):
        """Test aprobar solicitud exitosamente"""
        # Arrange
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        habilitacion = await habilitacion_factory(estado=EstadoHabilitacion.EN_REVISION)
        
        # Act
        response = await client.post(
            f"/api/v1/habilitaciones/{habilitacion.id}/aprobar",
            headers=headers,
            json={"observaciones": "Documentos completos y válidos"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "aprobado"
        assert data["aprobado_por"] == str(director_usuario.id)
        assert data["fecha_aprobacion"] is not None
    
    async def test_aprobar_solicitud_sin_autorizacion(
        self,
        client: AsyncClient,
        habilitacion_factory,
        operario_usuario
    ):
        """Test aprobar solicitud sin autorización (operario no puede)"""
        # Arrange
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(operario_usuario.id),
            "email": operario_usuario.email,
            "rol": operario_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        habilitacion = await habilitacion_factory(estado=EstadoHabilitacion.EN_REVISION)
        
        # Act
        response = await client.post(
            f"/api/v1/habilitaciones/{habilitacion.id}/aprobar",
            headers=headers,
            json={}
        )
        
        # Assert
        assert response.status_code == 403
    
    # ========================================================================
    # Tests para POST /api/v1/habilitaciones/{id}/observar
    # ========================================================================
    
    async def test_observar_solicitud_exitoso(
        self,
        client: AsyncClient,
        db_session,
        habilitacion_factory,
        operario_usuario
    ):
        """Test observar solicitud exitosamente"""
        # Arrange
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(operario_usuario.id),
            "email": operario_usuario.email,
            "rol": operario_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        habilitacion = await habilitacion_factory(estado=EstadoHabilitacion.EN_REVISION)
        
        # Act
        response = await client.post(
            f"/api/v1/habilitaciones/{habilitacion.id}/observar",
            headers=headers,
            json={"observaciones": "Falta certificado médico actualizado y licencia vencida"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "observado"
        assert "Falta certificado médico" in data["observaciones"]
    
    async def test_observar_solicitud_observaciones_cortas(
        self,
        client: AsyncClient,
        habilitacion_factory,
        operario_usuario
    ):
        """Test observar solicitud con observaciones muy cortas"""
        # Arrange
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(operario_usuario.id),
            "email": operario_usuario.email,
            "rol": operario_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        habilitacion = await habilitacion_factory(estado=EstadoHabilitacion.EN_REVISION)
        
        # Act
        response = await client.post(
            f"/api/v1/habilitaciones/{habilitacion.id}/observar",
            headers=headers,
            json={"observaciones": "Mal"}
        )
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    # ========================================================================
    # Tests para POST /api/v1/habilitaciones/{id}/habilitar
    # ========================================================================
    
    async def test_habilitar_conductor_exitoso(
        self,
        client: AsyncClient,
        db_session,
        habilitacion_factory,
        pago_factory,
        director_usuario
    ):
        """Test habilitar conductor exitosamente"""
        # Arrange
        from app.core.security import create_access_token
        from app.models.habilitacion import EstadoPago
        
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        habilitacion = await habilitacion_factory(estado=EstadoHabilitacion.APROBADO)
        
        # Crear pago confirmado
        await pago_factory(
            habilitacion_id=habilitacion.id,
            estado=EstadoPago.CONFIRMADO
        )
        await db_session.commit()
        
        vigencia = date.today() + timedelta(days=365)
        
        # Act
        response = await client.post(
            f"/api/v1/habilitaciones/{habilitacion.id}/habilitar",
            headers=headers,
            json={
                "vigencia_hasta": vigencia.isoformat(),
                "observaciones": "Habilitación otorgada por cumplir requisitos"
            }
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "habilitado"
        assert data["habilitado_por"] == str(director_usuario.id)
        assert data["fecha_habilitacion"] is not None
        assert data["vigencia_hasta"] == vigencia.isoformat()
    
    async def test_habilitar_conductor_sin_pago(
        self,
        client: AsyncClient,
        habilitacion_factory,
        director_usuario
    ):
        """Test habilitar conductor sin pago confirmado"""
        # Arrange
        from app.core.security import create_access_token
        
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        habilitacion = await habilitacion_factory(estado=EstadoHabilitacion.APROBADO)
        vigencia = date.today() + timedelta(days=365)
        
        # Act
        response = await client.post(
            f"/api/v1/habilitaciones/{habilitacion.id}/habilitar",
            headers=headers,
            json={"vigencia_hasta": vigencia.isoformat()}
        )
        
        # Assert
        assert response.status_code == 400
        assert "pago" in response.json()["detail"].lower()
    
    async def test_habilitar_conductor_vigencia_pasada(
        self,
        client: AsyncClient,
        db_session,
        habilitacion_factory,
        pago_factory,
        director_usuario
    ):
        """Test habilitar conductor con fecha de vigencia pasada"""
        # Arrange
        from app.core.security import create_access_token
        from app.models.habilitacion import EstadoPago
        
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        habilitacion = await habilitacion_factory(estado=EstadoHabilitacion.APROBADO)
        await pago_factory(
            habilitacion_id=habilitacion.id,
            estado=EstadoPago.CONFIRMADO
        )
        await db_session.commit()
        
        vigencia_pasada = date.today() - timedelta(days=1)
        
        # Act
        response = await client.post(
            f"/api/v1/habilitaciones/{habilitacion.id}/habilitar",
            headers=headers,
            json={"vigencia_hasta": vigencia_pasada.isoformat()}
        )
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    # ========================================================================
    # Tests para POST /api/v1/habilitaciones/{id}/suspender
    # ========================================================================
    
    async def test_suspender_habilitacion_exitoso(
        self,
        client: AsyncClient,
        db_session,
        habilitacion_factory,
        director_usuario
    ):
        """Test suspender habilitación exitosamente"""
        # Arrange
        from app.core.security import create_access_token
        
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.HABILITADO,
            fecha_habilitacion=datetime.utcnow(),
            vigencia_hasta=date.today() + timedelta(days=365)
        )
        
        # Act
        response = await client.post(
            f"/api/v1/habilitaciones/{habilitacion.id}/suspender",
            headers=headers,
            json={"motivo": "Conductor registró infracción muy grave según resolución N° 123-2024"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "SUSPENDIDO" in data["observaciones"]
        assert "infracción muy grave" in data["observaciones"]
    
    async def test_suspender_habilitacion_sin_autorizacion(
        self,
        client: AsyncClient,
        habilitacion_factory,
        operario_usuario
    ):
        """Test suspender habilitación sin autorización (operario no puede)"""
        # Arrange
        from app.core.security import create_access_token
        
        token = create_access_token({
            "sub": str(operario_usuario.id),
            "email": operario_usuario.email,
            "rol": operario_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        habilitacion = await habilitacion_factory(estado=EstadoHabilitacion.HABILITADO)
        
        # Act
        response = await client.post(
            f"/api/v1/habilitaciones/{habilitacion.id}/suspender",
            headers=headers,
            json={"motivo": "Motivo de suspensión válido con más de 20 caracteres"}
        )
        
        # Assert
        assert response.status_code == 403
    
    async def test_suspender_habilitacion_motivo_corto(
        self,
        client: AsyncClient,
        habilitacion_factory,
        director_usuario
    ):
        """Test suspender habilitación con motivo muy corto"""
        # Arrange
        from app.core.security import create_access_token
        
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        habilitacion = await habilitacion_factory(estado=EstadoHabilitacion.HABILITADO)
        
        # Act
        response = await client.post(
            f"/api/v1/habilitaciones/{habilitacion.id}/suspender",
            headers=headers,
            json={"motivo": "Mal"}
        )
        
        # Assert
        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
class TestHabilitacionesFlujosCompletos:
    """Tests de integración para flujos completos de habilitación"""
    
    async def test_flujo_completo_habilitacion_exitosa(
        self,
        client: AsyncClient,
        db_session,
        conductor_factory,
        pago_factory,
        operario_usuario,
        director_usuario
    ):
        """Test flujo completo: pendiente -> revisión -> aprobación -> habilitación"""
        from app.core.security import create_access_token
        from app.services.habilitacion_service import HabilitacionService
        from app.models.habilitacion import EstadoPago
        
        # 1. Crear conductor y solicitud de habilitación
        conductor = await conductor_factory()
        service = HabilitacionService(db_session)
        habilitacion = await service.crear_solicitud(conductor.id)
        
        # 2. Operario revisa la solicitud
        token_operario = create_access_token({
            "sub": str(operario_usuario.id),
            "email": operario_usuario.email,
            "rol": operario_usuario.rol.value
        })
        headers_operario = {"Authorization": f"Bearer {token_operario}"}
        
        response = await client.post(
            f"/api/v1/habilitaciones/{habilitacion.id}/revisar",
            headers=headers_operario,
            json={"observaciones": "Iniciando revisión"}
        )
        assert response.status_code == 200
        assert response.json()["estado"] == "en_revision"
        
        # 3. Director aprueba la solicitud
        token_director = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers_director = {"Authorization": f"Bearer {token_director}"}
        
        response = await client.post(
            f"/api/v1/habilitaciones/{habilitacion.id}/aprobar",
            headers=headers_director,
            json={"observaciones": "Documentos válidos"}
        )
        assert response.status_code == 200
        assert response.json()["estado"] == "aprobado"
        
        # 4. Registrar pago
        habilitacion_id = habilitacion.id  # Store ID before expiring
        pago = await pago_factory(
            habilitacion_id=habilitacion_id,
            estado=EstadoPago.CONFIRMADO
        )
        await db_session.commit()
        await db_session.refresh(pago)
        
        # Expire all objects to force reload from database
        db_session.expire_all()
        
        # 5. Director habilita al conductor
        vigencia = date.today() + timedelta(days=365)
        response = await client.post(
            f"/api/v1/habilitaciones/{habilitacion_id}/habilitar",
            headers=headers_director,
            json={
                "vigencia_hasta": vigencia.isoformat(),
                "observaciones": "Habilitación otorgada"
            }
        )
        if response.status_code != 200:
            print(f"Error response: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "habilitado"
        assert data["vigencia_hasta"] == vigencia.isoformat()
        
        # 6. Descargar certificado
        response = await client.get(
            f"/api/v1/habilitaciones/{habilitacion.id}/certificado",
            headers=headers_director
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
    
    async def test_flujo_habilitacion_con_observaciones(
        self,
        client: AsyncClient,
        db_session,
        conductor_factory,
        operario_usuario,
        director_usuario
    ):
        """Test flujo con observaciones: pendiente -> revisión -> observado"""
        from app.core.security import create_access_token
        from app.services.habilitacion_service import HabilitacionService
        
        # 1. Crear conductor y solicitud
        conductor = await conductor_factory()
        service = HabilitacionService(db_session)
        habilitacion = await service.crear_solicitud(conductor.id)
        
        # 2. Operario revisa
        token_operario = create_access_token({
            "sub": str(operario_usuario.id),
            "email": operario_usuario.email,
            "rol": operario_usuario.rol.value
        })
        headers_operario = {"Authorization": f"Bearer {token_operario}"}
        
        response = await client.post(
            f"/api/v1/habilitaciones/{habilitacion.id}/revisar",
            headers=headers_operario,
            json={}
        )
        assert response.status_code == 200
        
        # 3. Operario observa la solicitud
        response = await client.post(
            f"/api/v1/habilitaciones/{habilitacion.id}/observar",
            headers=headers_operario,
            json={"observaciones": "Falta certificado médico vigente y licencia está por vencer"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "observado"
        assert "certificado médico" in data["observaciones"]
    
    async def test_flujo_suspension_habilitacion(
        self,
        client: AsyncClient,
        db_session,
        habilitacion_factory,
        pago_factory,
        director_usuario
    ):
        """Test flujo de suspensión de habilitación activa"""
        from app.core.security import create_access_token
        from app.models.habilitacion import EstadoPago
        
        # 1. Crear habilitación activa
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.HABILITADO,
            fecha_habilitacion=datetime.utcnow(),
            vigencia_hasta=date.today() + timedelta(days=365)
        )
        
        # 2. Director suspende la habilitación
        token_director = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers_director = {"Authorization": f"Bearer {token_director}"}
        
        response = await client.post(
            f"/api/v1/habilitaciones/{habilitacion.id}/suspender",
            headers=headers_director,
            json={"motivo": "Conductor registró infracción muy grave según resolución administrativa"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "SUSPENDIDO" in data["observaciones"]
        assert "infracción muy grave" in data["observaciones"]
