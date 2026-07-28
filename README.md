# Newsletter Diária de Notícias Policiais para WhatsApp (100% gratuito)

Pipeline de agentes em Python puro que busca notícias sobre operações policiais, crimes, fraudes e segurança pública em fontes públicas na web, filtra duplicatas, respeita uma janela de tempo configurável, encurta links e gera uma **newsletter diária** pronta para envio via WhatsApp — **sem usar nenhuma API de IA paga ou cobrada por token**.

## Contexto

Este projeto nasceu de uma necessidade real de comunicação institucional: monitorar e consolidar notícias sobre segurança pública para distribuição diária via WhatsApp — a "Newsletter Diária - Fórum Integra" —, um processo que antes era feito manualmente. A primeira versão usava a API da Anthropic (Claude) para buscar e estruturar as notícias; esta versão foi reconstruída do zero para eliminar qualquer custo por token, usando técnicas determinísticas onde IA generativa não era, na prática, necessária.

## O que este projeto demonstra

- **Arquitetura de pipeline com múltiplos agentes** especializados (buscador, deduplicador, encurtador, organizador, formatador), cada um com responsabilidade única e testável isoladamente.
- **Critério técnico sobre quando usar IA e quando não usar.** Nem todo "agente" precisa de um LLM por trás — comparação de texto, filtro de datas e formatação de string são resolvidos com Python puro, de forma mais rápida, previsível e barata.
- **Engenharia com restrições reais de custo e produção:** parada antecipada (early stopping) para não desperdiçar requisições, fallback gracioso quando um serviço externo (encurtador) falha, e limites de janela de tempo para manter a relevância do conteúdo.
- **Documentação honesta de limitações técnicas** (veja a seção sobre o filtro de duplicatas abaixo) — a abordagem determinística tem trade-offs conhecidos frente a uma abordagem com IA, e isso está documentado, não escondido.

## Por que não usa IA generativa

Todo o pipeline anterior (baseado em Claude/Gemini) foi substituído por técnicas determinísticas e gratuitas:

| Etapa | Como era (com IA) | Como é agora (gratuito) |
|---|---|---|
| Buscar notícias | Tool `web_search` da Anthropic (pago por token) | RSS público do Google Notícias (gratuito, sem chave) |
| Detectar duplicatas | Modelo julgando semanticamente | `difflib` (similaridade de texto) + sobreposição de palavras-chave + data + localidade |
| Organizar por tópico | Modelo classificando | Mapeamento direto configurado em `config.py` |
| Gerar mensagem final | Modelo escrevendo HTML/texto | Formatação de string determinística |

Nenhuma chamada de API é feita em nenhuma etapa. O custo de rodar este projeto é **zero**, independentemente de quantas vezes ou quantas notícias você processar.

## Arquitetura

```
config.py (categorias, termos, janela de tempo, meta)
        │
        ▼
┌─────────────────────┐  RSS público do Google Notícias. Aplica NA HORA:
│  1. Buscador         │  - filtro de janela de tempo (só notícias das
│  buscador.py         │    últimas N horas, ex: 48h)
│  buscar_ate_          │  - filtro de duplicata (compara com o que já
│  atingir_meta()       │    foi coletado)
└──────────┬───────────┘  PARA assim que atingir a meta (ex: 10 notícias)
           ▼
┌─────────────────────┐  Encurta os links das notícias finais usando a
│  2. Encurtador        │  API pública e gratuita do TinyURL (sem chave).
│  encurtador.py        │  Se falhar, mantém o link original (fallback).
└──────────┬───────────┘
           ▼
┌─────────────────────┐  Agrupa as notícias selecionadas nas categorias
│  3. Organizador       │  definidas em config.py.
│  organizador.py       │
└──────────┬───────────┘
           ▼
┌─────────────────────┐  Monta a mensagem final no formato exato do seu
│  4. Formatador        │  modelo, usando o link curto.
│  formatador_whatsapp  │
└──────────┬───────────┘
           ▼
   mensagem_whatsapp_*.txt (pronta para copiar/colar no WhatsApp)
```

## Regras de busca (ajustáveis em `config.py`)

