"""
Cliente Google Ads API — Dr. Guilherme Mota
Conta: 559-021-2946
Campanha ativa: Psiquiatria Infantil 1.0 (R$40/dia, RJ)

Setup necessário (já feito):
1. Projeto no Google Cloud Console: psiquiatria-infantil
2. Google Ads API ativada no projeto
3. OAuth client ID tipo "Desktop app": DrGuilherme Ads
4. Developer Token solicitado na MCC (Dr. Guilherme Mota — Gerenciador)
5. credentials/google_ads_credentials.json (OAuth)
6. credentials/developer_token.txt (token)
7. credentials/google_ads_token.json (gerado pelo `auth`)
"""

import sys
import json
import csv
from pathlib import Path
from datetime import datetime

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Configurações
CREDENTIALS_DIR = Path(__file__).parent / "credentials"
CREDENTIALS_FILE = CREDENTIALS_DIR / "google_ads_credentials.json"
TOKEN_FILE = CREDENTIALS_DIR / "google_ads_token.json"
DEV_TOKEN_FILE = CREDENTIALS_DIR / "developer_token.txt"
REPORTS_DIR = Path(__file__).parent / "reports"

CUSTOMER_ID = "5590212946"  # sem hifens (formato API)
LOGIN_CUSTOMER_ID = CUSTOMER_ID  # MCC se houver; mesmo valor se não


def load_client() -> GoogleAdsClient:
    """Carrega cliente autenticado. Renova token automaticamente."""
    if not CREDENTIALS_FILE.exists():
        sys.exit(
            f"ERRO: {CREDENTIALS_FILE} não encontrado.\n"
            "Baixe o credentials.json do Google Cloud Console e coloque nessa pasta."
        )

    if not TOKEN_FILE.exists():
        sys.exit(
            f"ERRO: {TOKEN_FILE} não encontrado.\n"
            "Rode primeiro: python google_ads_client.py auth"
        )

    if not DEV_TOKEN_FILE.exists():
        sys.exit(
            f"ERRO: {DEV_TOKEN_FILE} não encontrado.\n"
            "Cole seu Developer Token nesse arquivo (um token por linha)."
        )

    token = json.loads(TOKEN_FILE.read_text())
    developer_token = DEV_TOKEN_FILE.read_text().strip()

    config = {
        "developer_token": developer_token,
        "client_id": token["client_id"],
        "client_secret": token["client_secret"],
        "refresh_token": token["refresh_token"],
        "login_customer_id": LOGIN_CUSTOMER_ID,
        "use_proto_plus": True,
    }

    return GoogleAdsClient.load_from_dict(config)


def auth_oauth():
    """Fluxo OAuth 2.0 local: abre browser, gera token.json."""
    from google_auth_oauthlib.flow import InstalledAppFlow

    SCOPES = ["https://www.googleapis.com/auth/adwords"]

    if not CREDENTIALS_FILE.exists():
        sys.exit(f"ERRO: {CREDENTIALS_FILE} não encontrado. Baixe do Google Cloud.")

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")

    token_data = {
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "refresh_token": creds.refresh_token,
        "token": creds.token,
        "scopes": list(creds.scopes),
        "obtained_at": datetime.now().isoformat(),
    }
    TOKEN_FILE.write_text(json.dumps(token_data, indent=2))
    print(f"\n✓ Token salvo em {TOKEN_FILE}")
    print("Daí pra frente é só chamar as funções.")


# ─────────────────────────────────────────────────────────────────────
# Queries
# ─────────────────────────────────────────────────────────────────────

