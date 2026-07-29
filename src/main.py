"""
main.py
========
ORQUESTRADOR

Liga os agentes gratuitos em sequência:

  config.py (categorias, termos, janela de tempo, meta)
        |
        v
  [Agente 1] buscador.buscar_ate_atingir_meta()
        -> busca por categoria/termo, aplicando NA HORA:
           - filtro de janela de tempo (só notícias recentes)
           - filtro de duplicata (compara com o que já foi coletado)
        -> PARA assim que atingir a meta configurada (ex: 10 notícias)
        |
        v
  [Agente 2] encurtador.encurtar_links_das_noticias()
        -> encurta os links só das notícias finais selecionadas
        |
        v
  [Agente 3] organizador.organizar_por_categoria()
        |
        v
  [Agente 4] formatador_whatsapp.gerar_mensagem_completa()
        |
        v
  arquivo .txt salvo em /saidas, pronto pra colar no WhatsApp

Nenhuma etapa faz chamada a API de IA paga. O encurtador usa uma API
pública gratuita (TinyURL), sem chave e sem custo.
"""

import os
from datetime import datetime

import config
from buscador import buscar_ate_atingir_meta
from encurtador import encurtar_links_das_noticias
from organizador import organizar_por_categoria
from formatador_whatsapp import gerar_mensagem_completa


def executar_pipeline() -> list[str]:
    print(
        f"[1/4] Buscando notícias das últimas {config.JANELA_HORAS_MAXIMA}h "
        f"(meta: {config.META_TOTAL_NOTICIAS} notícia(s))..."
    )
    noticias_selecionadas = buscar_ate_atingir_meta(
        config.CATEGORIAS_DE_BUSCA,
        meta_total=config.META_TOTAL_NOTICIAS,
        janela_horas=config.JANELA_HORAS_MAXIMA,
        max_por_termo=config.MAX_RESULTADOS_POR_TERMO,
    )
    print(f"       -> {len(noticias_selecionadas)} notícia(s) selecionada(s).")

    print(f"[2/4] Processando links (encurtador {'ativado' if config.ATIVAR_ENCURTADOR_DE_LINK else 'desativado -- usando link original'})...")
    noticias_selecionadas = encurtar_links_das_noticias(
        noticias_selecionadas,
        ativar_encurtador=config.ATIVAR_ENCURTADOR_DE_LINK,
    )

    print("[3/4] Organizando por categoria...")
    noticias_organizadas = organizar_por_categoria(noticias_selecionadas, config.CATEGORIAS_DE_BUSCA)

    print("[4/4] Gerando mensagem(ns) final(is) para WhatsApp...")
    mensagens = gerar_mensagem_completa(
        noticias_organizadas,
        nome_organizacao=config.NOME_ORGANIZACAO,
        cidade=config.CIDADE_TIMESTAMP,
        tamanho_maximo_por_parte=config.TAMANHO_MAXIMO_POR_PARTE,
    )

    return mensagens


def salvar_mensagens(mensagens: list[str]) -> str:
    os.makedirs("saidas", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho = os.path.join("saidas", f"mensagem_whatsapp_{timestamp}.txt")

    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n\n".join(mensagens))

    return caminho


if __name__ == "__main__":
    mensagens_finais = executar_pipeline()

    print("\n" + "=" * 60)
    print("MENSAGEM(NS) PRONTA(S):")
    print("=" * 60 + "\n")
    for mensagem in mensagens_finais:
        print(mensagem)
        print("\n" + "-" * 60 + "\n")

    caminho_salvo = salvar_mensagens(mensagens_finais)
    print(f"Mensagens também salvas em: {caminho_salvo}")
    print("Copie o texto e cole diretamente no WhatsApp.")
