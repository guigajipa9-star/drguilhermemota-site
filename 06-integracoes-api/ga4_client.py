"""
Cliente GA4 Data API — Dr. Guilherme Mota
Propriedade: G-VG15BYNMHL

Setup:
1. Google Cloud Console > ativar "Google Analytics Data API"
2. Criar OAuth 2.0 Client ID (Desktop app)
3. credentials.json → credentials/ga4_credentials.json
4. Primeiro uso: python ga4_client.py auth
"""

import sys
import json
import csv
from pathlib import Path
from datetime import datetime, timedelta

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Metric,
    Dimension,
    RunReportRequest,
    OrderBy,
)
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

CREDENTIALS_DIR = Path(__file__).parent / "credentials"
CREDENTIALS_FILE = CREDENTIALS_DIR / "ga4_credentials.json"
TOKEN_FILE = CREDENTIALS_DIR / "ga4_token.json"
REPORTS_DIR = Path(__file__).parent / "reports"

PROPERTY_ID = "VG15BYNMHL"  # do G-VG15BYNMHL, sem o "G-"
SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]


def get_client() -> BetaAnalyticsDataClient:
    """Cliente GA4 autenticado."""
    if not TOKEN_FILE.exists():
        sys.exit(
            f"ERRO: {TOKEN_FILE} não encontrado.\n"
            "Rode primeiro: python ga4_client.py auth"
        )

    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.write_text(creds.to_json())

    return BetaAnalyticsDataClient(credentials=creds)


def auth_oauth():
    """Fluxo OAuth 2.0 local pra GA4."""
    from google_auth_oauthlib.flow import InstalledAppFlow

    if not CREDENTIALS_FILE.exists():
        sys.exit(f"ERRO: {CREDENTIALS_FILE} não encontrado. Baixe do Google Cloud.")

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")
    TOKEN_FILE.write_text(creds.to_json())
    print(f"\n✓ Token salvo em {TOKEN_FILE}")


# ─────────────────────────────────────────────────────────────────────
# Relatórios prontos
# ─────────────────────────────────────────────────────────────────────

def overview(client, days: int = 7):
    """Painel rápido: sessões, usuários, conversões."""
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="newUsers"),
            Metric(name="engagedSessions"),
            Metric(name="engagementRate"),
            Metric(name="averageSessionDuration"),
            Metric(name="conversions"),
            Metric(name="conversionRate"),
        ],
    )
    response = client.run_report(request)
    row = response.rows[0]
    metrics = [m.name for m in response.metric_headers]

    result = dict(zip(metrics, [v.value for v in row.metric_values]))

    print(f"\n{'=' * 50}\nGA4 — últimos {days} dias\n{'=' * 50}")
    print(f"  Sessões:             {result['sessions']}")
    print(f"  Usuários únicos:     {result['totalUsers']}")
    print(f"  Novos:               {result['newUsers']}")
    print(f"  Engajadas:           {result['engagedSessions']} ({float(result['engagementRate'])*100:.1f}%)")
    print(f"  Duração média:       {float(result['averageSessionDuration']):.1f}s")
    print(f"  Conversões:          {result['conversions']}")
    print(f"  Taxa de conversão:   {float(result['conversionRate'])*100:.2f}%")
    return result


def traffic_sources(client, days: int = 30):
    """De onde vem o tráfego — agrupado por source/medium."""
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        dimensions=[
            Dimension(name="sessionSource"),
            Dimension(name="sessionMedium"),
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="conversions"),
        ],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
        limit=20,
    )
    response = client.run_report(request)
    rows = []
    for row in response.rows:
        rows.append({
            "source": row.dimension_values[0].value,
            "medium": row.dimension_values[1].value,
            "sessões": int(row.metric_values[0].value),
            "usuários": int(row.metric_values[1].value),
            "conversões": int(row.metric_values[2].value),
        })

    print(f"\n{'=' * 60}\nFontes de tráfego (últimos {days} dias)\n{'=' * 60}")
    for r in rows:
        print(f"  {r['source'][:30]:<30} {r['medium'][:15]:<15}  {r['sessões']:>5} sessões  {r['conversões']:>3} conv")
    return rows


