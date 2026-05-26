import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from database import (criar_tabelas, salvar_configuracao, buscar_configuracao, adicionar_conta, adicionar_lancamento, buscar_lacamentos, buscar_contas, atualizar_status_conta,deletar_lancamento,
                      deletar_conta)

st.set_page_config(
  page_title = "Minhas Finanças",
  page_icon = "💰",
  layout = "centered"
)

st.markdown("""
    <style>
        .stApp {background-color:  #0f0f0f; color: white;}
        .stButton>button {background-color: #6C63FF;
            color: white;
            border-radius: 10px;
            width: 100%;
            padding: 10px;
            border: none;
        }
        .stTextInput>div>input,
        .stNumberInput>div>input {
            background-color: #1e1e1e;
            color: white !important;
            border-radius: 8px;
            border: 1px solid #6C63FF;
        }
        h1, h2, h3 { color: #6C63FF; }
        .stTabs [data-baseweb="tab"] {
            color: white;
        }
        .stTabs [aria-selected="true"] {
            background-color: #6C63FF;
            border-radius: 8px;
        }

        .stNumberInput label,
        .stTextInput label,
        .stSelectBox label,
        .stDateInput label{
            color: white !important;
            font-size: 16px !important;
            font-weight: 600 !important;
        }
        
    </style>
  """, unsafe_allow_html = True)

criar_tabelas()

st.title("💰Minhas Finanças")
st.caption("Controle financeiro pessoal")
st.divider()

aba1, aba2, aba3, aba4 = st.tabs([
  "⚙️Configuração",
  "💾Dashboard",
  "💵Lançamentos",
  "🗓️Contas a pagar"
])

#______ABA 1:CONFIGURAÇÃO_____________
with aba1:
  st.subheader("Configuaração do perfil financeiro")    

  config = buscar_configuracao()
  salario_atual = config[0] if config else 0.0
  meta_atual = config[1] if config else 0.0

  salario = st.number_input("Seu salário mensal (R$)",
        min_value= 0.0,
        value= float(salario_atual),
        step= 100.0,
        format= "%.2f"
  )

  meta = st.number_input(
    "Meta de economia mensal (R$)",
    min_value= 0.0,
    value= float(meta_atual),
    step=   50.0,
    format= "%.2f"
  )

  if st.button("Salvar configuração"):
    salvar_configuracao(salario, meta)
    st.success("Configuração salva com sucesso!")


#_____ABA 2: DASHBOARD____________

with aba2:

  st.subheader("Resumo de mês")

  config = buscar_configuracao()

  if not config:
    st.warning("Configure seu salário na aba Configuração primeiro.")
  else:
    salario = config[0]
    meta = config[1]

    lancamentos = buscar_lacamentos()

    #Calculos totais

    total_entradas = sum(l[2] for l in lancamentos if l[3] == "Entrada")
    total_saidas =  sum(l[2] for l in lancamentos if l[3] == "Saída")
    saldo = salario + total_entradas - total_saidas
    economia = saldo - (salario - meta)

    #Cards com métricas

    col1, col2, col3 = st.columns(3)
    col1.metric("💵 Saldo atual", f"R$ {saldo:.2f}")
    col2.metric("📈 Total entradas",f"R$ {total_entradas:.2f}")
    col3. metric("📈 Total saídas", f"R$ {total_saidas:.2f}")

    st.divider()

    #Barra de progresso da meta

    st.markdown("**Meta de economia**")
    progresso = max(0.0, min(economia / meta, 1.0)) if meta > 0 else 0.0
    st.progress(progresso)
    if economia >= 0:
      st.success(f"✅ Você economizou R\$ {economia:.2f} da meta de R$ {meta:.2f}")
    else:
      st.warning(f"⚠️ Você gastou R\$ {abs(economia):.2f} além do permitido para atingir sua meta de R$ {meta:.2f}")

    st.divider()

    #Gráfico de gastos por categoria

    if lancamentos:
      saidas = [(l[4], l[2]) for l in lancamentos if l[3] == "Saída"]
      if saidas:
        df = pd.DataFrame(saidas, columns= ["Categoria", "Valor"])
        df_grupo = df.groupby("Categoria"). sum().reset_index()
        fig = px.pie(
          df_grupo,
          names = "Categoria",
          values = "Valor",
          title = "Gastos por categoria",
          color_discrete_sequence=px.colors.sequential.Purples_r
          )
        st.plotly_chart (fig, use_container_width=True)
    else:
      st.info("Nenhum lançamento registrado ainda.")


