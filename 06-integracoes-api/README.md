# Integrações de API — Dr. Guilherme Mota

Clientes Python para puxar métricas reais do **Google Ads** e **GA4**, sem precisar abrir o painel.

## O que tem aqui

- `google_ads_client.py` — campanhas ativas, relatório diário, termos de busca
- `ga4_client.py` — overview, fontes de tráfego, landing pages, eventos, séries temporais

## Setup (passo a passo, ~20 min)

### 1. Google Cloud Console (uma vez pra ambas as APIs)

1. Acesse https://console.cloud.google.com/
2. Crie um projeto novo (ex: "drguilherme-mkt")
3. No menu lateral → **APIs & Services → Library**
4. Ative **Google Ads API** e **Google Analytics Data API**

### 2. OAuth 2.0 (duas vezes — uma pra cada API)

Para **cada** uma das APIs:

1. **APIs & Services → Credentials → Create Credentials → OAuth client ID**
2. Tipo: **Desktop app**
3. Nome: "DrGuilherme Ads" e "DrGuilherme GA4" (diferentes)
4. Baixe o JSON e renomeie:
   - `google_ads_credentials.json` → `credentials/google_ads_credentials.json`
   - `ga4_credentials.json` → `credentials/ga4_credentials.json`

### 3. Developer Token (só Google Ads)

1. Acesse https://ads.google.com (a conta 559-021-2946)
2. **Tools & Settings → Setup → API Center**
3. Aplique pra um Developer Token. Em **test mode** você pode testar sem aprovação (limite de operações). Pra produção, tem que pedir aprovação do Google.
4. Cole o token em `credentials/developer_token.txt` (um arquivo de texto simples com o token)

### 4. Primeiro uso

```bash
cd "C:/Users/Pichau/Projects/DrGuilhermeMota-Marketing/06-integracoes-api"

# Google Ads — abre browser, pede login na conta Google
python google_ads_client.py auth

# GA4 — idem
python ga4_client.py auth
```

Os tokens ficam em `credentials/*.json` e são renovados automaticamente.

## Uso

```bash
# Painel rápido do Google Ads (campanhas + diário)
python google_ads_client.py

# Só as campanhas
python google_ads_client.py campaigns

# Termos de busca (pra KW negativas)
python google_ads_client.py search-terms

# Painel completo do GA4
python ga4_client.py

# Só overview
python ga4_client.py overview

# Só fontes de tráfego
python ga4_client.py sources
```

Todos os relatórios são exportados pra `reports/` em CSV.

## Limites

- **Google Ads API (test mode):** operações ilimitadas mas não pode mexer em campanhas de produção sem aprovação
- **GA4 API:** sem limite oficial, mas cotas por propriedade (10 req/s, ~100k linhas/dia)

## Segurança

- Os arquivos em `credentials/` **nunca** devem ir pro git
- O `developer_token.txt` dá acesso à sua conta de Ads — trate como senha
