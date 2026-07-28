"""
config.py
==========
ESTE É O ARQUIVO QUE VOCÊ VAI EDITAR COM MAIS FREQUÊNCIA.

Aqui ficam as categorias (tópicos) e as palavras-chave de busca de cada uma.
Sempre que quiser refinar a pesquisa, adicione/remova termos dentro de
CATEGORIAS_DE_BUSCA -- não precisa mexer em nenhum outro arquivo do projeto.

Estrutura: cada categoria vira uma seção na mensagem final do WhatsApp,
igual ao seu modelo (ex: "=== OPERAÇÕES POLICIAIS ===").
"""

# Nome da organização que aparece no cabeçalho da mensagem final
NOME_ORGANIZACAO = "Newsletter Diária - Fórum Integra"

# Cidade usada no timestamp da mensagem (ex: "Brasília, 28 de julho de 2026, 07:53")
CIDADE_TIMESTAMP = "Brasília"

# ---------------------------------------------------------------------
# CATEGORIAS E PALAVRAS-CHAVE
# Adicione quantas categorias e termos quiser. Cada termo dentro de uma
# categoria é uma busca separada no Google Notícias.
# ---------------------------------------------------------------------
CATEGORIAS_DE_BUSCA = {
    "OPERAÇÕES POLICIAIS": [
        "operação policial prisão",
        "operação policial tráfico de drogas",
        "operação policial facção criminosa",
    ],
    "CRIMES E INVESTIGAÇÕES": [
        "polícia civil investigação homicídio",
        "polícia prende suspeito",
        "polícia investiga fraude",
    ],
    "APREENSÕES": [
        "polícia apreensão armas",
        "polícia apreensão drogas",
    ],
    "SEGURANÇA PÚBLICA - GERAL": [
        "segurança pública Brasil",
        "polícia militar ação",
        "polícia civil ação",
    ],
}

# ---------------------------------------------------------------------
# PARÂMETROS DO PIPELINE
# ---------------------------------------------------------------------

# Quantas notícias buscar por termo (antes de aplicar filtro de data/duplicatas)
MAX_RESULTADOS_POR_TERMO = 15

# Janela de tempo: só considera notícias publicadas dentro das últimas X horas.
# Ex: 24 = notícias do último dia. Notícias mais antigas são descartadas.
JANELA_HORAS_MAXIMA = 24

# Meta de notícias: a busca PARA assim que atingir esse número de notícias
# únicas e dentro da janela de tempo (não busca além do necessário).
META_TOTAL_NOTICIAS = 10

# Duas notícias são consideradas duplicatas se:
# - a similaridade dos títulos for >= este valor (0.0 a 1.0)
LIMIAR_SIMILARIDADE_TITULO = 0.62

# - E as datas de publicação estiverem a até X dias de distância
TOLERANCIA_DIAS_ENTRE_DUPLICATAS = 1

# Tamanho máximo (em caracteres) de cada "Parte" da mensagem, para não
# esbarrar no limite de mensagem do WhatsApp
TAMANHO_MAXIMO_POR_PARTE = 3500