#_____ABA 3:  LANÇAMENTOS_______________________________

with aba3:
  st.subheader("Registrar lançamento")

  col1, col2 = st.columns(2)
  with col1:
    tipo = st.selectbox("Tipo", ["Saída", "Entrada"])
    valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0, format="%.2f")

  with col2:
    categorias_saida=[
      "Alimentação", "Aluguel", "Saúde", "Transporte",
      "Educação", "Lazer", "Roupas", "Contas fixas", "Outros"
    ]
    categorias_entrada = ["Salário extra", "Freelance", "Presente", "Outros"]
    categorias = categorias_saida if tipo == "Saída" else  categorias_entrada
    categorias = st.selectbox("Categoria", categorias)
    data = st. datetime_input("Data", value=date.today(), format="DD/MM/YYYY")

  descricao = st.text_input ("Descrição (ex: Mercado, Uber, etc)")

  if st.button("Registrar lançamento"):
    if descricao and valor > 0:
      adicionar_lancamento(descricao, valor, tipo, categorias, str(data))
      st.success("Lançamento registrado!")
      st.rerun()
    else:
      st.warning("Preencha a descrição e o valor.")

  st.divider()
  st.subheader("Histórico")

  lancamentos = buscar_lacamentos()
  if lancamentos:
    for l in lancamentos:
      col1, col2, col3 = st.columns([3, 1, 1])
      emoji = "🔴" if l[3] =="Saída" else "🟢"
      col1.markdown (f"{emoji} **{l[1]}** - {l[4]} - {l[5]}")
      col2.markdown (f"R$ {l[2]:.2f}")
      if col3.button("🗑️",  key= f"del_{l[0]}"):
        deletar_lancamento(l[0])
        st.rerun()

  else:
    st.info("Nenhum lançamento ainda.")


#_____ABA 4: CONTAS A PAGAR________________________________

with aba4:
  st.subheader("Cadastrar conta")

  col1,col2 = st.columns(2)
  with col1:
    desc_conta = st.text_input("Nome da conta (ex: Luz, Internet)")
    valor_conta = st.number_input("Valor (R$)", min_value=0.0,
                                  step=10.0, format="%.f", key="valor_conta")
  
  with col2:
    vencimento = st.date_input("Vencimento", key="venc", format="DD/MM/YYYY")

  if st.button ("Adicionar conta"):
    if desc_conta and valor_conta > 0:
      adicionar_conta(desc_conta, valor_conta, str(vencimento))
      st.success("Conta adicionada")
      st.rerun()
    else:
      st.warning("Preencha todos os campos")

  st.divider()
  st.subheader("Contas cadastradas")

  contas = buscar_contas()
  if contas:
    for c in contas:
      col1, col2, col3 = st.columns([3, 1, 1])
 
      #Emoji por status
      if c[4] == "Paga":
        emoji = "✅"
      elif c[4] == "Atrasada":
        emoji = "🔴"
      else:
        emoji = "⌛"

      from datetime import datetime 
      vencimento_formatado = datetime.strptime(c[3], r"%Y-%m-%d").strftime(r"%d-%m-%Y")
      col1.markdown(f"{emoji} **{c[1]} ** - vence {vencimento_formatado} ")
      col2.markdown(f"R$ {c[2]:.2f}")
      if col3.button("🗑️", key=f"del_conta_{c[0]}"):
        deletar_conta(c[0])
        st.rerun()

      novo_status = col3.selectbox(
        "Status",
        ["Pendente", "Paga", "Atrasada"],
        index=0 if c[4] not in ["Pendente", "Paga", "Atrasada"] else ["Pendente", "Paga", "Atrasada"].index(c[4]),
        key= f"status_{c[0]}"
        )

      if novo_status != c[4]:
        atualizar_status_conta(c[0], novo_status)
        st.rerun()
  
  else:
    st.info("Nenhuma conta cadastrada ainda.")

          




  





