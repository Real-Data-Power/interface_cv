import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
import sys
from adicionar import tela_adicionar_dados
from alterar import tela_alterar_dados
from modificar import modificar_processo


def conectar_banco():
    # Detalhes da conexão
    server = 'DESKTOP-32TMBU8\\SQLEXPRESS'
    database = 'colabvirtual'
    username = 'rdp'
    password = 'rdp'
    
    # String de conexão para o SQL Server via ODBC
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

    try:
        # Criar a conexão com o banco de dados
        conexao = pyodbc.connect(connection_string)
        return conexao
    except Exception as e:
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco de dados: {e}")
        return None

def listar_clientes():
    conn = conectar_banco()
    if conn is None:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT C001_ID, C001_NOME FROM tb001_clientes")
    clientes = cursor.fetchall()
    conn.close()
    return clientes

def listar_processos():
    conn = conectar_banco()
    if conn is None:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT C002_ID, C002_Nome, C002_Observacao FROM tb002_processos")
    processos = cursor.fetchall()
    conn.close()
    return processos

def adicionar_processos(cliente_id, processos_selecionados):
    conn = conectar_banco()
    if conn is None:
        return
    cursor = conn.cursor()

    # Insere os processos na ordem selecionada
    for ordem, processo_id in enumerate(processos_selecionados, start=1):
        cursor.execute("""
            INSERT INTO tb006_clienteprocesso (C001_ID, C002_ID, C006_Ordem)
            VALUES (?, ?, ?)
        """, (cliente_id, processo_id, ordem))
    
    conn.commit()
    conn.close()
    messagebox.showinfo("Sucesso", "Processos adicionados com sucesso!")

def tela_adicionar_processos():
    root = tk.Tk()
    root.title("Adicionar Processos a um Cliente")

    def voltar():
        root.destroy()  # Destrói a janela atual
        main_interface()  # Chama a função main_interface

    btn_voltar = tk.Button(root, text="Voltar", command=voltar)
    btn_voltar.pack(anchor="nw", padx=10, pady=10) 

    # Obtém as dimensões da tela
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()

    # Define as dimensões da janela
    largura_janela_cliente = 600
    altura_janela_cliente = 425

    # Calcula a posição para centralizar a janela
    pos_x_cliente = (largura_tela - largura_janela_cliente) // 2
    pos_y_cliente = (altura_tela - altura_janela_cliente) // 2

    # Centraliza a janela
    root.geometry(f"{largura_janela_cliente}x{altura_janela_cliente}+{pos_x_cliente}+{pos_y_cliente}")

    # 1. Listar os clientes em um Combobox (somente leitura)
    clientes = listar_clientes()
    cliente_names = [cliente[1] for cliente in clientes]
    cliente_ids = {cliente[1]: cliente[0] for cliente in clientes}

    label_cliente = tk.Label(root, text="Selecione um Cliente:")
    label_cliente.pack(pady=10)

    combobox_cliente = ttk.Combobox(root, values=cliente_names, state="readonly")
    combobox_cliente.pack(pady=10)

    # 2. Listar os processos em uma Listbox com múltiplas seleções
    processos = listar_processos()
    processos_names = [f"{processo[1]} - {processo[2]}" for processo in processos]
    processos_ids = {f"{processo[1]} - {processo[2]}": processo[0] for processo in processos}

    label_processos = tk.Label(root, text="Selecione os Processos:")
    label_processos.pack(pady=10)

    listbox_processos = tk.Listbox(root, selectmode=tk.MULTIPLE, height=10)
    for processo in processos_names:
        listbox_processos.insert(tk.END, processo)
    listbox_processos.pack(pady=10)

    # 3. Botão de adicionar processos
    def adicionar():
        cliente_selecionado = combobox_cliente.get()
        if not cliente_selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente.")
            return

        cliente_id = cliente_ids.get(cliente_selecionado)

        # Obter os processos selecionados
        processos_selecionados = [processos_ids[listbox_processos.get(i)] for i in listbox_processos.curselection()]
        if not processos_selecionados:
            messagebox.showwarning("Aviso", "Selecione pelo menos um processo.")
            return

        # Adicionar processos ao cliente
        adicionar_processos(cliente_id, processos_selecionados)

        # Fechar a janela atual
        root.destroy()

        # Voltar para a tela principal
        main_interface()

    btn_adicionar = tk.Button(root, text="Adicionar Processos", command=adicionar, width=20)
    btn_adicionar.pack(pady=20)

    root.mainloop()

# Função principal
def main_interface():
    root = tk.Tk()
    root.title("Gerenciador de Dados")

    # Configuração da janela
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()

    largura_janela_cliente = 400
    altura_janela_cliente = 350

    pos_x_cliente = (largura_tela - largura_janela_cliente) // 2
    pos_y_cliente = (altura_tela - altura_janela_cliente) // 2

    root.geometry(f"{largura_janela_cliente}x{altura_janela_cliente}+{pos_x_cliente}+{pos_y_cliente}")

    def alterar_dados():
        root.withdraw()
        tela_alterar_dados()

    def adicionar_dados():
        root.withdraw()
        tela_adicionar_dados()

    def adicionar_processos_cliente():
        root.withdraw()
        tela_adicionar_processos()

    def modificar_processo_cliente():
        root.withdraw()
        modificar_processo()

    # Função para sair
    def sair():
        root.quit()  # Encerra o loop principal do Tkinter, fechando a aplicação
        root.destroy()  # Destrói a janela do Tkinter
        sys.exit() # Força o encerramento do programa e libera o terminal

    # Botões principais
    btn_alterar = tk.Button(root, text="Alterar Dados", command=alterar_dados, width=20)
    btn_adicionar = tk.Button(root, text="Adicionar Dados", command=adicionar_dados, width=20)
    btn_adicionar_processos = tk.Button(root, text="Adicionar Processos a um Cliente", command=adicionar_processos_cliente, width=30)
    btn_modificar_processo = tk.Button(root, text="Modificar Processo", command=modificar_processo_cliente, width=30)  # Novo botão
    btn_sair = tk.Button(root, text="Sair", command=sair, width=20)

    btn_alterar.pack(pady=20)
    btn_adicionar.pack(pady=20)
    btn_adicionar_processos.pack(pady=20)
    btn_modificar_processo.pack(pady=20)
    btn_sair.pack(pady=20)

    root.mainloop()

# Inicializa o sistema
if __name__ == "__main__":
    main_interface()
