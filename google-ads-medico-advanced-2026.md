# Google Ads Médico Brasil — Tópicos Avançados (v3.0)

**Versão:** 1.0 · **Data:** 25/set/2026
**Aplicação:** Complementa os 9 docs existentes com tópicos avançados (LGPD prática, AI em anúncios, Privacy Sandbox 2026-2027, comparativos internacionais, Schema.org avançado, integração Memed/PRM, concorrentes Akatú, estratégia de conteúdo).
**Fontes oficiais:** Google Ads Help, CFM, ANPD, Privacy Sandbox Blog, Schema.org

---

## 1. LGPD Prática (Consent Mode v2 + Enhanced Conversions)

### 1.1 Consent Mode v2 — implementação técnica

**URL oficial:** https://developers.google.com/tag-platform/security/guides/consent

**Por que é obrigatório:** cada clique WA com GCLID = evento de tratamento de dado pessoal sensível (saúde mental = Art. 5°, II LGPD). Sem consentimento explícito, você está em não-conformidade.

**Snippet GTM (template padrão):**

```html
<!-- Default (carregado antes do consent) -->
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('consent', 'default', {
    'ad_storage': 'denied',
    'analytics_storage': 'denied',
    'ad_user_data': 'denied',
    'ad_personalization': 'denied',
    'wait_for_update': 500
  });
</script>

<!-- Google Tag Manager + GA4 + Google Ads -->
<script>
  (function(w,d,s,l,i){...})(window,document,'script','dataLayer','GTM-XXXXX');
</script>

<!-- Quando usuário aceita (disparado pelo banner de cookies) -->
<script>
  gtag('consent', 'update', {
    'ad_storage': 'granted',
    'analytics_storage': 'granted',
    'ad_user_data': 'granted',
    'ad_personalization': 'granted'
  });
</script>
```

**Banner de cookies:** pode ser implementado via CookieScript, Cookiebot, OneTrust, ou homemade. **Mínimo:** botão "Aceitar todos" e "Rejeitar" (ambos devem funcionar).

### 1.2 Enhanced Conversions — implementação

**URL oficial:** https://support.google.com/google-ads/answer/9888656

**O que faz:** envia dados do lead (email, nome, endereço, telefone) hasheados via SHA-256 para o Google, permitindo atribuição pós-cookies.

**Por que importa:** com Privacy Sandbox descontinuando third-party cookies em 2024-2026, Enhanced Conversions é a única forma confiável de atribuir conversões offline.

**Implementação típica (GTM):**

```javascript
// Capturar dados do lead após clique WA
function gtag_report_conversion(url) {
  var callback = function () {
    if (typeof url === 'string') {
      window.location = url;
    }
  };
  gtag('event', 'conversion', {
    'send_to': 'AW-18436097662/dh4_CNvs-PAcEP6MgtdE',
    'value': 500.0,
    'currency': 'BRL',
    'transaction_id': '',
    'enhanced_conversions_data': {
      'email': getHashedEmail(),
      'phone_number': getHashedPhone(),
      'first_name': getHashedFirstName(),
      'last_name': getHashedLastName(),
      'home_address': {
        'street': getHashedStreet(),
        'city': getHashedCity(),
        'region': getHashedRegion(),
        'postal_code': getHashedPostal(),
        'country': 'BR'
      }
    }
  });
  return false;
}
```

**Hash:** usar SHA-256 normalizado (trim + lowercase). Email `joao@silva.com` → hash diferente de `JOAO@silva.com` se não normalizar.

### 1.3 Casos ANPD para clínica médica

**Caso ANPD 2024:** organização social de saúde foi processada por falha na proteção de 500 mil pacientes. **Lição:** prontuário eletrônico + base de pacientes exige governança rigorosa.

**Multa ANPD típica:**
- Advertência (1ª infração)
- Multa de 2% do faturamento OU R$ 50 milhões por infração (limite)
- Bloqueio ou eliminação dos dados
- Publicização da infração

**Boas práticas:**
- DPO (Data Protection Officer) nomeado
- RIPD (Relatório de Impacto à Proteção de Dados Pessoais) para tratamento de dado sensível
- Política de privacidade acessível e em linguagem clara
- Termo de consentimento específico para tratamento de dado de saúde
- Backup criptografado de prontuários

---

## 2. AI em Anúncios Google (AI Max + Performance Max + Demand Gen)

### 2.1 AI Max (Lançado 2025-2026)

**O que é:** extensão do Search que usa IA generativa para expandir KW semanticamente, similar a Broad Match mas com mais controle.

**Quando usar para psiquiatria:**
- ❌ NÃO recomendado (Health in Personalized Ads pode bloquear)
- Testar em paralelo com budget baixo (R$ 10-20/dia) e monitorar

**Quando usar para outras especialidades:**
- ✅ Dermatologia, odontologia, ortopedia (sem bloqueio Health grave)
- ❌ Pediatria, psiquiatria, qualquer especialidade sensível

