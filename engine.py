import json
import hashlib
from datetime import datetime, timezone
from typing import Optional

PALAVRAS_PROIBIDAS = [
    "concorrente", "política", "religião", "discriminação",
    "promessa irreal", "garantia", "milagre", "cura",
]

DIRETRIZES_AZUL = {
    "tom_voz": [
        "acolhedor", "simples", "positivo", "transparente",
        "humano", "próximo", "descomplicado",
    ],
    "valores": [
        "segurança", "inovação", "eficiência", "respeito",
        "sustentabilidade", "diversidade",
    ],
    "vieses_proibidos": [
        "promessa excessiva", "tom agressivo", "desrespeito",
        "desinformação", "exclusão",
    ],
}

CATEGORIAS_ALINHAMENTO = {
    "marca": {"peso": 30, "rótulo": "Identidade de Marca"},
    "tom_voz": {"peso": 20, "rótulo": "Tom de Voz"},
    "publico": {"peso": 15, "rótulo": "Aderência ao Público"},
    "canais": {"peso": 10, "rótulo": "Adequação aos Canais"},
    "objetivos": {"peso": 15, "rótulo": "Clareza dos Objetivos"},
    "risco": {"peso": 10, "rótulo": "Análise de Risco"},
}


def _calcular_score_marca(descricao: str, objetivos: str) -> tuple[int, list[str], list[str]]:
    fortes = []
    riscos = []
    score = 70

    if "azul" in descricao.lower() or "azul" in objetivos.lower():
        fortes.append("Menção explícita à marca Azul")
        score += 10
    else:
        riscos.append("A marca Azul não foi mencionada — verifique identidade visual e naming")
        score -= 15

    if any(p in descricao.lower() for p in DIRETRIZES_AZUL["valores"]):
        fortes.append("Valores da Azul refletidos na proposta")
        score += 10
    else:
        riscos.append("Nenhum valor institucional da Azul foi identificado")

    if any(p in descricao.lower() for p in PALAVRAS_PROIBIDAS):
        riscos.append("Conteúdo com palavras ou temas restritos identificados")
        score -= 25

    score = max(0, min(100, score))
    return score, fortes, riscos


def _calcular_score_tom_voz(descricao: str) -> tuple[int, list[str], list[str]]:
    fortes = []
    riscos = []
    score = 70

    palavras_tom = sum(1 for p in DIRETRIZES_AZUL["tom_voz"] if p in descricao.lower())
    if palavras_tom >= 2:
        fortes.append("Tom de voz alinhado com as diretrizes da Azul")
        score += 15
        score += palavras_tom * 2
    elif palavras_tom == 1:
        fortes.append("Tom de voz parcialmente alinhado")
        score += 5
    else:
        riscos.append("Tom de voz não reflete as diretrizes da Azul (acolhedor, simples, positivo)")
        score -= 15

    for bias in DIRETRIZES_AZUL["vieses_proibidos"]:
        if bias in descricao.lower():
            riscos.append(f"Viés identificado: '{bias}' — revise a abordagem")
            score -= 10

    score = max(0, min(100, score))
    return score, fortes, riscos


def _calcular_score_publico(publico_alvo: str, descricao: str) -> tuple[int, list[str], list[str]]:
    fortes = []
    riscos = []
    score = 70

    if "todos" in publico_alvo.lower() or "geral" in publico_alvo.lower():
        riscos.append("Público muito genérico — segmente melhor para maior efetividade")
        score -= 15
    elif len(publico_alvo.strip()) > 10:
        fortes.append("Público-alvo bem definido")
        score += 15
    else:
        riscos.append("Público-alvo muito restrito ou indefinido")
        score -= 10

    score = max(0, min(100, score))
    return score, fortes, riscos


def _calcular_score_canais(canais: str) -> tuple[int, list[str], list[str]]:
    fortes = []
    riscos = []
    canais_validos = ["instagram", "facebook", "linkedin", "site", "e-mail",
                      "whatsapp", "youtube", "tiktok", "tv", "rádio", "app",
                      "sms", "outdoor", "mídia"]
    score = 70

    canais_informados = [c.strip().lower() for c in canais.replace(";", ",").split(",")]
    canais_reconhecidos = [c for c in canais_informados if any(v in c for v in canais_validos)]

    if len(canais_reconhecidos) >= 2:
        fortes.append("Canais adequados e diversificados")
        score += 15
    elif len(canais_reconhecidos) == 1:
        fortes.append("Canal definido, mas considere expandir para outros canais")
        score += 5
    else:
        riscos.append("Canais não reconhecidos ou não informados")
        score -= 15

    score = max(0, min(100, score))
    return score, fortes, riscos


