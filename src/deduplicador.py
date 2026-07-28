"""
deduplicador.py
================
AGENTE 2 - FILTRO DE DUPLICATAS (100% gratuito, sem chamada de IA)

Decide se duas notícias falam do MESMO fato (mesma data, mesma localidade,
título muito parecido) usando só Python puro: difflib (biblioteca padrão,
já vem instalada) para comparar textos, e um dicionário de estados
brasileiros para detectar localidade.

CONCEITO ENSINADO:
- Comparação de similaridade de texto (difflib.SequenceMatcher) é uma
  técnica clássica de NLP que não precisa de nenhum modelo de linguagem.
  Pra esse caso de uso -- "isso é a mesma notícia?" -- ela funciona bem
  e sai de graça. Guarde IA generativa pra tarefas que realmente exigem
  raciocínio, não para comparação de strings.
"""

import re
from difflib import SequenceMatcher
from dateutil import parser as date_parser

# Mapa de estados brasileiros (nome completo -> sigla) usado para detectar
# a localidade mencionada no título/resumo da notícia.
ESTADOS_BRASILEIROS = {
    "acre": "AC", "alagoas": "AL", "amapá": "AP", "amazonas": "AM", "bahia": "BA",
    "ceará": "CE", "distrito federal": "DF", "espírito santo": "ES", "goiás": "GO",
    "maranhão": "MA", "mato grosso do sul": "MS", "mato grosso": "MT",
    "minas gerais": "MG", "pará": "PA", "paraíba": "PB", "paraná": "PR",
    "pernambuco": "PE", "piauí": "PI", "rio de janeiro": "RJ",
    "rio grande do norte": "RN", "rio grande do sul": "RS", "rondônia": "RO",
    "roraima": "RR", "santa catarina": "SC", "são paulo": "SP", "sergipe": "SE",
    "tocantins": "TO",
}


def extrair_localidade(texto: str) -> str:
    """Tenta identificar o estado mencionado no texto. Retorna a sigla ou
    'não identificada' se não encontrar nenhuma menção."""
    texto_lower = texto.lower()
    for nome_estado, sigla in ESTADOS_BRASILEIROS.items():
        if nome_estado in texto_lower:
            return sigla

    correspondencia = re.search(r"\b([A-Z]{2})\b", texto)
    if correspondencia and correspondencia.group(1) in ESTADOS_BRASILEIROS.values():
        return correspondencia.group(1)

    return "não identificada"


def normalizar_data(data_bruta: str):
    """Converte a data (em qualquer formato comum de RSS) para um objeto
    date. Retorna None se não conseguir interpretar."""
    if not data_bruta:
        return None
    try:
        return date_parser.parse(data_bruta, fuzzy=True).date()
    except (ValueError, OverflowError):
        return None


def calcular_similaridade(titulo_a: str, titulo_b: str) -> float:
    """Retorna um valor de 0.0 a 1.0 indicando o quão parecidos são dois títulos
    caractere a caractere (bom para títulos quase idênticos)."""
    return SequenceMatcher(None, titulo_a.lower(), titulo_b.lower()).ratio()


# Palavras muito comuns que não ajudam a identificar se é o "mesmo fato"
PALAVRAS_IGNORADAS = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "em", "no", "na",
    "nos", "nas", "e", "é", "um", "uma", "para", "por", "com", "que", "se",
    "sobre", "após", "contra",
}


def calcular_sobreposicao_palavras(titulo_a: str, titulo_b: str) -> float:
    """
    Retorna a sobreposição (índice de Jaccard) das palavras significativas
    de dois títulos. Complementa calcular_similaridade(): pega casos em que
    duas fontes descrevem o MESMO fato com frases bem diferentes
    (ex: "prende suspeitos" vs. "deflagra ação"), desde que compartilhem
    palavras-chave centrais (nomes de local, "tráfico", "suspeitos" etc.).
    """
    def palavras_significativas(texto: str) -> set:
        brutas = re.findall(r"[a-zà-ú0-9]+", texto.lower())
        return {p for p in brutas if p not in PALAVRAS_IGNORADAS and len(p) > 2}

    conjunto_a = palavras_significativas(titulo_a)
    conjunto_b = palavras_significativas(titulo_b)

    if not conjunto_a or not conjunto_b:
        return 0.0

    intersecao = conjunto_a & conjunto_b
    uniao = conjunto_a | conjunto_b
    return len(intersecao) / len(uniao)


def sao_a_mesma_noticia(
    noticia_a: dict,
    noticia_b: dict,
    limiar_similaridade: float = 0.62,
    tolerancia_dias: int = 1,
) -> bool:
    """
    Decide se duas notícias descrevem o mesmo fato, cruzando:
    1. Proximidade de datas
    2. Coincidência de localidade (quando identificável em ambas)
    3. Similaridade textual dos títulos
    """

    data_a = normalizar_data(noticia_a.get("data_publicacao", ""))
    data_b = normalizar_data(noticia_b.get("data_publicacao", ""))
    if data_a and data_b and abs((data_a - data_b).days) > tolerancia_dias:
        return False

    localidade_a = extrair_localidade(noticia_a["titulo"])
    localidade_b = extrair_localidade(noticia_b["titulo"])
    if (
        localidade_a != "não identificada"
        and localidade_b != "não identificada"
        and localidade_a != localidade_b
    ):
        return False

    similaridade_caracteres = calcular_similaridade(noticia_a["titulo"], noticia_b["titulo"])
    sobreposicao_palavras = calcular_sobreposicao_palavras(noticia_a["titulo"], noticia_b["titulo"])

    # Consideramos duplicata se QUALQUER uma das duas heurísticas indicar
    # forte parecença -- isso cobre tanto títulos quase idênticos quanto
    # títulos reescritos de forma diferente sobre o mesmo fato.
    return (
        similaridade_caracteres >= limiar_similaridade
        or sobreposicao_palavras >= 0.4
    )


def remover_duplicadas(
    lista_noticias: list[dict],
    limiar_similaridade: float = 0.62,
    tolerancia_dias: int = 1,
) -> list[dict]:
    """
    Percorre a lista de notícias e devolve só as únicas -- quando encontra
    uma duplicata, mantém apenas a primeira ocorrência.
    """
    unicas: list[dict] = []

    for noticia in lista_noticias:
        eh_duplicada = any(
            sao_a_mesma_noticia(noticia, existente, limiar_similaridade, tolerancia_dias)
            for existente in unicas
        )
        if not eh_duplicada:
            unicas.append(noticia)

    return unicas


if __name__ == "__main__":
    exemplo = [
        {"titulo": "Polícia Civil prende suspeitos de tráfico em Salvador, Bahia",
         "data_publicacao": "Mon, 20 Jul 2026 10:00:00 GMT"},
        {"titulo": "PC-BA deflagra operação contra tráfico de drogas em Salvador",
         "data_publicacao": "Mon, 20 Jul 2026 14:00:00 GMT"},
        {"titulo": "Operação prende quadrilha em Curitiba, Paraná",
         "data_publicacao": "Tue, 21 Jul 2026 09:00:00 GMT"},
    ]
    resultado = remover_duplicadas(exemplo)
    print(f"Entrada: {len(exemplo)} | Saída (únicas): {len(resultado)}")
    for n in resultado:
        print("-", n["titulo"])
