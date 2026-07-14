import streamlit as st
import pandas as pd
from datetime import datetime, timezone

from engine import analisar_ideia

st.set_page_config(
    page_title="Alinhamento Azul — Validador de Ideias",
    page_icon="🔵",
    layout="centered",
    initial_sidebar_state="expanded",
)

if "historico" not in st.session_state:
    st.session_state.historico = []

st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/pt/thumb/f/ff/Azul_Linhas_A%C3%A9reas_logo.svg/256px-Azul_Linhas_A%C3%A9reas_logo.svg.png",
    width=150,
)
st.sidebar.title("🔵 Alinhamento Azul")
st.sidebar.markdown("---")
pagina = st.sidebar.radio("Navegação", ["Nova Análise", "Histórico", "Sobre"])

if pagina == "Nova Análise":
    st.title("📋 Validação de Alinhamento com Padrões Azul")
    st.markdown(
        "Preencha os campos abaixo para receber uma análise de alinhamento "
        "da sua ideia com as diretrizes de marca, tom de voz e comunicação da Azul."
    )

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

        st.markdown("---")
        st.subheader("📊 Resultado da Análise")

        col_score, col_id = st.columns([2, 1])
        with col_score:
            score = resultado["score_final"]
            nivel = resultado["nivel"]
            if nivel == "verde":
                cor = "#28a745"
                emoji = "🟢"
            elif nivel == "amarelo":
                cor = "#ffc107"
                emoji = "🟡"
            else:
                cor = "#dc3545"
                emoji = "🔴"

            st.markdown(
                f"<h1 style='color: {cor};'>{emoji} {score:.0f}/100</h1>",
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

elif pagina == "Histórico":
    st.title("📜 Histórico de Análises")

    if not st.session_state.historico:
        st.info("Nenhuma análise realizada nesta sessão.")
    else:
        dados_hist = []
        for h in reversed(st.session_state.historico):
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
        st.subheader("📈 Resumo da Sessão")
        scores = [h["score_final"] for h in st.session_state.historico]
        col_m, col_mm = st.columns(2)
        col_m.metric("Média Geral", f"{sum(scores)/len(scores):.0f}/100")
        col_mm.metric("Total de Análises", len(scores))

        if st.button("🗑️ Limpar Histórico", type="secondary"):
            st.session_state.historico = []
            st.rerun()

elif pagina == "Sobre":
    st.title("🔵 Sobre o Alinhamento Azul")
    st.markdown(
        """
        **Alinhamento Azul** é uma ferramenta de governança que ajuda
        gestores, líderes e colaboradores das verticais a validar ideias
        e projetos contra os padrões de marca, tom de voz e comunicação da Azul.

        ### Como funciona
        1. Você preenche os detalhes da sua ideia
        2. O sistema analisa o alinhamento com as diretrizes da Azul
        3. Você recebe um score (0–100) + parecer + recomendações

        ### O que a ferramenta NÃO faz
        - ❌ Aprovar projetos definitivamente (parecer consultivo)
        - ❌ Gerar conteúdo final sem revisão humana
        - ❌ Falar em nome da Azul como porta-voz oficial
        - ❌ Tratar temas proibidos (política, religião, discriminação)

        ### Privacidade
        - Todas as análises são registradas com ID único para auditoria
        - Os dados são armazenados apenas durante a sessão
        """
    )

st.sidebar.markdown("---")
st.sidebar.caption("🔵 Alinhamento Azul v1.0 • Ferramenta de Governança")
