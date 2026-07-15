from engine import (
    DIRETRIZES_AZUL,
    PALAVRAS_PROIBIDAS,
    CATEGORIAS_ALINHAMENTO,
)

NOME_BOT = "Lazuli"

CONHECIMENTO = [
    {
        "topicos": ["tom de voz", "tom", "voz", "linguagem", "estilo", "como escrever"],
        "resposta": (
            "O tom de voz recomendado da Azul é: acolhedor, simples, positivo, "
            "transparente, humano, próximo e descomplicado. Evite promessas "
            "excessivas, tom agressivo, desrespeito, desinformação e exclusão."
        ),
    },
    {
        "topicos": ["valor", "valores", "missão", "princípio", "cultura"],
        "resposta": (
            "Os valores institucionais da Azul são: segurança, inovação, "
            "eficiência, respeito, sustentabilidade e diversidade. Reflita "
            "esses valores na proposta para pontuar melhor na Identidade de Marca."
        ),
    },
    {
        "topicos": ["proibido", "proibida", "palavra", "banida", "restrito", "não posso", "vetado"],
        "resposta": (
            "Temas e palavras restritas incluem: concorrente, política, religião, "
            "discriminação, promessa irreal, garantia, milagre e cura. Palavras "
            "como 'melhor', 'maior', 'número um', 'líder', 'garantia', 'promessa', "
            "'todos', 'sempre' e 'nunca' geram expectativa exagerada e reduzem o score."
        ),
    },
    {
        "topicos": ["score", "pontuação", "nota", "cálculo", "peso", "como é medido"],
        "resposta": (
            "O score final (0–100) é ponderado por 6 categorias: "
            + ", ".join(f"{c['rótulo']} ({c['peso']}%)" for c in CATEGORIAS_ALINHAMENTO.values())
            + ". Cada categoria varia de 0 a 100 e contribui conforme seu peso."
        ),
    },
    {
        "topicos": ["melhorar", "aumentar", "subir", "aprimorar", "ajustar", "recomendação"],
        "resposta": (
            "Para melhorar o alinhamento: cite a marca Azul, reflita valores "
            "institucionais, use tom de voz acolhedor e simples, defina um "
            "público-alvo segmentado, estabeleça objetivos mensuráveis com verbos "
            "de ação e evite palavras de risco ou comparação com concorrentes."
        ),
    },
    {
        "topicos": ["concorrente", "concorrência", "comparar", "comparação"],
        "resposta": (
            "Comparação direta com concorrentes é desaconselhada e penalizada no "
            "score de risco. Foque na proposta de valor da Azul sem citar terceiros."
        ),
    },
    {
        "topicos": ["aprovar", "aprovação", "definitivo", "oficial", "final"],
        "resposta": (
            "Esta ferramenta emite apenas parecer consultivo. A aprovação final "
            "deve ser feita por um humano do time de Marketing ou Compliance da Azul."
        ),
    },
    {
        "topicos": ["categoria", "dimensão", "identidade", "objetivo", "canal", "público", "risco"],
        "resposta": (
            "As categorias avaliadas são: Identidade de Marca (30%), Tom de Voz "
            "(20%), Aderência ao Público (15%), Clareza dos Objetivos (15%), "
            "Adequação aos Canais (10%) e Análise de Risco (10%)."
        ),
    },
    {
        "topicos": ["dúvida", "ajuda", "como funciona", "o que você faz", "quem é você"],
        "resposta": (
            "Sou o Lazuli, assistente de governança da Azul. Tirei dúvidas sobre "
            "tom de voz, valores, regras de compliance, como o score é calculado "
            "e como melhorar o alinhamento da sua ideia com a marca."
        ),
    },
]


def responder_chatbot(pergunta: str, contexto: dict | None = None) -> str:
    texto = (pergunta or "").lower().strip()

    if not texto:
        return "Olá! Sou o Lazuli. Pergunte algo sobre tom de voz, valores, compliance ou como melhorar o alinhamento da sua ideia."

    if any(p in texto for p in ["olá", "oi", "oie", "bom dia", "boa tarde", "boa noite", "e aí", "salve"]):
        saudacao = "Olá! Sou o Lazuli, seu assistente de alinhamento com a Azul. "
        if contexto:
            saudacao += (
                f"Sua última análise teve score {contexto['score_final']:.0f}/100 "
                f"({contexto['nivel'].upper()}). Como posso ajudar?"
            )
        else:
            saudacao += "Como posso ajudar com sua ideia?"
        return saudacao

    if contexto and any(p in texto for p in ["minha ideia", "meu score", "meu resultado", "análise", "por que", "baixo", "baixa", "vermelho", "amarelo"]):
        if contexto["nivel"] == "vermelho":
            return (
                f"Sua análise ficou com score {contexto['score_final']:.0f}/100 "
                f"(vermelho). Os principais pontos de atenção foram: "
                + "; ".join(contexto["recomendacoes"][:3])
                + ". Recomendo reavaliar a proposta com o time de Marketing."
            )
        elif contexto["nivel"] == "amarelo":
            return (
                f"Sua análise ficou com score {contexto['score_final']:.0f}/100 "
                f"(amarelo). Há ajustes necessários: "
                + "; ".join(contexto["recomendacoes"][:3])
                + ". Ajuste e reenvie para nova análise."
            )
        else:
            return (
                f"Sua análise ficou com score {contexto['score_final']:.0f}/100 "
                f"(verde) — bom alinhamento! Próximos passos: "
                + "; ".join(contexto["proximos_passos"][:2])
                + "."
            )

    for item in CONHECIMENTO:
        if any(t in texto for t in item["topicos"]):
            return item["resposta"]

    return (
        "Não tenho certeza sobre isso. Posso ajudar com: tom de voz da Azul, "
        "valores institucionais, palavras/temas proibidos, como o score é "
        "calculado, como melhorar o alinhamento e regras de aprovação. "
        "Reformule sua dúvida ou pergunte sobre um desses temas."
    )
