# Sistema de Gerenciamento de Projetos Acadêmicos

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-blue?style=for-the-badge&logo=postgresql)
![Status](https://img.shields.io/badge/Status-Concluído-green?style=for-the-badge)

## Visão Geral
Este projeto é um sistema de banco de dados desenvolvido para gerenciar projetos acadêmicos, como Iniciação Científica, Extensão e Monitoria/Tutoria. A aplicação permite o cadastro e a consulta de informações sobre alunos, professores, departamentos, projetos, oportunidades de vagas e financiadores. Esse trabalho foi realizado por mim e outros colegas para a disciplina de Banco de Dados.

O sistema possui uma interface gráfica desenvolvida em Python que se conecta a um banco de dados PostgreSQL para realizar consultas e operações, como listar projetos, inscrever alunos, aprovar candidaturas e visualizar relatórios sobre vagas e contribuições financeiras.

## Tecnologias Utilizadas

* **Linguagem de Programação:** Python
* **Banco de Dados:** PostgreSQL
* **Interface Gráfica (GUI):** CustomTkinter
* **Conector do Banco:** Psycopg2

## Modelo do Banco de Dados

O projeto foi modelado em três níveis de abstração: conceitual, relacional e físico.

### 1. Esquema Conceitual

O Modelo Entidade-Relacionamento (MER) foi criado para representar as principais entidades do sistema e como elas se relacionam. As entidades incluem `Aluno`, `Professor`, `Projeto`, `Oportunidade`, `Departamento`, `Financiador`, entre outras.

O diagrama completo está disponível no arquivo `Esquema Conceitual.xml`.

### 2. Esquema Relacional

A partir do modelo conceitual, foi derivado o esquema relacional, que define a estrutura das tabelas, seus atributos, chaves primárias e estrangeiras. As principais relações (tabelas) são:

* **Aluno**: Armazena dados dos estudantes.
* **Professor**: Guarda informações dos professores e seu departamento de alocação.
* **Departamento**: Tabela com os departamentos da instituição.
* **Projeto**: Tabela central que armazena todos os projetos, com especializações para **ProjetodeExtensao**, **MonitoriaTutoria** e **IniciacaoCient**.
* **Oportunidade**: Define as vagas disponíveis nos projetos, podendo ser uma **OportunidadeRemunerada**.
* **Inscreve**: Tabela associativa que registra a inscrição de um aluno em uma oportunidade.
* **Financiador** e **Contribuicao**: Gerenciam as entidades que financiam os projetos e os valores contribuídos.
* **Coordena**: Associa os professores que coordenam cada projeto.

O detalhamento completo pode ser encontrado no arquivo `Esquema Relacional.pdf`.

### 3. Esquema Físico

O esquema físico foi implementado em PostgreSQL. O arquivo `Esquema Físico - SQL.sql` contém:
* Os comandos `CREATE TABLE` para todas as tabelas.
* A definição de todas as restrições de integridade, como `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE` e `CHECK`.
* Comandos `INSERT INTO` para popular o banco de dados com dados de exemplo, permitindo testar as funcionalidades do sistema imediatamente.

## Funcionalidades do Sistema

A interface gráfica (`system.py`) oferece as seguintes funcionalidades:

### Consultas
* **Listar Projetos e Professores**: Exibe todos os projetos, os professores que os coordenam e seus respectivos departamentos.
* **Listar Alunos por Projeto**: Permite buscar por um projeto (via código) e lista todos os alunos inscritos, indicando o status ("Aprovado" ou "Inscrito").
* **Listar Contribuições por Financiador**: Exibe todas as contribuições (projetos e valores) de um financiador específico.
* **Status de Vagas**: Mostra um relatório com o total de vagas, vagas preenchidas, inscrições pendentes e vagas restantes para cada oportunidade.
* **Listar Financiadores**: Apresenta todos os dados dos financiadores cadastrados.
* **Buscar Projetos por Professor**: Permite buscar projetos a partir do nome (ou parte do nome) de um professor.
* **Buscar Disciplinas por Departamento**: Lista as disciplinas de um departamento a partir do nome do mesmo.

### Operações
* **Aprovar Aluno Inscrito**: Altera o status de um aluno de "Inscrito" para "Aprovado", registrando a data de início e término de sua participação na oportunidade.
* **Excluir Inscrição**: Remove o registro de inscrição de um aluno em uma oportunidade.

## Configuração do Ambiente

Para executar este projeto, siga os passos abaixo:

### 1. Pré-requisitos
* Python 3.x instalado.
* PostgreSQL instalado e em execução.

### 2. Configuração do Banco de Dados
1.  Crie um banco de dados em seu servidor PostgreSQL
2.  Execute o script `Esquema Físico - SQL.sql` para criar as tabelas e popular o banco com os dados iniciais. Você pode usar um cliente como o DBeaver/pgAdmin ou a linha de comando:
    ```bash
    psql -U seu_usuario -d nome_do_banco -f "Esquema Físico - SQL.sql"
    ```

### 3. Configuração da Aplicação
1.  Clone este repositório ou faça o download dos arquivos.
2.  Crie e ative um ambiente virtual (recomendado):
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux / macOS
    source venv/bin/activate
    ```
3.  Instale as dependências a partir do arquivo `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Ajuste a conexão com o banco**: Abra o arquivo `system.py` e modifique a função `conectar_bd()` com suas credenciais do PostgreSQL (usuário, senha, host, porta e nome do banco, se for diferente de `postgres`).

    ```python
    def conectar_bd():
        try:
            conn = psycopg2.connect(
                dbname="postgres",      # Ou o nome do seu banco
                user="postgres",        # Seu usuário do PostgreSQL
                password="laura123",    # Sua senha
                host="localhost",
                port="5432"
            )
            return conn
        # ...
    ```

## Executando a Aplicação

Com o ambiente configurado e o banco de dados ativo, execute o seguinte comando no terminal:

```bash

python system.py

