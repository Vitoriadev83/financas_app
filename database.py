import sqlite3

def conectar():
  return sqlite3.connect("banco.db")

def criar_tabelas():
  conn = conectar()
  cursor = conn.cursor()


  cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracao (
            id INTEGER PRIMARY KEY,
            salario REAL NOT NULL,
            meta_economia REAL NOT NULL
        )
    """)
  
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS lancamentos(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             descricao TEXT NOT NULL,
             valor REAL NOT NULL,
             tipo TEXT NOT NULL,
             categoria TEXT NOT NULL,
             data TEXT NOT NULL
         )
    """)
  
  cursor.execute("""
         CREATE TABLE IF NOT EXISTS contas(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             descricao TEXT NOT NULL,
             valor REAL NOT NULL,
             vencimento TEXT NOT NULL,
             status TEXT NOT NULL
         )
    """)
  

  conn.commit()
  conn.close()

def salvar_configuracao(salario, meta):
  conn = conectar()
  cursor = conn.cursor()
  cursor.execute("DELETE FROM configuracao")
  cursor.execute("INSERT INTO configuracao(id, salario, meta_economia)  VALUES(1, ?, ?)", (salario, meta))

  conn.commit()
  conn.close()

def buscar_configuracao():
  conn = conectar()
  cursor = conn.cursor()
  cursor.execute("SELECT salario, meta_economia FROM configuracao WHERE id = 1")
  resultado = cursor.fetchone()
  conn.close()
  return resultado

def adicionar_lancamento(descricao, valor, tipo, categoria, data):
  conn = conectar()
  cursor = conn.cursor()
  cursor.execute("""INSERT INTO lancamentos (descricao, valor, tipo, categoria, data) 
                 VALUES (?, ?, ?, ?, ?)
    """, (descricao, valor, tipo, categoria, data))
  conn.commit()
  conn.close()

def buscar_lacamentos():
  conn = conectar()
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM lancamentos ORDER BY data DESC")
  resultado = cursor.fetchall()
  conn.close()
  return resultado

def adicionar_conta(descricao, valor, vencimento):
  conn = conectar()
  cursor = conn.cursor()
  cursor.execute("""INSERT INTO contas (descricao, valor, vencimento, status)
                 VALUES(?, ?, ?, 'pendente')
    """, (descricao, valor, vencimento))
  conn.commit()
  conn.close()

def buscar_contas():
  conn = conectar()
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM contas ORDER BY vencimento ASC")
  resultado = cursor.fetchall()
  conn.close()
  return resultado

def atualizar_status_conta(conta_id, status):
  conn = conectar()
  cursor = conn.cursor()
  cursor.execute("UPDATE contas SET status = ? WHERE id = ?", (status,      conta_id,))
  conn.commit()
  conn.close()

def deletar_lancamento(lancamento_id):
  conn = conectar()
  cursor = conn.cursor()
  cursor.execute("DELETE FROM lancamentos WHERE id = ?", (lancamento_id,))
  conn.commit()
  conn.close()

def deletar_conta(conta_id):
  conn = conectar()
  cursor = conn.cursor()
  cursor.execute("DELETE FROM contas WHERE id = ?", (conta_id,))
  conn.commit()
  conn.close()

if __name__ == "__main__":
  criar_tabelas()
  print("Banco criado com sucesso!!!")


  
