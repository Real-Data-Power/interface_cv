import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
from adicionar import tela_adicionar_dados
from alterar import tela_alterar_dados

# Funções para interagir com o banco de dados
def conectar_banco():
    DB_CONFIG = {
        "server": "DESKTOP-32TMBU8\\SQLEXPRESS",
        "database": "ColabVirtual",
        "username": "rdp",
        "password": "rdp",
    }
    try:
        conn = pyodbc.connect(
            f"DRIVER={{SQL Server}};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']};"
        )
        return conn
    except Exception as e:
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco de dados: {e}")
        return None

def listar_clientes():
    conn = conectar_banco()
    if conn is None:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT C001_ID, C001_Nome FROM TB001_CLIENTES")
    clientes = cursor.fetchall()
    conn.close()
    return clientes

def listar_processos():
    conn = conectar_banco()
    if conn is None:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT C002_ID, C002_Nome, C002_Observacao FROM TB002_PROCESSOS")
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
            INSERT INTO TB006_ClienteProcesso (C001_ID, C002_ID, C006_Ordem)
            VALUES (?, ?, ?)
        """, cliente_id, processo_id, ordem)
    
    conn.commit()
    conn.close()
    messagebox.showinfo("Sucesso", "Processos adicionados com sucesso!")

# Tela de adicionar processos a um cliente
def tela_adicionar_processos():
    root = tk.Tk()
    root.title("Adicionar Processos a um Cliente")

    # Obtém as dimensões da tela
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()

    # Define as dimensões da janela
    largura_janela_cliente = 600
    altura_janela_cliente = 400

    # Calcula a posição para centralizar a janela
    pos_x_cliente = (largura_tela - largura_janela_cliente) // 2
    pos_y_cliente = (altura_tela - altura_janela_cliente) // 2

    # Centraliza a janela
    root.geometry(f"{largura_janela_cliente}x{altura_janela_cliente}+{pos_x_cliente}+{pos_y_cliente}")

    # 1. Listar os clientes em um Combobox
    clientes = listar_clientes()
    cliente_names = [cliente[1] for cliente in clientes]
    cliente_ids = {cliente[1]: cliente[0] for cliente in clientes}

    label_cliente = tk.Label(root, text="Selecione um Cliente:")
    label_cliente.pack(pady=10)

    combobox_cliente = ttk.Combobox(root, values=cliente_names)
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
    altura_janela_cliente = 300

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

    # Botões principais
    btn_alterar = tk.Button(root, text="Alterar Dados", command=alterar_dados, width=20)
    btn_adicionar = tk.Button(root, text="Adicionar Dados", command=adicionar_dados, width=20)
    btn_adicionar_processos = tk.Button(root, text="Adicionar Processos a um Cliente", command=adicionar_processos_cliente, width=30)

    btn_alterar.pack(pady=20)
    btn_adicionar.pack(pady=20)
    btn_adicionar_processos.pack(pady=20)

    root.mainloop()

# Inicializa o sistema
if __name__ == "__main__":
    main_interface()
