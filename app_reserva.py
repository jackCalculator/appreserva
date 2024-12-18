import streamlit as st
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # Para lidar com anos bissextos corretamente

# Função para calcular anos, meses e dias entre duas datas (considerando anos bissextos)
def diferenca_data(data_final, data_inicial):
    delta = relativedelta(data_final, data_inicial)
    return delta.years, delta.months, delta.days

# Função principal para calcular a reserva
def calcular_reserva(data_nascimento, data_entrada, desconto_pre2020, desconto_pos2020, interrupcao_pre2020, interrupcao_pos2020):
    # Converte datas para datetime.datetime
    data_entrada = datetime.combine(data_entrada, datetime.min.time())
    data_nascimento = datetime.combine(data_nascimento, datetime.min.time())
    
    # Datas fixas de referência
    data_regra_2019 = datetime(2020, 1, 1)
    data_regra_2025 = datetime(2025, 1, 1)
    data_limite_55 = datetime(2032, 1, 1)

    # Ajuste da data de entrada com interrupções (antes e depois de 2020)
    data_entrada_ajustada = data_entrada + timedelta(days=int((interrupcao_pre2020 + interrupcao_pos2020) * 30.4375))

    # 1. Regra Original (1960): 30 anos ajustados com desconto antes de 2020
    data_base_1960 = data_entrada_ajustada + relativedelta(years=30)
    desconto_anos_pre2020 = desconto_pre2020 / 12
    data_reserva_original = data_base_1960 - relativedelta(months=int(desconto_anos_pre2020 * 12))

    # 2. Regra de 2019: Aplica pedágio de 17% sobre o tempo faltante ajustado com desconto
    tempo_faltante_2019 = (data_reserva_original - data_regra_2019).days / 365
    tempo_faltante_2019_com_pedagio = tempo_faltante_2019 * 1.17
    data_reserva_2019 = data_regra_2019 + relativedelta(days=int(tempo_faltante_2019_com_pedagio * 365))

    # 3. Proposta Atual (2025): Aplica pedágio de 9% sobre o tempo faltante ajustado com novo desconto
    desconto_anos_pos2020 = desconto_pos2020 / 12
    data_reserva_2019_ajustada = data_reserva_2019 - relativedelta(months=int(desconto_anos_pos2020 * 12))
    tempo_faltante_2025 = (data_reserva_2019_ajustada - data_regra_2025).days / 365
    tempo_faltante_2025_com_pedagio = tempo_faltante_2025 * 1.09
    data_reserva_proposta = data_regra_2025 + relativedelta(days=int(tempo_faltante_2025_com_pedagio * 365))

    # Variável para armazenar a explicação
    explicacao_proposta = ""

    # Ajuste da lógica para refletir os critérios legais corretamente
    if data_reserva_proposta >= data_limite_55:  
        # A partir de 2032, idade mínima é obrigatoriamente 55 anos
        idade_aos_55 = data_nascimento + relativedelta(years=55)
        data_reserva_proposta = idade_aos_55
        explicacao_proposta = "A reserva foi ajustada para 55 anos, conforme regra obrigatória a partir de 01/01/2032."
    else:
        # Antes de 2032: Verifica dedução do tempo excedente e aplicação do pedágio
        tempo_servico_total = (data_reserva_proposta - data_entrada_ajustada).days / 365
        tempo_excedente = max(0, tempo_servico_total - 35)  # Tempo que excede 35 anos

        if tempo_excedente > 0:
            idade_minima_ajustada = 55 - tempo_excedente
            idade_minima_ajustada = max(idade_minima_ajustada, 50)  # Limita até 50 anos
            data_reserva_proposta = data_nascimento + relativedelta(years=int(idade_minima_ajustada))
            explicacao_proposta = f"A idade mínima foi ajustada para {idade_minima_ajustada:.0f} anos devido ao tempo excedente de serviço."
        else:
            # Aplica pedágio de 9% sobre o tempo faltante até 2031
            tempo_faltante_com_pedagio = tempo_faltante_2025 * 1.09
            data_reserva_proposta = data_regra_2025 + relativedelta(days=int(tempo_faltante_com_pedagio * 365))
            explicacao_proposta = "A reserva foi calculada com o pedágio de 9% sobre o tempo faltante, conforme regra válida até 2031."

    # Diferenças em anos, meses e dias
    tempo1 = diferenca_data(data_reserva_original, data_entrada_ajustada)
    tempo2 = diferenca_data(data_reserva_2019, data_entrada_ajustada)
    tempo3 = diferenca_data(data_reserva_proposta, data_entrada_ajustada)

    return (data_reserva_original, data_reserva_2019, data_reserva_proposta, tempo1, tempo2, tempo3, explicacao_proposta)

# Interface Streamlit
st.markdown("## Calculadora de Tempo para Reserva Militar FFAA ([PL 4920/2024](https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao=2480445))")

st.write("*Solução gerada por LLM com nenhuma garantia que esteja certa, considere apenas como referência inicial*")

# Entrada de dados
data_nascimento = st.date_input("Data de Nascimento", value=datetime(1980, 1, 1).date())
data_entrada = st.date_input("Data de Entrada nas Forças Armadas", value=datetime(1999, 2, 22).date())



# Checkbox para descontos de localidade especial
desconto_pre2020 = 0
desconto_pos2020 = 0
if st.checkbox("Houve desconto de Localidade Especial?"):
    st.write("### Desconto de Localidade Especial (em meses)")
    desconto_pre2020 = st.number_input("Desconto antes de 2020 (meses):", min_value=0, value=0)
    desconto_pos2020 = st.number_input("Desconto após 2020 (meses):", min_value=0, value=0)

# Checkbox para interrupção no serviço ativo
interrupcao_pre2020 = 0
interrupcao_pos2020 = 0
if st.checkbox("Houve interrupção no serviço ativo?"):
    st.write("### Interrupções no Serviço Ativo")
    interrupcao_pre2020 = st.number_input("Interrupção antes de 2020 (em meses):", min_value=0, value=0)
    interrupcao_pos2020 = st.number_input("Interrupção após 2020 (em meses):", min_value=0, value=0)

if st.button("Calcular"):
    # Cálculo das datas de reserva
    data_original, data_2019, data_proposta, tempo1, tempo2, tempo3, explicacao_proposta = calcular_reserva(
        data_nascimento, data_entrada, desconto_pre2020, desconto_pos2020, interrupcao_pre2020, interrupcao_pos2020
    )

    # Resultados
    st.write("### Resultados com Base nas Regras:")
    st.write(f"**Regra Original (1960):** {data_original.strftime('%d/%m/%Y')} - {tempo1[0]} anos, {tempo1[1]} meses, {tempo1[2]} dias")
    st.write(f"**Mudança de 2019:** {data_2019.strftime('%d/%m/%Y')} - {tempo2[0]} anos, {tempo2[1]} meses, {tempo2[2]} dias")
    st.write(f"**Proposta Atual (2025):** {data_proposta.strftime('%d/%m/%Y')} - {tempo3[0]} anos, {tempo3[1]} meses, {tempo3[2]} dias")
    
    # Explicação da Proposta Atual    
    st.write(f"*{explicacao_proposta}*")

    # Contagem Regressiva
    tempo_restante_proposta = diferenca_data(data_proposta, datetime.now())
    st.write("### Contagem Regressiva para a Proposta Atual:")
    st.write(f"**Tempo Restante:** {tempo_restante_proposta[0]} anos, {tempo_restante_proposta[1]} meses, {tempo_restante_proposta[2]} dias")
