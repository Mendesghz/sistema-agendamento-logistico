#Desenvolvido por Lucas Mendes - 29/03/2026


import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

st.set_page_config(
    page_title="NSK | Sistema Logístico",
    layout="wide",
    page_icon="🗓️"
)

st.title("Sistema de Agendamento NSK")
st.caption("Sistema Inteligente de Controle de Demurrage")

CAPACIDADE_DIARIA = 4
CUSTO_DEMURRAGE_CONTAINER = 1500

# ==========================================================
# FUNÇÕES
# ==========================================================

CAPACIDADE_DIARIA = 4
SENHA_DESBLOQUEIO = "123456"

def containers_no_dia(data):
    df_local = st.session_state.db
    return df_local[df_local["Data_Agendamento"] == data]

def dia_lotado(data):
    return len(containers_no_dia(data)) >= CAPACIDADE_DIARIA

def bloqueio_dia_seguinte(data):
    df_local = st.session_state.db
    dia_anterior = data - timedelta(days=1)

    return not df_local[
        df_local["Data_Agendamento"] == dia_anterior
    ].empty

def eh_dia_util(data):
    return data.weekday() < 5

def capacidade_disponivel(data):

    df_local = st.session_state.db

    ocupados = df_local[df_local["Data_Agendamento"] == data]

    return len(ocupados) < CAPACIDADE_DIARIA


def data_disponivel(data):

    hoje_local = datetime.today().date()

    if data <= hoje_local:
        return False

    if not eh_dia_util(data):
        return False

    if not capacidade_disponivel(data):
        return False

    return True


# ==========================================================
# UPLOAD
# ==========================================================

st.sidebar.header("📥 Importar Base")

arquivo = st.sidebar.file_uploader(
    "Envie o Excel",
    type=["xlsx"]
)

if arquivo:

    if st.session_state.get("arquivo_id") != arquivo.file_id:

        st.session_state.arquivo_id = arquivo.file_id

    else:

        arquivo = None

