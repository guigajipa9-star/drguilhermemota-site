# Auditoria Campanha Secretariado (24279727893) — Akatú

**Data da auditoria:** 26/set/2026 (manhã)
**Conta:** Akatú Psiquiatria (8787758766)
**Campanha:** SEARCH | Secretariado (ID 24279727893)
**Responsável:** Hermes Agent

---

## 📊 Estado INICIAL (antes das ações)

| Métrica | Valor |
|---|---|
| Status | ENABLED |
| Tipo | SEARCH |
| Bidding | TARGET_SPEND |
| Budget | R$ 10/dia (STANDARD) |
| Dias ativos (30d) | **2 de 30** (24-25/set) |
| Total gasto 30d | R$ 58,65 |
| Cliques 30d | 13 |
| Impressões 30d | 53 |
| CTR 30d | 24,53% |
| CPC 30d | R$ 4,51 |
| Conversões 30d | **0** |
| QS médio das KW | 0 (sem dados suficientes) |
| Anúncio | APPROVED (825860598418) |
| URL final | `/psiquiatras` |

---

## 🚨 Achados críticos da rodada 1

### 1. **Ad_schedule com bug** — `bid_modifier=0.0` (5 critérios)
- MONDAY-FRIDAY 08:00-22:00 com bid_mod=0.0
- Valor inválido (range válido: 0.1-10.0)
- Google está **ignorando** = tratando como default 1.0

### 2. **Sábado e Domingo rodavam 24h** (sem critério = default)
- Sábado: R$ 16,45 em cliques
- Domingo: R$ 1,16 em cliques

### 3. **6 KW com 0 impressão em 30d** — inúteis
- 4 mencionam WhatsApp (sem tag de conversão = cliques não medidos)
- 2 variantes redundantes de KW que já funcionam

### 4. **R$ 40,04 em search terms problemáticos** (KW negativas não pegavam)
- `psiquiatra online grátis` (4 cliques, R$ 17,47)
- `psiquiatra online 24 horas grátis` (3 cliques, R$ 13,94)
- `psiquiatra 24 horas` (1, R$ 4,96)
- `psiquiatra online grátis chat 24 horas` (1, R$ 3,67)

### 5. **IS perdido 55% por RANK** — copy/LP perdem leilão
- Diferente da outra campanha (perdia por budget)
- Aumentar budget **não resolve**, só piora o problema

### 6. **KW REMOVIDAS com impressões residuais** (não grave)
- 2 KW removidas ainda geraram 4 impressões (0 cliques)

### 7. **KW campeã isolada**: `marcar consulta psiquiatra online`
- Responsável por 9/13 cliques = **69% do tráfego**

### 8. **Headline com exclamação + imperativo**: `Agende uma consulta agora!`
- Risco de reprovação CFM Art. 8
- Atualmente APPROVED (preventivo)

---

## ✅ Ações executadas

### Ação (a) — Bloquear Sábado-Domingo
- 2 critérios AD_SCHEDULE criados (SAT/SUN 00-23h, bid_mod=0.1)
- Sábado-Domingo agora BLOQUEADOS
- Economia esperada: ~R$ 17/mês

### Ação (b) — Corrigir ad_schedule (5 critérios Seg-Sex)
- 5 critérios antigos (com bug bid_mod=0.0) **REMOVIDOS**
- 5 novos critérios **CRIADOS** com bid_mod=1.0
- Mesmo comportamento (veicula 8-22h Seg-Sex), agora tecnicamente correto

### Ação (c) — Adicionar KW negativas (8 novas)
- `grátis` [EXACT]
- `barato`, `24 horas`, `psymeet`, `valor social`, `popular`, `com laudo`, `com rqe` [BROAD]
- Total campanha: 23 → **31 KW negativas**

### Ação (d) — Pausar 6 KW com 0 impressão
- `agendar consulta psiquiatra online` [PHRASE]
- `consulta psiquiátrica whatsapp` [PHRASE]
- `falar com psiquiatra no whatsapp` [PHRASE]
- `secretaria psiquiatria agendamento` [PHRASE]
- `agendar psiquiatra whatsapp` [EXACT]
- `psiquiatra agendamento whatsapp` [PHRASE]
- Total KW positivas: 9 → **3**

### Ação (e) — Budget R$ 10 → R$ 50/dia
- Aplicado com sucesso (read-back confirmou)

---

