"""Seed initial data

Revision ID: b716a52872a6
Revises: 3f990a2494f0
Create Date: 2025-10-31 14:40:32.093325

"""
from typing import Sequence, Union
from datetime import date

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b716a52872a6'
down_revision: Union[str, Sequence[str], None] = '3f990a2494f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Populate database with synthetic data for LightFM recommendation system."""
    
    # 1. Tabelas Independentes
    
    # Universidades
    op.execute("""
        INSERT INTO universidades (id_universidade, nome, cidade, estado) VALUES
        (1, 'Universidade de São Paulo', 'São Paulo', 'SP'),
        (2, 'Universidade Estadual de Campinas', 'Campinas', 'SP'),
        (3, 'Universidade Federal do Rio de Janeiro', 'Rio de Janeiro', 'RJ'),
        (4, 'Universidade Federal de Minas Gerais', 'Belo Horizonte', 'MG'),
        (5, 'Universidade Federal do Rio Grande do Sul', 'Porto Alegre', 'RS'),
        (6, 'Universidade Federal da Bahia', 'Salvador', 'BA'),
        (7, 'Universidade de Brasília', 'Brasília', 'DF'),
        (8, 'Universidade Federal de Santa Catarina', 'Florianópolis', 'SC'),
        (9, 'Pontifícia Universidade Católica do Rio de Janeiro', 'Rio de Janeiro', 'RJ')
    """)
    
    # Categorias_Estabelecimentos
    op.execute("""
        INSERT INTO categorias_estabelecimentos (id_categoria, nome_categoria) VALUES
        (1, 'Restaurante'),
        (2, 'Cafeteria'),
        (3, 'Biblioteca'),
        (4, 'Papelaria'),
        (5, 'Bar e Lazer'),
        (6, 'Lanchonete'),
        (7, 'Livraria'),
        (8, 'Espaço de Coworking'),
        (9, 'Academia'),
        (10, 'Parque / Área de Lazer')
    """)
    
    # Preferencias
    op.execute("""
        INSERT INTO preferencias (id_preferencia, nome_preferencia, tipo_preferencia) VALUES
        (1, 'Comida Barata', 'Alimentação'),
        (2, 'Opção Vegana', 'Alimentação'),
        (3, 'Silencioso para Estudo', 'Ambiente'),
        (4, 'Música ao Vivo', 'Lazer'),
        (5, 'Happy Hour', 'Lazer'),
        (6, 'Material de Desenho', 'Material'),
        (7, 'Café Especial', 'Alimentação'),
        (8, 'Wi-Fi Rápido', 'Infraestrutura'),
        (9, 'Tomadas Acessíveis', 'Infraestrutura'),
        (10, 'Aberto 24h', 'Horário'),
        (11, 'Opção Sem Glúten', 'Alimentação'),
        (12, 'Ambiente Pet-Friendly', 'Ambiente'),
        (13, 'Música Ambiente (Baixa)', 'Ambiente'),
        (14, 'Bom para Grupos', 'Ambiente'),
        (15, 'Aceita Vale-Refeição', 'Pagamento'),
        (16, 'Livros Técnicos', 'Material'),
        (17, 'Equipamento de Musculação', 'Fitness'),
        (18, 'Pista de Corrida', 'Lazer'),
        (19, 'Cerveja Artesanal', 'Lazer'),
        (20, 'Local para Reuniões', 'Ambiente'),
        (21, 'Comida Caseira', 'Alimentação')
    """)
    
    # 2. Tabelas Dependentes (Nível 1)
    
    # Usuarios
    op.execute("""
        INSERT INTO usuarios (id_usuario, nome, email, senha_hash, curso, idade, descricao, id_universidade, data_cadastro) VALUES
        (101, 'Ana Silva', 'ana.silva@email.com', 'hash_abc123', 'Engenharia de Computação', 20, 'Estudante da USP, buscando lugares para estudar e comer.', 1, '2024-03-15'),
        (102, 'Bruno Costa', 'bruno.costa@email.com', 'hash_def456', 'Medicina', 22, 'Estudante da UFRJ, gosto de sair nos fins de semana.', 3, '2024-02-10'),
        (103, 'Carla Dias', 'carla.dias@email.com', 'hash_ghi789', 'Design Digital', 19, 'Aluna da Unicamp. Vegetariana e amo cafés.', 2, '2024-05-01'),
        (104, 'Daniel Moreira', 'daniel.moreira@email.com', 'hash_jkl101', 'Engenharia de Computação', 21, 'USP, focado no TCC, preciso de locais silenciosos.', 1, '2024-01-20'),
        (105, 'Elisa Fernandes', 'elisa.fernandes@email.com', 'hash_mno112', 'Direito', 23, 'UFRJ. Gosto de bares com música e bons drinks.', 3, '2024-06-05'),
        (106, 'Felipe Alves', 'felipe.alves@email.com', 'hash_pqr113', 'Economia', 20, 'UFMG. Procurando restaurantes que aceitem VR.', 4, '2024-07-11'),
        (107, 'Gabriela Lima', 'gabi.lima@email.com', 'hash_stu114', 'Jornalismo', 21, 'UFRGS. Adoro cafés com música ambiente baixa para ler.', 5, '2024-08-01'),
        (108, 'Heitor Barros', 'heitor.barros@email.com', 'hash_vwx115', 'Engenharia Civil', 24, 'UFBA. Gosto de comida caseira e lugares para ir com a turma.', 6, '2024-09-15'),
        (109, 'Isabela Rocha', 'isabela.rocha@email.com', 'hash_yza116', 'Relações Internacionais', 19, 'UnB. Preciso de locais com Wi-Fi bom para reuniões de grupo.', 7, '2024-10-02'),
        (110, 'João Mendes', 'joao.mendes@email.com', 'hash_bcd117', 'Sistemas de Informação', 22, 'UFSC. Desenvolvedor, busco locais com tomadas e Wi-Fi.', 8, '2024-11-20'),
        (111, 'Larissa Souza', 'lari.souza@email.com', 'hash_efg118', 'Arquitetura', 21, 'Unicamp. Preciso de papelarias com material de desenho.', 2, '2024-12-01'),
        (112, 'Marcos Vinicius', 'mv@email.com', 'hash_hij119', 'Filosofia', 25, 'USP. Leitor assíduo, prefiro bibliotecas e livrarias silenciosas.', 1, '2025-01-10'),
        (113, 'Natalia Borges', 'nati.borges@email.com', 'hash_klm120', 'Psicologia', 20, 'PUC-Rio. Gosto de cafés especiais e ambientes tranquilos.', 9, '2025-02-15'),
        (114, 'Otavio Lacerda', 'otavio.lacerda@email.com', 'hash_nop121', 'Engenharia Elétrica', 22, 'UFRJ. Preciso de livros técnicos e tomadas.', 3, '2025-03-05'),
        (115, 'Patricia Ramos', 'paty.ramos@email.com', 'hash_qrs122', 'Biologia', 19, 'UFSC. Gosto de parques para correr e locais pet-friendly.', 8, '2025-04-10')
    """)
    
    # Estabelecimentos
    op.execute("""
        INSERT INTO estabelecimentos (id_estabelecimento, descricao, endereco, cidade, horario_funcionamento, dono_nome, dono_email, id_categoria) VALUES
        (201, 'Restaurante Prato Feito do Zé', 'Rua das Flores, 123', 'São Paulo', '11:00-15:00', 'José Oliveira', 'contato@pratofeitoze.com', 1),
        (202, 'Grão & Prosa Cafeteria', 'Av. Principal, 456', 'Campinas', '09:00-20:00', 'Maria Souza', 'maria@graoeprosa.com', 2),
        (203, 'Biblioteca Central da USP', 'Praça do Relógio, s/n', 'São Paulo', '08:00-22:00', 'Diretoria SIBI', 'sibi@usp.br', 3),
        (204, 'Lapa Sounds Bar', 'Rua da Lapa, 789', 'Rio de Janeiro', '18:00-02:00', 'Ricardo Mendes', 'ricardo@lapasounds.com', 5),
        (205, 'Papelaria Universitária', 'Rua da Reitoria, 10', 'Campinas', '08:00-18:00', 'Lúcia Mota', 'lucia@papelariauni.com', 4),
        (206, 'Cantina Verde', 'Rua do IFCH, 30', 'Campinas', '10:00-16:00', 'Marcos Andrade', 'marcos@cantinaverde.com', 1),
        (207, 'Café da Manhã da Gávea', 'Rua Marquês de São Vicente, 22', 'Rio de Janeiro', '08:00-12:00', 'Ana Clara Rezende', 'ana@cafedagavea.com', 2),
        (208, 'Coworking Campus BH', 'Av. Afonso Pena, 1500', 'Belo Horizonte', '09:00-21:00', 'TechSpace Ltda', 'contato@campusbh.com', 8),
        (209, 'Livraria Leitura Savassi', 'Rua Fernandes Tourinho, 500', 'Belo Horizonte', '10:00-22:00', 'Carlos Drummond', 'gerencia@leiturasavassi.com', 7),
        (210, 'Parque Redenção', 'Av. João Pessoa, s/n', 'Porto Alegre', '06:00-20:00', 'Prefeitura POA', 'parques@poa.gov.br', 10),
        (211, 'Lanchonete do Alemão', 'Rua dos Andradas, 90', 'Porto Alegre', '16:00-23:00', 'Werner Schmidt', 'werner@alemao.com', 6),
        (212, 'Acarajé da Dinha', 'Largo de Santana, 10', 'Salvador', '15:00-21:00', 'Ednalva Santos', 'dinhadoacaraje@email.com', 1),
        (213, 'SmartFit Asa Norte', 'SQN 205, Bloco C', 'Brasília', '06:00-23:00', 'Grupo SmartFit', 'asanorte@smartfit.com', 9),
        (214, 'Biblioteca Central UnB (BCE)', 'Campus Darcy Ribeiro', 'Brasília', '07:00-23:00', 'Diretoria BCE', 'bce@unb.br', 3),
        (215, 'Bar Canto da Lagoa', 'Av. das Rendeiras, 1700', 'Florianópolis', '17:00-01:00', 'Juliana Paes', 'juliana@cantodalagoa.com', 5),
        (216, 'O Papiro Papelaria', 'Rua Trindade, 404', 'Florianópolis', '09:00-19:00', 'Fernando Pessoa', 'contato@opapiro.com', 4),
        (217, 'QuickBite Lanches 24h', 'Rua Butantã, 550', 'São Paulo', '00:00-23:59', 'FastFood Inc.', 'sac@quickbite.com', 6),
        (218, 'Ponto do Açaí', 'Rua do Ouvidor, 30', 'Rio de Janeiro', '10:00-20:00', 'Silas Malafaia', 'pontoacai@email.com', 6)
    """)
    
    # 3. Tabelas de Junção (Nível 2)
    
    # Usuario_Preferencia
    op.execute("""
        INSERT INTO usuario_preferencia (id_usuario, id_preferencia, peso) VALUES
        (101, 1, 5), (101, 3, 4), (101, 8, 3),
        (102, 4, 5), (102, 5, 4),
        (103, 2, 5), (103, 7, 3), (103, 6, 4),
        (104, 3, 5), (104, 8, 5), (104, 9, 4),
        (105, 4, 4), (105, 5, 5), (105, 19, 3),
        (106, 15, 5), (106, 1, 4),
        (107, 13, 3), (107, 7, 4),
        (108, 14, 4), (108, 21, 5),
        (109, 20, 5), (109, 8, 4),
        (110, 8, 5), (110, 9, 5), (110, 10, 3),
        (111, 6, 5), (111, 12, 3),
        (112, 3, 5), (112, 16, 5),
        (113, 13, 4), (113, 7, 4),
        (114, 9, 5), (114, 16, 4),
        (115, 12, 3), (115, 18, 5)
    """)
    
    # Estabelecimento_Preferencia
    op.execute("""
        INSERT INTO estabelecimento_preferencia (id_estabelecimento, id_preferencia, peso) VALUES
        (201, 1, 5), (201, 21, 4), (201, 15, 3),
        (202, 7, 4), (202, 3, 3), (202, 8, 4),
        (203, 3, 5), (203, 9, 4), (203, 16, 4),
        (204, 4, 5), (204, 5, 4), (204, 19, 4),
        (205, 6, 4),
        (206, 1, 3), (206, 2, 5),
        (207, 7, 5), (207, 12, 3),
        (208, 8, 5), (208, 9, 5), (208, 20, 4),
        (209, 16, 4), (209, 7, 3), (209, 13, 4),
        (210, 18, 5), (210, 12, 4),
        (211, 1, 4), (211, 14, 4),
        (212, 21, 5),
        (213, 17, 5),
        (214, 3, 5), (214, 16, 5), (214, 8, 4),
        (215, 4, 4), (215, 5, 4),
        (216, 6, 5),
        (217, 1, 4), (217, 10, 3),
        (218, 1, 3), (218, 14, 3)
    """)
    
    # 4. Tabelas de Recomendação (Nível 3)
    
    # Recomendacao_Usuario
    op.execute("""
        INSERT INTO recomendacao_usuario (id_recomendacao, id_usuario1, id_usuario2, score, data_recomendacao) VALUES
        (301, 101, 104, 0.90, '2025-10-20'),
        (302, 102, 105, 0.85, '2025-10-21'),
        (303, 103, 111, 0.88, '2025-10-22'),
        (304, 101, 112, 0.75, '2025-10-23'),
        (305, 110, 115, 0.82, '2025-10-24'),
        (306, 105, 113, 0.70, '2025-10-25'),
        (307, 104, 110, 0.92, '2025-10-26'),
        (308, 109, 106, 0.65, '2025-10-27')
    """)
    
    # Recomendacao_Estabelecimento
    op.execute("""
        INSERT INTO recomendacao_estabelecimento (id_recomendacao, id_usuario, id_lugar, score, data_recomendacao) VALUES
        (401, 101, 203, 5, '2025-10-15'),
        (402, 103, 206, 5, '2025-10-16'),
        (403, 103, 202, 4, '2025-10-17'),
        (404, 102, 204, 5, '2025-10-18'),
        (405, 101, 201, 3, '2025-10-19'),
        (406, 104, 203, 5, '2025-10-20'),
        (407, 105, 204, 4, '2025-10-21'),
        (408, 106, 209, 3, '2025-10-22'),
        (409, 109, 214, 5, '2025-10-23'),
        (410, 109, 208, 4, '2025-10-24'),
        (411, 110, 216, 4, '2025-10-25'),
        (412, 111, 205, 5, '2025-10-26'),
        (413, 112, 203, 4, '2025-10-27'),
        (414, 113, 207, 5, '2025-10-28'),
        (415, 115, 210, 4, '2025-10-29'),
        (416, 108, 212, 5, '2025-10-30'),
        (417, 104, 217, 2, '2025-11-01'),
        (418, 110, 208, 4, '2025-11-02'),
        (419, 103, 206, 4, '2025-11-03'),
        (420, 101, 217, 3, '2025-11-04')
    """)


def downgrade() -> None:
    """Remove all seeded data."""
    op.execute("DELETE FROM recomendacao_estabelecimento")
    op.execute("DELETE FROM recomendacao_usuario")
    op.execute("DELETE FROM estabelecimento_preferencia")
    op.execute("DELETE FROM usuario_preferencia")
    op.execute("DELETE FROM estabelecimentos")
    op.execute("DELETE FROM usuarios")
    op.execute("DELETE FROM preferencias")
    op.execute("DELETE FROM categorias_estabelecimentos")
    op.execute("DELETE FROM universidades")
