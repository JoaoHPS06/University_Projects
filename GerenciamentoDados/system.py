import psycopg2
import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
from datetime import date

# conecta com o banco
def conectar_bd():
    try:
        conn = psycopg2.connect(
            dbname="postgres",  
            user="postgres",  
            password="laura123", 
            host="localhost",
            port="5432"
        )
        return conn
    except psycopg2.Error as e:
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco:\n{e}")
        return None


def executar_consulta(sql, params=None):
    # executa uma consulta SELECT e retorna os resultados e os nomes das colunas
    if not conn:
        messagebox.showwarning("Aviso", "Sem conexão com o banco de dados.")
        return [], []
    try:
        cur = conn.cursor()
        cur.execute(sql, params if params else ())
        resultados = cur.fetchall()
        # Pega os nomes das colunas da descrição do cursor
        cabecalhos = [desc[0] for desc in cur.description]
        cur.close()
        return resultados, cabecalhos
    except psycopg2.Error as e:
        messagebox.showerror("Erro de Consulta", f"Erro ao executar a consulta:\n{e}")
        return [], []

def executar_operacao(sql, params=None):
    # executa uma operação de UPDATE, INSERT ou DELETE
    if not conn:
        messagebox.showwarning("Aviso", "Sem conexão com o banco de dados.")
        return False
    try:
        cur = conn.cursor()
        cur.execute(sql, params if params else ())
        conn.commit()
        # retorna o numero de linhas afetadas, para saber se a operação teve efeito
        linhas_afetadas = cur.rowcount
        cur.close()
        return linhas_afetadas > 0
    except psycopg2.Error as e:
        conn.rollback() #dDesfaz a operacao em caso de erro
        messagebox.showerror("Erro de Operação", f"Erro ao executar a operação:\n{e}")
        return False

def formatar_resultados_com_cabecalho(texto_area, resultados, cabecalhos):
    # limpa a area de texto e exibe os resultados formatados com cabeçalhos
    texto_area.delete(1.0, tk.END)
    if not resultados:
        texto_area.insert(tk.END, "Nenhum resultado encontrado.")
        return

    # formatacao 
    header_string = " | ".join(cabecalhos)
    texto_area.insert(tk.END, header_string + "\n")
    texto_area.insert(tk.END, "-" * len(header_string) + "\n")

    for linha in resultados:
        # converte cada item da linha para string para poder usar o join
        linha_str = [str(item) for item in linha]
        texto_area.insert(tk.END, " | ".join(linha_str) + "\n")


def consulta1_listar_projetos_professores(texto_area):
    # lista todos os projetos, seus professores e o nome do departamento do professor
    sql = """
        SELECT
            p.CodProjeto,
            p.NomeProjeto,
            pr.NomeProfessor,
            dep.NomeDepto AS Departamento  -- Alterado para mostrar o nome do departamento
        FROM Projeto p
        JOIN Professor pr ON p.CodProf = pr.CodProf
        JOIN Departamento dep ON pr.CodDepto = dep.CodDepto -- Novo JOIN para acessar o nome do departamento
        ORDER BY dep.NomeDepto, pr.NomeProfessor, p.NomeProjeto;
    """
    resultados, cabecalhos = executar_consulta(sql)
    formatar_resultados_com_cabecalho(texto_area, resultados, cabecalhos)

