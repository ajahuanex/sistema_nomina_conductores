"""
Tests para endpoints de documentos de conductores
"""
import pytest
import pytest_asyncio
import io
from uuid import uuid4
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conductor import Conductor, EstadoConductor
from app.models.empresa import Empresa
from app.models.user import Usuario, RolUsuario
from app.models.documento_conductor import DocumentoConductor, TipoDocumento


@pytest_asyncio.fixture
async def conductor_test(db_session: AsyncSession, gerente_usuario_with_empresa) -> Conductor:
    """Fixture para crear un conductor de prueba"""
    from datetime import date
    usuario, empresa = gerente_usuario_with_empresa
    
    conductor = Conductor(
        dni="12345678",
        nombres="Juan",
        apellidos="Pérez",
        fecha_nacimiento=date(1990, 1, 1),
        direccion="Av. Test 123",
        telefono="987654321",
        email="juan.perez@test.com",
        licencia_numero="Q12345678",
        licencia_categoria="A-IIIb",
        licencia_emision=date(2023, 1, 1),
        licencia_vencimiento=date(2028, 1, 1),
        empresa_id=empresa.id,
        estado=EstadoConductor.PENDIENTE
    )
    db_session.add(conductor)
    await db_session.commit()
    await db_session.refresh(conductor)
    return conductor