### 2.2 Performance Max (PMax)

**O que é:** tipo de campanha que veicula em Search, Display, YouTube, Discover, Gmail, Maps simultaneamente, gerenciado por IA do Google.

**Quando usar para médico:**
- ❌ NÃO recomendado. Razões:
  - Display + YouTube podem mostrar anúncio em contextos inadequados
  - Política Health bloqueia vários assets
  - Modelo particular não tem budget para escalar PMax com confiança
  - Falta de controle sobre placement

### 2.3 Demand Gen

**O que é:** campanha focada em social/visual (YouTube, Discover, Gmail).

**Quando usar para médico:**
- ❌ NÃO recomendado. Razões: similar a PMax.

---

## 3. Privacy Sandbox 2026-2027 (Chrome)

### 3.1 O que vai mudar

**Timeline oficial (atualizada 2025-2026):**
- Google **NÃO vai descontinuar** third-party cookies (decisão revertida em 2024)
- Mas Privacy Sandbox Topics API está sendo adotada progressivamente
- Cookies ainda funcionam, mas com menos precisão

**Implicações para Google Ads médico:**
- **Enhanced Conversions** vira obrigatório (cookies menos confiáveis)
- **First-party data** (sua lista de emails, CRM) vira ainda mais importante
- **Consent Mode v2** vira padrão
- **Server-side tracking** (via GTM server) cresce

**Fonte:** https://blog.google/products-and-platforms/products/chrome/updated-timeline-privacy-sandbox-migration/

### 3.2 O que fazer agora

1. **Implementar Enhanced Conversions** (antes de Q2 2026)
2. **Server-side GTM** (avaliação técnica)
3. **Manter lista de emails de pacientes** (Customer Match, exceto para psiquiatria)
4. **Consent Mode v2** implementado com TCF v2.2

---

## 4. Schema.org Avançado para Médico

### 4.1 Tipos úteis

**MedicalClinic:** clínica física, com endereço, telefone, especialidades, médicos, avaliações.
**Physician:** médico individual, com NPI, CRM, especialidades, avaliação.
**MedicalProcedure:** procedimentos específicos (consulta, cirurgia).
**MedicalCondition:** doenças tratadas (ansiedade, TDAH, depressão).
**FAQPage:** perguntas frequentes com respostas.

### 4.2 JSON-LD para psiquiatra (modelo Dr. Guilherme)

```json
{
  "@context": "https://schema.org",
  "@type": "Physician",
  "name": "Dr. Guilherme Mota",
  "alternateName": "Dr. Guilherme",
  "image": "https://drguilhermemota.com.br/img/dr-guilherme.jpg",
  "telephone": "+55-51-98330-0503",
  "url": "https://drguilhermemota.com.br",
  "medicalSpecialty": ["Psychiatry", "ChildAndAdolescentPsychiatry"],
  "availableService": [
    {
      "@type": "MedicalProcedure",
      "name": "Consulta Psiquiátrica Online"
    },
    {
      "@type": "MedicalProcedure",
      "name": "Acompanhamento Psiquiátrico Infantojuvenil"
    }
  ],
  "address": {
    "@type": "PostalAddress",
    "addressCountry": "BR",
    "addressLocality": "Rio de Janeiro",
    "addressRegion": "RJ"
  },
  "identifier": "CRM-RJ 52.125913-0"
}
```

**Validar:** https://validator.schema.org/ ou Google Rich Results Test.

---

## 5. Integração com CRM / Prontuário (Memed + PEP)

### 5.1 Memed (receita digital)

**Integração possível:**
- Memed recebe paciente via WhatsApp
- Memed vincula lead → consulta → receita
- Webhook do Memed pode enviar evento para Google Ads como conversion offline

**Como configurar:**
- Memed → Webhook → sua URL → Google Ads Conversion Upload API

**Código exemplo:**

```python
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.v17.types import ConversionUpload

client = GoogleAdsClient.load_from_dict({...})

def upload_consultation_conversion(gclid, consultation_date, value=500.0):
    conversion = ConversionUpload.Conversion()
    conversion.gclid = gclid
    conversion.conversion_action = 'customers/559-021-2946/conversionActions/7753053787'
    conversion.conversion_date_time = consultation_date.isoformat()
    conversion.conversion_value = value
    conversion.currency_code = 'BRL'

    upload = ConversionUpload.ClickConversion()
    upload.conversion = conversion
    
    response = client.conversion_upload_service.upload_click_conversions(
        customer_id='559-021-2946',
        conversions=[upload]
    )
```

### 5.2 Prontuário Eletrônico (PEP)

**Integrações úteis:**
- PEP → Webhook → GA4 event → Google Ads conversion
- PEP → email do paciente → Customer Match (se permitido pela Health Policy)
- PEP → anamnese estruturada → tags automáticas para remarketing futuro

**Boas práticas:**
- Não enviar dados clínicos para Google Ads
- Apenas evento "consulta realizada" + valor
- Manter registro de consentimento em PEP

---

