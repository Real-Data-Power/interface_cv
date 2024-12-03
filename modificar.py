import tkinter as tk
from tkinter import ttk, messagebox

def modificar_processo():
    from cv import conectar_banco  # A função de conexão com o banco de dados
    root = tk.Tk()
    root.title("Modificar Processo")

    # Maximiza a janela ao abrir
    root.state('zoomed')

    # Configuração da janela
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()

    largura_janela_cliente = 800
    altura_janela_cliente = 600

    pos_x_cliente = (largura_tela - largura_janela_cliente) // 2
    pos_y_cliente = (altura_tela - altura_janela_cliente) // 2

    root.geometry(f"{largura_janela_cliente}x{altura_janela_cliente}+{pos_x_cliente}+{pos_y_cliente}")

    # Função para carregar os processos
    def carregar_processos():
        conn = conectar_banco()
        if conn is None:
            return []
        cursor = conn.cursor()
        cursor.execute("SELECT C002_ID, C002_Nome FROM tb002_processos")
        processos = cursor.fetchall()
        conn.close()
        return processos

    # Função para carregar as etapas de um processo
    def carregar_etapas(processo_id):
        conn = conectar_banco()
        if conn is None:
            return []
        cursor = conn.cursor()
        cursor.execute("""
            SELECT C007_Ordem, C007_TabelaAcao, C007_IdTabela
            FROM tb007_sequenciaacao
            WHERE C002_ID = %s
            ORDER BY C007_Ordem
        """, (processo_id,))
        etapas = cursor.fetchall()
        conn.close()
        return etapas

    # Função para carregar as ações e tipos de uma tabela (tb003_site ou tb004_erp)
    def carregar_acoes(tipo_tabela, id_tabela):
        conn = conectar_banco()
        if conn is None:
            return []
        cursor = conn.cursor()
        if tipo_tabela == "tb004_erp":
            cursor.execute("SELECT C004_ACAO, C004_TIPO FROM tb004_erp WHERE C004_ID = %s", (id_tabela,))
        elif tipo_tabela == "tb003_site":
            cursor.execute("SELECT C003_ACAO, C003_TIPO FROM tb003_site WHERE C003_ID = %s", (id_tabela,))
        acoes = cursor.fetchall()
        conn.close()
        return acoes
    
    def adicionar_nova_etapa():
        processo_selecionado = combobox_processo.get()
        if not processo_selecionado:
            messagebox.showerror("Erro", "Selecione um processo.")
            return
    
        processo_id = processos_ids.get(processo_selecionado)
        if processo_id is None:
            messagebox.showerror("Erro", "Erro ao encontrar o ID do processo.")
            return
    
        acao = entry_acao_site.get().strip()
        tipo_acao = entry_tipo_acao.get().strip()
        ordem = entry_ordem.get().strip()
    
        if not acao or not tipo_acao or not ordem.isdigit():
            messagebox.showerror("Erro", "Preencha todas as caixas de texto corretamente.")
            return
    
        ordem = int(ordem)
        conn = conectar_banco()
        if conn is None:
            messagebox.showerror("Erro", "Falha ao conectar ao banco de dados.")
            return
    
        cursor = conn.cursor()
        try:
            # Verificar a tabela de ação do processo selecionado
            cursor.execute("""
                SELECT C007_TabelaAcao
                FROM tb007_sequenciaacao
                WHERE C002_ID = %s
                LIMIT 1
            """, (processo_id,))
            resultado = cursor.fetchone()
            if not resultado:
                messagebox.showerror("Erro", "Tabela de ação não encontrada para o processo.")
                return
    
            tabela_acao = resultado[0]  # Pode ser "tb003_site" ou "tb004_erp"
    
            # Verificar se a ação e tipo já existem
            if tabela_acao == "tb003_site":
                cursor.execute("""
                    SELECT C003_ID
                    FROM tb003_site
                    WHERE C003_ACAO = %s AND C003_TIPO = %s
                    LIMIT 1
                """, (acao, tipo_acao))
            elif tabela_acao == "tb004_erp":
                cursor.execute("""
                    SELECT C004_ID
                    FROM tb004_erp
                    WHERE C004_ACAO = %s AND C004_TIPO = %s
                    LIMIT 1
                """, (acao, tipo_acao))
            else:
                messagebox.showerror("Erro", f"Tabela de ação desconhecida: {tabela_acao}")
                return
    
            id_tabela_acao = cursor.fetchone()
            if id_tabela_acao:
                id_tabela_acao = id_tabela_acao[0]  # Usar o ID existente
            else:
                # Inserir na tabela apropriada se não existir
                if tabela_acao == "tb003_site":
                    cursor.execute("INSERT INTO tb003_site (C003_ACAO, C003_TIPO) VALUES (%s, %s)", (acao, tipo_acao))
                elif tabela_acao == "tb004_erp":
                    cursor.execute("INSERT INTO tb004_erp (C004_ACAO, C004_TIPO) VALUES (%s, %s)", (acao, tipo_acao))
    
                id_tabela_acao = cursor.lastrowid  # Obter o ID da nova linha inserida
    
            # Atualizar C007_Ordem na tb007_sequenciaacao
            cursor.execute("""
                UPDATE tb007_sequenciaacao
                SET C007_Ordem = C007_Ordem + 1
                WHERE C002_ID = %s AND C007_Ordem >= %s
            """, (processo_id, ordem))
    
            # Inserir nova linha em tb007_sequenciaacao
            cursor.execute("""
                INSERT INTO tb007_sequenciaacao (C002_ID, C007_Ordem, C007_TabelaAcao, C007_IdTabela)
                VALUES (%s, %s, %s, %s)
            """, (processo_id, ordem, tabela_acao, id_tabela_acao))
    
            conn.commit()
    
            # Atualizar o Treeview
            atualizar_treeview(processo_id)
    
            messagebox.showinfo("Sucesso", "Nova etapa adicionada com sucesso!")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Erro ao adicionar nova etapa: {e}")
        finally:
            conn.close()


    def atualizar_treeview(processo_id):
        # Limpar o Treeview existente
        for item in treeview.get_children():
            treeview.delete(item)

        conn = conectar_banco()
        if conn is None:
            messagebox.showerror("Erro", "Falha ao conectar ao banco de dados para atualizar o Treeview.")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT C007_Ordem, C007_TabelaAcao, C007_IdTabela
                FROM tb007_sequenciaacao
                WHERE C002_ID = %s
                ORDER BY C007_Ordem
            """, (processo_id,))
            etapas = cursor.fetchall()

            for ordem, tabela_acao, id_tabela in etapas:
                if tabela_acao == "tb003_site":
                    cursor.execute("SELECT C003_ACAO, C003_TIPO FROM tb003_site WHERE C003_ID = %s", (id_tabela,))
                elif tabela_acao == "tb004_erp":
                    cursor.execute("SELECT C004_ACAO, C004_TIPO FROM tb004_erp WHERE C004_ID = %s", (id_tabela,))
                else:
                    continue
                acoes = cursor.fetchone()
                if acoes:
                    acao, tipo_acao = acoes
                    treeview.insert("", "end", values=(ordem, acao, tipo_acao))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar Treeview: {e}")
        finally:
            conn.close()


    # Carregar os processos
    processos = carregar_processos()
    processos_names = [processo[1] for processo in processos]  # Exibir apenas os nomes
    processos_ids = {processo[1]: processo[0] for processo in processos}  # Mapeia nomes para IDs

    # Label e Combobox para selecionar o processo
    label_processo = tk.Label(root, text="Selecione um Processo:")
    label_processo.pack(pady=10)

    combobox_processo = ttk.Combobox(root, values=processos_names, state="readonly", width=50)
    combobox_processo.pack(pady=10)

    # Adicionando o Treeview com barra de rolagem
    treeview_frame = tk.Frame(root)
    treeview_frame.pack(pady=10, fill="both", expand=True)

    scrollbar_treeview = tk.Scrollbar(treeview_frame, orient="vertical")
    scrollbar_treeview.pack(side="right", fill="y")

    treeview = ttk.Treeview(treeview_frame, columns=("Ordem", "Ação", "Tipo de Ação"), show="headings", yscrollcommand=scrollbar_treeview.set)
    treeview.pack(pady=10, fill="both", expand=True)

    scrollbar_treeview.config(command=treeview.yview)

    treeview.heading("Ordem", text="Ordem")
    treeview.heading("Ação", text="Ação")
    treeview.heading("Tipo de Ação", text="Tipo de Ação")
    treeview.column("Ordem", width=100, anchor="w")
    treeview.column("Ação", width=200, anchor="w")
    treeview.column("Tipo de Ação", width=200, anchor="w")

    # Função para mostrar as etapas e ações ao selecionar o processo
    def mostrar_etapas():
        processo_selecionado = combobox_processo.get()
        if not processo_selecionado:
            print("Selecione um processo.")
            return
        processo_id = processos_ids.get(processo_selecionado)
        if processo_id is None:
            print("Erro ao encontrar o ID do processo.")
            return

        etapas = carregar_etapas(processo_id)

        for item in treeview.get_children():
            treeview.delete(item)

        if not etapas:
            print("Nenhuma etapa encontrada para o processo selecionado.")
            return

        for etapa in etapas:
            ordem, tabela_acao, id_tabela = etapa
            acoes = carregar_acoes(tabela_acao, id_tabela)
            for acao, tipo_acao in acoes:
                treeview.insert("", "end", values=(ordem, acao, tipo_acao))

    combobox_processo.bind("<<ComboboxSelected>>", lambda event: mostrar_etapas())

    # Caixas de texto para adicionar nova ação
    tk.Label(root, text="Ordem").pack(pady=5)
    entry_ordem = tk.Entry(root, width=20)
    entry_ordem.pack(pady=5)

    tk.Label(root, text="Ação").pack(pady=5)
    entry_acao_site = tk.Entry(root, width=40)
    entry_acao_site.pack(pady=5)

    tk.Label(root, text="Tipo de Ação").pack(pady=5)
    entry_tipo_acao = tk.Entry(root, width=40)
    entry_tipo_acao.pack(pady=5)

    # Botão para adicionar nova etapa
    btn_adicionar_acao = tk.Button(root, text="Adicionar Nova Ação", width=20, command=adicionar_nova_etapa)
    btn_adicionar_acao.pack(pady=10)

    root.mainloop()
