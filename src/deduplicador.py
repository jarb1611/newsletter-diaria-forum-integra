"""
deduplicador.py
================
AGENTE 2 - FILTRO DE DUPLICATAS (100% gratuito, sem chamada de IA)

Decide se duas notícias falam do MESMO fato (mesma data, mesma localidade,
título muito parecido) usando só Python puro: difflib (biblioteca padrão,
já vem instalada) para comparar textos, e dicionários de estados/cidades
brasileiras para detectar localidade.

CONCEITO ENSINADO:
- Comparação de similaridade de texto (difflib.SequenceMatcher) é uma
  técnica clássica de NLP que não precisa de nenhum modelo de linguagem.
  Pra esse caso de uso -- "isso é a mesma notícia?" -- ela funciona bem
  e sai de graça. Guarde IA generativa pra tarefas que realmente exigem
  raciocínio, não para comparação de strings.
- Um refinamento importante: em domínios especializados (aqui, notícias
  policiais), certas palavras aparecem em QUASE TODA manchete ("polícia",
  "operação", "prende") e por isso não ajudam a distinguir se duas
  notícias são sobre o MESMO fato ou fatos diferentes -- elas só
  "diluem" a comparação. Remover essas palavras específicas do domínio
  (além das stopwords genéricas do português) aumenta muito a precisão
  da comparação, sem precisar de nenhum modelo de linguagem.
"""

import re
import unicodedata
from difflib import SequenceMatcher
from dateutil import parser as date_parser


def _remover_acentos(texto: str) -> str:
    """Remove acentos para tornar a comparação de palavras mais robusta
    a pequenas variações de escrita (ex: 'tráfico' e 'trafico')."""
    forma_normalizada = unicodedata.normalize("NFD", texto)
    return "".join(c for c in forma_normalizada if unicodedata.category(c) != "Mn")


# ---------------------------------------------------------------------
# LOCALIDADE: estados e principais cidades brasileiras
# ---------------------------------------------------------------------

ESTADOS_BRASILEIROS = {
    "acre": "AC", "alagoas": "AL", "amapa": "AP", "amazonas": "AM", "bahia": "BA",
    "ceara": "CE", "distrito federal": "DF", "espirito santo": "ES", "goias": "GO",
    "maranhao": "MA", "mato grosso do sul": "MS", "mato grosso": "MT",
    "minas gerais": "MG", "para": "PA", "paraiba": "PB", "parana": "PR",
    "pernambuco": "PE", "piaui": "PI", "rio de janeiro": "RJ",
    "rio grande do norte": "RN", "rio grande do sul": "RS", "rondonia": "RO",
    "roraima": "RR", "santa catarina": "SC", "sao paulo": "SP", "sergipe": "SE",
    "tocantins": "TO",
}

# Capitais e cidades grandes/frequentes em notícias policiais, mapeadas
# para o estado correspondente -- sem isso, "Niterói" ou "Curitiba" não
# eram reconhecidas como localidade, mesmo sendo tão específicas quanto
# o nome do estado.
CIDADES_BRASILEIRAS = {
    "niteroi": "RJ", "duque de caxias": "RJ", "nova iguacu": "RJ", "sao goncalo": "RJ",
    "curitiba": "PR", "londrina": "PR", "maringa": "PR", "morretes": "PR", "cascavel": "PR",
    "santa maria": "RS", "pelotas": "RS", "caxias do sul": "RS", "porto alegre": "RS",
    "campinas": "SP", "santos": "SP", "guarulhos": "SP", "sorocaba": "SP",
    "belem": "PA", "maraba": "PA", "santarem": "PA", "mae do rio": "PA",
    "salvador": "BA", "feira de santana": "BA", "vitoria da conquista": "BA",
    "fortaleza": "CE", "recife": "PE", "brasilia": "DF", "belo horizonte": "MG",
    "goiania": "GO", "manaus": "AM", "florianopolis": "SC", "joinville": "SC",
    "vitoria": "ES", "natal": "RN", "joao pessoa": "PB", "maceio": "AL",
    "aracaju": "SE", "teresina": "PI", "sao luis": "MA", "cuiaba": "MT",
    "campo grande": "MS", "porto velho": "RO", "boa vista": "RR", "macapa": "AP",
    "palmas": "TO", "rio branco": "AC",
}


def extrair_localidade(texto: str) -> str:
    """Tenta identificar o estado (por nome, sigla ou cidade mencionada)
    no texto. Retorna a sigla ou 'não identificada' se não encontrar."""
    texto_lower = _remover_acentos(texto.lower())

    for nome_estado, sigla in ESTADOS_BRASILEIROS.items():
        if nome_estado in texto_lower:
            return sigla

    for nome_cidade, sigla in CIDADES_BRASILEIRAS.items():
        if nome_cidade in texto_lower:
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


# Stopwords genéricas do português -- não carregam significado específico.
PALAVRAS_IGNORADAS = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "em", "no", "na",
    "nos", "nas", "e", "é", "um", "uma", "para", "por", "com", "que", "se",
    "sobre", "apos", "durante", "ao", "aos", "à", "às",
}

