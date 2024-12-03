import tkinter as tk
from tkinter import ttk, messagebox
import pymysql  # Usando pymysql para se conectar ao MySQL

def tela_adicionar_dados():

    from cv import main_interface
    from cv import conectar_banco
    janela = tk.Toplevel()
    janela.title("Adicionar Dados")
    
    # Obtém as dimensões da tela
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()

    largura_janela_cliente = 400
    altura_janela_cliente = 300

    pos_x_cliente = (largura_tela - largura_janela_cliente) // 2
    pos_y_cliente = (altura_tela - altura_janela_cliente) // 2

    janela.geometry(f"{largura_janela_cliente}x{altura_janela_cliente}+{pos_x_cliente}+{pos_y_cliente}")

    def voltar():
        janela.destroy()
        main_interface()

    def adicionar_clientes():
        janela_adicionar_cliente = tk.Toplevel(janela)
        largura_tela = janela.winfo_screenwidth()
        altura_tela = janela.winfo_screenheight()

        largura_janela_cliente = 400
        altura_janela_cliente = 300

        pos_x_cliente = (largura_tela - largura_janela_cliente) // 2
        pos_y_cliente = (altura_tela - altura_janela_cliente) // 2

        janela_adicionar_cliente.geometry(f"{largura_janela_cliente}x{altura_janela_cliente}+{pos_x_cliente}+{pos_y_cliente}")

        tk.Label(janela_adicionar_cliente, text="Nome do Cliente").pack(pady=10)
        entry_nome_cliente = tk.Entry(janela_adicionar_cliente)
        entry_nome_cliente.pack(pady=10)

        tk.Label(janela_adicionar_cliente, text="CNPJ do Cliente").pack(pady=10)
        entry_cnpj_cliente = tk.Entry(janela_adicionar_cliente)
        entry_cnpj_cliente.pack(pady=10)
        
        def salvar_cliente():
            nome_cliente = entry_nome_cliente.get()
            cnpj_cliente = entry_cnpj_cliente.get()

            if not nome_cliente or not cnpj_cliente:
                messagebox.showwarning("Aviso", "Todos os campos são obrigatórios!")
                return

            if not cnpj_cliente.isdigit():
                messagebox.showerror("Erro", "CNPJ deve ser um número inteiro!")
                return

            try:
                conn = conectar_banco()
                if conn is None:
                    return

                cursor = conn.cursor()

                query_cliente = """INSERT INTO tb001_clientes (C001_NOME, C001_CNPJ)
                                   VALUES (%s, %s)"""
                cursor.execute(query_cliente, (nome_cliente, cnpj_cliente))

                # Commit antes de acessar o último ID
                conn.commit()

                # Obter o último ID inserido no MySQL
                cursor.execute("SELECT LAST_INSERT_ID()")
                cliente_id = cursor.fetchone()[0]

                try:
                    query_associacao = """INSERT INTO tb006_clienteprocesso (C001_ID, C002_ID, C006_Ordem)
                                          VALUES (%s, %s, %s)"""
                    cursor.execute(query_associacao, (cliente_id, 1, 1))  # Alterar o ID do processo conforme necessário
                    conn.commit()
                except Exception as e:
                    if "NULL" in str(e) and "C001_ID" in str(e):
                        pass  # Ignora o erro específico
                    else:
                        raise  # Levanta o erro para ser tratado
                    
                conn.close()

                messagebox.showinfo("Sucesso", "Cliente adicionado com sucesso!")
                janela_adicionar_cliente.destroy()

            except Exception as e:
                if "CNPJ" not in str(e):
                    messagebox.showerror("Erro", f"Erro ao adicionar cliente: {e}")

        btn_salvar_cliente = tk.Button(janela_adicionar_cliente, text="Salvar Cliente", command=salvar_cliente)
        btn_salvar_cliente.pack(pady=20)

    def adicionar_processos():
        janela = tk.Tk()
        janela.withdraw()  # Esconde a janela principal
        
        janela_adicionar_processo = tk.Toplevel(janela)
        janela_adicionar_processo.title("Adicionar Processo")

        largura_tela = janela.winfo_screenwidth()
        altura_tela = janela.winfo_screenheight()

        largura_janela = 400
        altura_janela = 300

        pos_x = (largura_tela - largura_janela) // 2
        pos_y = (altura_tela - altura_janela) // 2

        janela_adicionar_processo.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

        def adicionar_processos_site():
            janela_adicionar_processo.destroy()
            adicionar_processos_site_actions()

        def adicionar_processos_erp():
            janela_adicionar_processo.destroy()
            adicionar_processos_erp_actions()

        btn_site = tk.Button(janela_adicionar_processo, text="Adicionar Processo - Site", command=adicionar_processos_site)
        btn_erp = tk.Button(janela_adicionar_processo, text="Adicionar Processo - ERP", command=adicionar_processos_erp)

        btn_site.pack(pady=10)
        btn_erp.pack(pady=10)

    def adicionar_processos_site_actions():
        janela_processos_site = tk.Toplevel(janela)
        janela_processos_site.title("Adicionar Processo - Site")

        largura_janela = 225
        altura_janela = 600
        janela_processos_site.geometry(f"{largura_janela}x{altura_janela}")

        largura_tela = janela_processos_site.winfo_screenwidth()
        altura_tela = janela_processos_site.winfo_screenheight()
        pos_x = (largura_tela - largura_janela) // 2
        pos_y = (altura_tela - altura_janela) // 2
        janela_processos_site.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

        canvas = tk.Canvas(janela_processos_site)
        scrollbar = tk.Scrollbar(janela_processos_site, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", on_frame_configure)

        tk.Label(frame, text="Nome do Processo", anchor="center").pack(pady=10, padx=10, anchor="center")

        entry_nome_processo = tk.Entry(frame)
        entry_nome_processo.pack(pady=10, padx=10, fill="x", anchor="center")

        tk.Label(frame, text="Observação do Processo (Opcional)", anchor="center").pack(pady=10, padx=10, anchor="center")
        entry_observacao_processo = tk.Entry(frame)
        entry_observacao_processo.pack(pady=10, padx=10, fill="x", anchor="center")

        lista_acoes = []
        lista_tipos = []

        def adicionar_acao():
            tk.Label(frame, text="Ação", anchor="center").pack(pady=5, padx=10, anchor="center")
            entry_acao_site = tk.Entry(frame)
            entry_acao_site.pack(pady=5, padx=10, fill="x", anchor="center")

            tk.Label(frame, text="Tipo da Ação", anchor="center").pack(pady=5, padx=10, anchor="center")
            entry_tipo_acao = tk.Entry(frame)
            entry_tipo_acao.pack(pady=5, padx=10, fill="x", anchor="center")

            lista_acoes.append(entry_acao_site)
            lista_tipos.append(entry_tipo_acao)

        btn_adicionar_acao = tk.Button(frame, text="Adicionar Ação", command=adicionar_acao)
        btn_adicionar_acao.pack(pady=10)

        def salvar_processo_site():
            nome_processo = entry_nome_processo.get()
            observacao_processo = entry_observacao_processo.get()

            if not nome_processo:
                messagebox.showwarning("Aviso", "O nome do processo é obrigatório!")
                return

            try:
                conn = conectar_banco()
                if conn is None:
                    return

                cursor = conn.cursor()

                query_processo = """INSERT INTO tb002_processos (C002_Nome, C002_Observacao)
                                    VALUES (%s, %s)"""
                cursor.execute(query_processo, (nome_processo, observacao_processo))

                # Commit para salvar o processo
                conn.commit()

                # Obter o último ID inserido
                cursor.execute("SELECT LAST_INSERT_ID()")
                processo_id = cursor.fetchone()[0]

                ordem = 1
                for acao_site, tipo_acao in zip(lista_acoes, lista_tipos):
                    acao = acao_site.get()
                    tipo = tipo_acao.get()

                    if not acao or not tipo:
                        break
                    
                    # Inserir a ação no site na tabela TB003_SITE
                    query_acao_site = """INSERT INTO tb003_site (C003_ACAO, C003_TIPO)
                                         VALUES (%s, %s)"""
                    cursor.execute(query_acao_site, (acao, tipo))

                    # Captura o último ID inserido no MySQL
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    acao_site_id = cursor.fetchone()[0]  # Obtém o ID da última inserção
                    print(f"Id da acao: {acao_site_id}")

                    # Definir sequência de ação
                    query_sequencia = """INSERT INTO tb007_sequenciaacao (C002_ID, C007_Ordem, C007_TabelaAcao, C007_IdTabela)
                                         VALUES (%s, %s, %s, %s)"""
                    cursor.execute(query_sequencia, (processo_id, ordem, 'tb003_site', acao_site_id))
                    ordem += 1

                conn.commit()
                conn.close()
                messagebox.showinfo("Sucesso", "Processo adicionado com sucesso!")
                janela_processos_site.destroy()

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar processo: {e}")

        btn_salvar_processo = tk.Button(frame, text="Salvar Processo", command=salvar_processo_site)
        btn_salvar_processo.pack(pady=10)

    def adicionar_processos_erp_actions():
        janela_processos_erp = tk.Toplevel(janela)
        janela_processos_erp.title("Adicionar Processo - ERP")

        largura_janela = 225
        altura_janela = 600
        janela_processos_erp.geometry(f"{largura_janela}x{altura_janela}")

        largura_tela = janela_processos_erp.winfo_screenwidth()
        altura_tela = janela_processos_erp.winfo_screenheight()
        pos_x = (largura_tela - largura_janela) // 2
        pos_y = (altura_tela - altura_janela) // 2
        janela_processos_erp.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

        canvas = tk.Canvas(janela_processos_erp)
        scrollbar = tk.Scrollbar(janela_processos_erp, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", on_frame_configure)

        tk.Label(frame, text="Nome do Processo", anchor="center").pack(pady=10, padx=10, anchor="center")

        entry_nome_processo = tk.Entry(frame)
        entry_nome_processo.pack(pady=10, padx=10, fill="x", anchor="center")

        tk.Label(frame, text="Observação do Processo (Opcional)", anchor="center").pack(pady=10, padx=10, anchor="center")
        entry_observacao_processo = tk.Entry(frame)
        entry_observacao_processo.pack(pady=10, padx=10, fill="x", anchor="center")

        lista_acoes = []
        lista_tipos = []

        def adicionar_acao():
            tk.Label(frame, text="Ação", anchor="center").pack(pady=5, padx=10, anchor="center")
            entry_acao_site = tk.Entry(frame)
            entry_acao_site.pack(pady=5, padx=10, fill="x", anchor="center")

            tk.Label(frame, text="Tipo da Ação", anchor="center").pack(pady=5, padx=10, anchor="center")
            entry_tipo_acao = tk.Entry(frame)
            entry_tipo_acao.pack(pady=5, padx=10, fill="x", anchor="center")

            lista_acoes.append(entry_acao_site)
            lista_tipos.append(entry_tipo_acao)

        btn_adicionar_acao = tk.Button(frame, text="Adicionar Ação", command=adicionar_acao)
        btn_adicionar_acao.pack(pady=10)

        def salvar_processo_erp():
            nome_processo = entry_nome_processo.get()
            observacao_processo = entry_observacao_processo.get()

            if not nome_processo:
                messagebox.showwarning("Aviso", "O nome do processo é obrigatório!")
                return

            try:
                conn = conectar_banco()
                if conn is None:
                    return

                cursor = conn.cursor()

                query_processo = """INSERT INTO tb002_processos (C002_Nome, C002_Observacao)
                                    VALUES (%s, %s)"""
                cursor.execute(query_processo, (nome_processo, observacao_processo))

                # Commit para salvar o processo
                conn.commit()

                # Obter o último ID inserido
                cursor.execute("SELECT LAST_INSERT_ID()")
                processo_id = cursor.fetchone()[0]

                ordem = 1
                for acao_site, tipo_acao in zip(lista_acoes, lista_tipos):
                    acao = acao_site.get()
                    tipo = tipo_acao.get()

                    if not acao or not tipo:
                        break
                    
                    # Inserir a ação no site na tabela tb004_erp
                    query_acao_site = """INSERT INTO tb004_erp (C004_ACAO, C004_TIPO)
                                         VALUES (%s, %s)"""
                    cursor.execute(query_acao_site, (acao, tipo))

                    # Captura o último ID inserido no MySQL
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    acao_site_id = cursor.fetchone()[0]  # Obtém o ID da última inserção
                    print(f"Id da acao: {acao_site_id}")

                    # Definir sequência de ação
                    query_sequencia = """INSERT INTO tb007_sequenciaacao (C002_ID, C007_Ordem, C007_TabelaAcao, C007_IdTabela)
                                         VALUES (%s, %s, %s, %s)"""
                    cursor.execute(query_sequencia, (processo_id, ordem, 'tb004_erp', acao_site_id))
                    ordem += 1

                conn.commit()
                conn.close()
                messagebox.showinfo("Sucesso", "Processo adicionado com sucesso!")
                janela_processos_erp.destroy()

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar processo: {e}")

        btn_salvar_processo = tk.Button(frame, text="Salvar Processo", command=salvar_processo_erp)
        btn_salvar_processo.pack(pady=10)

    # Botões para adicionar clientes ou processos
    btn_adicionar_cliente = tk.Button(janela, text="Adicionar Cliente", command=adicionar_clientes)
    btn_adicionar_cliente.pack(pady=10)

    btn_adicionar_processo = tk.Button(janela, text="Adicionar Processo", command=adicionar_processos)
    btn_adicionar_processo.pack(pady=10)

    btn_voltar = tk.Button(janela, text="Voltar", command=voltar)
    btn_voltar.pack(pady=10)

