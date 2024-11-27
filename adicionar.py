import tkinter as tk
from tkinter import ttk, messagebox

def tela_adicionar_dados():

    from cv import main_interface
    from cv import conectar_banco
    janela = tk.Toplevel()
    janela.title("Adicionar Dados")
    # Obtém as dimensões da tela
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    
    # Define as dimensões da janela
    largura_janela_cliente = 400
    altura_janela_cliente = 300
    
    # Calcula a posição para centralizar a janela
    pos_x_cliente = (largura_tela - largura_janela_cliente) // 2
    pos_y_cliente = (altura_tela - altura_janela_cliente) // 2
    
    # Centraliza a janela
    janela.geometry(f"{largura_janela_cliente}x{altura_janela_cliente}+{pos_x_cliente}+{pos_y_cliente}")

    def voltar():
        janela.destroy()
        main_interface()

    def adicionar_clientes():
        # Janela para inserir dados do cliente
        janela_adicionar_cliente = tk.Toplevel(janela)
        # Obtém as dimensões da tela
        largura_tela = janela.winfo_screenwidth()
        altura_tela = janela.winfo_screenheight()

        # Define as dimensões da janela
        largura_janela_cliente = 400
        altura_janela_cliente = 300

        # Calcula a posição para centralizar a janela
        pos_x_cliente = (largura_tela - largura_janela_cliente) // 2
        pos_y_cliente = (altura_tela - altura_janela_cliente) // 2

        # Centraliza a janela
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
        
            # Verifica se o CNPJ é um número inteiro
            if not cnpj_cliente.isdigit():
                messagebox.showerror("Erro", "CNPJ deve ser um número inteiro!")
                return
        
            try:
                conn = conectar_banco()
                if conn is None:
                    return
        
                cursor = conn.cursor()
        
                # Inserir dados na tabela TB001_CLIENTES sem especificar o C001_ID
                query_cliente = """INSERT INTO TB001_CLIENTES (C001_NOME, C001_CNPJ)
                                   VALUES (?, ?)"""
                cursor.execute(query_cliente, (nome_cliente, cnpj_cliente))
        
                # Commit antes de acessar o último ID (apesar do erro com o ID)
                conn.commit()
        
                # Obter o último ID inserido (para SQL Server, usamos SCOPE_IDENTITY())
                cursor.execute("SELECT SCOPE_IDENTITY()")
                cliente_id = cursor.fetchone()[0]  # Obtém o último ID inserido
        
                # Inserir dados na tabela TB006_ClienteProcesso (associando o cliente ao processo)
                try:
                    query_associacao = """INSERT INTO TB006_ClienteProcesso (C001_ID, C002_ID, C006_Ordem)
                                          VALUES (?, ?, ?)"""
                    cursor.execute(query_associacao, (cliente_id, 1, 1))  # Alterar o ID do processo conforme necessário
                    conn.commit()  # Commit novamente após a inserção na tabela TB006_ClienteProcesso
                except Exception as e:
                    # Ignora o erro se for relacionado à coluna C001_ID (erro específico de violação de constraint)
                    if "NULL" in str(e) and "C001_ID" in str(e):
                        pass  # Ignora o erro específico relacionado ao C001_ID
                    else:
                        raise  # Caso contrário, levanta o erro para ser tratado
                    
                # Fechar conexão
                conn.close()
        
                # Exibe a mensagem de sucesso
                messagebox.showinfo("Sucesso", "Cliente adicionado com sucesso!")
                janela_adicionar_cliente.destroy()
        
            except Exception as e:
                # Exibe erro se for algo diferente de conexão ou CNPJ inválido
                if "CNPJ" not in str(e):
                    messagebox.showerror("Erro", f"Erro ao adicionar cliente: {e}")
        



        # Botão para salvar o cliente
        btn_salvar_cliente = tk.Button(janela_adicionar_cliente, text="Salvar Cliente", command=salvar_cliente)
        btn_salvar_cliente.pack(pady=20)


    def adicionar_processos():
        # Janela principal
        janela = tk.Tk()
        janela.withdraw()  # Esconde a janela principal
        
        # Janela para escolher entre SITE ou ERP
        janela_adicionar_processo = tk.Toplevel(janela)
        janela_adicionar_processo.title("Adicionar Processo")
        
        # Obtém as dimensões da tela
        largura_tela = janela.winfo_screenwidth()
        altura_tela = janela.winfo_screenheight()
        
        # Define as dimensões da janela
        largura_janela = 400
        altura_janela = 300
        
        # Calcula a posição para centralizar a janela
        pos_x = (largura_tela - largura_janela) // 2
        pos_y = (altura_tela - altura_janela) // 2
        
        # Centraliza a janela
        janela_adicionar_processo.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")
        

        def adicionar_processos_site():
            janela_adicionar_processo.destroy()
            # Chama função para adicionar processo e ações de SITE
            adicionar_processos_site_actions()

        def adicionar_processos_erp():
            janela_adicionar_processo.destroy()
            # Chama função para adicionar processo e ações de ERP
            adicionar_processos_erp_actions()

        # Botões para escolher entre SITE ou ERP
        btn_site = tk.Button(janela_adicionar_processo, text="Adicionar Processo - Site", command=adicionar_processos_site)
        btn_erp = tk.Button(janela_adicionar_processo, text="Adicionar Processo - ERP", command=adicionar_processos_erp)

        btn_site.pack(pady=10)
        btn_erp.pack(pady=10)

    def adicionar_processos_site_actions():
        # Janela para adicionar dados ao processo e ações no site
        janela_processos_site = tk.Toplevel(janela)
        janela_processos_site.title("Adicionar Processo - Site")
        
        # Define o tamanho da janela
        largura_janela = 225
        altura_janela = 600
        janela_processos_site.geometry(f"{largura_janela}x{altura_janela}")  # Ajuste o tamanho conforme necessário

        # Centraliza a janela
        largura_tela = janela_processos_site.winfo_screenwidth()  # Largura da tela
        altura_tela = janela_processos_site.winfo_screenheight()  # Altura da tela
        pos_x = (largura_tela - largura_janela) // 2  # Calcula a posição X
        pos_y = (altura_tela - altura_janela) // 2  # Calcula a posição Y
        janela_processos_site.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")  # Coloca no centro
    

        # Impede a maximização e redimensionamento da janela
        janela_processos_site.state('normal')

        # Criando o canvas e a barra de rolagem
        canvas = tk.Canvas(janela_processos_site)
        scrollbar = tk.Scrollbar(janela_processos_site, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # Adiciona a barra de rolagem
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", on_frame_configure)

        # Criar um label centralizado
        tk.Label(frame, text="Nome do Processo", anchor="center").pack(pady=10, padx=10, anchor="center")

        # Criar a caixa de entrada centralizada
        entry_nome_processo = tk.Entry(frame)
        entry_nome_processo.pack(pady=10, padx=10, fill="x", anchor="center")

        tk.Label(frame, text="Observação do Processo (Opcional)", anchor="center").pack(pady=10, padx=10, anchor="center")
        entry_observacao_processo = tk.Entry(frame)
        entry_observacao_processo.pack(pady=10, padx=10, fill="x", anchor="center")

        # Listas para armazenar as ações e tipos
        lista_acoes = []
        lista_tipos = []

        def adicionar_acao():
            # Cria novos campos para Ação e Tipo da Ação
            tk.Label(frame, text="Ação", anchor="center").pack(pady=5, padx=10, anchor="center")
            entry_acao_site = tk.Entry(frame)
            entry_acao_site.pack(pady=5, padx=10, fill="x", anchor="center")

            tk.Label(frame, text="Tipo da Ação", anchor="center").pack(pady=5, padx=10, anchor="center")
            entry_tipo_acao = tk.Entry(frame)
            entry_tipo_acao.pack(pady=5, padx=10, fill="x", anchor="center")

            # Adiciona nas listas
            lista_acoes.append(entry_acao_site)
            lista_tipos.append(entry_tipo_acao)

        # Botão para adicionar uma nova ação
        btn_adicionar_acao = tk.Button(frame, text="Adicionar Ação", command=adicionar_acao)
        btn_adicionar_acao.pack(pady=10, padx=10, anchor="center")

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

                # Inserir dados na tabela TB002_PROCESSOS
                query_processo = """INSERT INTO TB002_PROCESSOS (C002_Nome, C002_Observacao)
                    OUTPUT INSERTED.C002_ID  -- Captura o ID gerado
                    VALUES (?, ?)"""
                cursor.execute(query_processo, (nome_processo, observacao_processo))

                processo_id = cursor.fetchone()[0]  # Obtém o último ID inserido
                print(f"Id do processo: {processo_id}")
                ordem = 1
                # Salvar as ações e tipos no banco
                for acao_site, tipo_acao in zip(lista_acoes, lista_tipos):
                    acao = acao_site.get()
                    tipo = tipo_acao.get()

                    if not acao or not tipo:
                        break

                    # Inserir a ação no site na tabela TB003_SITE
                    query_acao_site = """INSERT INTO TB003_SITE (C003_ACAO, C003_TIPO)
                                        OUTPUT INSERTED.C003_ID  -- Captura o ID gerado
                                         VALUES (?, ?)"""
                    cursor.execute(query_acao_site, (acao, tipo))

                    acao_site_id = cursor.fetchone()[0]  # Obtém o último ID inserido
                    print(f"Id da acao: {acao_site_id}")
                    # Definir sequência de ação
                    query_sequencia = """INSERT INTO TB007_SequenciaAcao (C002_ID, C007_Ordem, C007_TabelaAcao, C007_IdTabela)
                                        VALUES (?, ?, ?, ?)"""
                    cursor.execute(query_sequencia, (processo_id, ordem, 'TB003_SITE', acao_site_id))
                    ordem += 1

                # Commit final
                conn.commit()
                conn.close()

                messagebox.showinfo("Sucesso", "Processo e ações do site adicionados com sucesso!")
                janela_processos_site.destroy()

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar processo no site: {e}")

        # Botão para salvar o processo e as ações
        btn_salvar_processo_site = tk.Button(frame, text="Salvar Processo no Site", command=salvar_processo_site)
        btn_salvar_processo_site.pack(pady=20, padx=10, anchor="center")

        # Habilitar rolagem do mouse
        def mouse_wheel(event):
            if event.delta:
                canvas.yview_scroll(-1*(event.delta//120), "units")

        janela_processos_site.bind_all("<MouseWheel>", mouse_wheel)



    def adicionar_processos_erp_actions():
        # Janela para adicionar dados ao processo e ações no ERP
        janela_processos_erp = tk.Toplevel(janela)
        janela_processos_erp.title("Adicionar Processo - ERP")

        # Define o tamanho da janela
        largura_janela = 225
        altura_janela = 600
        janela_processos_erp.geometry(f"{largura_janela}x{altura_janela}")  # Ajuste o tamanho conforme necessário

        # Centraliza a janela
        largura_tela = janela_processos_erp.winfo_screenwidth()  # Largura da tela
        altura_tela = janela_processos_erp.winfo_screenheight()  # Altura da tela
        pos_x = (largura_tela - largura_janela) // 2  # Calcula a posição X
        pos_y = (altura_tela - altura_janela) // 2  # Calcula a posição Y
        janela_processos_erp.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")  # Coloca no centro
    

        # Impede a maximização e redimensionamento da janela
        janela_processos_erp.state('normal')

        # Criando o canvas e a barra de rolagem
        canvas = tk.Canvas(janela_processos_erp)
        scrollbar = tk.Scrollbar(janela_processos_erp, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # Adiciona a barra de rolagem
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", on_frame_configure)

        # Labels e entradas para o processo
        tk.Label(frame, text="Nome do Processo", anchor="center").pack(pady=10, padx=10, anchor="center")
        entry_nome_processo_erp = tk.Entry(frame)
        entry_nome_processo_erp.pack(pady=10, padx=10, fill="x", anchor="center")

        tk.Label(frame, text="Observação do Processo (Opcional)", anchor="center").pack(pady=10, padx=10, anchor="center")
        entry_observacao_processo_erp = tk.Entry(frame)
        entry_observacao_processo_erp.pack(pady=10, padx=10, fill="x", anchor="center")


        # Listas para armazenar as ações e tipos
        lista_acoes = []
        lista_tipos = []

        def adicionar_acao():
            # Cria novos campos para Ação e Tipo da Ação
            tk.Label(frame, text="Ação", anchor="center").pack(pady=5, padx=10, anchor="center")
            entry_acao_erp = tk.Entry(frame)
            entry_acao_erp.pack(pady=5, padx=10, fill="x", anchor="center")
            
            tk.Label(frame, text="Tipo da Ação", anchor="center").pack(pady=5, padx=10, anchor="center")
            entry_tipo_acao = tk.Entry(frame)
            entry_tipo_acao.pack(pady=5, padx=10, fill="x", anchor="center")


            # Adiciona nas listas
            lista_acoes.append(entry_acao_erp)
            lista_tipos.append(entry_tipo_acao)

        # Botão para adicionar uma nova ação
        btn_adicionar_acao = tk.Button(frame, text="Adicionar Ação", command=adicionar_acao)
        btn_adicionar_acao.pack(pady=10, padx=10, anchor="center")

        def salvar_processo_erp():
            nome_processo_erp = entry_nome_processo_erp.get()
            observacao_processo_erp = entry_observacao_processo_erp.get()

            if not nome_processo_erp:
                messagebox.showwarning("Aviso", "O nome do processo é obrigatório!")
                return

            try:
                conn = conectar_banco()
                if conn is None:
                    return

                cursor = conn.cursor()
                # Inserir dados na tabela TB002_PROCESSOS
                query_processo = """INSERT INTO TB002_PROCESSOS (C002_Nome, C002_Observacao)
                                    OUTPUT INSERTED.C002_ID  -- Captura o ID gerado
                                    VALUES (?, ?)"""
                cursor.execute(query_processo, (nome_processo_erp, observacao_processo_erp))
                processo_id = cursor.fetchone()[0]  # Obtém o último ID inserido
                print(f"Id do processo: {processo_id}")
                ordem = 1
                # Salvar as ações e tipos no banco
                for acao_erp, tipo_acao in zip(lista_acoes, lista_tipos):
                    acao = acao_erp.get()
                    tipo = tipo_acao.get()

                    if not acao or not tipo:
                        break

                    # Inserir a ação no ERP na tabela TB004_ERP
                    query_acao_erp = """INSERT INTO TB004_ERP (C004_ACAO, C004_TIPO)
                                        OUTPUT INSERTED.C004_ID  -- Captura o ID gerado
                                        VALUES (?, ?)"""
                    cursor.execute(query_acao_erp, (acao, tipo))

                    acao_erp_id = cursor.fetchone()[0]  # Obtém o último ID inserido
                    print(f"Id da acao ERP: {acao_erp_id}")
                    # Definir sequência de ação
                    query_sequencia = """INSERT INTO TB007_SequenciaAcao (C002_ID, C007_Ordem, C007_TabelaAcao, C007_IdTabela)
                                        VALUES (?, ?, ?, ?)"""
                    cursor.execute(query_sequencia, (processo_id, ordem, 'TB004_ERP', acao_erp_id))
                    ordem += 1

                # Commit final
                conn.commit()
                conn.close()

                messagebox.showinfo("Sucesso", "Processo e ações do ERP adicionados com sucesso!")
                janela_processos_erp.destroy()

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar processo no ERP: {e}")

        # Botão para salvar o processo e as ações
        btn_salvar_processo_erp = tk.Button(frame, text="Salvar Processo no ERP", command=salvar_processo_erp)
        btn_salvar_processo_erp.pack(pady=20, padx=10, anchor="center")

        # Habilitar rolagem do mouse
        def mouse_wheel(event):
            if event.delta:
                canvas.yview_scroll(-1*(event.delta//120), "units")

        janela_processos_erp.bind_all("<MouseWheel>", mouse_wheel)


    # Botões para adicionar
    btn_add_clientes = tk.Button(janela, text="Adicionar Clientes", command=adicionar_clientes, width=20)
    btn_add_processos = tk.Button(janela, text="Adicionar Processos", command=adicionar_processos, width=20)

    btn_add_clientes.pack(pady=20)
    btn_add_processos.pack(pady=20)