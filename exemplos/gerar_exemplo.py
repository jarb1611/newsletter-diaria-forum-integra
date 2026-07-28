"""
gerar_exemplo.py
==================
Script auxiliar SÓ para gerar um exemplo de saída, usando dados fictícios
no lugar da busca real (que precisa de acesso à internet). Roda 100%
offline. Não faz parte do pipeline de produção -- é só para você ver o
resultado final antes de rodar com dados reais na sua máquina.
"""

import sys
sys.path.insert(0, "../src")

from deduplicador import remover_duplicadas
from organizador import organizar_por_categoria
from formatador_whatsapp import gerar_mensagem_completa

# Dados fictícios simulando o que o buscador.py traria do RSS real
noticias_simuladas = [
    {"titulo": "Polícia Civil prende 5 suspeitos de tráfico de drogas em Salvador",
     "link": "https://g1.globo.com/exemplo-1", "fonte": "G1",
     "data_publicacao": "Mon, 27 Jul 2026 08:00:00 GMT", "categoria": "OPERAÇÕES POLICIAIS"},
    {"titulo": "Operação da PM apreende armas e drogas em favela do Rio de Janeiro",
     "link": "https://oglobo.globo.com/exemplo-2", "fonte": "O Globo",
     "data_publicacao": "Mon, 27 Jul 2026 09:15:00 GMT", "categoria": "APREENSÕES"},
    {"titulo": "Suspeito de homicídio é preso pela Polícia Civil em Curitiba",
     "link": "https://gazetadopovo.com.br/exemplo-3", "fonte": "Gazeta do Povo",
     "data_publicacao": "Mon, 27 Jul 2026 10:30:00 GMT", "categoria": "CRIMES E INVESTIGAÇÕES"},
    {"titulo": "Polícia Militar reforça policiamento em bairros de São Paulo",
     "link": "https://uol.com.br/exemplo-4", "fonte": "UOL",
     "data_publicacao": "Mon, 27 Jul 2026 07:45:00 GMT", "categoria": "SEGURANÇA PÚBLICA - GERAL"},
    {"titulo": "Facção criminosa é alvo de operação em Fortaleza, Ceará",
     "link": "https://diariodonordeste.verdesmares.com.br/exemplo-5", "fonte": "Diário do Nordeste",
     "data_publicacao": "Mon, 27 Jul 2026 11:00:00 GMT", "categoria": "OPERAÇÕES POLICIAIS"},
    {"titulo": "PM apreende arsenal de armas em ação contra o tráfico no Recife",
     "link": "https://folhape.com.br/exemplo-6", "fonte": "Folha de Pernambuco",
     "data_publicacao": "Mon, 27 Jul 2026 12:20:00 GMT", "categoria": "APREENSÕES"},
    {"titulo": "Investigação da Polícia Civil identifica autor de homicídio em Belo Horizonte",
     "link": "https://otempo.com.br/exemplo-7", "fonte": "O Tempo",
     "data_publicacao": "Mon, 27 Jul 2026 13:10:00 GMT", "categoria": "CRIMES E INVESTIGAÇÕES"},
    {"titulo": "Governo do Amazonas anuncia reforço no efetivo da Polícia Militar",
     "link": "https://acritica.com/exemplo-8", "fonte": "A Crítica",
     "data_publicacao": "Mon, 27 Jul 2026 14:00:00 GMT", "categoria": "SEGURANÇA PÚBLICA - GERAL"},
    {"titulo": "Operação policial prende integrantes de quadrilha em Porto Alegre",
     "link": "https://gaucha.com.br/exemplo-9", "fonte": "Rádio Gaúcha",
     "data_publicacao": "Mon, 27 Jul 2026 15:30:00 GMT", "categoria": "OPERAÇÕES POLICIAIS"},
    {"titulo": "Polícia apreende drogas avaliadas em R$ 2 milhões em Brasília",
     "link": "https://correiobraziliense.com.br/exemplo-10", "fonte": "Correio Braziliense",
     "data_publicacao": "Mon, 27 Jul 2026 16:00:00 GMT", "categoria": "APREENSÕES"},
    {"titulo": "PCBA deflagra ação contra tráfico e prende suspeitos em Salvador",
     "link": "https://bahianoticias.com.br/exemplo-11-duplicata", "fonte": "Bahia Notícias",
     "data_publicacao": "Mon, 27 Jul 2026 08:45:00 GMT", "categoria": "OPERAÇÕES POLICIAIS"},
]

CATEGORIAS_ORDEM = {
    "OPERAÇÕES POLICIAIS": [],
    "CRIMES E INVESTIGAÇÕES": [],
    "APREENSÕES": [],
    "SEGURANÇA PÚBLICA - GERAL": [],
}

print(f"Notícias simuladas (entrada): {len(noticias_simuladas)}")

unicas = remover_duplicadas(noticias_simuladas)
print(f"Notícias após remover duplicatas: {len(unicas)}")

organizadas = organizar_por_categoria(unicas, CATEGORIAS_ORDEM)

mensagens = gerar_mensagem_completa(
    organizadas,
    nome_organizacao="FÓRUM INTEGRA",
    cidade="Brasília",
)

texto_final = "\n\n".join(mensagens)
print("\n" + texto_final)

with open("exemplo_mensagem.txt", "w", encoding="utf-8") as f:
    f.write(texto_final)

print("\n\n[Salvo em exemplo_mensagem.txt]")
