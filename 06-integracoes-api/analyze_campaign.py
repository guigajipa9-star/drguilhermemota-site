#!/usr/bin/env python3
"""
analyze_campaign.py — Analise read-only de campanhas Google Ads
Projeto: Dr. Guilherme Mota — Psiquiatria infantil

PRÉ-REQUISITOS:
    pip install google-ads
    credentials/google_ads_credentials.json  (OAuth client_id/secret)
    credentials/google_ads_token.json       (refresh_token)
    credentials/developer_token.txt         (developer token)

USO:
    python analyze_campaign.py                 # ultimos 7 dias
    python analyze_campaign.py --days 30       # ultimos 30 dias

O que faz (READ-ONLY, seguro em qualquer nivel que leia producao):
    1. Lista campanhas ativas com metricas
    2. Search terms: cliques/custo/conversao por termo de pesquisa
    3. Palavras-chave: custo, conversoes e Quality Score
    4. Lista "dinheiro jogado fora": KW com custo e ZERO conversao
    5. Sugere KW negativas (termos com gasto, 0 conversao)
    6. Exporta CSVs (encoding utf-8-sig pro Excel BR abrir certo)

NAO FAZ (deixado de proposito para depois do diagnostico de escrita):
    - Pausar keywords (mutacao) — secao comentada no final
    - Keyword Planner (bloqueado no nivel Explorer)

Usa os mesmos arquivos do google_ads_client.py — nenhum setup novo.
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# ─────────────────────────── CONFIGURAÇÃO ───────────────────────────
CREDENTIALS_DIR = Path(__file__).parent / "credentials"
CREDENTIALS_FILE = CREDENTIALS_DIR / "google_ads_credentials.json"
TOKEN_FILE = CREDENTIALS_DIR / "google_ads_token.json"
DEV_TOKEN_FILE = CREDENTIALS_DIR / "developer_token.txt"
OUT_DIR = "relatorios"

CUSTOMER_ID = "5590212946"        # conta de producao (sem hifens)
LOGIN_CUSTOMER_ID = "3696718154"  # MCC — OBRIGATORIO em toda chamada
# ────────────────────────────────────────────────────────────────────

METRICS = ("metrics.impressions, metrics.clicks, metrics.cost_micros, "
           "metrics.conversions, metrics.cost_per_conversion")


def micros_to_reais(v: int) -> float:
    return round(v / 1_000_000, 2)


def load_client() -> GoogleAdsClient:
    """Carrega cliente a partir dos arquivos existentes (sem YAML novo)."""
    if not all(p.exists() for p in [CREDENTIALS_FILE, TOKEN_FILE, DEV_TOKEN_FILE]):
        sys.exit("[ERRO] Arquivos faltando em credentials/. Rode google_ads_client.py auth primeiro.")
    with open(TOKEN_FILE, encoding="utf-8") as f:
        token = json.load(f)
    dev_token = DEV_TOKEN_FILE.read_text().strip()
    config = {
        "developer_token": dev_token,
        "client_id": token["client_id"],
        "client_secret": token["client_secret"],
        "refresh_token": token["refresh_token"],
        "login_customer_id": LOGIN_CUSTOMER_ID,
        "use_proto_plus": True,
    }
    return GoogleAdsClient.load_from_dict(config)


def run_query(client, customer_id: str, query: str) -> list:
    ga_service = client.get_service("GoogleAdsService")
    response = ga_service.search(customer_id=customer_id, query=query)
    return list(response)


def analyze_campaigns(client, customer_id: str, days: int) -> list:
    query = f"""
        SELECT
            campaign.id, campaign.name, campaign.status,
            campaign.advertising_channel_type,
            {METRICS}
        FROM campaign
        WHERE segments.date DURING LAST_{days}_DAYS
          AND campaign.status = 'ENABLED'
        ORDER BY metrics.cost_micros DESC
    """
    rows = []
    for r in run_query(client, customer_id, query):
        m = r.metrics
        rows.append({
            "campanha": r.campaign.name,
            "canal": r.campaign.advertising_channel_type.name,
            "impressoes": m.impressions,
            "cliques": m.clicks,
            "custo_r$": micros_to_reais(m.cost_micros),
            "conversoes": round(m.conversions, 2),
            "custo_por_conversao_r$": (micros_to_reais(m.cost_micros) / m.conversions)
                                      if m.conversions else None,
        })
    return rows


def analyze_search_terms(client, customer_id: str, days: int) -> list:
    query = f"""
        SELECT
            search_term_view.search_term,
            campaign.name,
            ad_group.name,
            {METRICS}
        FROM search_term_view
        WHERE segments.date DURING LAST_{days}_DAYS
        ORDER BY metrics.cost_micros DESC
        LIMIT 500
    """
    rows = []
    for r in run_query(client, customer_id, query):
        m = r.metrics
        rows.append({
            "termo_de_pesquisa": r.search_term_view.search_term,
            "campanha": r.campaign.name,
            "grupo": r.ad_group.name,
            "cliques": m.clicks,
            "custo_r$": micros_to_reais(m.cost_micros),
            "conversoes": round(m.conversions, 2),
        })
    return rows


def analyze_keywords(client, customer_id: str, days: int) -> list:
    query = f"""
        SELECT
            ad_group_criterion.keyword.text,
            ad_group_criterion.quality_info.quality_score,
            campaign.name,
            {METRICS}
        FROM keyword_view
        WHERE segments.date DURING LAST_{days}_DAYS
          AND ad_group_criterion.status != 'REMOVED'
        ORDER BY metrics.cost_micros DESC
        LIMIT 500
    """
    rows = []
    for r in run_query(client, customer_id, query):
        m = r.metrics
        rows.append({
            "keyword": r.ad_group_criterion.keyword.text,
            "campanha": r.campaign.name,
            "quality_score": r.ad_group_criterion.quality_info.quality_score,
            "cliques": m.clicks,
            "custo_r$": micros_to_reais(m.cost_micros),
            "conversoes": round(m.conversions, 2),
        })
    return rows


def find_wasted_spend(keywords: list, min_cost: float = 20.0) -> list:
    """KW com gasto >= min_cost e ZERO conversao."""
    return [k for k in keywords
            if k["conversoes"] == 0 and k["custo_r$"] >= min_cost]


def suggest_negatives(search_terms: list, min_cost: float = 10.0) -> list:
    """Search terms com gasto, 0 conversoes — candidatos a KW negativa."""
    return [s for s in search_terms
            if s["conversoes"] == 0 and s["custo_r$"] >= min_cost]


def export_csv(name: str, rows: list) -> None:
    if not rows:
        print(f"  (sem dados para {name})")
        return
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name)
    # utf-8-sig pro Excel BR abrir certo (acentos + R$)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"  -> {path} ({len(rows)} linhas)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7,
                    help="janela de analise em dias (padrao: 7)")
    args = ap.parse_args()

    print(f"== Analise Dr. Guilherme Mota — ultimos {args.days} dias ==")
    print(f"Conta: {CUSTOMER_ID} via MCC: {LOGIN_CUSTOMER_ID}")

    try:
        client = load_client()
        print("[OK] Cliente carregado.\n")
    except Exception as e:
        sys.exit(f"[ERRO] Falha ao carregar cliente: {e}")

    try:
        print("[1/5] Campanhas ativas...")
        campaigns = analyze_campaigns(client, CUSTOMER_ID, args.days)
        for c in campaigns:
            cpc = (c['custo_r$'] / c['cliques']) if c['cliques'] else 0
            print(f"  {c['campanha']}: R$ {c['custo_r$']} | "
                  f"{c['cliques']} cliques | CPC R${cpc:.2f} | {c['conversoes']} conv.")
        export_csv(f"campanhas_{args.days}d.csv", campaigns)

        print("[2/5] Search terms...")
        search_terms = analyze_search_terms(client, CUSTOMER_ID, args.days)
        export_csv(f"search_terms_{args.days}d.csv", search_terms)

        print("[3/5] Palavras-chave...")
        keywords = analyze_keywords(client, CUSTOMER_ID, args.days)
        export_csv(f"keywords_{args.days}d.csv", keywords)

        print("[4/5] Dinheiro jogado fora (KW com custo e 0 conversao)...")
        wasted = find_wasted_spend(keywords)
        total_wasted = sum(k["custo_r$"] for k in wasted)
        for k in wasted[:15]:
            print(f"  R$ {k['custo_r$']:>8} | QS {k['quality_score']} | {k['keyword']}")
        print(f"  TOTAL desperdiçado: R$ {total_wasted:.2f}")
        export_csv(f"desperdicio_{args.days}d.csv", wasted)

        print("[5/5] Sugestoes de KW negativas (search terms)...")
        negatives = suggest_negatives(search_terms)
        for s in negatives[:15]:
            print(f"  R$ {s['custo_r$']:>8} | {s['termo_de_pesquisa']}")
        export_csv(f"negativas_sugeridas_{args.days}d.csv", negatives)

        print("\n[OK] Analise completa. CSVs em ./relatorios/")

    except GoogleAdsException as e:
        print("\n[ERRO] Erro da API:")
        for err in e.failure.errors:
            print(f"  codigo: {err.error_code} | motivo: {err.message}")
        print("\nSe o erro for CLOUD_PROJECT_NOT_APPROVED_FOR_PRODUCTION:")
        print("  -> acesso ainda em analise. Aguarde aprovacao do Explorer.")
        print("Se for USER_PERMISSION_DENIED:")
        print("  -> verifique login_customer_id (linha 30 deste arquivo).")


# ═════════════════════════════════════════════════════════════════════
# MUTACOES - NAO DESCOMENTAR ANTES DO diagnose.py CONFIRMAR QUE EXPLORER
# PERMITE ESCRITA (teste 5). Quando liberado, usar ad_group_criterion
# com resource_name e operation.update/pause.
# ═════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
