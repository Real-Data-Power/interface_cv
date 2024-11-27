import tkinter as tk
from tkinter import ttk, messagebox

def tela_alterar_dados():
    from cv import main_interface
    from cv import conectar_banco
    janela = tk.Toplevel()
    janela.title("Alterar Dados")
    janela.geometry("900x600")
    janela.state('zoomed')

    tabela_selecionada = tk.StringVar()
    colunas_atuais = []
    dados_originais = []
    dados_editados = {}

    def voltar():
        janela.destroy()
        main_interface()

    def carregar_tabelas():
        conn = conectar_banco()
        if conn is None:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
            tabelas = [row[0] for row in cursor.fetchall()]
            conn.close()

            # Remover tabelas indesejadas
            tabelas = [tabela for tabela in tabelas if tabela.lower() != "sysdiagrams"]
            return tabelas
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar tabelas: {e}")
            return []

    def carregar_dados():
        nonlocal colunas_atuais, dados_originais, dados_editados
        tabela = tabela_selecionada.get()
        if not tabela:
            return

        conn = conectar_banco()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {tabela}")
            colunas_atuais = [desc[0] for desc in cursor.description]
            dados_originais = cursor.fetchall()
            dados_editados = {}
            conn.close()

            # Atualizar Treeview
            tree.delete(*tree.get_children())
            tree["columns"] = colunas_atuais

            for col in colunas_atuais:
                tree.heading(col, text=col, anchor="center")
                tree.column(col, width=150, anchor="center")  # Melhor espaçamento

            # Inserir dados formatados
            for row in dados_originais:
                # Converte os valores para strings limpas
                row_formatada = [str(valor) if valor is not None else "" for valor in row]
                tree.insert("", "end", values=row_formatada)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {e}")
            conn.close()


    def salvar_alteracoes():
        if not messagebox.askyesno("Confirmação", "Tem certeza de que deseja salvar as alterações?"):
            return

        if not dados_editados:
            messagebox.showinfo("Aviso", "Nenhuma alteração realizada.")
            return

        try:
            conn = conectar_banco()
            if conn is None:
                return

            cursor = conn.cursor()
            tabela = tabela_selecionada.get()

            for item_id, novo_valor in dados_editados.items():
                set_clauses = ", ".join(
                    f"{col} = ?" for col in colunas_atuais if col != colunas_atuais[0]  # Ignorar o ID principal
                )
                query = f"UPDATE {tabela} SET {set_clauses} WHERE {colunas_atuais[0]} = ?"
                cursor.execute(query, *novo_valor[1:], item_id)

            conn.commit()
            conn.close()

            messagebox.showinfo("Sucesso", "Alterações salvas com sucesso!")
            carregar_dados()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar alterações: {e}")

    def editar_celula(event):
        nonlocal dados_editados
        item = tree.focus()
        if not item:
            return

        col_index = tree.identify_column(event.x).replace("#", "")
        col_index = int(col_index) - 1

        if col_index < 0 or col_index >= len(colunas_atuais):
            return

        coluna = colunas_atuais[col_index]
        if col_index == 0:  # Bloquear edição do ID principal
            messagebox.showinfo("Aviso", f"Você não pode editar o campo '{coluna}'.")
            return

        item_valores = tree.item(item)["values"]

        def salvar_edicao():
            novo_valor = entry.get()
            item_valores[col_index] = novo_valor
            tree.item(item, values=item_valores)

            item_id = item_valores[0]
            dados_editados[item_id] = item_valores
            janela_edicao.destroy()

        janela_edicao = tk.Toplevel(janela)
        janela_edicao.title("Editar Célula")
        janela_edicao.geometry("300x150")

        # Centralizar a janela de edição na tela
        screen_width = janela.winfo_screenwidth()
        screen_height = janela.winfo_screenheight()
        window_width = 300
        window_height = 150
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        janela_edicao.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        tk.Label(janela_edicao, text=f"Editando: {coluna}").pack(pady=10)
        entry = tk.Entry(janela_edicao)
        entry.insert(0, item_valores[col_index])
        entry.pack(pady=5)
        btn_salvar = tk.Button(janela_edicao, text="Salvar", command=salvar_edicao)
        btn_salvar.pack(pady=10)

    # Botão Voltar
    btn_voltar = tk.Button(janela, text="Voltar", command=voltar)
    btn_voltar.pack(anchor="nw", padx=10, pady=10)

    # Dropdown de Tabelas
    tabelas_disponiveis = carregar_tabelas()
    if not tabelas_disponiveis:
        messagebox.showerror("Erro", "Nenhuma tabela encontrada no banco de dados.")
        janela.destroy()
        main_interface()
        return

    tk.Label(janela, text="Selecione uma Tabela").pack()
    tabela_selecionada.set(tabelas_disponiveis[0])  # Define a tabela inicial
    dropdown = ttk.OptionMenu(janela, tabela_selecionada, tabelas_disponiveis[0], *tabelas_disponiveis, command=lambda _: carregar_dados())
    dropdown.pack(pady=5)

    # Treeview para exibir dados
    tree_frame = tk.Frame(janela)
    tree_frame.pack(fill="both", expand=True)
    tree = ttk.Treeview(tree_frame, show="headings")
    tree.pack(side="left", fill="both", expand=True)
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscroll=scrollbar.set)

    # Vincular evento de clique para edição
    tree.bind("<Double-1>", editar_celula)

    # Botão Salvar
    btn_salvar = tk.Button(janela, text="Salvar Alterações", command=salvar_alteracoes)
    btn_salvar.pack(pady=10)
