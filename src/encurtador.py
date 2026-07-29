"""
encurtador.py
==============
AGENTE (auxiliar) - ENCURTADOR DE LINKS (100% gratuito, sem chave de API)

Usa a API pública do TinyURL (gratuita, sem necessidade de cadastro ou
chave) para transformar links longos em links curtos, deixando a
mensagem final mais limpa.

⚠️ CONSIDERAÇÃO DE SEGURANÇA:
Links encurtados escondem o domínio de destino até o clique -- o que é
uma técnica comum usada em golpes de phishing. Para um público que
inclui agentes de inteligência e segurança pública (que precisam
inspecionar visualmente o domínio antes de clicar), isso pode ser
indesejável mesmo sendo um encurtador legítimo. Por isso, o encurtamento
é OPCIONAL e controlado por `config.ATIVAR_ENCURTADOR_DE_LINK` -- por
padrão, vem DESATIVADO, priorizando a transparência do link original.

CONCEITO ENSINADO:
- Nem toda "API" é paga. Serviços como TinyURL oferecem endpoints
  públicos que qualquer script pode chamar via HTTP simples, sem
  autenticação -- não é IA, não cobra por uso.
- Sempre trate falhas de rede com um "fallback": se o encurtador falhar
  por qualquer motivo (fora do ar, sem internet, timeout), o programa
  não deve quebrar -- ele deve continuar com o link original.
- Nem toda funcionalidade "legal de ter" é apropriada para todo público.
  Uma decisão de UX (link mais limpo) pode entrar em conflito com uma
  necessidade de segurança (verificar o domínio antes de clicar) -- e
  quando isso acontece, a opção mais segura deve ser o padrão.
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


def encurtar_links_das_noticias(noticias: list[dict], ativar_encurtador: bool = False) -> list[dict]:
    """
    Adiciona a chave "link_curto" a cada notícia da lista.

    Args:
        noticias: lista de notícias finais selecionadas
        ativar_encurtador: se True, encurta os links via TinyURL. Se False
            (padrão), mantém o link original -- recomendado quando o
            público precisa inspecionar o domínio antes de clicar, para
            reduzir risco de confusão com phishing.
    """
    for noticia in noticias:
        if ativar_encurtador:
            noticia["link_curto"] = encurtar_link(noticia["link"])
        else:
            noticia["link_curto"] = noticia["link"]
    return noticias


if __name__ == "__main__":
    exemplo = "https://www.exemplo.com.br/noticias/2026/07/28/uma-url-bem-longa-de-teste-para-encurtar"
    print("Original:", exemplo)
    print("Com encurtador ativado:", encurtar_link(exemplo))
    print("Com encurtador desativado (padrão recomendado):", exemplo)