def consulta2_listar_alunos_por_projeto(texto_area):
    # pede ao usuário o codigo de um projeto e lista todos os alunos inscritos em qualquer oportunidade daquele projeto
    cod_proj = simpledialog.askinteger("Entrada", "Digite o Código do Projeto:")
    if cod_proj is None:
        return
    sql = """
        SELECT
            a.Matricula,
            a.NomeAluno,
            i.IdOportunidade,
            CASE WHEN i.DataInicio IS NOT NULL THEN 'Aprovado' ELSE 'Inscrito' END as Status
        FROM Inscreve i
        JOIN Aluno a ON i.Matricula = a.Matricula
        WHERE i.CodProjeto = %s
        ORDER BY i.IdOportunidade, a.NomeAluno;
    """
    resultados, cabecalhos = executar_consulta(sql, (cod_proj,))
    
    # adiciona o nome do projeto no topo dos resultados para contextualizar
    nome_projeto_sql = "SELECT NomeProjeto FROM Projeto WHERE CodProjeto = %s;"
    nome_proj_res, _ = executar_consulta(nome_projeto_sql, (cod_proj,))
    if nome_proj_res:
        texto_area.delete(1.0, tk.END)
        texto_area.insert(tk.END, f"Alunos inscritos no projeto: '{nome_proj_res[0][0]}'\n\n")
        formatar_resultados_com_cabecalho(texto_area, resultados, cabecalhos)
    else:
        # caso o projeto nao seja encontrado
        texto_area.delete(1.0, tk.END)
        texto_area.insert(tk.END, f"Nenhum projeto encontrado com o código {cod_proj}.")

def consulta3_listar_contribuicoes_por_financiador(texto_area):
    # pede o codigo de um financiador e lista suas contribuicoes para projetos
    cod_fin = simpledialog.askinteger("Entrada", "Digite o Código do Financiador:")
    if cod_fin is None:
        return
    sql = """
        SELECT p.NomeProjeto, c.DescricaoContrib, c.ValorContrib
        FROM Contribuicao c
        JOIN Projeto p ON c.CodProjeto = p.CodProjeto
        WHERE c.CodFinanciador = %s
        ORDER BY p.NomeProjeto;
    """
    resultados, cabecalhos = executar_consulta(sql, (cod_fin,))
    formatar_resultados_com_cabecalho(texto_area, resultados, cabecalhos)

def consulta4_contar_vagas_por_oportunidade(texto_area):
    # mostra o status de vagas de todas as oportunidades
    sql = """
         SELECT
            o.CodProjeto,
            o.IdOportunidade,
            p.NomeProjeto,
            o.QtVagas AS Vagas_Totais,
            COUNT(i.DataInicio) AS Vagas_Preenchidas, -- Conta apenas os aprovados (DataInicio NOT NULL)
            (COUNT(i.Matricula) - COUNT(i.DataInicio)) AS Inscritos_Pendentes, -- Total de inscritos menos os aprovados
            (o.QtVagas - COUNT(i.DataInicio)) AS Vagas_Restantes -- Total de vagas menos os aprovados
        FROM Oportunidade o
        JOIN Projeto p ON o.CodProjeto = p.CodProjeto
        LEFT JOIN Inscreve i ON o.CodProjeto = i.CodProjeto AND o.IdOportunidade = i.IdOportunidade
        GROUP BY o.CodProjeto, o.IdOportunidade, p.NomeProjeto
        ORDER BY o.CodProjeto, o.IdOportunidade;
    """
    resultados, cabecalhos = executar_consulta(sql)
    formatar_resultados_com_cabecalho(texto_area, resultados, cabecalhos)

def consulta5_listar_financiadores(texto_area):
    # lista todas as informacoes de todos os financiadores cadastrados
    sql = """
        SELECT
            CodFinanciador,
            NomeFinanciador,
            Sigla,
            Telefone,
            EmailFinanciador
        FROM Financiador
        ORDER BY NomeFinanciador;
    """
    resultados, cabecalhos = executar_consulta(sql)
    formatar_resultados_com_cabecalho(texto_area, resultados, cabecalhos)

