import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import django
import sys
from collections import Counter
import json
from statistics import mean
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncMonth, Now

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juridico.settings')
django.setup()

from documentos.models import Relatorio, DadosExtraidos, AnaliseTexto

# --- Streamlit page config ---
st.set_page_config(
    page_title="Dashboard Jurimetria",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Estilo customizado para deixar clean ---
st.markdown("""
<style>
body, .block-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    padding: 1rem;
    background-color: #f9f9f9;
}
h1, h2, h3, h4 {
    color: #003366;
    font-weight: 700;
}
.stMetric > div {
    background: #ffffff;
    border-radius: 8px;
    padding: 1rem 1.5rem;
    box-shadow: 0 1px 4px rgb(0 0 0 / 0.1);
}
[data-testid="stDataFrame"] {
    background-color: white !important;
    border-radius: 6px !important;
    box-shadow: 0 2px 8px rgb(0 0 0 / 0.08);
    padding: 10px;
    font-size: 14px;
}
figure {
    background: white;
    border-radius: 8px;
    padding: 0.8rem;
    box-shadow: 0 2px 10px rgb(0 0 0 / 0.1);
}
[role="tablist"] button {
    font-weight: 600;
    color: #003366;
}
.sidebar .css-1d391kg { 
    background-color: #003366 !important; 
}
.sidebar .css-1d391kg * {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# --- Cabeçalho lateral personalizado ---
st.sidebar.markdown("<h2 style='color: #fff; margin-bottom: 1rem;'>Jurimetria</h2>", unsafe_allow_html=True)
menu_items = ["Dashboard", "Dados Upload", "Jurimetria", "Relatórios", "Configurações"]
for item in menu_items:
    st.sidebar.markdown(f"<div style='padding: 0.5rem 1rem; font-weight: 600; cursor: pointer;'>{item}</div>", unsafe_allow_html=True)

# --- Título principal ---
st.title("Dashboard Jurimetria")
st.markdown("Visão geral de performance jurídica e financeira")

# --- Sidebar filtros ---
st.sidebar.header("Filtros")
status_filter = st.sidebar.multiselect(
    "Selecione o status dos relatórios:",
    options=['pendente', 'baixado', 'processado', 'erro'],
    default=['processado']
)

# --- Estatísticas principais ---
st.header("Visão Geral")

total_processos = Relatorio.objects.filter(status__in=status_filter).count()
processos_concluidos = Relatorio.objects.filter(status='processado').count()

valores = []
for de in DadosExtraidos.objects.all():
    try:
        dados_json = json.loads(de.conteudo)
        valores_extraidos = dados_json.get('VALOR', [])
        for v in valores_extraidos:
            v_str = str(v).replace('R$', '').replace('.', '').replace(',', '.').strip()
            try:
                valores.append(float(v_str))
            except:
                continue
    except:
        continue
valor_medio_causa = mean(valores) if valores else 0

qs_tempo = Relatorio.objects.filter(status='processado', processado_em__isnull=False, criado_em__isnull=False)
tempo_medio = qs_tempo.annotate(
    duracao=ExpressionWrapper(F('processado_em') - F('criado_em'), output_field=DurationField())
).aggregate(media_tempo=Avg('duracao'))['media_tempo']
tempo_medio_dias = tempo_medio.total_seconds()/86400 if tempo_medio else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Processos", total_processos)
col2.metric("Processos Concluídos", processos_concluidos)
col3.metric("Valor Médio da Causa (R$)", f"R$ {valor_medio_causa:,.2f}")
col4.metric("Tempo Médio até Conclusão (dias)", f"{tempo_medio_dias:.1f}")

# --- Gráficos lado a lado ---
st.header("Análise Mensal")

# Processos por mês
processos_mes_qs = Relatorio.objects.filter(status__in=status_filter) \
    .annotate(mes=TruncMonth('criado_em')) \
    .values('mes') \
    .annotate(qtd=Count('id')) \
    .order_by('mes')

df_processos_mes = pd.DataFrame(processos_mes_qs)
fig1, ax1 = plt.subplots(figsize=(5, 2.5))
if not df_processos_mes.empty:
    sns.lineplot(data=df_processos_mes, x='mes', y='qtd', marker='o', ax=ax1, color='#003366')
ax1.set_xlabel("")
ax1.set_ylabel("Qtd")
ax1.set_title("Processos por Mês")
ax1.tick_params(axis='x', rotation=45)
ax1.grid(True, linestyle='--', alpha=0.5)

# Valores envolvidos por mês
valores_por_mes = {}
for de in DadosExtraidos.objects.select_related('relatorio').all():
    try:
        mes = de.relatorio.criado_em.strftime('%Y-%m') if de.relatorio and de.relatorio.criado_em else None
        dados_json = json.loads(de.conteudo)
        valores_extraidos = dados_json.get('VALOR', [])
        for v in valores_extraidos:
            v_str = str(v).replace('R$', '').replace('.', '').replace(',', '.').strip()
            try:
                val_float = float(v_str)
                if mes:
                    valores_por_mes[mes] = valores_por_mes.get(mes, 0) + val_float
            except:
                continue
    except:
        continue

df_valores_mes = pd.DataFrame(sorted(valores_por_mes.items()), columns=['mes', 'total_valores'])
fig2, ax2 = plt.subplots(figsize=(5, 2.5))
if not df_valores_mes.empty:
    sns.barplot(data=df_valores_mes, x='mes', y='total_valores', color='#0055a5', ax=ax2)
ax2.set_xlabel("")
ax2.set_ylabel("R$")
ax2.set_title("Valores Envolvidos por Mês")
ax2.tick_params(axis='x', rotation=45)
ax2.grid(True, axis='y', linestyle='--', alpha=0.5)

# Distribuição dos status dos relatórios
status_counts = Relatorio.objects.filter(status__in=status_filter) \
    .values('status') \
    .annotate(qtd=Count('id')) \
    .order_by('status')

df_status = pd.DataFrame(status_counts)
fig3, ax3 = plt.subplots(figsize=(5, 3))
if not df_status.empty:
    ax3.pie(df_status['qtd'], labels=df_status['status'], autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
    ax3.set_title("Distribuição dos Status dos Relatórios")

# Exibir os três gráficos lado a lado
col_g1, col_g2, col_g3 = st.columns(3)
col_g1.pyplot(fig1)
col_g2.pyplot(fig2)
col_g3.pyplot(fig3)

# Gráfico: Top 10 entidades mais citadas
entidades_dict = {}
for analise in AnaliseTexto.objects.all():
    try:
        entidades = json.loads(analise.entidades)
        for tipo, valores_ in entidades.items():
            if tipo not in ['NUMERO_PROCESSO', 'VALOR']:
                entidades_dict.setdefault(tipo, []).extend(valores_)
    except:
        continue

if entidades_dict:
    tipo_mais_comum = max(entidades_dict.items(), key=lambda x: len(x[1]))[0]
    counter_top = Counter(entidades_dict[tipo_mais_comum]).most_common(10)
    df_top_ent = pd.DataFrame(counter_top, columns=['Entidade', 'Ocorrências'])
    fig4, ax4 = plt.subplots(figsize=(6, 3))
    sns.barplot(data=df_top_ent, y='Entidade', x='Ocorrências', palette='Blues_d', ax=ax4)
    ax4.set_title(f"Top 10 Entidades mais citadas - {tipo_mais_comum}")
    st.pyplot(fig4)

# Gráfico: Histograma dos valores extraídos
valores_all = []
for analise in AnaliseTexto.objects.all():
    try:
        entidades = json.loads(analise.entidades)
        vals = entidades.get('VALOR', [])
        for v in vals:
            v_str = str(v).replace('R$', '').replace('.', '').replace(',', '.').strip()
            try:
                valores_all.append(float(v_str))
            except:
                continue
    except:
        continue

if valores_all:
    fig5, ax5 = plt.subplots(figsize=(6, 3))
    sns.histplot(valores_all, bins=30, kde=True, color='#0055a5', ax=ax5)
    ax5.set_title("Distribuição dos Valores Extraídos")
    ax5.set_xlabel("Valor (R$)")
    ax5.set_ylabel("Frequência")
    st.pyplot(fig5)

# Gráfico: Tempo médio até conclusão por mês
qs_tempo_mes = Relatorio.objects.filter(status='processado', processado_em__isnull=False, criado_em__isnull=False) \
    .annotate(mes=TruncMonth('criado_em')) \
    .annotate(duracao=ExpressionWrapper(F('processado_em') - F('criado_em'), output_field=DurationField())) \
    .values('mes') \
    .annotate(media_tempo=Avg('duracao')) \
    .order_by('mes')

df_tempo_mes = pd.DataFrame(qs_tempo_mes)
if not df_tempo_mes.empty:
    df_tempo_mes['media_tempo_dias'] = df_tempo_mes['media_tempo'].apply(lambda x: x.total_seconds()/86400 if x else 0)
    fig6, ax6 = plt.subplots(figsize=(6, 3))
    sns.lineplot(data=df_tempo_mes, x='mes', y='media_tempo_dias', marker='o', ax=ax6, color='#003366')
    ax6.set_title("Tempo Médio até Conclusão por Mês")
    ax6.set_xlabel("")
    ax6.set_ylabel("Dias")
    ax6.tick_params(axis='x', rotation=45)
    ax6.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig6)

# --- Tabs para dados tabulares ---
st.header("Detalhes dos Dados")

with st.expander("Mostrar Relatórios Recentes"):
    qs_recent = Relatorio.objects.filter(status__in=status_filter).order_by('-criado_em')[:20]
    df_recent = pd.DataFrame(list(qs_recent.values('id', 'status', 'criado_em', 'processado_em')))
    if not df_recent.empty:
        st.dataframe(df_recent)

with st.expander("Mostrar Análise de Texto (Entidades)"):
    rows = []
    for analise in AnaliseTexto.objects.all()[:20]:
        rows.append({
            'ID Relatório': analise.relatorio_id,
            'Entidades': analise.entidades
        })
    df_analise = pd.DataFrame(rows)
    if not df_analise.empty:
        st.dataframe(df_analise)

with st.expander("Mostrar Dados Extraídos"):
    rows = []
    for de in DadosExtraidos.objects.all()[:20]:
        rows.append({
            'ID Relatório': de.relatorio_id,
            'Conteúdo': de.conteudo
        })
    df_de = pd.DataFrame(rows)
    if not df_de.empty:
        st.dataframe(df_de)


# Executar com: streamlit run dashboard.py