def list_active_campaigns(client: GoogleAdsClient):
    """Lista campanhas ativas com métricas dos últimos 7 dias."""
    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.ctr,
            metrics.average_cpc,
            metrics.conversions,
            metrics.cost_per_conversion
        FROM campaign
        WHERE campaign.status = 'ENABLED'
        AND segments.date DURING LAST_7_DAYS
        ORDER BY metrics.cost_micros DESC
    """

    response = ga_service.search(customer_id=CUSTOMER_ID, query=query)
    rows = []
    for row in response:
        cost_reais = row.metrics.cost_micros / 1_000_000
        cpc_reais = row.metrics.average_cpc / 1_000_000
        cpa_reais = (row.metrics.cost_per_conversion / 1_000_000) if row.metrics.cost_per_conversion else None
        rows.append({
            "id": row.campaign.id,
            "nome": row.campaign.name,
            "status": row.campaign.status.name,
            "tipo": row.campaign.advertising_channel_type.name,
            "impressões": row.metrics.impressions,
            "cliques": row.metrics.clicks,
            "custo_R$": round(cost_reais, 2),
            "ctr_%": round(row.metrics.ctr * 100, 2),
            "cpc_médio_R$": round(cpc_reais, 2),
            "conversões": row.metrics.conversions,
            "custo_por_conv_R$": round(cpa_reais, 2) if cpa_reais else None,
        })
    return rows


def campaign_daily_report(client: GoogleAdsClient, campaign_id: int, days: int = 30):
    """Relatório diário de uma campanha específica."""
    ga_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
            segments.date,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM campaign
        WHERE campaign.id = {campaign_id}
        AND segments.date DURING LAST_{days}_DAYS
        ORDER BY segments.date ASC
    """

    response = ga_service.search(customer_id=CUSTOMER_ID, query=query)
    return [
        {
            "data": row.segments.date,
            "impressões": row.metrics.impressions,
            "cliques": row.metrics.clicks,
            "custo_R$": round(row.metrics.cost_micros / 1_000_000, 2),
            "conversões": row.metrics.conversions,
        }
        for row in response
    ]


def search_terms_report(client: GoogleAdsClient, days: int = 30):
    """Termos de busca que acionaram anúncios — útil pra KW negativas."""
    ga_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
            search_term_view.search_term,
            search_term_view.status,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM search_term_view
        WHERE segments.date DURING LAST_{days}_DAYS
        AND metrics.impressions > 10
        ORDER BY metrics.cost_micros DESC
        LIMIT 100
    """

    response = ga_service.search(customer_id=CUSTOMER_ID, query=query)
    return [
        {
            "termo": row.search_term_view.search_term,
            "status": row.search_term_view.status.name,
            "impressões": row.metrics.impressions,
            "cliques": row.metrics.clicks,
            "custo_R$": round(row.metrics.cost_micros / 1_000_000, 2),
            "conversões": row.metrics.conversions,
        }
        for row in response
    ]


# ─────────────────────────────────────────────────────────────────────
# Saída
# ─────────────────────────────────────────────────────────────────────

def print_table(rows: list[dict], title: str):
    """Imprime tabela formatada no terminal."""
    if not rows:
        print(f"\n{title}: nenhum resultado.")
        return
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")
    keys = list(rows[0].keys())
    widths = {k: max(len(k), max(len(str(r.get(k, ''))) for r in rows)) for k in keys}
    print(" | ".join(k.ljust(widths[k]) for k in keys))
    print("-+-".join("-" * widths[k] for k in keys))
    for row in rows:
        print(" | ".join(str(row.get(k, "")).ljust(widths[k]) for k in keys))


def export_csv(rows: list[dict], filename: str):
    """Exporta lista de dicts pra CSV."""
    if not rows:
        return
    REPORTS_DIR.mkdir(exist_ok=True)
    filepath = REPORTS_DIR / filename
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"✓ Exportado: {filepath}")


# ─────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "auth":
        auth_oauth()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "campaigns":
        client = load_client()
        rows = list_active_campaigns(client)
        print_table(rows, "Campanhas ativas (últimos 7 dias)")
        export_csv(rows, f"campaigns_{datetime.now():%Y%m%d_%H%M}.csv")
        return

    if len(sys.argv) > 1 and sys.argv[1] == "search-terms":
        client = load_client()
        rows = search_terms_report(client)
        print_table(rows[:30], "Top 30 termos de busca (últimos 30 dias)")
        export_csv(rows, f"search_terms_{datetime.now():%Y%m%d_%H%M}.csv")
        return

    # Padrão: painel rápido
    client = load_client()
    print("Google Ads — conta 559-021-2946\n")
    rows = list_active_campaigns(client)
    print_table(rows, "Campanhas ativas (últimos 7 dias)")

    infantil = next((r for r in rows if "infantil" in r["nome"].lower()), None)
    if infantil:
        daily = campaign_daily_report(client, infantil["id"], days=14)
        print_table(daily[-14:], f"Diário: {infantil['nome']} (últimos 14 dias)")
        export_csv(daily, f"diario_infantil_{datetime.now():%Y%m%d_%H%M}.csv")


if __name__ == "__main__":
    try:
        main()
    except GoogleAdsException as ex:
        print(f"\n✗ Erro Google Ads: {ex.error.code().name}")
        print(ex.failure)
        sys.exit(1)
    except Exception as ex:
        print(f"\n✗ Erro: {ex}")
        sys.exit(1)