def _calcular_score_objetivos(objetivos: str) -> tuple[int, list[str], list[str]]:
    fortes = []
    riscos = []
    score = 70

    palavras_objetivo = ["aumentar", "reduzir", "melhorar", "engajar",
                         "converter", "vender", "comunicar", "lançar",
                         "fortalecer", "informar"]
    verbos = [v for v in palavras_objetivo if v in objetivos.lower()]

    if len(verbos) >= 2:
        fortes.append("Objetivos claros e mensuráveis")
        score += 20
    elif len(verbos) == 1:
        fortes.append("Objetivo identificado, mas pode ser mais específico")
        score += 5
    else:
        riscos.append("Objetivos não estão claros — defina metas concretas")
        score -= 20

    if len(objetivos.strip()) < 20:
        riscos.append("Objetivos muito curtos — detalhe melhor o propósito")
        score -= 5

    score = max(0, min(100, score))
    return score, fortes, riscos


def _calcular_score_risco(descricao: str, objetivos: str, publico_alvo: str) -> tuple[int, list[str], list[str]]:
    fortes = []
    riscos = []
    score = 80
    texto = (descricao + " " + objetivos + " " + publico_alvo).lower()

    palavras_risco = [
        "melhor", "maior", "número um", "lider", "garantia",
        "promessa", "todos", "sempre", "nunca",
    ]
    encontradas = [p for p in palavras_risco if p in texto]
    if encontradas:
        riscos.append(f"Palavras que podem gerar expectativa exagerada: {', '.join(encontradas)}")
        score -= 15

    if "concorrente" in texto or "concorrência" in texto:
        riscos.append("Menção a concorrentes — evite comparação direta")
        score -= 10

    score = max(0, min(100, score))
    return score, fortes, riscos


def analisar_ideia(
    descricao: str,
    objetivos: str,
    publico_alvo: str,
    canais: str,
    materiais: Optional[str] = None,
    cronograma: Optional[str] = None,
    duvidas: Optional[str] = None,
) -> dict:
    resultados = {}

    for cat, config in CATEGORIAS_ALINHAMENTO.items():
        if cat == "marca":
            score, fts, rsc = _calcular_score_marca(descricao, objetivos)
        elif cat == "tom_voz":
            score, fts, rsc = _calcular_score_tom_voz(descricao)
        elif cat == "publico":
            score, fts, rsc = _calcular_score_publico(publico_alvo, descricao)
        elif cat == "canais":
            score, fts, rsc = _calcular_score_canais(canais)
        elif cat == "objetivos":
            score, fts, rsc = _calcular_score_objetivos(objetivos)
        elif cat == "risco":
            score, fts, rsc = _calcular_score_risco(descricao, objetivos, publico_alvo)
        else:
            continue

        resultados[cat] = {
            "score": score,
            "peso": config["peso"],
            "rótulo": config["rótulo"],
            "fortes": fts,
            "riscos": rsc,
        }

    score_ponderado = sum(
        r["score"] * r["peso"] / 100 for r in resultados.values()
    )
    score_final = round(max(0, min(100, score_ponderado)), 1)

    if score_final >= 80:
        nivel = "verde"
        parecer = "Alinhamento forte com os padrões da Azul. Recomenda-se prosseguir com os ajustes sugeridos."
    elif score_final >= 50:
        nivel = "amarelo"
        parecer = "Alinhamento parcial. Ajustes necessários antes de prosseguir."
    else:
        nivel = "vermelho"
        parecer = "Baixo alinhamento. Reavalie a proposta com o time de Marketing antes de prosseguir."

    todas_recomendacoes = []
    for cat, r in resultados.items():
        for risco in r["riscos"]:
            todas_recomendacoes.append(risco)
        if r["score"] < 60:
            todas_recomendacoes.append(
                f"Pontuação baixa em '{r['rótulo']}' — revise esta dimensão"
            )

    if score_final >= 80:
        if cronograma:
            proximos_passos = [
                "Submeter para validação final do time de Marketing",
                f"Executar conforme cronograma informado: {cronograma}",
                "Preparar materiais finais com revisão humana obrigatória",
                "Registrar no sistema de governança para auditoria",
            ]
        else:
            proximos_passos = [
                "Submeter para validação final do time de Marketing",
                "Definir cronograma de execução",
                "Preparar materiais finais com revisão humana obrigatória",
                "Registrar no sistema de governança para auditoria",
            ]
    elif score_final >= 50:
        proximos_passos = [
            "Agendar reunião com Marketing para alinhar ajustes necessários",
            "Revisar a proposta com base nas recomendações acima",
            "Reenviar para nova análise após ajustes",
        ]
    else:
        proximos_passos = [
            "Não prosseguir com a proposta no formato atual",
            "Agendar sessão de alinhamento estratégico com Marketing",
            "Construir nova proposta com suporte do time de governança",
        ]

    analise_id = hashlib.sha256(
        (descricao + objetivos + datetime.now(timezone.utc).isoformat()).encode()
    ).hexdigest()[:12]

    return {
        "id": analise_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "score_final": score_final,
        "nivel": nivel,
        "parecer": parecer,
        "categorias": resultados,
        "recomendacoes": todas_recomendacoes,
        "proximos_passos": proximos_passos,
        "inputs": {
            "descricao": descricao,
            "objetivos": objetivos,
            "publico_alvo": publico_alvo,
            "canais": canais,
            "materiais": materiais,
            "cronograma": cronograma,
            "duvidas": duvidas,
        },
    }
