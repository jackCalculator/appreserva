import streamlit as st
from datetime import datetime, timedelta

# Função para calcular anos, meses e dias entre duas datas
def diferenca_data(data_final, data_inicial):
    delta = data_final - data_inicial
    dias_totais = delta.days
    anos = dias_totais // 365
    meses = (dias_totais % 365) // 30
    dias = (dias_totais % 365) % 30
    return anos, meses, dias

# Função principal para calcular a reserva
def calcular_reserva(data_nascimento, data_entrada, desconto_pre2020, desconto_pos2020):
    # Converte datas para datetime.datetime
    data_entrada = datetime.combine(data_entrada, datetime.min.time())
    data_nascimento = datetime.combine(data_nascimento, datetime.min.time())
    
    # Datas fixas de referência
    data_regra_2019 = datetime(2020, 1, 1)
    data_regra_2025 = datetime(2025, 1, 1)
    data_limite_55 = datetime(2032, 1, 1)

    # 1. Regra Original (1960): 30 anos ajustados com desconto antes de 2020
    data_base_1960 = data_entrada + timedelta(days=30 * 365)
    desconto_anos_pre2020 = desconto_pre2020 / 12
    data_reserva_original = data_base_1960 - timedelta(days=int(desconto_anos_pre2020 * 365))

    # 2. Regra de 2019: Aplica pedágio de 17% sobre o tempo faltante ajustado com desconto
    tempo_faltante_2019 = (data_reserva_original - data_regra_2019).days / 365
    tempo_faltante_2019_com_pedagio = tempo_faltante_2019 * 1.17
    data_reserva_2019 = data_regra_2019 + timedelta(days=int(tempo_faltante_2019_com_pedagio * 365))

    # 3. Proposta Atual (2025): Aplica pedágio de 9% sobre o tempo faltante ajustado com novo desconto
    desconto_anos_pos2020 = desconto_pos2020 / 12
    data_reserva_2019_ajustada = data_reserva_2019 - timedelta(days=int(desconto_anos_pos2020 * 365))
    tempo_faltante_2025 = (data_reserva_2019_ajustada - data_regra_2025).days / 365
    tempo_faltante_2025_com_pedagio = tempo_faltante_2025 * 1.09
    data_reserva_proposta = data_regra_2025 + timedelta(days=int(tempo_faltante_2025_com_pedagio * 365))

    # 4. Critério de 55 Anos após 01/01/2032
    if data_reserva_proposta >= data_limite_55:
        idade_aos_55 = data_nascimento + timedelta(days=55 * 365)
        data_reserva_proposta = max(data_limite_55, idade_aos_55)
    else:
        # 5. Dedução do Tempo Excedente antes de 2032
        tempo_servico_total = (data_reserva_proposta - data_entrada).days / 365
        tempo_excedente = max(0, tempo_servico_total - 35)  # Tempo que excede 35 anos
        idade_minima_ajustada = 55 - tempo_excedente
        if idade_minima_ajustada < 55:
            data_reserva_proposta = data_nascimento + timedelta(days=int(idade_minima_ajustada * 365))

    # Diferenças em anos, meses e dias
    tempo1 = diferenca_data(data_reserva_original, data_entrada)
    tempo2 = diferenca_data(data_reserva_2019, data_entrada)
    tempo3 = diferenca_data(data_reserva_proposta, data_entrada)

    return (data_reserva_original, data_reserva_2019, data_reserva_proposta, tempo1, tempo2, tempo3)

# Interface Streamlit
st.write("## Calculadora de Tempo para Reserva Militar (PL de 2024)")
st.write("*Solução gerada por LLM com nenhuma garantia que esteja certa, considere apenas para se ter uma ideia")

# Entrada de dados
data_nascimento = st.date_input("Data de Nascimento", value=datetime(1980, 1, 1).date())
data_entrada = st.date_input("Data de Entrada nas Forças Armadas", value=datetime(1999, 2, 22).date())

st.write("### Desconto de Localidade Especial (em meses)")
desconto_pre2020 = st.number_input("Desconto antes de 2020 (meses)", min_value=0, value=0)
desconto_pos2020 = st.number_input("Desconto após 2020 (meses)", min_value=0, value=0)

if st.button("Calcular"):
    # Cálculo das datas de reserva
    data_original, data_2019, data_proposta, tempo1, tempo2, tempo3 = calcular_reserva(
        data_nascimento, data_entrada, desconto_pre2020, desconto_pos2020
    )

    # Resultados
    st.write("### Resultados com Base nas Regras:")
    st.write(f"**Regra Original (1960):** {data_original.strftime('%d/%m/%Y')} - {tempo1[0]} anos, {tempo1[1]} meses, {tempo1[2]} dias")
    st.write(f"**Mudança de 2019:** {data_2019.strftime('%d/%m/%Y')} - {tempo2[0]} anos, {tempo2[1]} meses, {tempo2[2]} dias")
    st.write(f"**Proposta Atual (2025):** {data_proposta.strftime('%d/%m/%Y')} - {tempo3[0]} anos, {tempo3[1]} meses, {tempo3[2]} dias")

    # Countdown para a Proposta Atual
    tempo_restante_proposta = diferenca_data(data_proposta, datetime.now())
    st.write("### Contagem Proposta Atual:")
    st.write(f"**Tempo Restante:** {tempo_restante_proposta[0]} anos, {tempo_restante_proposta[1]} meses, {tempo_restante_proposta[2]} dias")