- **Janela de tempo:** só considera notícias publicadas dentro de `JANELA_HORAS_MAXIMA` (padrão: 48h). Notícias sem data reconhecível são descartadas por segurança.
- **Meta de notícias:** a busca **para automaticamente** assim que atingir `META_TOTAL_NOTICIAS` (padrão: 10) — não continua buscando os termos restantes.
- **Encurtamento de link:** feito só nas notícias finais selecionadas (não nas descartadas), usando a API gratuita do TinyURL. Se o serviço estiver fora do ar, o link original é usado sem quebrar o pipeline.

## Como usar

```bash
pip install -r requirements.txt
cd src
python main.py
```

O resultado aparece no terminal e também é salvo em `saidas/mensagem_whatsapp_<timestamp>.txt` — é só copiar o conteúdo e colar na conversa do WhatsApp.

## Como ajustar a busca (o que você vai mexer com frequência)

Edite **`src/config.py`**. Cada categoria é uma lista de termos de busca:

```python
NOME_ORGANIZACAO = "Newsletter Diária - Fórum Integra"

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
    # adicione novas categorias ou termos aqui
}
```

Cada termo vira uma busca separada no Google Notícias. Quanto mais termos, mais cobertura — mas também mais tempo de execução (o buscador espera um intervalo entre requisições para não sobrecarregar o serviço gratuito).

## Formato da mensagem final

O cabeçalho é gerado com a data em **português**, no formato:

```
🖥 - *Newsletter Diária - Fórum Integra*
*Brasília,* *28* *de* *julho* *de* *2026*

 *===* *OPERAÇÕES POLICIAIS* *===*
=====================================
*Título da notícia em negrito*
https://link-encurtado
--------------------------------------
```

Quando você tiver ajustes adicionais no modelo oficial, é só mexer em `src/formatador_whatsapp.py` — a lógica de divisão em partes e organização por categoria continua igual.

## Limitação importante e honesta sobre o filtro de duplicatas

Sem usar um modelo de linguagem, a detecção de "é a mesma notícia?" depende de:
1. Datas próximas
2. Localidade em comum (quando identificável)
3. Parecença de texto (caractere a caractere) OU sobreposição de palavras-chave centrais

Isso funciona bem para a maioria dos casos, mas **pode deixar passar** duas notícias sobre o mesmo fato se as fontes usarem vocabulário muito diferente e sem palavras-chave em comum suficientes. É a diferença fundamental entre uma abordagem determinística (gratuita) e uma com IA (paga, mas com raciocínio semântico real).

**Se isso virar um problema na prática**, o próximo passo natural — ainda gratuito — é usar embeddings locais (biblioteca `sentence-transformers`, roda no seu computador, sem API, sem custo por token) para comparar o *significado* dos títulos em vez de só o texto. Posso implementar isso se notar que o filtro atual está deixando passar duplicatas com frequência.

## Limitações técnicas do RSS gratuito

- O Google Notícias pode limitar requisições muito frequentes — por isso há uma pausa de 1,5s entre buscas.
- Nem toda fonte pública tem RSS indexado pelo Google Notícias; a cobertura é ampla, mas não é 100% de tudo que existe na web.
- Este projeto não roda no ambiente do Claude (sandbox sem acesso à internet geral) — rode na sua própria máquina, onde há acesso normal à web.

## Próximos passos possíveis

- [ ] Automatizar o envio da mensagem (ex: `pywhatkit`, biblioteca gratuita que abre o WhatsApp Web e envia automaticamente)
- [ ] Agendar execução diária (ex: `cron` no Linux, Agendador de Tarefas no Windows, ou um workflow no N8N)
- [ ] Trocar o filtro de duplicatas por embeddings locais gratuitos (`sentence-transformers`) se a precisão atual não for suficiente
- [ ] Guardar notícias já enviadas (ex: em um `.json` local) para nunca repetir a mesma notícia em execuções futuras

## Stack

`Python` · `feedparser` (RSS) · `python-dateutil` · `difflib` (biblioteca padrão) — **zero APIs pagas, zero custo por token**
