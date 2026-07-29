"""
resolver_link.py
==================
AGENTE (auxiliar) - RESOLVEDOR DE LINK ORIGINAL (100% gratuito, sem custo de token)

O RSS do Google Notícias entrega links "embrulhados", do tipo:
    https://news.google.com/rss/articles/CBMi...
que redirecionam para a matéria de verdade, mas escondem o domínio de
destino até o clique. Para o público deste projeto (que já pediu, por
segurança contra phishing, para não usar encurtador de link), esse
comportamento do próprio Google causa exatamente o mesmo problema.

Este agente decodifica esses links usando a biblioteca open-source
`googlenewsdecoder` (sem chave de API, sem custo por uso), entregando a
URL real da matéria (ex: https://g1.globo.com/...).

CONCEITO ENSINADO:
- Um "link direto" nem sempre é direto. Vale a pena inspecionar o que
  uma fonte de dados realmente entrega antes de assumir que está pronto
  para uso -- nesse caso, o RSS parecia dar o link certo, mas na
  prática entregava um redirecionamento do próprio agregador.
- Mais uma vez, fallback: se a decodificação falhar (fora do ar, rate
  limit, formato inesperado), o pipeline mantém o link original em vez
  de quebrar.
"""

import requests
from googlenewsdecoder import gnewsdecoder

# A biblioteca googlenewsdecoder faz sua primeira requisição (buscar a
# página da matéria, para extrair os parâmetros de decodificação) SEM
# enviar um cabeçalho de User-Agent de navegador. O Google bloqueia com
# erro 403 requisições que parecem vir de um script em vez de um
# navegador real. Para contornar isso, adicionamos um User-Agent padrão
# de navegador a toda chamada requests.get() feita pela biblioteca.
_USER_AGENT_NAVEGADOR = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
)
_requests_get_original = requests.get


def _requests_get_com_user_agent(url, **kwargs):
    cabecalhos = kwargs.pop("headers", None) or {}
    cabecalhos.setdefault("User-Agent", _USER_AGENT_NAVEGADOR)
    kwargs["headers"] = cabecalhos
    return _requests_get_original(url, **kwargs)


requests.get = _requests_get_com_user_agent

# Pequeno intervalo entre decodificações, para não sermos bloqueados por
# excesso de requisições ao serviço gratuito do Google.
INTERVALO_ENTRE_DECODIFICACOES_SEGUNDOS = 1


def resolver_link_original(url: str) -> str:
    """
    Se a URL for um link "embrulhado" do Google Notícias, devolve o link
    de origem real. Para qualquer outra URL (ou se a decodificação
    falhar por qualquer motivo), devolve a URL original sem quebrar o
    pipeline.
    """
    if not url or "news.google.com" not in url:
        return url

    try:
        resultado = gnewsdecoder(url, interval=INTERVALO_ENTRE_DECODIFICACOES_SEGUNDOS)
        if resultado.get("status") and resultado.get("decoded_url"):
            return resultado["decoded_url"]
        else:
            print(f"[resolver_link] Não foi possível decodificar (sem erro, mas sem sucesso): {resultado.get('message', 'sem mensagem')} -- URL: {url[:80]}...")
    except Exception as erro:
        print(f"[resolver_link] Falha ao decodificar ({type(erro).__name__}: {erro}) -- URL: {url[:80]}...")

    return url


def resolver_links_das_noticias(noticias: list[dict]) -> list[dict]:
    """
    Substitui o campo "link" de cada notícia pelo link de origem real,
    quando aplicável. Roda só sobre a lista final já selecionada (não
    desperdiça decodificações em notícias descartadas).
    """
    for noticia in noticias:
        noticia["link"] = resolver_link_original(noticia["link"])
    return noticias


if __name__ == "__main__":
    exemplo_normal = "https://g1.globo.com/noticia-exemplo"
    exemplo_google = "https://news.google.com/rss/articles/CBMiXEFVX3lxTE1leGVtcGxvRGVUZXN0ZQ"

    print("URL normal (não deve mudar):", resolver_link_original(exemplo_normal))
    print("URL do Google Notícias (tenta decodificar):", resolver_link_original(exemplo_google))
