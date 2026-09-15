"""
Diagnostico Google Ads API v2 - Dr. Guilherme Mota
Conta: 559-021-2946 | MCC: 369-671-8154

Identifica o que o token/nivel atual permite fazer.
login_customer_id da MCC eh OBRIGATORIO - sem isso, falsos negativos.

Uso: python diagnose.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

CREDENTIALS_DIR = Path(__file__).parent / "credentials"
CREDENTIALS_FILE = CREDENTIALS_DIR / "google_ads_credentials.json"
TOKEN_FILE = CREDENTIALS_DIR / "google_ads_token.json"
DEV_TOKEN_FILE = CREDENTIALS_DIR / "developer_token.txt"

CUSTOMER_ID = "5590212946"          # conta de producao
LOGIN_CUSTOMER_ID = "3696718154"    # MCC (header obrigatorio)


def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def green(t):  return color(t, "32")
def red(t):    return color(t, "31")
def yellow(t): return color(t, "33")
def blue(t):   return color(t, "34")
def bold(t):   return color(t, "1")


def parse_error(e: GoogleAdsException):
    """Extrai codigo exato do erro pra diagnostico preciso."""
    if not e.failure or not e.failure.errors:
        return "UNKNOWN", "sem mensagem"
    err = e.failure.errors[0]
    code_str = "UNKNOWN"
    if hasattr(err.error_code, "authorization_error") and err.error_code.authorization_error:
        code_str = f"AUTHZ:{err.error_code.authorization_error.name}"
    elif hasattr(err.error_code, "quota_error") and err.error_code.quota_error:
        code_str = f"QUOTA:{err.error_code.quota_error.name}"
    elif hasattr(err.error_code, "request_error") and err.error_code.request_error:
        code_str = f"REQ:{err.error_code.request_error.name}"
    else:
        code_str = type(err.error_code).__name__
    msg = err.message[:200] if err.message else "sem mensagem"
    return code_str, msg


def classify_error(code_str: str, msg: str) -> str:
    """Classifica o erro em categoria diagnostica."""
    s = f"{code_str} {msg}".upper()
    if "CLOUD_PROJECT_NOT_APPROVED_FOR_PRODUCTION" in s or "TEST" in s and "ACCOUNT" in s:
        return "TEST_LEVEL"
    if "DEVELOPER_TOKEN_NOT_APPROVED" in s:
        return "DEV_TOKEN_NOT_APPROVED"
    if "USER_PERMISSION_DENIED" in s:
        return "USER_PERMISSION_DENIED"
    if "LOGIN_CUSTOMER_ID" in s or "AUTHENTICATION_ERROR" in s:
        return "AUTH_ERROR"
    if "MUTATE_NOT_ALLOWED" in s or "AUTHORIZATION" in s and "WRITE" in s:
        return "EXPLORER_WRITE_BLOCKED"
    return code_str


def load_client():
    if not CREDENTIALS_FILE.exists():
        sys.exit(red(f"ERRO: {CREDENTIALS_FILE} nao encontrado."))
    if not TOKEN_FILE.exists():
        sys.exit(red(f"ERRO: {TOKEN_FILE} nao encontrado. Rode auth primeiro."))
    if not DEV_TOKEN_FILE.exists():
        sys.exit(red(f"ERRO: {DEV_TOKEN_FILE} nao encontrado."))

    with open(TOKEN_FILE) as f:
        token = json.load(f)
    developer_token = DEV_TOKEN_FILE.read_text().strip()

    # CRITICO: login_customer_id da MCC vai no config
    # A Google Ads Python client inclui isso em TODA chamada automaticamente
    config = {
        "developer_token": developer_token,
        "client_id": token["client_id"],
        "client_secret": token["client_secret"],
        "refresh_token": token["refresh_token"],
        "login_customer_id": LOGIN_CUSTOMER_ID,  # MCC header automatico
        "use_proto_plus": True,
    }
    print(blue(f"  [config] login_customer_id={LOGIN_CUSTOMER_ID} (MCC)"))
    return GoogleAdsClient.load_from_dict(config)


def test_list_accessible_customers(client):
    print(bold("\n[1/5] Listar contas acessiveis (read via MCC)"))
    print("-" * 60)
    try:
        service = client.get_service("CustomerService")
        accessible = service.list_accessible_customers()
        customers = [str(c) for c in accessible.resource_names]
        print(green(f"  OK - {len(customers)} contas via MCC"))
        for c in customers[:10]:
            print(f"    {c}")
        return "OK"
    except GoogleAdsException as e:
        code, msg = parse_error(e)
        cls = classify_error(code, msg)
        print(red(f"  FALHOU [{cls}] {code}"))
        print(f"  Msg: {msg}")
        return cls


def test_read_campaigns(client):
    print(bold("\n[2/5] Ler campanhas 5590212946 (read em producao)"))
    print("-" * 60)
    query = """
        SELECT campaign.id, campaign.name, campaign.status
        FROM campaign
        LIMIT 5
    """
    try:
        service = client.get_service("GoogleAdsService")
        response = service.search(customer_id=CUSTOMER_ID, query=query)
        campaigns = list(response)
        print(green(f"  OK - {len(campaigns)} campanhas"))
        for c in campaigns:
            print(f"    [{c.campaign.status.name}] {c.campaign.name}")
        return "OK"
    except GoogleAdsException as e:
        code, msg = parse_error(e)
        cls = classify_error(code, msg)
        print(red(f"  FALHOU [{cls}] {code}"))
        print(f"  Msg: {msg}")
        return cls


def test_read_search_terms(client):
    print(bold("\n[3/5] Ler termos de pesquisa (search terms - 7 dias)"))
    print("-" * 60)
    query = """
        SELECT
            search_term_view.search_term,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros
        FROM search_term_view
        WHERE segments.date DURING LAST_7_DAYS
        ORDER BY metrics.cost_micros DESC
        LIMIT 15
    """
    try:
        service = client.get_service("GoogleAdsService")
        response = service.search(customer_id=CUSTOMER_ID, query=query)
        terms = list(response)
        print(green(f"  OK - {len(terms)} termos retornados"))
        for t in terms[:7]:
            cost = t.metrics.cost_micros / 1_000_000
            print(f"    {t.search_term_view.search_term[:48]:48} "
                  f"imp={t.metrics.impressions} clk={t.metrics.clicks} "
                  f"R${cost:.2f}")
        return "OK"
    except GoogleAdsException as e:
        code, msg = parse_error(e)
        cls = classify_error(code, msg)
        print(red(f"  FALHOU [{cls}] {code}"))
        print(f"  Msg: {msg}")
        return cls


def test_keyword_planner(client):
    print(bold("\n[4/5] Keyword Planner (sentinela de nivel)"))
    print("-" * 60)
    try:
        service = client.get_service("KeywordPlanIdeaService")
        request = client.get_type("GenerateKeywordIdeasRequest")
        request.customer_id = CUSTOMER_ID
        request.language = "languageConstants/1014"
        request.geo_target_constants.append("geoTargetConstants/1056")
        request.keyword_seed.keywords.append("psiquiatra infantil")
        request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
        response = service.generate_keyword_ideas(request=request)
        ideas = list(response.results)
        print(green(f"  OK - {len(ideas)} ideias (BASIC+ confirmado)"))
        for i in ideas[:3]:
            print(f"    {i.text}: {i.keyword_metrics.avg_monthly_searches} buscas/mes")
        return "OK"
    except GoogleAdsException as e:
        code, msg = parse_error(e)
        cls = classify_error(code, msg)
        print(yellow(f"  FALHOU [{cls}] {code}"))
        print(f"  Msg: {msg}")
        if cls in ("TEST_LEVEL", "DEV_TOKEN_NOT_APPROVED"):
            print(yellow("  -> Nivel TEST ou Developer Token nao aprovado"))
        else:
            print(yellow("  -> Provavelmente EXPLORER (read OK, planning bloqueado)"))
        return cls


def test_reversible_write(client):
    print(bold("\n[5/5] Escrita reversivel (re-pausar keyword ja pausada)"))
    print("-" * 60)
    # Buscar keyword pausada de campanha PAUSADA (seguranca maxima)
    query_paused_campaign_kw = """
        SELECT
            ad_group_criterion.criterion_id,
            ad_group_criterion.keyword.text,
            ad_group_criterion.status,
            campaign.id,
            campaign.name,
            campaign.status
        FROM ad_group_criterion
        WHERE ad_group_criterion.type = "KEYWORD"
            AND ad_group_criterion.status = "PAUSED"
            AND campaign.status = "PAUSED"
        LIMIT 1
    """
    query_any_paused_kw = """
        SELECT
            ad_group_criterion.criterion_id,
            ad_group_criterion.keyword.text,
            ad_group_criterion.status,
            campaign.id,
            campaign.name,
            campaign.status
        FROM ad_group_criterion
        WHERE ad_group_criterion.type = "KEYWORD"
            AND ad_group_criterion.status = "PAUSED"
        LIMIT 1
    """
    service = client.get_service("GoogleAdsService")
    kw_info = None
    for label, q in [("KW pausada de campanha pausada", query_paused_campaign_kw),
                     ("Qualquer KW pausada", query_any_paused_kw)]:
        try:
            response = service.search(customer_id=CUSTOMER_ID, query=q)
            rows = list(response)
            if rows:
                kw_info = rows[0]
                print(blue(f"  Encontrada ({label}):"))
                print(f"    KW: {kw_info.ad_group_criterion.keyword.text}")
                print(f"    Campaign: [{kw_info.campaign.status.name}] {kw_info.campaign.name}")
                print(f"    Criterion ID: {kw_info.ad_group_criterion.criterion_id}")
                break
        except GoogleAdsException:
            continue

    if not kw_info:
        print(yellow("  AVISO: nenhuma KW pausada encontrada na conta."))
        print(yellow("  Crie manualmente 1 KW pausada numa campanha pausada antes de testar."))
        return "NO_TEST_DATA"

    # Tentar re-pausar (no-op, zero efeito real)
    ad_group_resource = client.get_service("GoogleAdsService")
    try:
        # Buscar ad_group_id da keyword
        ag_query = f"""
            SELECT ad_group.id, ad_group.name
            FROM ad_group_criterion
            WHERE ad_group_criterion.criterion_id = {kw_info.ad_group_criterion.criterion_id}
            LIMIT 1
        """
        ag_resp = list(service.search(customer_id=CUSTOMER_ID, query=ag_query))
        if not ag_resp:
            return "NO_AD_GROUP"
        ad_group_id = ag_resp[0].ad_group.id
        resource_name = (
            f"customers/{CUSTOMER_ID}/adGroupCriteria/"
            f"{ad_group_id}~{kw_info.ad_group_criterion.criterion_id}"
        )

        op = client.get_type("AdGroupCriterionOperation")
        criterion = op.update
        criterion.resource_name = resource_name
        criterion.status = client.enums.AdGroupCriterionStatusEnum.PAUSED  # ja esta, no-op
        op.update_mask.paths.append("status")

        ad_criterion_service = client.get_service("AdGroupCriterionService")
        response = ad_criterion_service.mutate_ad_group_criteria(
            customer_id=CUSTOMER_ID, operations=[op]
        )
        print(green(f"  OK - escrita executada (BASIC+ confirmado)"))
        print(f"    Resource: {resource_name}")
        return "OK"
    except GoogleAdsException as e:
        code, msg = parse_error(e)
        cls = classify_error(code, msg)
        print(yellow(f"  FALHOU [{cls}] {code}"))
        print(f"  Msg: {msg}")
        if "EXPLORER" in cls or "MUTATE" in cls.upper() or "AUTHORIZATION" in cls.upper():
            print(yellow("  -> EXPLORER confirmado (read OK, escrita bloqueada por nivel)"))
        elif cls in ("TEST_LEVEL", "DEV_TOKEN_NOT_APPROVED"):
            print(yellow("  -> Nivel TEST (escrita em producao bloqueada por definicao)"))
        return cls


def main():
    print(bold("\n" + "=" * 60))
    print(bold(" DIAGNOSTICO GOOGLE ADS API v2 - Dr. Guilherme Mota "))
    print(bold("=" * 60))
    print(f" Conta: {CUSTOMER_ID}")
    print(f" MCC:   {LOGIN_CUSTOMER_ID}")
    print(f" Data:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        client = load_client()
        print(green("\n  Cliente carregado.\n"))
    except Exception as e:
        sys.exit(red(f"ERRO ao carregar cliente: {e}"))

    r1 = test_list_accessible_customers(client)
    r2 = test_read_campaigns(client)
    r3 = test_read_search_terms(client)
    r4 = test_keyword_planner(client)
    r5 = test_reversible_write(client)

    print(bold("\n" + "=" * 60))
    print(bold(" DIAGNOSTICO FINAL "))
    print(bold("=" * 60))

    read_ok = r2 == "OK"
    planner_ok = r4 == "OK"
    write_ok = r5 == "OK"

    if r1 in ("AUTH_ERROR", "USER_PERMISSION_DENIED") or r2 in ("TEST_LEVEL", "DEV_TOKEN_NOT_APPROVED"):
        level = red("TEST (token nao aprovado pra producao)")
        msg = "Token ainda em nivel TEST. Nao consegue ler producao 559-021-2946."
        action = "Aplicar para BASIC no API Center da MCC. Backlog de fev/2026, melhor aplicar HOJE."
    elif read_ok and not planner_ok and not write_ok:
        level = yellow("EXPLORER (provavel)")
        msg = "Leitura de producao OK. Keyword Planner + escrita bloqueados."
        action = "Suficiente pra relatorios, search terms, metricas. Escrita via UI."
    elif read_ok and planner_ok and not write_ok:
        level = yellow("BASIC (provavel)")
        msg = "Leitura + Keyword Planner OK. Escrita requer teste adicional."
        action = "Pode usar planning completo. Escrita limitada."
    elif read_ok and planner_ok and write_ok:
        level = green("BASIC+ com escrita (BASIC/STANDARD)")
        msg = "Leitura + Keyword Planner + escrita OK."
        action = "Operacao completa via API. Pode pausar KW, ajustar lances via Python."
    else:
        level = yellow("INDETERMINADO")
        msg = "Cenario nao mapeado. Veja tabela abaixo."
        action = "Investigar caso a caso com base nos codigos de erro."

    print(f"\n Nivel provavel: {level}")
    print(f" Diagnostico:    {msg}")
    print(f" Acao:           {action}")
    print()
    print(bold(" Tabela de testes:"))
    labels = [
        ("1. Listar contas (MCC)", r1),
        ("2. Ler campanhas", r2),
        ("3. Ler search terms", r3),
        ("4. Keyword Planner", r4),
        ("5. Escrita reversivel", r5),
    ]
    for label, status in labels:
        if status == "OK":
            icon = green("OK")
        elif status in ("NO_TEST_DATA", "NO_AD_GROUP"):
            icon = yellow(status)
        elif status == "SKIP":
            icon = yellow("SKIP")
        else:
            icon = red(status)
        print(f"   {label:30} {icon}")
    print()
    print(bold(" Legenda:"))
    print("   OK                       = passou")
    print("   TEST_LEVEL               = nivel TEST, nao le producao")
    print("   DEV_TOKEN_NOT_APPROVED   = developer token nao aprovado")
    print("   EXPLORER_WRITE_BLOCKED   = Explorer, escrita bloqueada")
    print("   USER_PERMISSION_DENIED   = sem permissao na conta")
    print("   AUTH_ERROR               = problema de autenticacao")
    print()


if __name__ == "__main__":
    main()
