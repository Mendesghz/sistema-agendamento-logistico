# 🚢 Sistema de Agendamento Logístico

Sistema desenvolvido para controle de agendamento de containers com foco na redução de custos de demurrage e organização operacional.

---

## 📌 Problema

Na operação logística, a falta de controle no agendamento pode gerar:

- Custos elevados de demurrage
- Falta de organização no recebimento
- Sobrecarga em dias específicos

---

## 💡 Solução

Este sistema permite:

- 📥 Importar planilhas Excel
- 📊 Analisar datas críticas automaticamente
- 📅 Agendar containers com regras inteligentes
- 🚫 Evitar conflitos e erros operacionais

---

## ⚙️ Funcionalidades

- Upload de planilha
- Cálculo de risco de demurrage
- Agendamento automático/manual
- Visualização em calendário
- Controle de capacidade por dia

---

## 🧠 Regras de Negócio

- Máximo de **4 containers por dia**
- Não permite finais de semana
- Bloqueio de dias consecutivos
- Não permite datas passadas

---

## 🛠️ Tecnologias

- Python
- Streamlit
- Pandas

---

## ▶️ Como rodar

```bash
pip install -r requirements.txt
streamlit run app.py
