CREATE TABLE Aluno (
    Matricula INT PRIMARY KEY,
    NomeAluno VARCHAR(255) NOT NULL,
    Curso VARCHAR(255) NOT NULL,
    EmailAluno VARCHAR(255) NOT NULL UNIQUE
); 

CREATE TABLE Departamento (
    CodDepto INT PRIMARY KEY,
    NomeDepto VARCHAR(255) NOT NULL,
    EmailDepto VARCHAR(255) UNIQUE,
    LocalDepto VARCHAR(255)
);

CREATE TABLE Financiador (
    CodFinanciador INT PRIMARY KEY,
    NomeFinanciador VARCHAR(255) NOT NULL,
    Sigla VARCHAR(50) UNIQUE,
    Telefone VARCHAR(20),
    EmailFinanciador VARCHAR(255) UNIQUE
);

CREATE TABLE AreaAtuacao (
    CodAtuacao INT PRIMARY KEY,
    Area VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE AreaPesquisa (
    CodPesquisa INT PRIMARY KEY,
    Campo VARCHAR(255) NOT NULL UNIQUE
); 

CREATE TABLE Professor (
    CodProf INT PRIMARY KEY,
    NomeProfessor VARCHAR(255) NOT NULL,
    EmailProf VARCHAR(255) NOT NULL UNIQUE,
    CodDepto INT NOT NULL,
    CONSTRAINT fk_professor_depto FOREIGN KEY (CodDepto) REFERENCES Departamento(CodDepto)
        ON DELETE RESTRICT 
        ON UPDATE CASCADE
); 

CREATE TABLE Disciplina (
    CodDisciplina INT PRIMARY KEY,
    NomeDisciplina VARCHAR(255) NOT NULL,
    CargaHoraria INT NOT NULL,
    CodDepto INT NOT NULL,
    CONSTRAINT fk_disciplina_depto FOREIGN KEY (CodDepto) REFERENCES Departamento(CodDepto)
        ON DELETE CASCADE
        ON UPDATE CASCADE
); 

CREATE TABLE Projeto (
    CodProjeto INT PRIMARY KEY,
    NomeProjeto VARCHAR(255) NOT NULL,
    DescricaoProj TEXT,
    DataInicio DATE,
    DataTermino DATE,
    CargaHorariaProjeto INT,
    CodProf INT NOT NULL,
    CONSTRAINT fk_projeto_professor FOREIGN KEY (CodProf) REFERENCES Professor(CodProf)
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    CONSTRAINT chk_datas CHECK (DataTermino >= DataInicio) 
); 

CREATE TABLE ProjetodeExtensao (
    CodProjeto INT PRIMARY KEY,
    ModalidadeAcao VARCHAR(255),
    CONSTRAINT fk_extensao_projeto FOREIGN KEY (CodProjeto) REFERENCES Projeto(CodProjeto)
        ON DELETE CASCADE 
        ON UPDATE CASCADE
); 

CREATE TABLE MonitoriaTutoria (
    CodProjeto INT PRIMARY KEY,
    CodDisciplina INT NOT NULL,
    CONSTRAINT fk_monitoria_projeto FOREIGN KEY (CodProjeto) REFERENCES Projeto(CodProjeto)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_monitoria_disciplina FOREIGN KEY (CodDisciplina) REFERENCES Disciplina(CodDisciplina)
        ON DELETE RESTRICT 
        ON UPDATE CASCADE
); 

CREATE TABLE IniciacaoCient (
    CodProjeto INT PRIMARY KEY,
    CONSTRAINT fk_ic_projeto FOREIGN KEY (CodProjeto) REFERENCES Projeto(CodProjeto)
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

CREATE TABLE Contribuicao (
    CodFinanciador INT,
    CodProjeto INT,
    IdContribuicao INT,
    DescricaoContrib TEXT,
    ValorContrib FLOAT,
    CONSTRAINT pk_contribuicao PRIMARY KEY (CodFinanciador, CodProjeto, IdContribuicao),
    CONSTRAINT fk_contribuicao_financiador FOREIGN KEY (CodFinanciador) REFERENCES Financiador(CodFinanciador)
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    CONSTRAINT fk_contribuicao_projeto FOREIGN KEY (CodProjeto) REFERENCES Projeto(CodProjeto)
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

CREATE TABLE Oportunidade (
    CodProjeto INT,
    IdOportunidade INT,
    QtVagas INT NOT NULL,
    CONSTRAINT pk_oportunidade PRIMARY KEY (CodProjeto, IdOportunidade),
    CONSTRAINT fk_oportunidade_projeto FOREIGN KEY (CodProjeto) REFERENCES Projeto(CodProjeto)
        ON DELETE CASCADE 
        ON UPDATE CASCADE
); 

CREATE TABLE OportunidadeRemunerada (
    CodProjeto INT,
    IdOportunidade INT,
    ValorAuxilio FLOAT NOT NULL,
    CONSTRAINT pk_oportunidade_remunerada PRIMARY KEY (CodProjeto, IdOportunidade),
    CONSTRAINT fk_opremunerada_oportunidade FOREIGN KEY (CodProjeto, IdOportunidade) REFERENCES Oportunidade(CodProjeto, IdOportunidade)
        ON DELETE CASCADE 
        ON UPDATE CASCADE
); 

CREATE TABLE Atua (
    CodProjeto INT,
    CodAtuacao INT,
    CONSTRAINT pk_atua PRIMARY KEY (CodProjeto, CodAtuacao),
    CONSTRAINT fk_atua_extensao FOREIGN KEY (CodProjeto) REFERENCES ProjetodeExtensao(CodProjeto)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_atua_area FOREIGN KEY (CodAtuacao) REFERENCES AreaAtuacao(CodAtuacao)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
); 

CREATE TABLE Pesquisa (
    CodProjeto INT,
    CodPesquisa INT,
    CONSTRAINT pk_pesquisa PRIMARY KEY (CodProjeto, CodPesquisa),
    CONSTRAINT fk_pesquisa_ic FOREIGN KEY (CodProjeto) REFERENCES IniciacaoCient(CodProjeto)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_pesquisa_area FOREIGN KEY (CodPesquisa) REFERENCES AreaPesquisa(CodPesquisa)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE Inscreve (
    Matricula INT,
    CodProjeto INT,
    IdOportunidade INT,
    DataInicio DATE, 
    DataTermino DATE,
    CONSTRAINT pk_inscreve PRIMARY KEY (Matricula, CodProjeto, IdOportunidade),
    CONSTRAINT fk_inscreve_aluno FOREIGN KEY (Matricula) REFERENCES Aluno(Matricula)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_inscreve_oportunidade FOREIGN KEY (CodProjeto, IdOportunidade) REFERENCES Oportunidade(CodProjeto, IdOportunidade)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT chk_datas_inscricao CHECK (DataTermino >= DataInicio)
);

CREATE TABLE Coordena (
    CodProjeto INT,
    CodProf INT,
    CONSTRAINT pk_coordena PRIMARY KEY (CodProjeto, CodProf),
    CONSTRAINT fk_coordena_projeto FOREIGN KEY (CodProjeto) REFERENCES Projeto(CodProjeto)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_coordena_professor FOREIGN KEY (CodProf) REFERENCES Professor(CodProf)
        ON DELETE RESTRICT 
        ON UPDATE CASCADE
);

INSERT INTO Aluno (Matricula, NomeAluno, Curso, EmailAluno) VALUES
(202210, 'João Silva', 'Ciência da Computação', 'joao.silva@aluno.ufop.edu.br'),
(202220, 'Maria Oliveira', 'Engenharia de Produção', 'maria.oliveira@aluno.ufop.edu.br'),
(202310, 'Pedro Souza', 'Ciência da Computação', 'pedro.souza@aluno.ufop.edu.br'),
(202320, 'Ana Costa', 'Sistemas de Informação', 'ana.costa@aluno.ufop.edu.br'),
(202110, 'Lucas Martins', 'Engenharia de Computação', 'lucas.martins@aluno.ufop.edu.br');

INSERT INTO Departamento (CodDepto, NomeDepto, EmailDepto, LocalDepto) VALUES
(1, 'Departamento de Computação', 'decom@ufop.edu.br', 'Bloco C, Campus Morro do Cruzeiro'),
(2, 'Departamento de Engenharia de Produção', 'depro@ufop.edu.br', 'Bloco de Aulas I, Campus Morro do Cruzeiro'),
(3, 'Departamento de Matemática', 'demat@ufop.edu.br', 'Bloco de Aulas II, Campus Morro do Cruzeiro');

INSERT INTO Financiador (CodFinanciador, NomeFinanciador, Sigla, EmailFinanciador) VALUES
(100, 'Fundação de Amparo à Pesquisa do Estado de Minas Gerais', 'FAPEMIG', 'contato@fapemig.br'),
(101, 'Conselho Nacional de Desenvolvimento Científico e Tecnológico', 'CNPq', 'atendimento@cnpq.br');

INSERT INTO AreaAtuacao (CodAtuacao, Area) VALUES
(10, 'Educação Básica'),
(11, 'Tecnologia Social'),
(12, 'Saúde Comunitária');

INSERT INTO AreaPesquisa (CodPesquisa, Campo) VALUES
(20, 'Inteligência Artificial'),
(21, 'Otimização de Processos Industriais'),
(22, 'Cálculo Numérico Aplicado');

INSERT INTO Professor (CodProf, NomeProfessor, EmailProf, CodDepto) VALUES
(1001, 'Carlos Batista', 'carlos.batista@ufop.edu.br', 1),
(1002, 'Fernanda Lima', 'fernanda.lima@ufop.edu.br', 2),
(1003, 'Ricardo Neves', 'ricardo.neves@ufop.edu.br', 1);

INSERT INTO Disciplina (CodDisciplina, NomeDisciplina, CargaHoraria, CodDepto) VALUES
(301, 'Cálculo I', 90, 3),
(302, 'Banco de Dados I', 60, 1),
(303, 'Pesquisa Operacional', 60, 2);

INSERT INTO Projeto (CodProjeto, NomeProjeto, DescricaoProj, DataInicio, DataTermino, CargaHorariaProjeto, CodProf) VALUES
(10, 'Sistema de Reconhecimento Facial para Segurança', 'Desenvolvimento de um sistema de IA para identificação em tempo real.', '2025-03-01', '2026-02-28', 20, 1001),
(11, 'Otimização da Logística de uma Empresa Local', 'Aplicação de técnicas de pesquisa operacional para otimizar rotas.', '2025-04-01', '2025-10-30', 15, 1002),
(12, 'Inclusão Digital para a Terceira Idade', 'Cursos de informática básica para a comunidade local.', '2025-08-15', '2025-12-15', 10, 1002),
(13, 'Monitoria da Disciplina de Banco de Dados I', 'Apoio aos alunos da disciplina de BCC321.', '2025-08-01', '2025-12-20', 12, 1003);

INSERT INTO ProjetodeExtensao (CodProjeto, ModalidadeAcao) VALUES (12, 'Curso de Extensão');

INSERT INTO MonitoriaTutoria (CodProjeto, CodDisciplina) VALUES (13, 302);

INSERT INTO IniciacaoCient (CodProjeto) VALUES (10), (11);

INSERT INTO Contribuicao (CodFinanciador, CodProjeto, IdContribuicao, DescricaoContrib, ValorContrib) VALUES
(100, 10, 1, 'Bolsas de Iniciação Científica', 16800.00),
(101, 10, 1, 'Auxílio para compra de equipamentos', 5000.00);

INSERT INTO Oportunidade (CodProjeto, IdOportunidade, QtVagas) VALUES
(10, 1, 2), -- Oportunidade para o projeto de IA
(12, 1, 3), -- Oportunidade para o projeto de extensão
(13, 1, 1); -- Oportunidade para a monitoria de BD

INSERT INTO OportunidadeRemunerada (CodProjeto, IdOportunidade, ValorAuxilio) VALUES
(10, 1, 700.00), -- Bolsa de R$700 para o projeto de IA
(13, 1, 500.00); -- Bolsa de R$500 para a monitoria

INSERT INTO Atua (CodProjeto, CodAtuacao) VALUES (12, 10), (12, 11);

INSERT INTO Pesquisa (CodProjeto, CodPesquisa) VALUES (10, 20), (11, 21);

INSERT INTO Inscreve (Matricula, CodProjeto, IdOportunidade, DataInicio, DataTermino) VALUES
(202210, 10, 1, '2025-03-10', '2026-02-28'), -- João Silva, APROVADO para o projeto de IA
(202310, 10, 1, NULL, NULL);                 -- Pedro Souza, INSCRITO (pendente) para o projeto de IA

INSERT INTO Inscreve (Matricula, CodProjeto, IdOportunidade, DataInicio, DataTermino) VALUES
(202220, 12, 1, '2025-08-20', '2025-12-15'); -- Maria Oliveira, APROVADA para o projeto de extensão

INSERT INTO Inscreve (Matricula, CodProjeto, IdOportunidade, DataInicio, DataTermino) VALUES
(202110, 13, 1, '2025-08-05', '2025-12-20'); -- Lucas Martins, APROVADO para a monitoria

INSERT INTO Coordena (CodProjeto, CodProf) VALUES
(10, 1001), -- Carlos Batista coordena o projeto de IA
(11, 1002), -- Fernanda Lima coordena o projeto de otimização
(12, 1002), -- Fernanda Lima coordena o projeto de extensão
(13, 1003); -- Ricardo Neves coordena a monitoria
