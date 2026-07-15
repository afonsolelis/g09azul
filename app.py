import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path

from engine import analisar_ideia
from db import salvar_analise, listar_analises, limpar_analises
from chatbot import responder_chatbot

LOGO_PATH = Path(__file__).parent / "logo_lazuli.svg"

# Cores da marca Azul
AZUL_CORES = {
    "azul_escuro": "#003366",
    "azul_medio": "#0055A4",
    "azul_claro": "#0077CC",
    "azul_ceu": "#0099E5",
    "azul_claro_claro": "#E6F2FA",
    "branco": "#FFFFFF",
    "cinza_claro": "#F5F5F5",
    "cinza_medio": "#CCCCCC",
    "cinza_escuro": "#666666",
    "verde_sucesso": "#28A745",
    "amarelo_atencao": "#FFC107",
    "vermelho_erro": "#DC3545",
}

st.set_page_config(
    page_title="Lazuli — Validador de Alinhamento",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="expanded",
)

# CSS customizado com cores da Azul
st.markdown(f"""
<style>
    :root {{
        --azul-escuro: {AZUL_CORES['azul_escuro']};
        --azul-medio: {AZUL_CORES['azul_medio']};
        --azul-claro: {AZUL_CORES['azul_claro']};
        --azul-ceu: {AZUL_CORES['azul_ceu']};
        --azul-bg: {AZUL_CORES['azul_claro_claro']};
        --branco: {AZUL_CORES['branco']};
        --cinza-claro: {AZUL_CORES['cinza_claro']};
        --cinza-medio: {AZUL_CORES['cinza_medio']};
        --cinza-escuro: {AZUL_CORES['cinza_escuro']};
        --verde: {AZUL_CORES['verde_sucesso']};
        --amarelo: {AZUL_CORES['amarelo_atencao']};
        --vermelho: {AZUL_CORES['vermelho_erro']};
    }}
    
    .stApp {{
        background-color: var(--branco);
    }}
    
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {{
        background-color: var(--azul-escuro) !important;
    }}
    
    section[data-testid="stSidebar"] * {{
        color: var(--branco) !important;
    }}
    
    section[data-testid="stSidebar"] .stRadio label {{
        color: var(--branco) !important;
    }}
    
    section[data-testid="stSidebar"] .stMarkdown {{
        color: var(--branco) !important;
    }}
    
    section[data-testid="stSidebar"] hr {{
        border-color: var(--azul-medio) !important;
    }}
    
    section[data-testid="stSidebar"] .stCaption {{
        color: var(--cinza-medio) !important;
    }}
    
    /* Buttons */
    .stButton > button[kind="primary"] {{
        background-color: var(--azul-medio) !important;
        border-color: var(--azul-medio) !important;
        color: var(--branco) !important;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        background-color: var(--azul-escuro) !important;
        border-color: var(--azul-escuro) !important;
    }}
    
    .stButton > button[kind="secondary"] {{
        background-color: transparent !important;
        border-color: var(--azul-medio) !important;
        color: var(--azul-medio) !important;
    }}
    
    .stButton > button[kind="secondary"]:hover {{
        background-color: var(--azul-bg) !important;
        border-color: var(--azul-escuro) !important;
        color: var(--azul-escuro) !important;
    }}
    
    /* Form submit button */
    .stFormSubmitButton > button {{
        background-color: var(--azul-medio) !important;
        border-color: var(--azul-medio) !important;
        color: var(--branco) !important;
        width: 100% !important;
    }}
    
    .stFormSubmitButton > button:hover {{
        background-color: var(--azul-escuro) !important;
        border-color: var(--azul-escuro) !important;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: var(--cinza-claro);
        border-radius: 8px;
        padding: 4px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent !important;
        color: var(--cinza-escuro) !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: var(--azul-medio) !important;
        color: var(--branco) !important;
    }}
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        border-color: var(--cinza-medio) !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: var(--azul-medio) !important;
        box-shadow: 0 0 0 2px var(--azul-bg) !important;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: var(--azul-bg) !important;
        border-color: var(--azul-claro) !important;
        color: var(--azul-escuro) !important;
        font-weight: 600 !important;
    }}
    
    .streamlit-expanderContent {{
        border-color: var(--azul-claro) !important;
    }}
    
    /* Metric cards */
    .stMetric {{
        background-color: var(--azul-bg);
        border: 1px solid var(--azul-claro);
        border-radius: 8px;
        padding: 1rem;
    }}
    
    /* Dataframe */
    .stDataFrame {{
        border: 1px solid var(--cinza-medio);
        border-radius: 8px;
    }}
    
    /* Divider */
    hr {{
        border-color: var(--cinza-medio) !important;
    }}
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: var(--azul-escuro) !important;
    }}
    
    /* Info/Success/Warning/Error boxes */
    .stAlert {{
        border-radius: 8px !important;
    }}
    
    .stSuccess {{
        background-color: #E8F5E9 !important;
        border-color: var(--verde) !important;
        color: #1B5E20 !important;
    }}
    
    .stInfo {{
        background-color: var(--azul-bg) !important;
        border-color: var(--azul-claro) !important;
        color: var(--azul-escuro) !important;
    }}
    
    .stWarning {{
        background-color: #FFF8E1 !important;
        border-color: var(--amarelo) !important;
        color: #F57F17 !important;
    }}
    
    .stError {{
        background-color: #FDEDEC !important;
        border-color: var(--vermelho) !important;
        color: #C62828 !important;
    }}
    
    /* Code blocks */
    code {{
        background-color: var(--azul-bg) !important;
        color: var(--azul-escuro) !important;
        border-radius: 4px;
        padding: 2px 6px;
    }}
    
    /* Logo container */
    .azul-logo-container {{
        text-align: center;
        padding: 1rem 0;
    }}
    
    .azul-logo-container img {{
        max-width: 180px;
        height: auto;
    }}
    
    /* Custom header */
    .azul-header {{
        background: linear-gradient(135deg, var(--azul-escuro) 0%, var(--azul-medio) 100%);
        color: white;
        padding: 2rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }}
    
    .azul-header h1 {{
        color: white !important;
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
    }}
    
    .azul-header p {{
        color: rgba(255,255,255,0.9) !important;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }}
    
    /* Score display */
    .score-circle {{
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin: 0 auto;
        font-weight: 700;
        color: white;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }}
    
    .score-circle.verde {{
        background: linear-gradient(135deg, #28A745 0%, #1E7E34 100%);
    }}
    
    .score-circle.amarelo {{
        background: linear-gradient(135deg, #FFC107 0%, #F57F17 100%);
        color: #333;
    }}
    
    .score-circle.vermelho {{
        background: linear-gradient(135deg, #DC3545 0%, #C62828 100%);
    }}
    
    .score-circle .score-value {{
        font-size: 2.5rem;
        line-height: 1;
    }}
    
    .score-circle .score-label {{
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        opacity: 0.9;
    }}
    
    /* Category cards */
    .category-card {{
        background: var(--branco);
        border: 1px solid var(--cinza-medio);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }}
    
    .category-card.high {{
        border-left: 4px solid var(--verde);
    }}
    
    .category-card.medium {{
        border-left: 4px solid var(--amarelo);
    }}
    
    .category-card.low {{
        border-left: 4px solid var(--vermelho);
    }}
</style>
""", unsafe_allow_html=True)