@pytest.mark.asyncio
class TestSubirDocumento:
    """Tests para subir documentos"""
    
    async def test_subir_documento_pdf_exitoso(
        self,
        client: AsyncClient,
        conductor_test: Conductor,
        auth_headers_gerente: dict
    ):
        """Test subir documento PDF exitosamente"""
        # Crear archivo PDF de prueba
        pdf_content = b"%PDF-1.4\n%Test PDF content"
        files = {
            "file": ("test_documento.pdf", io.BytesIO(pdf_content), "application/pdf")
        }
        data = {
            "tipo_documento": TipoDocumento.LICENCIA_CONDUCIR.value,
            "descripcion": "Licencia de conducir del conductor"
        }
        
        response = await client.post(
            f"/api/v1/conductores/{conductor_test.id}/documentos",
            files=files,
            data=data,
            headers=auth_headers_gerente
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nombre_archivo"] == "test_documento.pdf"
        assert data["tipo_documento"] == TipoDocumento.LICENCIA_CONDUCIR.value
        assert data["mensaje"] == "Documento subido exitosamente"
        assert "id" in data
    
    async def test_subir_documento_imagen_exitoso(
        self,
        client: AsyncClient,
        conductor_test: Conductor,
        auth_headers_gerente: dict
    ):
        """Test subir imagen exitosamente"""
        # Crear imagen de prueba (PNG simple)
        png_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        files = {
            "file": ("foto.png", io.BytesIO(png_content), "image/png")
        }
        data = {
            "tipo_documento": TipoDocumento.FOTO_CONDUCTOR.value
        }
        
        response = await client.post(
            f"/api/v1/conductores/{conductor_test.id}/documentos",
            files=files,
            data=data,
            headers=auth_headers_gerente
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nombre_archivo"] == "foto.png"
        assert data["tipo_documento"] == TipoDocumento.FOTO_CONDUCTOR.value
    
    async def test_subir_documento_tipo_no_permitido(
        self,
        client: AsyncClient,
        conductor_test: Conductor,
        auth_headers_gerente: dict
    ):
        """Test subir documento con tipo no permitido"""
        # Intentar subir archivo .txt
        txt_content = b"Este es un archivo de texto"
        files = {
            "file": ("documento.txt", io.BytesIO(txt_content), "text/plain")
        }
        data = {
            "tipo_documento": TipoDocumento.OTRO.value
        }
        
        response = await client.post(
            f"/api/v1/conductores/{conductor_test.id}/documentos",
            files=files,
            data=data,
            headers=auth_headers_gerente
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "no permitido" in response.json()["detail"].lower()
    
    async def test_subir_documento_tamano_excedido(
        self,
        client: AsyncClient,
        conductor_test: Conductor,
        auth_headers_gerente: dict
    ):
        """Test subir documento que excede el tamaño máximo"""
        # Crear archivo de más de 10MB
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        files = {
            "file": ("large_file.pdf", io.BytesIO(large_content), "application/pdf")
        }
        data = {
            "tipo_documento": TipoDocumento.LICENCIA_CONDUCIR.value
        }
        
        response = await client.post(
            f"/api/v1/conductores/{conductor_test.id}/documentos",
            files=files,
            data=data,
            headers=auth_headers_gerente
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "tamaño máximo" in response.json()["detail"].lower()
    
    async def test_subir_documento_conductor_no_existe(
        self,
        client: AsyncClient,
        auth_headers_gerente: dict
    ):
        """Test subir documento a conductor inexistente"""
        pdf_content = b"%PDF-1.4\n%Test"
        files = {
            "file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")
        }
        data = {
            "tipo_documento": TipoDocumento.LICENCIA_CONDUCIR.value
        }
        
        conductor_id_falso = uuid4()
        response = await client.post(
            f"/api/v1/conductores/{conductor_id_falso}/documentos",
            files=files,
            data=data,
            headers=auth_headers_gerente
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_subir_documento_sin_autenticacion(
        self,
        client: AsyncClient,
        conductor_test: Conductor
    ):
        """Test subir documento sin autenticación"""
        pdf_content = b"%PDF-1.4\n%Test"
        files = {
            "file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")
        }
        data = {
            "tipo_documento": TipoDocumento.LICENCIA_CONDUCIR.value
        }
        
        response = await client.post(
            f"/api/v1/conductores/{conductor_test.id}/documentos",
            files=files,
            data=data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
class TestListarDocumentos:
    """Tests para listar documentos"""
    
    async def test_listar_documentos_conductor(
        self,
        client: AsyncClient,
        conductor_test: Conductor,
        auth_headers_gerente: dict,
        db_session: AsyncSession
    ):
        """Test listar documentos de un conductor"""
        # Crear algunos documentos de prueba
        doc1 = DocumentoConductor(
            conductor_id=conductor_test.id,
            tipo_documento=TipoDocumento.LICENCIA_CONDUCIR,
            nombre_archivo="licencia.pdf",
            nombre_archivo_almacenado="uuid1.pdf",
            ruta_archivo="/uploads/uuid1.pdf",
            tipo_mime="application/pdf",
            tamano_bytes=1024
        )
        doc2 = DocumentoConductor(
            conductor_id=conductor_test.id,
            tipo_documento=TipoDocumento.CERTIFICADO_MEDICO,
            nombre_archivo="certificado.pdf",
            nombre_archivo_almacenado="uuid2.pdf",
            ruta_archivo="/uploads/uuid2.pdf",
            tipo_mime="application/pdf",
            tamano_bytes=2048
        )
        db_session.add_all([doc1, doc2])
        await db_session.commit()
        
        response = await client.get(
            f"/api/v1/conductores/{conductor_test.id}/documentos",
            headers=auth_headers_gerente
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert len(data["documentos"]) == 2
    
    async def test_listar_documentos_filtrado_por_tipo(
        self,
        client: AsyncClient,
        conductor_test: Conductor,
        auth_headers_gerente: dict,
        db_session: AsyncSession
    ):
        """Test listar documentos filtrados por tipo"""
        # Crear documentos de diferentes tipos
        doc1 = DocumentoConductor(
            conductor_id=conductor_test.id,
            tipo_documento=TipoDocumento.LICENCIA_CONDUCIR,
            nombre_archivo="licencia.pdf",
            nombre_archivo_almacenado="uuid1.pdf",
            ruta_archivo="/uploads/uuid1.pdf",
            tipo_mime="application/pdf",
            tamano_bytes=1024
        )
        doc2 = DocumentoConductor(
            conductor_id=conductor_test.id,
            tipo_documento=TipoDocumento.CERTIFICADO_MEDICO,
            nombre_archivo="certificado.pdf",
            nombre_archivo_almacenado="uuid2.pdf",
            ruta_archivo="/uploads/uuid2.pdf",
            tipo_mime="application/pdf",
            tamano_bytes=2048
        )
        db_session.add_all([doc1, doc2])
        await db_session.commit()
        
        response = await client.get(
            f"/api/v1/conductores/{conductor_test.id}/documentos",
            params={"tipo_documento": TipoDocumento.LICENCIA_CONDUCIR.value},
            headers=auth_headers_gerente
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["documentos"][0]["tipo_documento"] == TipoDocumento.LICENCIA_CONDUCIR.value
    
    async def test_listar_documentos_conductor_sin_documentos(
        self,
        client: AsyncClient,
        conductor_test: Conductor,
        auth_headers_gerente: dict
    ):
        """Test listar documentos de conductor sin documentos"""
        response = await client.get(
            f"/api/v1/conductores/{conductor_test.id}/documentos",
            headers=auth_headers_gerente
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["documentos"]) == 0


@pytest.mark.asyncio
class TestDescargarDocumento:
    """Tests para descargar documentos"""
    
    async def test_descargar_documento_exitoso(
        self,
        client: AsyncClient,
        conductor_test: Conductor,
        auth_headers_gerente: dict,
        db_session: AsyncSession,
        tmp_path
    ):
        """Test descargar documento exitosamente"""
        # Crear archivo temporal
        import os
        os.makedirs("uploads/conductores", exist_ok=True)
        test_file_path = "uploads/conductores/test_uuid.pdf"
        with open(test_file_path, "wb") as f:
            f.write(b"%PDF-1.4\n%Test content")
        
        # Crear documento en BD
        documento = DocumentoConductor(
            conductor_id=conductor_test.id,
            tipo_documento=TipoDocumento.LICENCIA_CONDUCIR,
            nombre_archivo="licencia.pdf",
            nombre_archivo_almacenado="test_uuid.pdf",
            ruta_archivo=test_file_path,
            tipo_mime="application/pdf",
            tamano_bytes=1024
        )
        db_session.add(documento)
        await db_session.commit()
        await db_session.refresh(documento)
        
        try:
            response = await client.get(
                f"/api/v1/conductores/{conductor_test.id}/documentos/{documento.id}",
                headers=auth_headers_gerente
            )
            
            assert response.status_code == status.HTTP_200_OK
            assert response.headers["content-type"] == "application/pdf"
        finally:
            # Limpiar archivo temporal
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
    
    async def test_descargar_documento_no_existe(
        self,
        client: AsyncClient,
        conductor_test: Conductor,
        auth_headers_gerente: dict
    ):
        """Test descargar documento inexistente"""
        documento_id_falso = uuid4()
        response = await client.get(
            f"/api/v1/conductores/{conductor_test.id}/documentos/{documento_id_falso}",
            headers=auth_headers_gerente
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
class TestEliminarDocumento:
    """Tests para eliminar documentos"""
    
    async def test_eliminar_documento_exitoso(
        self,
        client: AsyncClient,
        conductor_test: Conductor,
        auth_headers_gerente: dict,
        db_session: AsyncSession
    ):
        """Test eliminar documento exitosamente"""
        # Crear documento
        documento = DocumentoConductor(
            conductor_id=conductor_test.id,
            tipo_documento=TipoDocumento.LICENCIA_CONDUCIR,
            nombre_archivo="licencia.pdf",
            nombre_archivo_almacenado="uuid_test.pdf",
            ruta_archivo="/uploads/uuid_test.pdf",
            tipo_mime="application/pdf",
            tamano_bytes=1024
        )
        db_session.add(documento)
        await db_session.commit()
        await db_session.refresh(documento)
        
        response = await client.delete(
            f"/api/v1/conductores/{conductor_test.id}/documentos/{documento.id}",
            headers=auth_headers_gerente
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    async def test_eliminar_documento_sin_permisos(
        self,
        client: AsyncClient,
        conductor_test: Conductor,
        auth_headers_operario: dict,
        db_session: AsyncSession
    ):
        """Test eliminar documento sin permisos (Operario no puede eliminar)"""
        # Crear documento
        documento = DocumentoConductor(
            conductor_id=conductor_test.id,
            tipo_documento=TipoDocumento.LICENCIA_CONDUCIR,
            nombre_archivo="licencia.pdf",
            nombre_archivo_almacenado="uuid_test.pdf",
            ruta_archivo="/uploads/uuid_test.pdf",
            tipo_mime="application/pdf",
            tamano_bytes=1024
        )
        db_session.add(documento)
        await db_session.commit()
        await db_session.refresh(documento)
        
        response = await client.delete(
            f"/api/v1/conductores/{conductor_test.id}/documentos/{documento.id}",
            headers=auth_headers_operario
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
