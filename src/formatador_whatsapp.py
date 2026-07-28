"""
formatador_whatsapp.py
=======================
AGENTE 4 - FORMATADOR DE MENSAGEM (100% gratuito, sem chamada de IA)

Monta o texto final exatamente no formato do seu modelo:

    🖥 - *Newsletter Diária - Fórum Integra*
    *Brasília,* *28* *de* *julho* *de* *2026*
    *Parte 01*

     *===* *CATEGORIA* *===*
    =====================================
    *Título da notícia*
    https://link-da-materia
    --------------------------------------

Se a mensagem ficar grande demais para uma única mensagem de WhatsApp,
ela é dividida automaticamente em "Partes" (Parte 01, Parte 02, ...).

Esta etapa é 100% determinística -- não chama nenhuma API de IA.
"""

from datetime import datetime

MESES_EM_PORTUGUES = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho",
    7: "julho", 8: "agosto", 9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro",
}


def _montar_cabecalho(nome_organizacao: str, cidade: str, numero_parte: int, total_partes: int) -> str:
    agora = datetime.now()
    dia = agora.day
    mes = MESES_EM_PORTUGUES[agora.month]
    ano = agora.year

    linhas = [
        f"🖥 - *{nome_organizacao}*",
        f"*{cidade},* *{dia}* *de* *{mes}* *de* *{ano}*",
    ]
    if total_partes > 1:
        linhas.append(f"*Parte {numero_parte:02d}*")
    linhas.append("")  # linha em branco depois do cabeçalho

    return "\n".join(linhas)


def _montar_secao(nome_categoria: str, noticias: list[dict]) -> str:
    linhas = [
        f" *===* *{nome_categoria}* *===*",
        "=====================================",
    ]
    for noticia in noticias:
        linhas.append(f"*{noticia['titulo']}*")
        linhas.append(noticia.get("link_curto") or noticia["link"])
        linhas.append("--------------------------------------")
    linhas.append("")  # espaço entre seções

    return "\n".join(linhas)


def gerar_mensagem_completa(
    noticias_organizadas: dict,
    nome_organizacao: str,
    cidade: str,
    tamanho_maximo_por_parte: int = 3500,
) -> list[str]:
    """
    Gera o texto de todas as seções e divide em partes que respeitem o
    limite de caracteres, sem cortar uma notícia no meio.

    Args:
        noticias_organizadas: saída de organizador.organizar_por_categoria()
        nome_organizacao: ex. "FÓRUM INTEGRA"
        cidade: ex. "Brasília"
        tamanho_maximo_por_parte: limite de caracteres por mensagem

    Returns:
        Lista de strings -- cada item é o texto completo de uma "Parte",
        já pronta pra copiar e colar (ou enviar) no WhatsApp.
    """

    blocos_de_secao = [
        _montar_secao(categoria, noticias)
        for categoria, noticias in noticias_organizadas.items()
    ]

    # Agrupa os blocos de seção em partes, respeitando o tamanho máximo
    partes_de_conteudo: list[str] = []
    parte_atual = ""

    for bloco in blocos_de_secao:
        if parte_atual and len(parte_atual) + len(bloco) > tamanho_maximo_por_parte:
            partes_de_conteudo.append(parte_atual)
            parte_atual = bloco
        else:
            parte_atual += bloco

    if parte_atual:
        partes_de_conteudo.append(parte_atual)

    if not partes_de_conteudo:
        partes_de_conteudo = ["Nenhuma notícia relevante encontrada nesta busca."]

    total_partes = len(partes_de_conteudo)
    mensagens_finais = []
    for indice, conteudo in enumerate(partes_de_conteudo, start=1):
        cabecalho = _montar_cabecalho(nome_organizacao, cidade, indice, total_partes)
        mensagens_finais.append(f"{cabecalho}\n{conteudo}")

    return mensagens_finais


if __name__ == "__main__":
    exemplo = {
        "OPERAÇÕES POLICIAIS": [
            {"titulo": "Polícia prende 5 suspeitos de tráfico em Salvador",
             "link": "https://exemplo.com/noticia1"},
            {"titulo": "Operação apreende armas em Curitiba",
             "link": "https://exemplo.com/noticia2"},
        ],
    }
    for parte in gerar_mensagem_completa(exemplo, "FÓRUM INTEGRA", "Brasília"):
        print(parte)
        print("\n" + "#" * 50 + "\n")
