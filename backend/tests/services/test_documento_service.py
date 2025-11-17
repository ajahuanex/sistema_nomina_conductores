"""
Tests para DocumentoService
"""
import pytest
import io
from uuid import uuid4
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conductor import Conductor, EstadoConductor
from app.models.empresa import Empresa
from app.models.documento_conductor import DocumentoConductor, TipoDocumento
from app.services.documento_service import DocumentoService
from app.core.exceptions import RecursoNoEncontrado


@pytest.fixture
async def conductor_test(db_session: AsyncSession, empresa_test: Empresa) -> Conductor:
    """Fixture para crear un conductor de prueba"""
    conductor = Conductor(
        dni="87654321",
        nombres="María",
        apellidos="García",
        fecha_nacimiento="1992-05-15",
        direccion="Jr. Test 456",
        telefono="987654321",
        email="maria.garcia@test.com",
        licencia_numero="Q87654321",
        licencia_categoria="A-IIIb",
        licencia_emision="2023-01-01",
        licencia_vencimiento="2028-01-01",
        empresa_id=empresa_test.id,
        estado=EstadoConductor.PENDIENTE
    )
    db_session.add(conductor)
    await db_session.commit()
    await db_session.refresh(conductor)
    return conductor


@pytest.mark.asyncio
class TestDocumentoService:
    """Tests para DocumentoService"""
    
    async def test_subir_documento_exitoso(
        self,
        db_session: AsyncSession,
        conductor_test: Conductor
    ):
        """Test subir documento exitosamente"""
        service = DocumentoService(db_session)
        
        # Crear archivo de prueba
        pdf_content = b"%PDF-1.4\n%Test PDF content"
        upload_file = UploadFile(
            filename="test_licencia.pdf",
            file=io.BytesIO(pdf_content)
        )
        upload_file.content_type = "application/pdf"
        
        usuario_id = uuid4()
        
        documento = await service.subir_documento(
            conductor_id=conductor_test.id,
            upload_file=upload_file,
            tipo_documento=TipoDocumento.LICENCIA_CONDUCIR,
            descripcion="Licencia de conducir",
            usuario_id=usuario_id
        )
        
        assert documento.id is not None
        assert documento.conductor_id == conductor_test.id
        assert documento.tipo_documento == TipoDocumento.LICENCIA_CONDUCIR
        assert documento.nombre_archivo == "test_licencia.pdf"
        assert documento.tipo_mime == "application/pdf"
        assert documento.subido_por == usuario_id
        assert documento.descripcion == "Licencia de conducir"
    
    async def test_subir_documento_conductor_no_existe(
        self,
        db_session: AsyncSession
    ):
        """Test subir documento a conductor inexistente"""
        service = DocumentoService(db_session)
        
        pdf_content = b"%PDF-1.4\n%Test"
        upload_file = UploadFile(
            filename="test.pdf",
            file=io.BytesIO(pdf_content)
        )
        upload_file.content_type = "application/pdf"
        
        conductor_id_falso = uuid4()
        usuario_id = uuid4()
        
        with pytest.raises(RecursoNoEncontrado):
            await service.subir_documento(
                conductor_id=conductor_id_falso,
                upload_file=upload_file,
                tipo_documento=TipoDocumento.LICENCIA_CONDUCIR,
                descripcion=None,
                usuario_id=usuario_id
            )
    
    async def test_obtener_documentos_conductor(
        self,
        db_session: AsyncSession,
        conductor_test: Conductor
    ):
        """Test obtener documentos de un conductor"""
        service = DocumentoService(db_session)
        
        # Crear documentos de prueba
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
        
        documentos = await service.obtener_documentos_conductor(conductor_test.id)
        
        assert len(documentos) == 2
        assert all(doc.conductor_id == conductor_test.id for doc in documentos)
    
    async def test_obtener_documentos_filtrado_por_tipo(
        self,
        db_session: AsyncSession,
        conductor_test: Conductor
    ):
        """Test obtener documentos filtrados por tipo"""
        service = DocumentoService(db_session)
        
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
        
        documentos = await service.obtener_documentos_conductor(
            conductor_test.id,
            tipo_documento=TipoDocumento.LICENCIA_CONDUCIR
        )
        
        assert len(documentos) == 1
        assert documentos[0].tipo_documento == TipoDocumento.LICENCIA_CONDUCIR
    
    async def test_obtener_documento_por_id(
        self,
        db_session: AsyncSession,
        conductor_test: Conductor
    ):
        """Test obtener documento por ID"""
        service = DocumentoService(db_session)
        
        # Crear archivo temporal para la prueba
        import os
        os.makedirs("uploads/conductores", exist_ok=True)
        test_file_path = "uploads/conductores/test_doc.pdf"
        with open(test_file_path, "wb") as f:
            f.write(b"%PDF-1.4\n%Test")
        
        try:
            # Crear documento
            documento = DocumentoConductor(
                conductor_id=conductor_test.id,
                tipo_documento=TipoDocumento.LICENCIA_CONDUCIR,
                nombre_archivo="licencia.pdf",
                nombre_archivo_almacenado="test_doc.pdf",
                ruta_archivo=test_file_path,
                tipo_mime="application/pdf",
                tamano_bytes=1024
            )
            db_session.add(documento)
            await db_session.commit()
            await db_session.refresh(documento)
            
            # Obtener documento
            doc_obtenido = await service.obtener_documento(documento.id)
            
            assert doc_obtenido.id == documento.id
            assert doc_obtenido.conductor_id == conductor_test.id
        finally:
            # Limpiar
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
    
    async def test_obtener_documento_no_existe(
        self,
        db_session: AsyncSession
    ):
        """Test obtener documento inexistente"""
        service = DocumentoService(db_session)
        
        documento_id_falso = uuid4()
        
        with pytest.raises(RecursoNoEncontrado):
            await service.obtener_documento(documento_id_falso)
    
    async def test_eliminar_documento(
        self,
        db_session: AsyncSession,
        conductor_test: Conductor
    ):
        """Test eliminar documento"""
        service = DocumentoService(db_session)
        
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
        
        # Eliminar documento
        await service.eliminar_documento(documento.id)
        
        # Verificar que fue eliminado
        with pytest.raises(RecursoNoEncontrado):
            await service.obtener_documento(documento.id)
    
    async def test_contar_documentos_conductor(
        self,
        db_session: AsyncSession,
        conductor_test: Conductor
    ):
        """Test contar documentos de un conductor"""
        service = DocumentoService(db_session)
        
        # Crear documentos
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
        
        count = await service.contar_documentos_conductor(conductor_test.id)
        
        assert count == 2
