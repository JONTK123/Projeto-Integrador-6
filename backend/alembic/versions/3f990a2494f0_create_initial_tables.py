"""Create initial tables

Revision ID: 3f990a2494f0
Revises: 
Create Date: 2025-10-31 14:39:03.377712

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f990a2494f0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables for LightFM recommendation system."""
    
    # Create Universidades table
    op.create_table(
        'universidades',
        sa.Column('id_universidade', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('cidade', sa.String(length=100), nullable=False),
        sa.Column('estado', sa.String(length=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id_universidade')
    )
    op.create_index(op.f('ix_universidades_id_universidade'), 'universidades', ['id_universidade'], unique=False)

    # Create Categorias_Estabelecimentos table
    op.create_table(
        'categorias_estabelecimentos',
        sa.Column('id_categoria', sa.Integer(), nullable=False),
        sa.Column('nome_categoria', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id_categoria'),
        sa.UniqueConstraint('nome_categoria')
    )
    op.create_index(op.f('ix_categorias_estabelecimentos_id_categoria'), 'categorias_estabelecimentos', ['id_categoria'], unique=False)

    # Create Preferencias table
    op.create_table(
        'preferencias',
        sa.Column('id_preferencia', sa.Integer(), nullable=False),
        sa.Column('nome_preferencia', sa.String(length=100), nullable=False),
        sa.Column('tipo_preferencia', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id_preferencia')
    )
    op.create_index(op.f('ix_preferencias_id_preferencia'), 'preferencias', ['id_preferencia'], unique=False)

    # Create Usuarios table
    op.create_table(
        'usuarios',
        sa.Column('id_usuario', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('senha_hash', sa.String(length=255), nullable=False),
        sa.Column('curso', sa.String(length=100), nullable=True),
        sa.Column('idade', sa.Integer(), nullable=True),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('id_universidade', sa.Integer(), nullable=True),
        sa.Column('data_cadastro', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['id_universidade'], ['universidades.id_universidade'], ),
        sa.PrimaryKeyConstraint('id_usuario'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_usuarios_email'), 'usuarios', ['email'], unique=True)
    op.create_index(op.f('ix_usuarios_id_usuario'), 'usuarios', ['id_usuario'], unique=False)

    # Create Estabelecimentos table
    op.create_table(
        'estabelecimentos',
        sa.Column('id_estabelecimento', sa.Integer(), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=False),
        sa.Column('endereco', sa.String(length=255), nullable=False),
        sa.Column('cidade', sa.String(length=100), nullable=False),
        sa.Column('horario_funcionamento', sa.String(length=100), nullable=True),
        sa.Column('dono_nome', sa.String(length=255), nullable=True),
        sa.Column('dono_email', sa.String(length=255), nullable=True),
        sa.Column('id_categoria', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['id_categoria'], ['categorias_estabelecimentos.id_categoria'], ),
        sa.PrimaryKeyConstraint('id_estabelecimento')
    )
    op.create_index(op.f('ix_estabelecimentos_id_estabelecimento'), 'estabelecimentos', ['id_estabelecimento'], unique=False)

    # Create Usuario_Preferencia table
    op.create_table(
        'usuario_preferencia',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_usuario', sa.Integer(), nullable=False),
        sa.Column('id_preferencia', sa.Integer(), nullable=False),
        sa.Column('peso', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['id_preferencia'], ['preferencias.id_preferencia'], ),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_usuario_preferencia_id'), 'usuario_preferencia', ['id'], unique=False)

    # Create Estabelecimento_Preferencia table
    op.create_table(
        'estabelecimento_preferencia',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_estabelecimento', sa.Integer(), nullable=False),
        sa.Column('id_preferencia', sa.Integer(), nullable=False),
        sa.Column('peso', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['id_estabelecimento'], ['estabelecimentos.id_estabelecimento'], ),
        sa.ForeignKeyConstraint(['id_preferencia'], ['preferencias.id_preferencia'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_estabelecimento_preferencia_id'), 'estabelecimento_preferencia', ['id'], unique=False)

    # Create Recomendacao_Usuario table
    op.create_table(
        'recomendacao_usuario',
        sa.Column('id_recomendacao', sa.Integer(), nullable=False),
        sa.Column('id_usuario1', sa.Integer(), nullable=False),
        sa.Column('id_usuario2', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('data_recomendacao', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['id_usuario1'], ['usuarios.id_usuario'], ),
        sa.ForeignKeyConstraint(['id_usuario2'], ['usuarios.id_usuario'], ),
        sa.PrimaryKeyConstraint('id_recomendacao')
    )
    op.create_index(op.f('ix_recomendacao_usuario_id_recomendacao'), 'recomendacao_usuario', ['id_recomendacao'], unique=False)

    # Create Recomendacao_Estabelecimento table
    op.create_table(
        'recomendacao_estabelecimento',
        sa.Column('id_recomendacao', sa.Integer(), nullable=False),
        sa.Column('id_usuario', sa.Integer(), nullable=False),
        sa.Column('id_lugar', sa.Integer(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('data_recomendacao', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['id_lugar'], ['estabelecimentos.id_estabelecimento'], ),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario'], ),
        sa.PrimaryKeyConstraint('id_recomendacao')
    )
    op.create_index(op.f('ix_recomendacao_estabelecimento_id_recomendacao'), 'recomendacao_estabelecimento', ['id_recomendacao'], unique=False)


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index(op.f('ix_recomendacao_estabelecimento_id_recomendacao'), table_name='recomendacao_estabelecimento')
    op.drop_table('recomendacao_estabelecimento')
    op.drop_index(op.f('ix_recomendacao_usuario_id_recomendacao'), table_name='recomendacao_usuario')
    op.drop_table('recomendacao_usuario')
    op.drop_index(op.f('ix_estabelecimento_preferencia_id'), table_name='estabelecimento_preferencia')
    op.drop_table('estabelecimento_preferencia')
    op.drop_index(op.f('ix_usuario_preferencia_id'), table_name='usuario_preferencia')
    op.drop_table('usuario_preferencia')
    op.drop_index(op.f('ix_estabelecimentos_id_estabelecimento'), table_name='estabelecimentos')
    op.drop_table('estabelecimentos')
    op.drop_index(op.f('ix_usuarios_id_usuario'), table_name='usuarios')
    op.drop_index(op.f('ix_usuarios_email'), table_name='usuarios')
    op.drop_table('usuarios')
    op.drop_index(op.f('ix_preferencias_id_preferencia'), table_name='preferencias')
    op.drop_table('preferencias')
    op.drop_index(op.f('ix_categorias_estabelecimentos_id_categoria'), table_name='categorias_estabelecimentos')
    op.drop_table('categorias_estabelecimentos')
    op.drop_index(op.f('ix_universidades_id_universidade'), table_name='universidades')
    op.drop_table('universidades')