## 6. Concorrentes Akatú (análise competitiva)

### 6.1 Espaço Abra

**URL:** espacoabra.com.br
**Modelo:** clínica presencial em SP + RJ (consultório)
**Ticket:** R$ 250 (consulta)
**Posicionamento:** "Psicologia e Psiquiatria"
**Marketing:** foco em blog mensal (conteúdo SEO) + LinkedIn + Facebook
**Diferencial:** multidisciplinaridade

**Posicionamento da Akatú:** psiquiatria infantojuvenil online = mais nichado.

### 6.2 MPO Saúde

**URL:** mposaude.com.br
**Modelo:** multi-especialidade + clube de assinatura (R$ 49,90/mês)
**Ticket:** R$ 49,90/mês assinatura + R$ X por consulta
**Posicionamento:** "Saúde integrada"
**Marketing:** volume alto, Instagram + Facebook + Telepet (aplicativo próprio)

**Diferencial:** ecossistema completo.

### 6.3 Zenklub

**URL:** zenklub.com.br
**Modelo:** marketplace de psicólogos online
**Ticket:** R$ X por sessão de 50 min
**Posicionamento:** "Terapia online acessível"
**Marketing:** Google Ads agressivo (broad match em "psicólogo online")
**Diferencial:** preço competitivo

**KW em disputa:** "psicólogo online" CPC R$ 4-8 (KOP benchmark).

### 6.4 Vittude

**URL:** vittude.com
**Modelo:** terapia online + presencial
**Ticket:** R$ 80-150/sessão
**Posicionamento:** "Terapia para todos"
**Marketing:** SEO forte + Google Ads + partnerships

### 6.5 Doctoralia

**URL:** doctoralia.com.br
**Modelo:** marketplace de médicos (marketplace style)
**Ticket:** comissão sobre consulta
**Posicionamento:** "Encontre seu médico"
**Marketing:** SEO fortíssimo (autoridade de domínio alta)

### 6.6 Tese competitiva

**Para Dr. Guilherme:**
- **Nicho:** psiquiatria infantojuvenil online
- **Vs Espaço Abra:** nichado, não multidisciplinar
- **Vs MPO:** especializado, não assinatura
- **Vs Zenklub:** psiquiatra (não psicólogo), CRM/RQE visível
- **Vs Vittude:** foco em psiquiatria, não terapia
- **Vs Doctoralia:** não dependemos de marketplace (autoridade própria)

**Janela competitiva:** pouca concorrência paga em "psiquiatra infantil online" (apenas Espaço Abra com blog orgânico).

---

## 7. Estratégia de Conteúdo (blog para SEO + LP)

### 7.1 Estrutura de blog médico CFM-compliant

**Permitido (CFM 2.336/2023 Art. 5):**
- Conteúdo educativo
- Esclarecimento de dúvidas
- Informação sobre doenças, sintomas, tratamentos
- Apresentação do médico/especialidade

**Vedado:**
- Antes/depois (mesmo com contexto educativo)
- Promessa de resultado
- Imagem de paciente sem consentimento específico

### 7.2 Tópicos para a Akatú (10 ideias)

1. "Como escolher um psiquiatra infantil" (topo de funil)
2. "Sinais de TDAH em adolescentes" (meio de funil)
3. "Quando procurar ajuda para ansiedade em crianças" (meio)
4. "Psicoterapia online funciona para crianças?" (meio)
5. "O que esperar da primeira consulta psiquiátrica" (fundo)
6. "Diferença entre psicólogo e psiquiatra infantil" (topo)
7. "Saúde mental na adolescência: o que pais precisam saber" (topo)
8. "Transtornos de ansiedade em adolescentes: como tratar" (meio)
9. "Como a família participa do tratamento" (fundo)
10. "Burnout em adolescentes: sinais e prevenção" (meio)

### 7.3 Cronograma

- 2 posts/mês no blog
- Cada post: ~1.500 palavras
- Tópicos: 50% topo de funil, 30% meio, 20% fundo
- Linkagem interna para LP principal

---

## 8. Resumo Executivo

**O que muda em 2026-2027:**
- Enhanced Conversions vira obrigatório
- Privacy Sandbox Topics API cresce
- LGPD enforcement mais rigoroso (ANPD multando clínicas)
- Customer Match bloqueado para saúde mental

**O que NÃO muda:**
- CFM 2.336/2023 (vigente)
- Compliance via CRM/RQE + "atendimento por telemedicina"
- Benchmarks CPC/CPA (Wordstream 2026 ainda referência)

**Recomendações de curto prazo:**
1. Implementar Consent Mode v2 (4-8h TI)
2. Implementar Enhanced Conversions (2-4h TI)
3. Criar Schema.org Physician para o site (4-6h)
4. Configurar Memed webhook para Google Ads Conversion Upload (8h)
5. Escrever 10 posts de blog (20h conteúdo)

---

*Documento complementar aos 9 docs existentes. Total do projeto Google Ads médico: ~395 KB.*