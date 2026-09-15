#!/usr/bin/env python3
"""
apply_negatives.py — Adiciona KW negativas via API Google Ads
Dr. Guilherme Mota — Psiquiatria infantil

Usa os mesmos arquivos do google_ads_client.py (sem setup novo).

USO:
    python apply_negatives.py
    python apply_negatives.py --dry-run   # mostra o que faria, sem aplicar
"""

import argparse
import json
import sys
from pathlib import Path

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

CREDENTIALS_DIR = Path(__file__).parent / "credentials"
CREDENTIALS_FILE = CREDENTIALS_DIR / "google_ads_credentials.json"
TOKEN_FILE = CREDENTIALS_DIR / "google_ads_token.json"
DEV_TOKEN_FILE = CREDENTIALS_DIR / "developer_token.txt"

CUSTOMER_ID = "5590212946"
LOGIN_CUSTOMER_ID = "3696718154"  # MCC

# Lista de KW negativas (nivel CAMPAIGN).
# Adicione aqui conforme aparecer busca errada no search terms.
NEGATIVAS = [
    # Fora de area (voce atende Taquara + online RJ/Brasil)
    "psiquiatra infantil brasilia",
    "psiquiatra infantil em joao pessoa",
    "psiquiatra infantil em montes claros",
    "psiquiatra infantil ipatinga",
    "psiquiatra infantil uberlandia",
    "psiquiatra infantil governador valadares",
    "psiquiatra infantil duque de caxias",
    "psiquiatra infantil barra da tijuca",
    "psiquiatra infantil niteroi",
    "psiquiatra infantil campo grande rj",   # NAO atende
    "psiquiatra infantil jacarepagua",
    "psiquiatra infantil zona oeste",
    # Concorrentes / outros profissionais
    "dr fabio barbirato psiquiatra",
    "daniel segenreich",
    "dra juracy",
    "lisia silva de faria",          # aparecido 2x nos search terms (R$5,82, 0 conv)
    "caio abujadi",                  # aparecido nos search terms (preventivo)
    # Testes / busca academica
    "psiquiatra teste tdah",
    "crianca imperativo",
    "neurologista psiquiatra infantil",
    # Outras especialidades (voce nao atende)
    "psicologo infantil",
    "fonoaudiologo infantil",
    "terapia ocupacional infantil",
    "nutricionista infantil",
    "ortopedista infantil",
    # Ortopedista homonimo (proteger contra confusao)
    "guilherme motta ortopedista",
    "dr guilherme motta ortopedista",
]


def load_client():
    if not all(p.exists() for p in [CREDENTIALS_FILE, TOKEN_FILE, DEV_TOKEN_FILE]):
        sys.exit("[ERRO] Rode google_ads_client.py auth primeiro.")
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="apenas mostra o que faria, nao aplica")
    args = ap.parse_args()

    print(f"== Adicionar {len(NEGATIVAS)} KW negativas ==\n")
    if args.dry_run:
        print("[DRY RUN] nada sera aplicado.\n")

    try:
        client = load_client()
    except Exception as e:
        sys.exit(f"[ERRO] {e}")

    print(f"Conta: {CUSTOMER_ID} (MCC: {LOGIN_CUSTOMER_ID})\n")

    if args.dry_run:
        for kw in NEGATIVAS:
            print(f"  [dry] campanha: {kw}")
        print(f"\nTotal: {len(NEGATIVAS)} KW a adicionar.")
        return

    # Monta operacoes em batch (mais rapido)
    operations = []
    for kw in NEGATIVAS:
        op = client.get_type("CampaignCriterionOperation")
        criterion = op.create
        criterion.negative = True
        criterion.keyword.text = kw
        criterion.keyword.match_type = (
            client.enums.KeywordMatchTypeEnum.BROAD
        )
        # Vincula a TODAS campanhas ativas via resource name temporario
        # A API substitui por customer ID ao aplicar
        operations.append(op)

    # Pega todas as campanhas ativas
    try:
        ga_service = client.get_service("GoogleAdsService")
        camp_query = """
            SELECT campaign.id, campaign.name, campaign.status
            FROM campaign
            WHERE campaign.status = 'ENABLED'
        """
        rows = list(ga_service.search(customer_id=CUSTOMER_ID, query=camp_query))
        campanhas_ativas = [r.campaign.id for r in rows]
        print(f"Campanhas ativas: {len(campanhas_ativas)}")
        for cid in campanhas_ativas:
            print(f"  {cid}")
    except GoogleAdsException as e:
        err = e.failure.errors[0]
        sys.exit(f"[ERRO] Listar campanhas: {err.message}")

    if not campanhas_ativas:
        sys.exit("[ERRO] Nenhuma campanha ativa.")

    # Constroi operacoes finais: 1 operacao por (KW x campanha)
    final_ops = []
    for kw in NEGATIVAS:
        for cid in campanhas_ativas:
            op = client.get_type("CampaignCriterionOperation")
            criterion = op.create
            criterion.campaign = f"customers/{CUSTOMER_ID}/campaigns/{cid}"
            criterion.negative = True
            criterion.keyword.text = kw
            criterion.keyword.match_type = (
                client.enums.KeywordMatchTypeEnum.BROAD
            )
            final_ops.append(op)

    print(f"\nAplicando {len(final_ops)} operacoes "
          f"({len(NEGATIVAS)} KW x {len(campanhas_ativas)} campanhas)...\n")

    try:
        service = client.get_service("CampaignCriterionService")
        response = service.mutate_campaign_criteria(
            customer_id=CUSTOMER_ID,
            operations=final_ops,
        )
        results = list(response.results)
        ok = len(results)
        print(f"[OK] {ok} KW negativas adicionadas com sucesso.")
        if ok < len(final_ops):
            print(f"[AVISO] {len(final_ops) - ok} podem ter falhado silenciosamente.")
    except GoogleAdsException as e:
        for err in e.failure.errors:
            print(f"  [ERRO] {err.error_code}: {err.message}")
        print("\nDica: KW duplicada (ja existe) retorna erro. Normal.")


if __name__ == "__main__":
    main()