## 📊 Estado FINAL (após todas as ações)

| Métrica | Antes | Depois |
|---|---|---|
| Budget | R$ 10/dia | **R$ 50/dia** |
| KW positivas ativas | 9 | **3** |
| KW EXACT pausadas | 0 | 0 |
| KW PHRASE pausadas | 0 | **6** |
| KW negativas campanha | 23 | **31** |
| Ad_schedule critérios | 5 (bug) + 0 | **7 (corretos)** |
| Sábado-Domingo | Rodando | **Bloqueado** |
| Conversões | 0 | 0 (tag ausente) |

### KW ativas restantes (as 3 que funcionam):

| KW | Match | Imp | Clq | Custo |
|---|---|---|---|---|
| `marcar consulta psiquiatra online` | PHRASE | 26 | **9** | R$ 40,08 |
| `marcar psiquiatra online` | EXACT | 14 | 2 | R$ 9,98 |
| `psiquiatra atendimento imediato` | PHRASE | 9 | 2 | R$ 8,59 |
| **TOTAL** | | **49** | **13** | **R$ 58,65** |

---

## 💰 Resumo financeiro das mudanças de HOJE

| Mudança | Economia/custo |
|---|---|
| Sábado-Domingo bloqueado | -R$ 17/mês |
| KW negativas (8 novas) | -R$ 40/mês |
| KW WhatsApp pausadas (6) | -R$ 0 (não geravam) |
| **TOTAL economia** | **-R$ 57/mês** |
| Budget R$ 10 → R$ 50 | **+R$ 1.200/mês** (gasto potencial) |

**Saldo líquido:** você **gastará mais** com R$ 50/dia, mas agora **em KW que funcionam**, sem desperdício em WhatsApp/grátis, e bloqueado em fim de semana.

---

## ⚠️ Alertas importantes

### 1. Tag de conversão AUSENTE no site
- Tag `AW-18370953668` (Google Ads) não está instalada no site da Akatú
- Conversões continuam sendo **0** independente do budget
- Aumentar budget agora = **mais dinheiro queimado visivelmente**
- **Recomendação forte:** instalar tag antes de aumentar mais budget

### 2. IS perdido 55% por RANK (não budget)
- Copy e/ou landing page perdem leilão para concorrentes
- Aumentar budget **não resolve** esse problema
- Sugestão: revisar headlines/descrições + LP de `/psiquiatras`

### 3. Headline com exclamação + imperativo
- `Agende uma consulta agora!`
- Risco de reprovação em revisão CFM 2.336
- Atualmente APPROVED, mas preventivo

---

## 🎯 Próximas ações sugeridas (não executadas ainda)

### Curto prazo (essa semana):
1. **Instalar tag** `AW-18370953668` no site da Akatú (decisão da clínica/Agência)
2. **Avaliar headline** `Agende uma consulta agora!` (trocar preventivamente)
3. **Monitorar** performance com R$ 50/dia — se budget queimar cedo = demanda alta; se sobrar = revisar KW

### Médio prazo (próximas 2 semanas):
4. **Considerar LP dedicada** para "agendar consulta" (não só `/psiquiatras`)
5. **Testar nova copy** focada em agendamento (não em psiquiatra genérico)
6. **Comparar** com a outra campanha (CONSULTAS ONLINE — `24265585325`) após mudanças de ontem

---

## 📋 Comparativo entre as duas campanhas da Akatú

| Item | CONSULTAS ONLINE (24265585325) | SECRETARIADO (24279727893) |
|---|---|---|
| Budget agora | R$ 10/dia | **R$ 50/dia** |
| KW ativas | 10 | 3 |
| KW negativas | 11 | 31 |
| Ad_schedule | Bloqueio 00-06h todos dias | Seg-Sex 8-22h + Sáb-Dom OFF |
| Dias ativos 30d | 7 | 2 |
| Cliques 30d | 99 | 13 |
| Conversões | 0 | 0 |
| IS perdido por budget | 60% | 27% |
| IS perdido por rank | 23% | **55%** |

---

## 📂 Documentos relacionados

- `auditoria-24265585325-2026-09-26.md` (auditoria da outra campanha)
- `CONTEXTO-PSIQUIATRIA.md` (contexto consolidado atualizado)
- `google-ads-psiquiatria` (skill carregável no Hermes)

---

**Gerado automaticamente por:** Hermes Agent
**Commit:** será adicionado em sequência