if arquivo:

    df = pd.read_excel(arquivo, engine="openpyxl")

    df.columns = df.columns.astype(str).str.strip()

    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    COL_DEMURRAGE = next(
        (c for c in df.columns if "demurrage" in c.lower()),
        None
    )

    COL_ETA = next(
        (c for c in df.columns if "eta" in c.lower()),
        None
    )

    if COL_DEMURRAGE is None or COL_ETA is None:

        st.error("Coluna de Demurrage ou ETA não encontrada.")

        st.write(df.columns.tolist())

        st.stop()

    df["Vencimento_Demurrage"] = pd.to_datetime(
        df[COL_DEMURRAGE],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    df["ETA_SZ"] = pd.to_datetime(
        df[COL_ETA],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    df = df.dropna(subset=["Vencimento_Demurrage"])

    if "Data_Agendamento" not in df.columns:

        df["Data_Agendamento"] = pd.NaT

    else:

        df["Data_Agendamento"] = pd.to_datetime(
            df["Data_Agendamento"],
            errors="coerce"
        ).dt.date

    st.session_state.db = df


if "db" not in st.session_state:

    st.warning("Envie a planilha para iniciar.")

    st.stop()

df = st.session_state.db

hoje = datetime.today().date()

# ==========================================================
# CÁLCULOS
# ==========================================================

df["Dias_para_Demurrage"] = (
    df["Vencimento_Demurrage"] - hoje
).apply(lambda x: x.days)

df["Dias_para_ETA"] = (
    df["ETA_SZ"] - hoje
).apply(lambda x: x.days if pd.notnull(x) else 999)


def classificar_risco(dias):

    if dias <= 3:
        return "🔴 CRÍTICO"

    elif dias <= 7:
        return "🟡 ALERTA"

    else:
        return "🟢 CONTROLADO"


df["Status_Risco"] = df["Dias_para_Demurrage"].apply(classificar_risco)

df = df.sort_values(by=["Dias_para_Demurrage", "Dias_para_ETA"])

st.session_state.db = df

# ==========================================================
# PAINEL
# ==========================================================

st.subheader("🔥 Painel de Risco")

col1, col2, col3 = st.columns(3)

col1.metric("Invoices Totais", len(df))

col2.metric(
    "Críticas",
    len(df[df["Status_Risco"] == "🔴 CRÍTICO"])
)

col3.metric(
    "Risco Financeiro Estimado",
    f"R$ {len(df[df['Status_Risco']=='🔴 CRÍTICO']) * CUSTO_DEMURRAGE_CONTAINER:,.0f}"
)

st.divider()

# ==========================================================
# ABAS
# ==========================================================

aba1, aba2, aba3 = st.tabs([
    "📅 Agendamento",
    "📆 Agenda Mensal",
    "📊 Base Completa"
])

# ==========================================================
# ABA 1 — AGENDAMENTO
# ==========================================================

with aba1:

    pendentes = st.session_state.db[
        st.session_state.db["Data_Agendamento"].isna()
    ]

    if pendentes.empty:
        st.success("Nenhuma invoice pendente.")
    else:

        st.dataframe(
            pendentes[
                [
                    "Invoices",
                    "Vencimento_Demurrage",
                    "ETA_SZ",
                    "Dias_para_Demurrage",
                    "Status_Risco",
                ]
            ],
            use_container_width=True
        )

        invoice_escolhida = st.selectbox(
            "Selecione a Invoice para Agendar:",
            pendentes["Invoices"].tolist()
        )

        data_escolhida = st.date_input(
            "Escolher data",
            min_value=datetime.today().date() + timedelta(days=1)
        )

        # 🔥 AQUI ESTAVA O ERRO
        if st.button("🚀 Confirmar Agendamento"):

            if not eh_dia_util(data_escolhida):
                st.error("❌ Final de semana não permitido")

            elif dia_lotado(data_escolhida):
                st.error("❌ Dia já atingiu capacidade máxima (4)")

            elif bloqueio_dia_seguinte(data_escolhida):
                st.error("❌ Não pode agendar em dias consecutivos")

            else:
                idx = st.session_state.db[
                    st.session_state.db["Invoices"] == invoice_escolhida
                ].index[0]

                st.session_state.db.loc[idx, "Data_Agendamento"] = data_escolhida

                st.success("✅ Agendado com sucesso!")
                st.rerun()

# ==========================================================
# ABA 2 — AGENDA MENSAL
# ==========================================================

with aba2:

    st.subheader("📅 Agenda de Containers")

    agendados = st.session_state.db[
        st.session_state.db["Data_Agendamento"].notna()
    ].copy()

    if agendados.empty:

        st.info("Nenhum container agendado ainda.")

    else:

        agendados["Data_Agendamento"] = pd.to_datetime(
            agendados["Data_Agendamento"]
        )

        mes = st.selectbox(
            "Selecionar mês",
            sorted(
                agendados["Data_Agendamento"]
                .dt.to_period("M")
                .astype(str)
                .unique()
            )
        )

        agenda_mes = agendados[
            agendados["Data_Agendamento"]
            .dt.to_period("M")
            .astype(str) == mes
        ]

        agenda_dia = (
            agenda_mes
            .groupby("Data_Agendamento")
            .size()
            .reset_index(name="Containers")
        )

        ano = agenda_mes["Data_Agendamento"].dt.year.iloc[0]
        mes_num = agenda_mes["Data_Agendamento"].dt.month.iloc[0]

        cal = calendar.monthcalendar(ano, mes_num)

        for semana in cal:

            cols = st.columns(7)

            for i, dia in enumerate(semana):

                if dia == 0:

                    cols[i].write("")

                else:

                    data = datetime(ano, mes_num, dia).date()

                    qtd = agenda_dia[
                        agenda_dia["Data_Agendamento"].dt.date == data
                    ]["Containers"]

                    if not qtd.empty:

                        cols[i].metric(
                            f"Dia {dia}",
                            f"{int(qtd.iloc[0])} cont."
                        )

                    else:

                        cols[i].metric(
                            f"Dia {dia}",
                            "0"
                        )

# ==========================================================
# ABA 3 — BASE COMPLETA
# ==========================================================

with aba3:

    st.subheader("📊 Base Completa")

    st.dataframe(
        st.session_state.db,
        use_container_width=True
    )