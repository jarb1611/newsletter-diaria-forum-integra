"""
organizador.py
===============
AGENTE 3 - ORGANIZADOR (100% gratuito)

Agrupa a lista de notícias (já sem duplicatas) nas categorias definidas
em config.py, na mesma ordem em que aparecem lá -- para virar as seções
da mensagem final (ex: "=== OPERAÇÕES POLICIAIS ===").
"""


def organizar_por_categoria(noticias: list[dict], categorias_config: dict) -> dict:
    """
    Args:
        noticias: lista de notícias únicas, cada uma já com a chave
                  "categoria" preenchida pelo buscador.py
        categorias_config: o dicionário config.CATEGORIAS_DE_BUSCA
                            (usado aqui só para definir a ORDEM das seções)

    Returns:
        Dicionário {nome_categoria: [notícias...]}, na ordem de config.py,
        e sem categorias vazias.
    """
    organizado = {nome_categoria: [] for nome_categoria in categorias_config}

    for noticia in noticias:
        categoria = noticia.get("categoria", "OUTROS")
        organizado.setdefault(categoria, [])
        organizado[categoria].append(noticia)

    # Remove categorias que ficaram vazias (sem notícias suficientes/relevantes)
    return {nome: lista for nome, lista in organizado.items() if lista}


def garantir_minimo_de_noticias(noticias_unicas: list[dict], minimo: int) -> list[dict]:
    """
    Verifica se há notícias suficientes. Se não houver, apenas registra um
    aviso -- a decisão de rodar uma nova busca com termos mais amplos fica
    a critério de quem chama esta função (main.py), para não disparar
    buscas extras silenciosamente.
    """
    if len(noticias_unicas) < minimo:
        print(
            f"[Organizador] Aviso: apenas {len(noticias_unicas)} notícia(s) única(s) "
            f"encontrada(s), abaixo do mínimo configurado ({minimo}). "
            f"Considere adicionar mais termos de busca em config.py."
        )
    return noticias_unicas
