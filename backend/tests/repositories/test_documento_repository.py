"""
Tests para DocumentoRepository
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conductor import Conductor, EstadoConductor
from app.models.empresa import Empresa
from app.models.documento_conductor import DocumentoConductor, TipoDocumento
from app.repositories.documento_repository import DocumentoRepository


@pytest.fixture
async def conductor_test(db_session: AsyncSession, empresa_test: Empresa) -> Conductor:
    """Fixture para crear un conductor de prueba"""
    conductor = Conductor(
        dni="11223344",
        nombres="Pedro",
        apellidos="López",
        fecha_nacimiento="1988-03-20",
        direccion="Av. Prueba 789",
        telefono="987654321",
        email="pedro.lopez@test.com",
        licencia_numero="Q11223344",
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
class TestDocumentoRepository:
    """Tests para DocumentoRepository"""
    
    async def test_create_documento(
        self,
        db_session: AsyncSession,
        conductor_test: Conductor
    ):
        """Test crear documento"""
        repo = DocumentoRepository(db_session)
        
        documento = DocumentoConductor(
            conductor_id=conductor_test.id,
            tipo_documento=TipoDocumento.LICENCIA_CONDUCIR,
            nombre_archivo="licencia.pdf",
            nombre_archivo_almacenado="uuid_test.pdf",
            ruta_archivo="/uploads/uuid_test.pdf",
            tipo_mime="application/pdf",
            tamano_bytes=1024,
            descripcion="Licencia de conducir"
        )
        
        documento_creado = await repo.create(documento)
        await db_session.commit()
        
        assert documento_creado.id is not None
        assert documento_creado.conductor_id == conductor_test.id
        assert documento_creado.tipo_documento == TipoDocumento.LICENCIA_CONDUCIR
    
    async def test_get_by_conductor(
        self,
        db_session: AsyncSession,
        conductor_test: Conductor
    ):
        """Test obtener documentos por conductor"""
        repo = DocumentoRepository(db_session)
        
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
        
        documentos = await repo.get_by_conductor(conductor_test.id)
        
        assert len(documentos) == 2
        assert all(doc.conductor_id == conductor_test.id for doc in documentos)
    
    async def test_get_by_conductor_con_filtro_tipo(
        self,
        db_session: AsyncSession,
        conductor_test: Conductor
    ):
        """Test obtener documentos por conductor filtrado por tipo"""
        repo = DocumentoRepository(db_session)
        
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
        doc3 = DocumentoConductor(
            conductor_id=conductor_test.id,
            tipo_documento=TipoDocumento.LICENCIA_CONDUCIR,
            nombre_archivo="licencia_reverso.pdf",
            nombre_archivo_almacenado="uuid3.pdf",
            ruta_archivo="/uploads/uuid3.pdf",
            tipo_mime="application/pdf",
            tamano_bytes=1024
        )
        db_session.add_all([doc1, doc2, doc3])
        await db_session.commit()
        
        documentos = await repo.get_by_conductor(
            conductor_test.id,
            tipo_documento=TipoDocumento.LICENCIA_CONDUCIR
        )
        
        assert len(documentos) == 2
        assert all(doc.tipo_documento == TipoDocumento.LICENCIA_CONDUCIR for doc in documentos)
    
    async def test_get_by_nombre_almacenado(
        self,
        db_session: AsyncSession,
        conductor_test: Conductor
    ):
        """Test obtener documento por nombre almacenado"""
        repo = DocumentoRepository(db_session)
        
        documento = DocumentoConductor(
            conductor_id=conductor_test.id,
            tipo_documento=TipoDocumento.LICENCIA_CONDUCIR,
            nombre_archivo="licencia.pdf",
            nombre_archivo_almacenado="uuid_unico.pdf",
            ruta_archivo="/uploads/uuid_unico.pdf",
            tipo_mime="application/pdf",
            tamano_bytes=1024
        )
        db_session.add(documento)
        await db_session.commit()
        
        doc_encontrado = await repo.get_by_nombre_almacenado("uuid_unico.pdf")
        
        assert doc_encontrado is not None
        assert doc_encontrado.nombre_archivo_almacenado == "uuid_unico.pdf"
    
    async def test_get_by_nombre_almacenado_no_existe(
        self,
        db_session: AsyncSession
    ):
        """Test obtener documento por nombre almacenado que no existe"""
        repo = DocumentoRepository(db_session)
        
        doc_encontrado = await repo.get_by_nombre_almacenado("no_existe.pdf")
        
        assert doc_encontrado is None
    
    async def test_count_by_conductor(
        self,
        db_session: AsyncSession,
        conductor_test: Conductor
    ):
        """Test contar documentos por conductor"""
        repo = DocumentoRepository(db_session)
        
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
        doc3 = DocumentoConductor(
            conductor_id=conductor_test.id,
            tipo_documento=TipoDocumento.FOTO_CONDUCTOR,
            nombre_archivo="foto.jpg",
            nombre_archivo_almacenado="uuid3.jpg",
            ruta_archivo="/uploads/uuid3.jpg",
            tipo_mime="image/jpeg",
            tamano_bytes=512
        )
        db_session.add_all([doc1, doc2, doc3])
        await db_session.commit()
        
        count = await repo.count_by_conductor(conductor_test.id)
        
        assert count == 3
    
    async def test_delete_by_conductor(
        self,
        db_session: AsyncSession,
        conductor_test: Conductor
    ):
        """Test eliminar todos los documentos de un conductor"""
        repo = DocumentoRepository(db_session)
        
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
        
        # Eliminar todos los documentos
        count = await repo.delete_by_conductor(conductor_test.id)
        await db_session.commit()
        
        assert count == 2
        
        # Verificar que fueron eliminados
        documentos_restantes = await repo.get_by_conductor(conductor_test.id)
        assert len(documentos_restantes) == 0
    
    async def test_get_by_id(
        self,
        db_session: AsyncSession,
        conductor_test: Conductor
    ):
        """Test obtener documento por ID"""
        repo = DocumentoRepository(db_session)
        
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
        
        doc_encontrado = await repo.get_by_id(documento.id)
        
        assert doc_encontrado is not None
        assert doc_encontrado.id == documento.id
        assert doc_encontrado.conductor_id == conductor_test.id
    
    async def test_delete(
        self,
        db_session: AsyncSession,
        conductor_test: Conductor
    ):
        """Test eliminar documento por ID"""
        repo = DocumentoRepository(db_session)
        
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
        
        # Eliminar
        await repo.delete(documento.id)
        await db_session.commit()
        
        # Verificar que fue eliminado
        doc_eliminado = await repo.get_by_id(documento.id)
        assert doc_eliminado is None
