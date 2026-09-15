/**
 * Google Ads Script - Agendamento de anuncios
 * Campanha: Psiquiatria Infantil 1.0
 * Criado em: 12/set/2026
 *
 * O QUE FAZ:
 *   Substitui toda a programacao de horarios da campanha por:
 *     - Dias ativos: quarta, sexta, sabado (agenda real de setembro/26)
 *     - Janelas de alta probabilidade: 06h-09h, 12h-14h, 20h-23h
 *     - Total: 8h/dia x 3 dias = 24h/semana (contra 72h se rodasse 24/7)
 *
 * COMO RODAR (uma vez):
 *   1. ads.google.com -> login
 *   2. Menu lateral -> Acoes em massa -> Scripts
 *   3. Botao + (Novo script) -> apagar tudo -> colar este codigo
 *   4. Autorizar quando pedir
 *   5. Clicar em VISUALIZAR (nao altera nada, so mostra o que faria)
 *   6. Conferir o log -> se estiver certo, clicar em EXECUTAR
 *
 * COMO AGENDAR (opcional, para rodar sozinho):
 *   Na tela do script -> Frequencia -> escolher "Uma vez" ou mensal.
 *
 * ATENCAO:
 *   O script REMOVE toda a programacao existente antes de aplicar a nova.
 *   Rodar de novo em outubro com a lista de dias atualizada e o correto.
 *
 * OUTUBRO/26: adicionar 'MONDAY' na lista DIAS_ATIVOS (segunda de manha).
 */

function main() {

  // ---------------------------------------------------------------
  // CONFIGURACOES - mexer aqui
  // ---------------------------------------------------------------
  var NOME_CAMPANHA = 'Psiquiatria Infantil 1.0';

  // Dias da semana com atendimento.
  // Setembro/26: quarta, sexta, sabado
  // Outubro/26:  adicionar 'MONDAY'
  var DIAS_ATIVOS = ['WEDNESDAY', 'FRIDAY', 'SATURDAY'];

  // Janelas de horario (hora_inicio, min_inicio, hora_fim, min_fim)
  // Baseado na tabela de probabilidade de clique qualificado (>=4 estrelas)
  var JANELAS = [
    [ 6, 0,  9, 0],   // manha   - responsavel pesquisa antes do trabalho
    [12, 0, 14, 0],   // almoco  - celular na mao, decisao emocional
    [20, 0, 23, 0]    // noite   - pico real, apos a crianca dormir
  ];

  // ---------------------------------------------------------------
  // NAO PRECISA MEXER DAQUI PRA BAIXO
  // ---------------------------------------------------------------
  var campanhas = AdsApp.campaigns()
    .withCondition("Name = '" + NOME_CAMPANHA + "'")
    .get();

  var encontrou = false;

  while (campanhas.hasNext()) {
    encontrou = true;
    var campanha = campanhas.next();

    Logger.log('Campanha encontrada: ' + campanha.getName());

    // 1. Limpa a programacao atual
    var antigos = campanha.targeting().adSchedules().get();
    var removidos = 0;
    while (antigos.hasNext()) {
      antigos.next().remove();
      removidos++;
    }
    Logger.log('Blocos de horario removidos: ' + removidos);

    // 2. Aplica a nova programacao
    var adicionados = 0;
    for (var d = 0; d < DIAS_ATIVOS.length; d++) {
      for (var j = 0; j < JANELAS.length; j++) {
        var w = JANELAS[j];
        campanha.addAdSchedule(DIAS_ATIVOS[d], w[0], w[1], w[2], w[3]);
        adicionados++;
        Logger.log('  + ' + DIAS_ATIVOS[d] + ' ' +
                   pad(w[0]) + ':' + pad(w[1]) + '-' + pad(w[2]) + ':' + pad(w[3]));
      }
    }
    Logger.log('Blocos de horario adicionados: ' + adicionados);
  }

  if (!encontrou) {
    Logger.log('ERRO: nenhuma campanha encontrada com o nome "' + NOME_CAMPANHA + '".');
    Logger.log('Confira o nome exato em Campanhas (pode ter espaco ou acento diferente).');
  } else {
    Logger.log('Concluido com sucesso.');
  }
}

function pad(n) {
  return (n < 10 ? '0' : '') + n;
}
