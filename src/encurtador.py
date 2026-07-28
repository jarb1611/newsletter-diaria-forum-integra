"""
encurtador.py
==============
AGENTE (auxiliar) - ENCURTADOR DE LINKS (100% gratuito, sem chave de API)

Usa a API pública do TinyURL (gratuita, sem necessidade de cadastro ou
chave) para transformar links longos em links curtos, deixando a
mensagem final mais limpa.

CONCEITO ENSINADO:
- Nem toda "API" é paga. Serviços como TinyURL oferecem endpoints
  públicos que qualquer script pode chamar via HTTP simples, sem
  autenticação -- não é IA, não cobra por uso.
- Sempre trate falhas de rede com um "fallback": se o encurtador falhar
  por qualquer motivo (fora do ar, sem internet, timeout), o programa
  não deve quebrar -- ele deve continuar com o link original.
"""

import requests

URL_API_TINYURL = "https://tinyurl.com/api-create.php"
TIMEOUT_SEGUNDOS = 5


def encurtar_link(url_original: str) -> str:
    """
    Encurta uma URL usando o TinyURL. Se a chamada falhar por qualquer
    motivo, devolve a URL original -- nunca quebra o pipeline por causa
    de um encurtador fora do ar.
    """
    if not url_original:
        return url_original

    try:
        resposta = requests.get(
            URL_API_TINYURL,
            params={"url": url_original},
            timeout=TIMEOUT_SEGUNDOS,
        )
        texto = resposta.text.strip()
        if resposta.status_code == 200 and texto.startswith("http"):
            return texto
    except requests.RequestException:
        pass

    return url_original


def encurtar_links_das_noticias(noticias: list[dict]) -> list[dict]:
    """
    Adiciona a chave "link_curto" a cada notícia da lista, encurtando o
    campo "link" original. Roda só sobre a lista final (já filtrada e
    limitada pela meta), para não desperdiçar chamadas encurtando links
    de notícias que nem vão entrar na mensagem final.
    """
    for noticia in noticias:
        noticia["link_curto"] = encurtar_link(noticia["link"])
    return noticias


if __name__ == "__main__":
    exemplo = "https://www.exemplo.com.br/noticias/2026/07/28/uma-url-bem-longa-de-teste-para-encurtar"
    print("Original:", exemplo)
    print("Encurtado:", encurtar_link(exemplo))