def consulta6_listar_projetos_por_nome_professor(texto_area):
    # pede o nome (ou parte do nome) de um professor e lista os projetos que ele coordena
    nome_prof = simpledialog.askstring("Entrada", "Digite o nome ou parte do nome do professor:")

    if not nome_prof:
        return

    termo_busca = f"%{nome_prof}%"

    sql = """
        SELECT
            p.CodProjeto,
            p.NomeProjeto,
            pr.NomeProfessor,
            p.DataInicio,
            p.DataTermino
        FROM Projeto p
        JOIN Professor pr ON p.CodProf = pr.CodProf
        WHERE pr.NomeProfessor ILIKE %s -- ILIKE para busca case-insensitive
        ORDER BY pr.NomeProfessor, p.NomeProjeto;
    """
    
    resultados, cabecalhos = executar_consulta(sql, (termo_busca,))
    formatar_resultados_com_cabecalho(texto_area, resultados, cabecalhos)

def consulta7_listar_disciplinas_por_departamento(texto_area):
    # pede o nome de um departamento e lista todas as suas disciplinas
    nome_depto = simpledialog.askstring("Entrada", "Digite o nome ou parte do nome do Departamento:")
    
    if not nome_depto:
        return

    termo_busca = f"%{nome_depto}%"

    sql = """
        SELECT
            d.CodDisciplina,
            d.NomeDisciplina,
            d.CargaHoraria,
            dep.NomeDepto AS Departamento
        FROM Disciplina d
        JOIN Departamento dep ON d.CodDepto = dep.CodDepto
        WHERE dep.NomeDepto ILIKE %s
        ORDER BY d.NomeDisciplina;
    """
    
    resultados, cabecalhos = executar_consulta(sql, (termo_busca,))
    formatar_resultados_com_cabecalho(texto_area, resultados, cabecalhos)

def atualizacao1_aprovar_aluno(texto_area):
    """Atualização 1 (UPDATE): Aprova um aluno para uma vaga, definindo data de início e término."""
    matricula = simpledialog.askinteger("Aprovar Aluno", "Digite a Matrícula do aluno:")
    cod_proj = simpledialog.askinteger("Aprovar Aluno", "Digite o Código do Projeto da vaga:")
    id_op = simpledialog.askinteger("Aprovar Aluno", "Digite o ID da Oportunidade da vaga:")
    if matricula is None or cod_proj is None or id_op is None:
        return

    # usa a data de hoje como exemplo
    data_inicio = date.today().strftime('%Y-%m-%d')
    # adicionando 1 ano como data de termino de exemplo
    data_termino = (date.today().replace(year=date.today().year + 1)).strftime('%Y-%m-%d')

    sql = """
        UPDATE Inscreve
        SET DataInicio = %s, DataTermino = %s
        WHERE Matricula = %s AND CodProjeto = %s AND IdOportunidade = %s AND DataInicio IS NULL;
    """
    if executar_operacao(sql, (data_inicio, data_termino, matricula, cod_proj, id_op)):
        messagebox.showinfo("Sucesso", f"Aluno de matrícula {matricula} aprovado com sucesso!")
        # mostra a lista de alunos da oportunidade para confirmar a mudanca
        consulta2_listar_alunos_por_projeto(texto_area)
    else:
        messagebox.showwarning("Falha", "Operação falhou. Verifique se a inscrição existe e se o aluno já não foi aprovado.")

def atualizacao2_excluir_inscricao(texto_area):
    # exclui a inscricao de um aluno de uma oportunidade
    matricula = simpledialog.askinteger("Excluir Inscrição", "Digite a Matrícula do aluno:")
    cod_proj = simpledialog.askinteger("Excluir Inscrição", "Digite o Código do Projeto:")
    id_op = simpledialog.askinteger("Excluir Inscrição", "Digite o ID da Oportunidade:")
    if matricula is None or cod_proj is None or id_op is None:
        return
    
    confirmar = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir a inscrição do aluno {matricula} na oportunidade {cod_proj}-{id_op}?")
    if not confirmar:
        return

    sql = "DELETE FROM Inscreve WHERE Matricula = %s AND CodProjeto = %s AND IdOportunidade = %s;"
    
    if executar_operacao(sql, (matricula, cod_proj, id_op)):
        messagebox.showinfo("Sucesso", "Inscrição excluída com sucesso.")
        texto_area.delete(1.0, tk.END)
        texto_area.insert(tk.END, "Inscrição removida.")
    else:
        messagebox.showwarning("Falha", "Não foi possível excluir a inscrição. Verifique os dados.")

