# Resumo do Projeto — Dr. Guilherme Mota

**Data:** 07/09/2026  
**Responsável técnico:** OpenCode  
**Status:** Landing page pronta, Google Ads em configuração

---

## ✅ O que está pronto

### 1. Landing Page (`04-landing-pages/psiquiatria-infantil.html`)
- HTML funcional, responsivo, mobile-first
- Paleta dourada/cream, design moderno e acolhedor
- 5 pontos de contato WhatsApp (header, hero, online, presencial, sticky bar)
- Copy humanizada, sem jargão médico
- Sinais de alerta, especialidades, FAQ, sobre o médico
- JSON-LD (structured data) para SEO
- Acessibilidade: skip link, focus-visible, prefers-reduced-motion
- **Imagens existem** em `fotos-consultorio/web/`
- **Telefone no JSON-LD já é o real:** +55 51 98330-0503
- **Instagram:** @drguilhermemota (confirmado)

### 2. Google Business Profile (`01-perfil-google/guia-correcao.md`)
- Guia de correção pronto: site, nome, descrição, serviços
- Categoria principal: Psiquiatra
- Serviços listados: TDAH, ansiedade, depressão, burnout, telemedicina

### 3. Google Ads (`02-campanha-google-ads/guia-configuracao.md`)
- Campanha configurada com objetivo "Leads → Clientes marcam um horário"
- 8 títulos e 4 descrições otimizados para psiquiatria infantil
- 11 palavras-chave específicas selecionadas
- Segmentação: 10 km de Taquara/Jacarepaguá, RJ
- Orçamento: R$ 40/dia (R$ 1.216/mês)
- Rede: Pesquisar (sem Display)
- Aquisição: novos e antigos clientes (sem restrição)

---

## ⚠️ O que NÃO fazer

- **Não usar `estrategia-novo-site.md`** — contém depoimentos fictícios e cita clínica em Taquara que não existe
- **Não adicionar banner de cookies** — site ainda não rastreia nada, é desnecessário
- **Não restringir a "apenas novos clientes"** — sem base de dados, só limita alcance

---

## 🔧 O que falta fazer

| Tarefa | Prioridade | Observação |
|--------|------------|------------|
| Instalar Google Analytics 4 | Média | Só precisa do ID da conta do cliente |
| Instalar tag de conversão Google Ads | Média | Mesmo ID acima |
| Criar página de Política de Privacidade | Alta | Obrigatório para saúde (LGPD) |
| Substituir homepage atual ou criar subdomínio | Alta | Decidir: `drguilhermemota.com.br` ou `infantil.drguilhermemota.com.br` |
| Ativar campanha Google Ads | Alta | Aguardando decisão de meta ("Leads" vs "Tráfego") |

---

## 📊 Métricas de sucesso (30 dias)

- 500+ visitas no site
- 50+ cliques no WhatsApp
- 10+ agendamentos
- Custo por agendamento < R$ 120

---

## 📁 Arquivos válidos no projeto

```
DrGuilhermeMota-Marketing/
├── README.md                          # Visão geral
├── 01-perfil-google/
│   └── guia-correcao.md               # ✅ Usar
├── 02-campanha-google-ads/
│   └── guia-configuracao.md           # ✅ Usar
├── 04-landing-pages/
│   ├── psiquiatria-infantil.html      # ✅ Usar (landing pronta)
│   ├── estrategia-novo-site.md        # ❌ NÃO usar (tem erros)
│   └── fotos-consultorio/             # ✅ Imagens existem
```

---

*Resumo preparado parahandoff técnico. Landing page funcional em `psiquiatria-infantil.html`.*