# Palavras genéricas ESPECÍFICAS DO DOMÍNIO (notícias policiais) -- aparecem
# em praticamente toda manchete deste tipo e por isso não ajudam a
# distinguir um fato do outro. Removê-las faz a comparação focar no que
# realmente diferencia uma notícia da outra (o assunto, o local, o objeto).
PALAVRAS_GENERICAS_DO_DOMINIO = {
    "policia", "policial", "policiais", "civil", "militar", "penal", "federal",
    "operacao", "operação", "acao", "ação", "contra", "alvo", "alvos",
    "prende", "presa", "preso", "presos", "prisao", "prende",
    "suspeito", "suspeitos", "investigado", "investigada", "indiciado",
    "flagrante", "delegacia", "mira", "miram", "fazem", "faz", "leva", "levar",
    "e", "durante", "apos", "nesta", "neste", "leia",
}

# Sinônimos e variações (singular/plural, formas diferentes da mesma
# palavra) normalizados para uma forma única -- sem isso, "presídios" e
# "prisões" (mesmo assunto, palavras diferentes) contam como não-relacionadas.
MAPA_SINONIMOS = {
    "drogas": "droga", "entorpecentes": "droga", "narcoticos": "droga",
    "trafico": "droga", "toxicos": "droga",
    "presidio": "presidio", "presidios": "presidio", "prisao": "presidio",
    "prisoes": "presidio", "cadeia": "presidio", "cadeias": "presidio",
    "penitenciaria": "presidio", "penitenciarias": "presidio",
    "celular": "celular", "celulares": "celular",
    "arma": "arma", "armas": "arma",
    "roubo": "roubo", "roubos": "roubo", "furto": "roubo", "furtos": "roubo",
    "corrupcao": "corrupcao",
}

# Quantas palavras significativas em comum, junto com localidade
# confirmada igual, já são suficientes para considerar duplicata --
# mesmo que a proporção geral (Jaccard) não atinja o limiar padrão.
MINIMO_PALAVRAS_COM_LOCAL_CONFIRMADO = 2


def _palavras_significativas(texto: str) -> set:
    """Extrai o conjunto de palavras 'que importam' de um título: remove
    acentos, stopwords genéricas do português E palavras genéricas do
    domínio policial, e normaliza sinônimos/variações para uma forma única."""
    texto_normalizado = _remover_acentos(texto.lower())
    brutas = re.findall(r"[a-z0-9]+", texto_normalizado)

    significativas = set()
    for palavra in brutas:
        if palavra in PALAVRAS_IGNORADAS or palavra in PALAVRAS_GENERICAS_DO_DOMINIO:
            continue
        if len(palavra) <= 2:
            continue
        significativas.add(MAPA_SINONIMOS.get(palavra, palavra))

    return significativas


def calcular_sobreposicao_palavras(titulo_a: str, titulo_b: str) -> tuple[float, int]:
    """
    Retorna (índice de Jaccard, número de palavras em comum) das palavras
    significativas de dois títulos. Complementa calcular_similaridade():
    pega casos em que duas fontes descrevem o MESMO fato com frases bem
    diferentes (ex: "prende suspeitos" vs. "deflagra ação"), desde que
    compartilhem palavras-chave centrais (local, "droga", "celular" etc.).
    """
    conjunto_a = _palavras_significativas(titulo_a)
    conjunto_b = _palavras_significativas(titulo_b)

    if not conjunto_a or not conjunto_b:
        return 0.0, 0

    intersecao = conjunto_a & conjunto_b
    uniao = conjunto_a | conjunto_b
    return len(intersecao) / len(uniao), len(intersecao)


def sao_a_mesma_noticia(
    noticia_a: dict,
    noticia_b: dict,
    limiar_similaridade: float = 0.62,
    tolerancia_dias: int = 2,
    limiar_sobreposicao: float = 0.4,
) -> bool:
    """
    Decide se duas notícias descrevem o mesmo fato, cruzando:
    1. Proximidade de datas
    2. Coincidência de localidade (quando identificável em ambas)
    3. Similaridade textual dos títulos (caractere a caractere)
    4. Sobreposição de palavras-chave significativas (após remover termos
       genéricos do domínio policial e normalizar sinônimos)
    5. Regra combinada: localidade confirmada igual + pelo menos
       MINIMO_PALAVRAS_COM_LOCAL_CONFIRMADO palavras-chave em comum
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

    localidade_confirmada = (
        localidade_a != "não identificada"
        and localidade_a == localidade_b
    )

    similaridade_caracteres = calcular_similaridade(noticia_a["titulo"], noticia_b["titulo"])
    sobreposicao_jaccard, palavras_em_comum = calcular_sobreposicao_palavras(
        noticia_a["titulo"], noticia_b["titulo"]
    )

    if similaridade_caracteres >= limiar_similaridade:
        return True

    if sobreposicao_jaccard >= limiar_sobreposicao:
        return True

    if localidade_confirmada and palavras_em_comum >= MINIMO_PALAVRAS_COM_LOCAL_CONFIRMADO:
        return True

    return False


def remover_duplicadas(
    lista_noticias: list,
    limiar_similaridade: float = 0.62,
    tolerancia_dias: int = 2,
) -> list:
    """
    Percorre a lista de notícias e devolve só as únicas -- quando encontra
    uma duplicata, mantém apenas a primeira ocorrência.
    """
    unicas = []

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
