import streamlit as st
import pandas as pd
import json
from datetime import datetime, timezone
from pathlib import Path

from engine import analisar_ideia
from db import salvar_analise, listar_analises, limpar_analises
from chatbot import responder_chatbot

LOGO_PATH = Path(__file__).parent / "logo_lazuli.svg"

# ==================== CORES DA MARCA AZUL ====================
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
    layout="wide",                    # ← MELHORADO
    initial_sidebar_state="expanded",
)

# ==================== CSS APRIMORADO ====================
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
    
    .stApp {{ background-color: var(--branco); }}
    .main .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1280px; }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{ background-color: var(--azul-escuro) !important; }}
    section[data-testid="stSidebar"] * {{ color: var(--branco) !important; }}
    section[data-testid="stSidebar"] hr {{ border-color: var(--azul-medio) !important; }}
    
    /* Botões */
    .stButton > button[kind="primary"] {{
        background-color: var(--azul-medio) !important;
        border-color: var(--azul-medio) !important;
        color: var(--branco) !important;
        font-weight: 600;
    }}
    .stButton > button[kind="primary"]:hover {{ background-color: var(--azul-escuro) !important; }}
    
    .stButton > button[kind="secondary"] {{
        background-color: transparent !important;
        border-color: var(--azul-medio) !important;
        color: var(--azul-medio) !important;
        font-weight: 500;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{ background-color: var(--cinza-claro); border-radius: 10px; padding: 4px; }}
    .stTabs [aria-selected="true"] {{ background-color: var(--azul-medio) !important; color: white !important; }}
    
    /* Inputs */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {{
        border-color: var(--cinza-medio) !important;
        border-radius: 8px;
    }}
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {{
        border-color: var(--azul-medio) !important;
        box-shadow: 0 0 0 3px var(--azul-bg) !important;
    }}
    
    /* Score Circle */
    .score-circle {{
        width: 140px; height: 140px; border-radius: 50%;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        margin: 0 auto; font-weight: 700; color: white;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }}
    .score-circle.verde {{ background: linear-gradient(135deg, #28A745 0%, #1E7E34 100%); }}
    .score-circle.amarelo {{ background: linear-gradient(135deg, #FFC107 0%, #F57F17 100%); color: #333; }}
    .score-circle.vermelho {{ background: linear-gradient(135deg, #DC3545 0%, #C62828 100%); }}
    .score-circle .score-value {{ font-size: 2.8rem; line-height: 1; }}
    .score-circle .score-label {{ font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9; }}
    
    /* Category Cards - NOVO E MELHORADO */
    .category-card {{
        background: white;
        border: 1px solid var(--cinza-medio);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
    }}
    .category-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    }}
    .category-card.high {{ border-left: 5px solid var(--verde); }}
    .category-card.medium {{ border-left: 5px solid var(--amarelo); }}
    .category-card.low {{ border-left: 5px solid var(--vermelho); }}
    
    .category-card h4 {{ color: var(--azul-escuro); margin: 0; }}
    
    /* Header */
    .azul-header {{
        background: linear-gradient(135deg, var(--azul-escuro) 0%, var(--azul-medio) 100%);
        color: white; padding: 2.25rem 2rem; border-radius: 16px;
        margin-bottom: 2rem; text-align: center;
    }}
    .azul-header h1 {{ color: white !important; margin: 0; font-size: 2.1rem; font-weight: 700; }}
    .azul-header p {{ color: rgba(255,255,255,0.92) !important; margin-top: 0.6rem; font-size: 1.1rem; }}
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if "historico" not in st.session_state:
    st.session_state.historico = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "form_defaults" not in st.session_state:
    st.session_state.form_defaults = {}
if "ultima_analise" not in st.session_state:
    st.session_state.ultima_analise = None

# ==================== FUNÇÕES AUXILIARES ====================
def gerar_relatorio_md(r):
    linhas = [
        "# 📋 Relatório de Validação de Alinhamento — Lazuli",
        "",
        f"**ID da Análise:** `{r['id']}`",
        f"**Data/Hora:** {r['timestamp'][:19]} UTC",
        f"**Score Final:** {r['score_final']:.0f} / 100",
        f"**Nível:** {r['nivel'].upper()}",
        "",
        "## 📝 Parecer Geral",
        "",
        r['parecer'],
        "",
        "## 📊 Avaliação por Categoria",
        ""
    ]
    for cat, dados in r.get("categorias", {}).items():
        linhas.append(f"### {dados['rótulo']} — Score: {dados['score']}")
        if dados.get("fortes"):
            linhas.append("**✅ Pontos Fortes:**")
            for f in dados["fortes"]:
                linhas.append(f"- {f}")
        if dados.get("riscos"):
            linhas.append("**⚠️ Riscos Identificados:**")
            for ri in dados["riscos"]:
                linhas.append(f"- {ri}")
        linhas.append("")
    
    linhas.append("## ✅ Recomendações")
    for i, rec in enumerate(r.get("recomendacoes", []), 1):
        linhas.append(f"{i}. {rec}")
    linhas.append("")
    
    linhas.append("## 📌 Próximos Passos")
    for i, passo in enumerate(r.get("proximos_passos", []), 1):
        linhas.append(f"{i}. {passo}")
    
    linhas.extend([
        "",
        "---",
        "*Relatório gerado automaticamente pelo Lazuli v1.0 — Ferramenta de Governança de Marca da Azul.*",
        "",
        "*Este documento é confidencial e de uso interno.*"
    ])
    return "\n".join(linhas)


def exibir_analise(resultado):
    """Renderiza o resultado da análise de forma bonita e reutilizável"""
    st.markdown("---")
    st.subheader("📊 Resultado da Análise")
    
    col_score, col_id = st.columns([2.2, 1])
    with col_score:
        score = resultado["score_final"]
        nivel = resultado["nivel"]
        score_class = "verde" if nivel == "verde" else "amarelo" if nivel == "amarelo" else "vermelho"
        emoji = "🟢" if nivel == "verde" else "🟡" if nivel == "amarelo" else "🔴"
        
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
    
    # Parecer destacado
    cor_parecer = {"verde": "#28A745", "amarelo": "#F57F17", "vermelho": "#DC3545"}.get(nivel, "#003366")
    st.markdown(
        f"""
        <div style="background:#f8f9fa; border-left: 6px solid {cor_parecer}; 
                    padding: 1.1rem 1.4rem; border-radius: 10px; margin: 1.25rem 0 1.5rem 0;">
            <h3 style="margin:0; color:{cor_parecer};">{resultado['parecer']}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    tabs = st.tabs(["📋 Detalhamento por Categoria", "✅ Recomendações", "📌 Próximos Passos"])
    
    with tabs[0]:
        for cat, dados in resultado["categorias"].items():
            score = dados["score"]
            if score >= 70:
                nivel_class, score_color, score_emoji = "high", "#28A745", "✅"
            elif score >= 40:
                nivel_class, score_color, score_emoji = "medium", "#F57F17", "⚠️"
            else:
                nivel_class, score_color, score_emoji = "low", "#DC3545", "❌"
            
            fortes = dados.get("fortes", []) or []
            riscos = dados.get("riscos", []) or []
            
            fortes_html = "".join(f"<li>🟢 {f}</li>" for f in fortes) if fortes else "<li style='color:#888'>Nenhum destaque positivo</li>"
            riscos_html = "".join(f"<li>🔴 {r}</li>" for r in riscos) if riscos else "<li style='color:#888'>Nenhum risco identificado</li>"
            
            card_html = f"""
            <div class="category-card {nivel_class}">
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.7rem;">
                    <h4 style="margin:0; font-size:1.15rem;">{dados['rótulo']}</h4>
                    <div style="background:{score_color}; color:white; padding:0.3rem 1rem; border-radius:999px; 
                                font-weight:700; font-size:1rem; display:flex; align-items:center; gap:0.35rem;">
                        {score_emoji} {score}
                    </div>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:1.5rem;">
                    <div>
                        <div style="font-weight:700; color:#28A745; margin-bottom:0.3rem; font-size:0.92rem;">PONTOS FORTES</div>
                        <ul style="margin:0; padding-left:1.15rem; font-size:0.92rem; line-height:1.55;">{fortes_html}</ul>
                    </div>
                    <div>
                        <div style="font-weight:700; color:#DC3545; margin-bottom:0.3rem; font-size:0.92rem;">RISCOS / PONTOS DE ATENÇÃO</div>
                        <ul style="margin:0; padding-left:1.15rem; font-size:0.92rem; line-height:1.55;">{riscos_html}</ul>
                    </div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
        
        # Campos opcionais
        inputs = resultado.get("inputs", {})
        if inputs.get("materiais"):
            with st.expander("📎 Materiais informados"):
                st.write(inputs["materiais"])
        if inputs.get("cronograma"):
            with st.expander("📅 Cronograma informado"):
                st.write(inputs["cronograma"])
        if inputs.get("duvidas"):
            with st.expander("❓ Dúvidas específicas"):
                st.write(inputs["duvidas"])
    
    with tabs[1]:
        recs = resultado.get("recomendacoes", [])
        if recs:
            for i, rec in enumerate(recs, 1):
                st.markdown(f"**{i}.** {rec}")
        else:
            st.success("Nenhuma recomendação crítica — proposta bem alinhada!")
    
    with tabs[2]:
        for i, passo in enumerate(resultado.get("proximos_passos", []), 1):
            st.markdown(f"**{i}.** {passo}")
    
    # ==================== EXPORTAÇÃO ====================
    st.markdown("---")
    st.subheader("📥 Exportar Análise")
    col1, col2 = st.columns(2)
    
    with col1:
        json_str = json.dumps(resultado, ensure_ascii=False, indent=2, default=str)
        st.download_button(
            "📄 Baixar como JSON",
            data=json_str,
            file_name=f"lazuli_analise_{resultado['id']}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        md_content = gerar_relatorio_md(resultado)
        st.download_button(
            "📝 Baixar Relatório (Markdown)",
            data=md_content,
            file_name=f"relatorio_lazuli_{resultado['id']}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    st.info(
        "⚠️ **Importante**: Esta é uma análise consultiva. "
        "A aprovação final deve ser feita por um humano do time de Marketing ou Compliance da Azul."
    )


# ==================== SIDEBAR ====================
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=160)
    else:
        st.markdown(
            '<div style="text-align:center; padding:1rem 0;">'
            '<img src="https://upload.wikimedia.org/wikipedia/pt/thumb/f/ff/Azul_Linhas_A%C3%A9reas_logo.svg/256px-Azul_Linhas_A%C3%A9reas_logo.svg.png" width="160">'
            '</div>',
            unsafe_allow_html=True
        )
    
    st.markdown("<h2 style='color:white; text-align:center; margin:0.3rem 0 0.8rem 0;'>Lazuli</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#0055A4; margin:0.3rem 0;'>", unsafe_allow_html=True)
    
    pagina = st.radio(
        "Navegação",
        ["Nova Análise", "Histórico", "Sobre"],
        label_visibility="collapsed"
    )
    
    st.markdown("<hr style='border-color:#0055A4;'>", unsafe_allow_html=True)
    st.caption("🔵 Lazuli v1.1 • Ferramenta de Governança")

# ==================== PÁGINA: NOVA ANÁLISE ====================
if pagina == "Nova Análise":
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=220)
    
    st.markdown("""
    <div class="azul-header">
        <h1>📋 Validação de Alinhamento com Padrões Azul</h1>
        <p>Preencha os campos abaixo para receber uma análise completa de alinhamento da sua ideia com as diretrizes de marca, tom de voz e comunicação da Azul.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botão de exemplo
    col_btn, _ = st.columns([2, 5])
    with col_btn:
        if st.button("📋 Carregar Exemplo de Campanha", type="secondary", use_container_width=True):
            st.session_state.form_defaults = {
                "descricao": "Campanha de incentivo ao uso do App Azul durante a alta temporada de férias de julho, com foco em famílias que viajam com crianças.",
                "objetivos": "Aumentar downloads do aplicativo em 25% e engajamento de usuários em 40% durante o período da campanha.",
                "publico_alvo": "Famílias com crianças de 5 a 12 anos, residentes em capitais do Sudeste e Nordeste, que viajam pelo menos 2x por ano.",
                "canais": "Instagram Reels, WhatsApp Business, Notificações push no App, Site Azul, Parcerias com influenciadores de viagem familiar",
                "materiais": "Artes do kit de verão 2025, manual de marca atualizado, resultados de pesquisa de NPS Q1/2026",
                "cronograma": "Campanha de 15/06 a 31/07/2026, com reforço na primeira quinzena de julho",
                "duvidas": "Podemos destacar o 'melhor custo-benefício'? O tom está suficientemente acolhedor para famílias?"
            }
            st.rerun()
    
    with st.expander("📌 Instruções de uso", expanded=False):
        st.markdown("""
        - **Campos obrigatórios**: Descrição, Objetivos, Público-alvo e Canais
        - A análise é **consultiva** — a aprovação final é sempre humana
        - O resultado inclui score (0–100), parecer colorido, pontos fortes, riscos e recomendações
        - Um **ID de auditoria** é gerado para rastreabilidade
        """)
    
    with st.form("form_analise"):
        col1, col2 = st.columns(2)
        with col1:
            descricao = st.text_area(
                "Descrição da ideia/projeto *",
                height=130,
                value=st.session_state.form_defaults.get("descricao", ""),
                placeholder="Ex: Campanha sazonal de final de ano com foco em..."
            )
            objetivos = st.text_area(
                "Objetivos esperados *",
                height=110,
                value=st.session_state.form_defaults.get("objetivos", ""),
                placeholder="Ex: Aumentar reconhecimento de marca em 15%..."
            )
        with col2:
            publico_alvo = st.text_input(
                "Público-alvo *",
                value=st.session_state.form_defaults.get("publico_alvo", ""),
                placeholder="Ex: Jovens adultos 25–40 anos, viajantes frequentes"
            )
            canais = st.text_input(
                "Canais/plataformas *",
                value=st.session_state.form_defaults.get("canais", ""),
                placeholder="Ex: Instagram, E-mail, Site"
            )
        
        col3, col4 = st.columns(2)
        with col3:
            materiais = st.text_area(
                "Materiais já existentes (opcional)",
                height=90,
                value=st.session_state.form_defaults.get("materiais", ""),
                placeholder="Ex: Briefing criativo, artes anteriores..."
            )
        with col4:
            cronograma = st.text_input(
                "Cronograma ou prazo (opcional)",
                value=st.session_state.form_defaults.get("cronograma", ""),
                placeholder="Ex: Lançamento em dezembro/2026"
            )
        
        duvidas = st.text_area(
            "Dúvidas específicas (opcional)",
            height=90,
            value=st.session_state.form_defaults.get("duvidas", ""),
            placeholder="Ex: Gostaria de saber se o tom está adequado..."
        )
        
        submitted = st.form_submit_button("🔍 Analisar Alinhamento", type="primary", use_container_width=True)
    
    if submitted:
        if not all([descricao.strip(), objetivos.strip(), publico_alvo.strip(), canais.strip()]):
            st.error("Por favor, preencha todos os campos obrigatórios (*).")
            st.stop()
        
        with st.spinner("🔄 Analisando alinhamento com os padrões da Azul..."):
            resultado = analisar_ideia(
                descricao=descricao,
                objetivos=objetivos,
                publico_alvo=publico_alvo,
                canais=canais,
                materiais=materiais.strip() or None,
                cronograma=cronograma.strip() or None,
                duvidas=duvidas.strip() or None,
            )
        
        st.session_state.historico.append(resultado)
        salvar_analise(resultado)
        st.session_state.ultima_analise = resultado
        st.session_state.form_defaults = {}   # limpa o exemplo
        
        exibir_analise(resultado)
        
        # ==================== CHAT ====================
        st.markdown("---")
        col_title, col_clear = st.columns([4, 1.3])
        with col_title:
            st.subheader("💬 Tire suas dúvidas com o Lazuli")
        with col_clear:
            if st.button("🗑️ Limpar conversa", type="secondary", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
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

# ==================== PÁGINA: HISTÓRICO ====================
elif pagina == "Histórico":
    st.title("📜 Histórico de Análises")
    
    historico_db = listar_analises()
    
    if not historico_db:
        st.info("Nenhuma análise registrada ainda no banco de dados.")
    else:
        dados_hist = []
        for h in historico_db:
            dados_hist.append({
                "ID": h["id"],
                "Data": h["timestamp"][:19],
                "Score": f"{h['score_final']:.0f}/100",
                "Nível": h["nivel"].upper(),
                "Ideia": h["inputs"]["descricao"][:75] + ("..." if len(h["inputs"]["descricao"]) > 75 else ""),
            })
        
        df_hist = pd.DataFrame(dados_hist)
        st.dataframe(
            df_hist,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Score": st.column_config.TextColumn("Score", help="Pontuação de alinhamento"),
                "Nível": st.column_config.TextColumn("Nível", help="Verde / Amarelo / Vermelho"),
            },
        )
        
        # Resumo
        st.markdown("---")
        col_m, col_t = st.columns(2)
        scores = [h["score_final"] for h in historico_db]
        col_m.metric("Média Geral", f"{sum(scores)/len(scores):.0f}/100")
        col_t.metric("Total de Análises", len(scores))
        
        # Visualizar análise completa
        st.markdown("---")
        st.subheader("🔍 Visualizar Análise Completa")
        
        opcoes = {f"{h['id']}  |  Score: {h['score_final']:.0f}  |  {h['timestamp'][:16]}": h for h in historico_db}
        escolha = st.selectbox("Selecione uma análise para ver os detalhes:", list(opcoes.keys()))
        
        if escolha:
            analise = opcoes[escolha]
            with st.expander("📄 Detalhes completos da análise selecionada", expanded=True):
                exibir_analise(analise)
        
        if st.button("🗑️ Limpar todo o Histórico", type="secondary"):
            limpar_analises()
            st.session_state.historico = []
            st.session_state.chat_history = []
            st.rerun()

# ==================== PÁGINA: SOBRE ====================
elif pagina == "Sobre":
    st.title("🔵 Sobre o Lazuli")
    
    st.markdown("""
    **Lazuli** é uma ferramenta de governança que ajuda gestores e times a validar ideias e projetos 
    contra os padrões de marca, tom de voz e comunicação da Azul Linhas Aéreas.
    """)
    
    with st.expander("🏢 Valores da Azul", expanded=True):
        st.markdown("""
        - **Segurança** — compromisso com a segurança em todas as operações  
        - **Inovação** — busca por soluções criativas e modernas  
        - **Eficiência** — otimização de recursos e processos  
        - **Respeito** — tratamento digno a clientes, colaboradores e parceiros  
        - **Sustentabilidade** — responsabilidade ambiental e social  
        - **Diversidade** — valorização da pluralidade e inclusão
        """)
    
    with st.expander("🎯 Tom de Voz Recomendado", expanded=True):
        st.markdown("""
        O tom de voz da Azul deve ser: **Acolhedor**, **Simples**, **Positivo**, **Transparente**, 
        **Humano**, **Próximo** e **Descomplicado**.
        
        **Vieses proibidos:** promessa excessiva, tom agressivo, desrespeito, desinformação ou exclusão.
        """)
    
    with st.expander("📊 Categorias de Avaliação (Score 0–100)", expanded=False):
        st.markdown("""
        | Categoria              | Peso  | O que avalia                              |
        |------------------------|-------|-------------------------------------------|
        | Identidade de Marca    | 30%   | Menção à Azul + alinhamento com valores   |
        | Tom de Voz             | 20%   | Adequação ao tom de voz institucional     |
        | Aderência ao Público   | 15%   | Definição e adequação do público-alvo     |
        | Clareza dos Objetivos  | 15%   | Objetivos mensuráveis e concretos         |
        | Adequação aos Canais   | 10%   | Canais compatíveis com a estratégia       |
        | Análise de Risco       | 10%   | Palavras de risco, promessas, concorrência|
        """)
    
    with st.expander("❌ O que a ferramenta NÃO faz", expanded=False):
        st.markdown("""
        - Não aprova projetos definitivamente (é apenas consultiva)
        - Não gera conteúdo final sem revisão humana
        - Não fala em nome oficial da Azul
        - Não trata temas proibidos (política, religião, discriminação)
        - Não substitui o time de Marketing
        """)
    
    st.markdown("---")
    st.caption("Lazuli v1.1 • Ferramenta interna de Governança de Marca • Azul Linhas Aéreas")

# Rodapé da sidebar
st.sidebar.markdown("---")
st.sidebar.caption("🔵 Lazuli v1.1 • Ferramenta de Governança")