def criar_interface():
    # cria a janela principal e os widgets da interface
    root = ctk.CTk()
    root.title("Sistema de Projetos Acadêmicos")
    root.geometry("700x500")
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # frame para os botoes e frame para a area de texto
    frame_botoes = ctk.CTkFrame(root, bg_color="transparent")
    frame_texto = ctk.CTkFrame(root, bg_color="transparent")
    frame_botoes.pack(side=ctk.LEFT, fill=ctk.Y, padx=10, pady=10)
    frame_texto.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True, padx=10, pady=10)

    # area de texto para exibir resultados
    texto_area = scrolledtext.ScrolledText(frame_texto, width=80, height=25, font=("Courier New", 10))
    texto_area.pack(fill=ctk.BOTH, expand=True)

    # botoes consulta
    label_consultas = ctk.CTkLabel(frame_botoes, text="Consultas", font=("Arial", 14, "bold"))
    label_consultas.pack(pady=10)

    btn1 = ctk.CTkButton(frame_botoes, text="Listar Projetos", command=lambda: consulta1_listar_projetos_professores(texto_area))
    btn1.pack(fill=ctk.X, pady=2)

    btn2 = ctk.CTkButton(frame_botoes, text="Listar Alunos Por Projetos", command=lambda: consulta2_listar_alunos_por_projeto(texto_area))
    btn2.pack(fill=ctk.X, pady=2)

    btn3 = ctk.CTkButton(frame_botoes, text="Listar Contribuições por Financiador", command=lambda: consulta3_listar_contribuicoes_por_financiador(texto_area))
    btn3.pack(fill=ctk.X, pady=2)
    
    btn4 = ctk.CTkButton(frame_botoes, text="Status de Vagas", command=lambda: consulta4_contar_vagas_por_oportunidade(texto_area))
    btn4.pack(fill=ctk.X, pady=2)

    btn5 = ctk.CTkButton(frame_botoes, text="Listar Financiadores", command=lambda:consulta5_listar_financiadores(texto_area))
    btn5.pack(fill=ctk.X, pady=2)

    btn_consulta6 = ctk.CTkButton(frame_botoes, text="Projetos por Nome do Professor", command=lambda: consulta6_listar_projetos_por_nome_professor(texto_area))
    btn_consulta6.pack(fill=ctk.X, pady=2)

    btn_consulta7 = ctk.CTkButton(frame_botoes, text="Disciplinas por Departamento", command=lambda:consulta7_listar_disciplinas_por_departamento(texto_area))
    btn_consulta7.pack(fill=ctk.X, pady=2)

    # botoes atualizacao
    label_updates = ctk.CTkLabel(frame_botoes, text="Operações", font=("Arial", 14, "bold"))
    label_updates.pack(pady=(20, 10))

    btn5 = ctk.CTkButton(frame_botoes, text="Aprovar Aluno Inscrito", command=lambda: atualizacao1_aprovar_aluno(texto_area))
    btn5.pack(fill=ctk.X, pady=2)

    btn6 = ctk.CTkButton(frame_botoes, text="Excluir Inscrição", command=lambda: atualizacao2_excluir_inscricao(texto_area))
    btn6.pack(fill=ctk.X, pady=2)

    def fechar_janela():
        if conn:
            conn.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", fechar_janela) # Garante que a conexão feche ao clicar no 'X'
    btn_sair = ctk.CTkButton(frame_botoes, text="Sair", command=fechar_janela)
    btn_sair.pack(fill=ctk.X, pady=(20, 5))

    return root

if __name__ == "__main__":
    conn = conectar_bd()
    if conn:
        app = criar_interface()
        app.mainloop()