def landing_pages(client, days: int = 30):
    """Performance por página de entrada."""
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        dimensions=[
            Dimension(name="landingPagePlusQueryString"),
            Dimension(name="sessionDefaultChannelGroup"),
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="engagementRate"),
            Metric(name="conversions"),
        ],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
        limit=30,
    )
    response = client.run_report(request)
    rows = []
    for row in response.rows:
        rows.append({
            "página": row.dimension_values[0].value[:80],
            "canal": row.dimension_values[1].value,
            "sessões": int(row.metric_values[0].value),
            "engajamento_%": round(float(row.metric_values[1].value) * 100, 1),
            "conversões": int(row.metric_values[2].value),
        })

    print(f"\n{'=' * 60}\nLanding pages (últimos {days} dias)\n{'=' * 60}")
    for r in rows:
        print(f"  {r['página'][:50]:<50}  {r['sessões']:>5}  eng={r['engajamento_%']:>5}%  conv={r['conversões']:>3}")
    return rows


def conversions_by_event(client, days: int = 30):
    """Quais eventos de conversão estão disparando."""
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount"), Metric(name="conversions")],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)],
        limit=15,
    )
    response = client.run_report(request)
    rows = []
    for row in response.rows:
        rows.append({
            "evento": row.dimension_values[0].value,
            "contagem": int(row.metric_values[0].value),
            "conversões": int(row.metric_values[1].value),
        })

    print(f"\n{'=' * 50}\nEventos (últimos {days} dias)\n{'=' * 50}")
    for r in rows:
        marker = "★" if r["conversões"] > 0 else " "
        print(f"  {marker} {r['evento'][:35]:<35}  {r['contagem']:>5}  conv={r['conversões']}")
    return rows


def daily_traffic(client, days: int = 30):
    """Séries temporais pra ver tendências."""
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        dimensions=[Dimension(name="date")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="conversions"),
        ],
        order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date"))],
    )
    response = client.run_report(request)
    rows = []
    for row in response.rows:
        rows.append({
            "data": row.dimension_values[0].value,
            "sessões": int(row.metric_values[0].value),
            "conversões": int(row.metric_values[1].value),
        })

    print(f"\n{'=' * 50}\nTráfego diário (últimos {days} dias)\n{'=' * 50}")
    for r in rows:
        print(f"  {r['data']}  {r['sessões']:>4} sessões  {r['conversões']:>3} conv")
    return rows


def export_csv(rows: list[dict], filename: str):
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

    client = get_client()

    if len(sys.argv) > 1 and sys.argv[1] == "overview":
        overview(client, days=7)
        return
    if len(sys.argv) > 1 and sys.argv[1] == "sources":
        rows = traffic_sources(client)
        export_csv(rows, f"ga4_sources_{datetime.now():%Y%m%d_%H%M}.csv")
        return
    if len(sys.argv) > 1 and sys.argv[1] == "pages":
        rows = landing_pages(client)
        export_csv(rows, f"ga4_pages_{datetime.now():%Y%m%d_%H%M}.csv")
        return
    if len(sys.argv) > 1 and sys.argv[1] == "events":
        rows = conversions_by_event(client)
        export_csv(rows, f"ga4_events_{datetime.now():%Y%m%d_%H%M}.csv")
        return
    if len(sys.argv) > 1 and sys.argv[1] == "daily":
        rows = daily_traffic(client)
        export_csv(rows, f"ga4_daily_{datetime.now():%Y%m%d_%H%M}.csv")
        return

    # Padrão: painel completo
    overview(client, days=7)
    rows = traffic_sources(client, days=30)
    export_csv(rows, f"ga4_sources_{datetime.now():%Y%m%d_%H%M}.csv")
    rows = landing_pages(client, days=30)
    export_csv(rows, f"ga4_pages_{datetime.now():%Y%m%d_%H%M}.csv")
    rows = conversions_by_event(client, days=30)
    export_csv(rows, f"ga4_events_{datetime.now():%Y%m%d_%H%M}.csv")


if __name__ == "__main__":
    main()