if "historico" not in st.session_state:
    st.session_state.historico = []

# Sidebar com logo da Azul
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=160)
    else:
        st.markdown("""
        <div class="azul-logo-container">
            <img src="https://upload.wikimedia.org/wikipedia/pt/thumb/f/ff/Azul_Linhas_A%C3%A9reas_logo.svg/256px-Azul_Linhas_A%C3%A9reas_logo.svg.png" alt="Azul Linhas Aéreas">
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<h2 style='color: white; text-align: center; margin-bottom: 0.5rem;'>Lazuli</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #0055A4;'>", unsafe_allow_html=True)
    
    pagina = st.radio("Navegação", ["Nova Análise", "Histórico", "Sobre"], label_visibility="collapsed")
    
    st.markdown("<hr style='border-color: #0055A4;'>", unsafe_allow_html=True)
    st.caption("🔵 Lazuli v1.0 • Ferramenta de Governança")

if pagina == "Nova Análise":
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=240)

    st.markdown("""
    <div class="azul-header">
        <h1>📋 Validação de Alinhamento com Padrões Azul</h1>
        <p>Preencha os campos abaixo para receber uma análise de alinhamento da sua ideia com as diretrizes de marca, tom de voz e comunicação da Azul.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📌 Instruções", expanded=False):
        st.markdown(
            """
            - **Campos obrigatórios**: Descrição, Objetivos, Público-alvo, Canais
            - A análise é **consultiva** — a aprovação final é sempre humana
            - O resultado inclui score (0–100), parecer verde/amarelo/vermelho,
              pontos fortes, riscos e recomendações
            - Um ID de auditoria é gerado para cada análise
            """
        )

    with st.form("form_analise"):
        col1, col2 = st.columns(2)

        with col1:
            descricao = st.text_area(
                "Descrição da ideia/projeto *",
                height=120,
                placeholder="Ex: Campanha sazonal de final de ano com foco em...",
            )
            objetivos = st.text_area(
                "Objetivos esperados *",
                height=100,
                placeholder="Ex: Aumentar reconhecimento de marca em 15% no público...",
            )

        with col2:
            publico_alvo = st.text_input(
                "Público-alvo *",
                placeholder="Ex: Jovens adultos 25–40 anos, viajantes frequentes",
            )
            canais = st.text_input(
                "Canais/plataformas *",
                placeholder="Ex: Instagram, E-mail, Site",
            )

        col3, col4 = st.columns(2)
        with col3:
            materiais = st.text_area(
                "Materiais já existentes (opcional)",
                height=80,
                placeholder="Ex: Briefing criativo, artes anteriores, pesquisa...",
            )
        with col4:
            cronograma = st.text_input(
                "Cronograma ou prazo (opcional)",
                placeholder="Ex: Lançamento em dezembro/2026",
            )

        duvidas = st.text_area(
            "Dúvidas específicas (opcional)",
            height=80,
            placeholder="Ex: Gostaria de saber se o tom está adequado para...",
        )

        submitted = st.form_submit_button("🔍 Analisar Alinhamento", type="primary", width="stretch")

    if submitted:
        if not descricao.strip():
            st.error("Descrição da ideia é obrigatória.")
            st.stop()
        if not objetivos.strip():
            st.error("Objetivos esperados são obrigatórios.")
            st.stop()
        if not publico_alvo.strip():
            st.error("Público-alvo é obrigatório.")
            st.stop()
        if not canais.strip():
            st.error("Canais/plataformas é obrigatório.")
            st.stop()

        with st.spinner("🔄 Analisando alinhamento com os padrões Azul..."):
            resultado = analisar_ideia(
                descricao=descricao,
                objetivos=objetivos,
                publico_alvo=publico_alvo,
                canais=canais,
                materiais=materiais if materiais.strip() else None,
                cronograma=cronograma if cronograma.strip() else None,
                duvidas=duvidas if duvidas.strip() else None,
            )

        st.session_state.historico.append(resultado)
        salvar_analise(resultado)
        st.session_state.ultima_analise = resultado

        st.markdown("---")
        st.subheader("📊 Resultado da Análise")

        col_score, col_id = st.columns([2, 1])
        with col_score:
            score = resultado["score_final"]
            nivel = resultado["nivel"]
            if nivel == "verde":
                score_class = "verde"
                emoji = "🟢"
            elif nivel == "amarelo":
                score_class = "amarelo"
                emoji = "🟡"
            else:
                score_class = "vermelho"
                emoji = "🔴"

            st.markdown(
                f"""
                <div class="score-circle {score_class}">
                    <span class="score-value">{emoji} {score:.0f}</span>
                    <span class="score-label">/ 100</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_id:
            st.markdown("**ID da Análise**")
            st.code(resultado["id"])
            st.caption(f"Gerado em {resultado['timestamp'][:19]} UTC")

        st.markdown(f"### {resultado['parecer']}")

        tabs = st.tabs(["📋 Detalhamento", "✅ Recomendações", "📌 Próximos Passos"])

        with tabs[0]:
            for cat, dados in resultado["categorias"].items():
                cols = st.columns([3, 1, 4])
                with cols[0]:
                    st.markdown(f"**{dados['rótulo']}**")
                with cols[1]:
                    if dados["score"] >= 70:
                        st.markdown(f"✅ **{dados['score']}**")
                    elif dados["score"] >= 40:
                        st.markdown(f"⚠️ **{dados['score']}**")
                    else:
                        st.markdown(f"❌ **{dados['score']}**")
                with cols[2]:
                    if dados["fortes"]:
                        for f in dados["fortes"]:
                            st.markdown(f"🟢 {f}")
                    if dados["riscos"]:
                        for r in dados["riscos"]:
                            st.markdown(f"🔴 {r}")
                    if not dados["fortes"] and not dados["riscos"]:
                        st.markdown("—")
                st.divider()

            if resultado["inputs"]["materiais"]:
                with st.expander("📎 Materiais informados"):
                    st.write(resultado["inputs"]["materiais"])
            if resultado["inputs"]["cronograma"]:
                with st.expander("📅 Cronograma informado"):
                    st.write(resultado["inputs"]["cronograma"])
            if resultado["inputs"]["duvidas"]:
                with st.expander("❓ Dúvidas específicas"):
                    st.write(resultado["inputs"]["duvidas"])

        with tabs[1]:
            if resultado["recomendacoes"]:
                for i, rec in enumerate(resultado["recomendacoes"], 1):
                    st.markdown(f"{i}. {rec}")
            else:
                st.success("Nenhuma recomendação crítica — proposta bem alinhada!")

        with tabs[2]:
            for i, passo in enumerate(resultado["proximos_passos"], 1):
                st.markdown(f"{i}. **{passo}**")

        st.markdown("---")
        st.info(
            "⚠️ **Importante**: Esta é uma análise consultiva. "
            "A aprovação final deve ser feita por um humano do time de Marketing "
            "ou Compliance da Azul."
        )

        st.markdown("---")
        st.subheader("💬 Tire suas dúvidas (Lazuli)")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        contexto_chat = st.session_state.get("ultima_analise")

        for role, msg in st.session_state.chat_history:
            with st.chat_message(role):
                st.markdown(msg)

        pergunta_usuario = st.chat_input("Pergunte algo sobre a análise ou os padrões da Azul...")
        if pergunta_usuario:
            st.session_state.chat_history.append(("user", pergunta_usuario))
            with st.chat_message("user"):
                st.markdown(pergunta_usuario)
            resposta = responder_chatbot(pergunta_usuario, contexto_chat)
            st.session_state.chat_history.append(("assistant", resposta))
            with st.chat_message("assistant"):
                st.markdown(resposta)

elif pagina == "Histórico":
    st.title("📜 Histórico de Análises")

    historico_db = listar_analises()

    if not historico_db:
        st.info("Nenhuma análise registrada no banco de dados (SQLite).")
    else:
        dados_hist = []
        for h in historico_db:
            dados_hist.append({
                "ID": h["id"],
                "Data": h["timestamp"][:19],
                "Score": f"{h['score_final']:.0f}/100",
                "Nível": h["nivel"].upper(),
                "Ideia": h["inputs"]["descricao"][:80] + ("..." if len(h["inputs"]["descricao"]) > 80 else ""),
            })

        df_hist = pd.DataFrame(dados_hist)

        st.dataframe(
            df_hist,
            width="stretch",
            hide_index=True,
            column_config={
                "Score": st.column_config.TextColumn("Score", help="Pontuação de alinhamento"),
                "Nível": st.column_config.TextColumn("Nível", help="Verde / Amarelo / Vermelho"),
            },
        )

        st.markdown("---")
        st.subheader("📈 Resumo")
        scores = [h["score_final"] for h in historico_db]
        col_m, col_mm = st.columns(2)
        col_m.metric("Média Geral", f"{sum(scores)/len(scores):.0f}/100")
        col_mm.metric("Total de Análises", len(scores))

        if st.button("🗑️ Limpar Histórico", type="secondary"):
            limpar_analises()
            st.session_state.historico = []
            st.session_state.chat_history = []
            st.rerun()

elif pagina == "Sobre":
    st.title("🔵 Sobre o Lazuli")
    st.markdown(
        """
        **Lazuli** é uma ferramenta de governança que ajuda
        gestores, líderes e colaboradores das verticais a validar ideias
        e projetos contra os padrões de marca, tom de voz e comunicação da Azul.

        ### Como funciona
        1. Você preenche os detalhes da sua ideia
        2. O sistema analisa o alinhamento com as diretrizes da Azul
        3. Você recebe um score (0–100) + parecer + recomendações

        ---
        """
    )

    with st.expander("🏢 Valores da Azul", expanded=True):
        st.markdown(
            """
            As análises verificam se a proposta reflete os valores institucionais da Azul:
            - **Segurança** — compromisso com a segurança em todas as operações
            - **Inovação** — busca por soluções criativas e modernas
            - **Eficiência** — otimização de recursos e processos
            - **Respeito** — tratamento digno a clientes, colaboradores e parceiros
            - **Sustentabilidade** — responsabilidade ambiental e social
            - **Diversidade** — valorização da pluralidade e inclusão
            """
        )

    with st.expander("🎯 Tom de Voz", expanded=True):
        st.markdown(
            """
            O tom de voz recomendado para comunicações da Azul deve ser:
            - **Acolhedor** — transmite conforto e pertencimento
            - **Simples** — linguagem clara e acessível
            - **Positivo** — foco em soluções e boas experiências
            - **Transparente** — honesto e direto
            - **Humano** — conecta com as emoções das pessoas
            - **Próximo** — cria intimidade sem ser invasivo
            - **Descomplicado** — remove barreiras e burocracia

            **Vieses proibidos:** promessa excessiva, tom agressivo, desrespeito,
            desinformação, exclusão.
            """
        )

    with st.expander("⚠️ Regras de Compliance e Risco", expanded=True):
        st.markdown(
            """
            A análise de risco verifica:

            **Palavras de risco** — termos que podem gerar expectativa exagerada
            ou comprometer a credibilidade da marca:
            `melhor`, `maior`, `número um`, `líder`, `garantia`, `promessa`,
            `todos`, `sempre`, `nunca`

            **Temas proibidos** — não podem ser utilizados em comunicações:
            `concorrente`, `política`, `religião`, `discriminação`,
            `promessa irreal`, `milagre`, `cura`

            **Comparação direta** com concorrentes é desaconselhada e penalizada no score.
            """
        )

    st.markdown("---")

    with st.expander("📊 Categorias de Avaliação", expanded=False):
        st.markdown(
            """
            O score final (0–100) é composto por 6 categorias com pesos distintos:

            | Categoria | Peso | O que avalia |
            |---|---|---|
            | Identidade de Marca | 30% | Menção à Azul e alinhamento com valores |
            | Tom de Voz | 20% | Adequação ao tom de voz institucional |
            | Aderência ao Público | 15% | Definição e adequação do público-alvo |
            | Clareza dos Objetivos | 15% | Objetivos mensuráveis e concretos |
            | Adequação aos Canais | 10% | Canais compatíveis com a estratégia |
            | Análise de Risco | 10% | Palavras de risco, promessas, concorrência |
            """
        )

    with st.expander("❌ O que a ferramenta NÃO faz", expanded=False):
        st.markdown(
            """
            - ❌ Aprovar projetos definitivamente (parecer consultivo)
            - ❌ Gerar conteúdo final sem revisão humana
            - ❌ Falar em nome da Azul como porta-voz oficial
            - ❌ Tratar temas proibidos (política, religião, discriminação)
            - ❌ Dar garantias jurídicas ou de performance de campanha
            - ❌ Substituir o time de Marketing (é um facilitador de governança)
            """
        )

    with st.expander("🔒 Privacidade e Auditoria", expanded=False):
        st.markdown(
            """
            - Todas as análises são registradas com ID único para auditoria
            - Os dados são armazenados apenas durante a sessão (não persistem)
            - Nenhum dado é enviado para terceiros
            """
        )

st.sidebar.markdown("---")
st.sidebar.caption("🔵 Lazuli v1.0 • Ferramenta de Governança")
 