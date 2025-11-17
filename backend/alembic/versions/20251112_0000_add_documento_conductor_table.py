"""Add documento_conductor table

Revision ID: add_documento_conductor
Revises: 28c93c65a4bf
Create Date: 2025-11-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_documento_conductor'
down_revision: Union[str, None] = '28c93c65a4bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type if it doesn't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE tipodocumento AS ENUM (
                'licencia_conducir',
                'certificado_medico',
                'antecedentes_penales',
                'antecedentes_policiales',
                'antecedentes_judiciales',
                'foto_conductor',
                'otro'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$
    """)
    
    # Create documentos_conductor table
    op.execute("""
        CREATE TABLE documentos_conductor (
            id UUID NOT NULL,
            conductor_id UUID NOT NULL,
            tipo_documento tipodocumento NOT NULL,
            nombre_archivo VARCHAR(255) NOT NULL,
            nombre_archivo_almacenado VARCHAR(255) NOT NULL,
            ruta_archivo VARCHAR(500) NOT NULL,
            tipo_mime VARCHAR(100) NOT NULL,
            tamano_bytes INTEGER NOT NULL,
            descripcion VARCHAR(500),
            subido_por UUID,
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
            updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
            CONSTRAINT pk_documentos_conductor PRIMARY KEY (id),
            CONSTRAINT fk_documentos_conductor_conductor_id FOREIGN KEY(conductor_id) REFERENCES conductores (id) ON DELETE CASCADE,
            CONSTRAINT fk_documentos_conductor_subido_por FOREIGN KEY(subido_por) REFERENCES usuarios (id) ON DELETE SET NULL,
            CONSTRAINT uq_documentos_conductor_nombre_archivo_almacenado UNIQUE (nombre_archivo_almacenado)
        )
    """)
    
    # Create indexes
    op.execute("CREATE INDEX idx_documento_conductor_tipo ON documentos_conductor (conductor_id, tipo_documento)")
    op.execute("CREATE INDEX ix_documentos_conductor_conductor_id ON documentos_conductor (conductor_id)")
    op.execute("CREATE INDEX ix_documentos_conductor_subido_por ON documentos_conductor (subido_por)")
    op.execute("CREATE INDEX ix_documentos_conductor_tipo_documento ON documentos_conductor (tipo_documento)")


def downgrade() -> None:
    # Drop everything using raw SQL
    op.execute("DROP INDEX IF EXISTS ix_documentos_conductor_tipo_documento")
    op.execute("DROP INDEX IF EXISTS ix_documentos_conductor_subido_por")
    op.execute("DROP INDEX IF EXISTS ix_documentos_conductor_conductor_id")
    op.execute("DROP INDEX IF EXISTS idx_documento_conductor_tipo")
    op.execute("DROP TABLE IF EXISTS documentos_conductor")
    op.execute("DROP TYPE IF EXISTS tipodocumento")
