-- Características (features) transacionais dos clientes

-- Prepara base de transações adicionando a granularidade diária e horária para análises temporais
WITH tb_transacao AS (

    SELECT *,
           DATE(DtCriacao) AS dtDia,
           CAST(STRFTIME('%H', DtCriacao) AS INT) -3 AS dtHora
    FROM transacoes
    WHERE dtCriacao < '{date}'
),

/* 
Agrega features dos clientes:
- Idade na base
- Atividade e volume transacional em múltiplas janelas (D7, D14, D28, D56 e vida)
- Métricas de saldo e pontos (positivos e negativos)
- Distribuição temporal e percentual das transações (manhã, tarde e noite)
*/
tb_agg_transacao AS (
    
    SELECT idCliente,

           -- Calcula a idade na base
           MAX(julianday('{date}') - julianday(DtCriacao)) AS idadeDias,

            -- Atividade do cliente: número de dias com transações em diferentes janelas temporais
           COUNT(DISTINCT dtDia) AS qtdeAtivacaoVida,
           
           COUNT(DISTINCT 
                         CASE 
                             WHEN dtDia >= DATE('{date}', '-7 day') THEN dtDia 
                         END
           ) AS qtdeAtivacaoD7,

           COUNT(DISTINCT 
                         CASE 
                              WHEN dtDia >= DATE('{date}', '-14 day') THEN dtDia
                         END
           ) AS qtdeAtivacaoD14,

           COUNT(DISTINCT 
                         CASE 
                              WHEN dtDia >= DATE('{date}', '-28 day')THEN dtDia
                         END
           ) AS qtdeAtivacaoD28,

           COUNT(DISTINCT 
                         CASE 
                              WHEN dtDia >= DATE('{date}', '-56 day') THEN dtDia
                         END
           ) AS qtdeAtivacaoD56,

           -- Volume transacional: quantidade de transações por janela temporal 
           COUNT(DISTINCT IdTransacao) AS qtdeTransacaoVida,

           COUNT(DISTINCT 
                         CASE 
                              WHEN dtDia >= DATE('{date}', '-7 day') THEN IdTransacao
                         END
           ) AS qtdeTransacaoD7,

           COUNT(DISTINCT 
                         CASE 
                              WHEN dtDia >= DATE('{date}', '-14 day') THEN IdTransacao
                         END
                ) AS qtdeTransacaoD14,

           COUNT(DISTINCT 
                         CASE 
                              WHEN dtDia >= DATE('{date}', '-28 day') THEN IdTransacao
                         END
           ) AS qtdeTransacaoD28,

           COUNT(DISTINCT 
                         CASE 
                              WHEN dtDia >= DATE('{date}', '-56 day') THEN IdTransacao
                         END
           ) AS qtdeTransacaoD56,

           -- Saldo de pontos (ganhos - gastos) em diferentes janelas temporais
           SUM(qtdePontos) AS saldoVida,
           
           SUM(
                CASE 
                    WHEN dtDia >= DATE('{date}', '-7 day') THEN qtdePontos 
                    ELSE 0 
                END
           ) AS saldoD7,

           SUM(
                CASE 
                    WHEN dtDia >= DATE('{date}', '-14 day') THEN qtdePontos 
                    ELSE 0 
                END
           ) AS saldoD14,

           SUM(
                CASE 
                    WHEN dtDia >= DATE('{date}', '-28 day') THEN qtdePontos 
                    ELSE 0 
                END
           ) AS saldoD28,

           SUM(
                CASE 
                    WHEN dtDia >= DATE('{date}', '-56 day') THEN qtdePontos 
                    ELSE 0 
                END
           ) AS saldoD56,

           -- Pontos positivos acumulados por janela temporal
           SUM(
                CASE 
                    WHEN qtdePontos > 0 THEN qtdePontos 
                    ELSE 0 
                END
           ) AS qtdePontosPosVida,
           
           SUM(
                CASE 
                    WHEN dtDia >= DATE('{date}', '-7 day') AND qtdePontos > 0 THEN qtdePontos 
                    ELSE 0
                END
           ) AS qtdePontosPosD7,
           
           SUM(
                CASE 
                    WHEN dtDia >= DATE('{date}', '-14 day') AND qtdePontos > 0 THEN qtdePontos 
                    ELSE 0
                END
           ) AS qtdePontosPosD14,
           
           SUM(
                CASE 
                    WHEN dtDia >= DATE('{date}', '-28 day') AND qtdePontos > 0 THEN qtdePontos 
                    ELSE 0
                END
           ) AS qtdePontosPosD28,
           
           SUM(
                CASE 
                    WHEN dtDia >= DATE('{date}', '-56 day') AND qtdePontos > 0 THEN qtdePontos 
                    ELSE 0
                END
           ) AS qtdePontosPosD56,
 
           -- Pontos gastos em cada janela temporal
           SUM(
                CASE 
                    WHEN qtdePontos < 0 THEN qtdePontos 
                    ELSE 0 
                END
           ) AS qtdePontosNegVida,
           
           SUM(
               CASE 
                   WHEN dtDia >= DATE('{date}', '-7 day') AND qtdePontos < 0 THEN qtdePontos
                   ELSE 0
                END
           ) AS qtdePontosNegD7,

           SUM(
               CASE 
                   WHEN dtDia >= DATE('{date}', '-14 day') AND qtdePontos < 0 THEN qtdePontos
                   ELSE 0
                END
           ) AS qtdePontosNegD14,

           SUM(
               CASE 
                   WHEN dtDia >= DATE('{date}', '-28 day') AND qtdePontos < 0 THEN qtdePontos
                   ELSE 0
                END
           ) AS qtdePontosNegD28,

           SUM(
               CASE 
                   WHEN dtDia >= DATE('{date}', '-56 day') AND qtdePontos < 0 THEN qtdePontos
                   ELSE 0
                END
           ) AS qtdePontosNegD56,
           
           -- Distribuição das transações por período do dia (manhã, tarde e noite)
           COUNT(
                 CASE 
                     WHEN dtHora BETWEEN 7 AND 11 THEN IdTransacao 
                 END
           ) AS qtdeTransacaoManha,
           
           COUNT(
                 CASE 
                     WHEN dtHora BETWEEN 12 AND 18 THEN IdTransacao 
                 END
           ) AS qtdeTransacaoTarde,
           
           COUNT(
                 CASE 
                     WHEN dtHora > 18 OR dtHora < 7 THEN IdTransacao 
                 END
           ) AS qtdeTransacaoNoite,
           
           -- Proporção de transações por período do dia
           1. * COUNT(
                      CASE
                          WHEN dtHora BETWEEN 7 AND 11 THEN IdTransacao
                      END
           ) / COUNT(IdTransacao) AS pctTransacaoManha,

           1. * COUNT(
                      CASE
                          WHEN dtHora BETWEEN 12 AND 18 THEN IdTransacao
                      END
           ) / COUNT(IdTransacao) AS pctTransacaoTarde,

           1. * COUNT(
                      CASE
                          WHEN dtHora > 18 OR dtHora < 7 THEN IdTransacao
                      END
           ) / COUNT(IdTransacao) AS pctTransacaoNoite
           
    FROM tb_transacao

    GROUP BY idCliente

),

/* 
Média de transações por dia ativo (Vida, D7, D14, D28, D56) 
% de dias ativos em D28 (Contribuição para o MAU)
*/
tb_agg_calc AS (

    SELECT *,
           -- Coalesce: Escolhe 1º argumento que não for nulo (quando for nulo, preenche com 0) 
           COALESCE(1. * qtdeTransacaoVida / qtdeAtivacaoVida, 0) AS qtdeTransacaoDiaVida,
           COALESCE(1. * qtdeTransacaoD7  / qtdeAtivacaoD7, 0) AS qtdeTransacaoDiaD7,
           COALESCE(1. * qtdeTransacaoD14 / qtdeAtivacaoD14, 0) AS qtdeTransacaoDiaD14,
           COALESCE(1. * qtdeTransacaoD28 / qtdeAtivacaoD28, 0) AS qtdeTransacaoDiaD28,
           COALESCE(1. * qtdeTransacaoD56 / qtdeAtivacaoD56, 0) AS qtdeTransacaoDiaD56,

           COALESCE(1. * qtdeAtivacaoD28 / 28, 0) AS pctAtivacaoMAU
    
    FROM tb_agg_transacao

),

-- Horas assistidas de cada transmissão ao vivo por cliente
tb_horas_dia AS (

    SELECT idCliente,
           dtDia,
           24 * (MAX(julianday(DtCriacao)) - MIN(julianday(DtCriacao))) AS duracao

    FROM tb_transacao
  
    GROUP BY idCliente, dtDia

),

-- Total de horas assistidas em diferentes janelas temporais (Vida, D7, D14, D28, D56) 
tb_hora_cliente AS (
    
    SELECT idCliente,

           SUM(duracao) AS qtdeHorasVida,
    
           SUM(
               CASE 
                   WHEN dtDia >= DATE('{date}', '-7 day') THEN duracao 
                   ELSE 0
                END
           ) AS qtdeHorasD7,

           SUM(
               CASE 
                   WHEN dtDia >= DATE('{date}', '-14 day') THEN duracao 
                   ELSE 0
                END
           ) AS qtdeHorasD14,

           SUM(
               CASE 
                   WHEN dtDia >= DATE('{date}', '-28 day') THEN duracao 
                   ELSE 0
                END
           ) AS qtdeHorasD28,

           SUM(
               CASE 
                   WHEN dtDia >= DATE('{date}', '-56 day') THEN duracao 
                   ELSE 0
                END
           ) AS qtdeHorasD56
           
    FROM tb_horas_dia
    
    GROUP BY idCliente

),

-- Tabela auxiliar para calcular o intervalo médio entre as transações de um cliente
tb_lag_dia AS (

    SELECT idCliente,
           dtDia,
           -- Cria uma coluna com o dia anterior em que o usuário esteve ativo
           LAG(dtDia) OVER (PARTITION BY idCliente ORDER BY dtDia) AS lagDia

    FROM tb_horas_dia
),

-- Calcula quantos dias, em média, um cliente demora para realizar novamente uma transação (Vida, D28)
tb_intervalo_dias AS (
    
    SELECT idCliente,
           AVG(julianday(dtDia) - julianday(lagDia)) AS avgIntervaloDiasVida,
           
           AVG(
                CASE 
                    WHEN dtDia >= DATE('{date}', '-28 day') THEN julianday(dtDia) - julianday(lagDia) 
                END
           ) AS avgIntervaloDiasD28

    FROM tb_lag_dia

    GROUP BY idCliente

),

-- % que cada produto representa das compras de cada cliente
tb_share_produtos AS (
    
    SELECT idCliente,

           1. * COUNT(
                      CASE
                          WHEN DescNomeProduto = 'ChatMessage' THEN t1.IdTransacao 
                      END
           ) / COUNT(t1.IdTransacao) AS qtdeChatMessage,
           
           1. * COUNT(
                      CASE
                          WHEN DescNomeProduto = 'Airflow Lover' THEN t1.IdTransacao 
                      END
           ) / COUNT(t1.IdTransacao) AS qtdeAirflowLover,
           
           1. * COUNT(
                      CASE
                          WHEN DescNomeProduto = 'R Lover' THEN t1.IdTransacao 
                      END
           ) / COUNT(t1.IdTransacao) AS qtdeRLover,
           
           1. * COUNT(
                      CASE
                          WHEN DescNomeProduto = 'Lista de presença' THEN t1.IdTransacao 
                      END
           ) / COUNT(t1.IdTransacao) AS qtdeListaPresenca,
           
           1. * COUNT(
                      CASE
                          WHEN DescNomeProduto = 'Presença Streak' THEN t1.IdTransacao 
                      END
           ) / COUNT(t1.IdTransacao) AS qtdePresencaStreak,
           
           1. * COUNT(
                      CASE
                          WHEN DescNomeProduto = 'Troca de Pontos StreamElements' THEN t1.IdTransacao 
                      END
           ) / COUNT(t1.IdTransacao) AS qtdeTrocaDePontosStreamElements,
           
           1. * COUNT(
                      CASE
                          WHEN DescNomeProduto = 'Reembolso: Troca de Pontos StreamElements' THEN t1.IdTransacao 
                      END
           ) / COUNT(t1.IdTransacao) AS qtdeReembolsoTrocaDePontosStreamElements,
           
           1. * COUNT(
                      CASE
                          WHEN DescCategoriaProduto = 'rpg' THEN t1.IdTransacao 
                      END
           ) / COUNT(t1.IdTransacao) AS qtdeRpg,

           1. * COUNT(
                      CASE
                          WHEN DescCategoriaProduto = 'churn-model' THEN t1.IdTransacao 
                      END
           ) / COUNT(t1.IdTransacao) AS qtdeChurnModel

    FROM tb_transacao AS t1

    LEFT JOIN transacao_produto AS t2
        ON t1.IdTransacao = t2.IdTransacao

    LEFT JOIN produtos AS t3
        ON t2.IdProduto = t3.IdProduto 

    GROUP BY idCliente

),

-- Consolida as características (features) transacionais dos clientes  
tb_join AS (
    SELECT t1.*,
           t2.qtdeHorasVida,
           t2.qtdeHorasD7,
           t2.qtdeHorasD14,
           t2.qtdeHorasD28,
           t2.qtdeHorasD56,
           t3.avgIntervaloDiasVida,
           t3.avgIntervaloDiasD28,
           t4.qtdeChatMessage,
           t4.qtdeAirflowLover,
           t4.qtdeRLover,
           t4.qtdeListaPresenca,
           t4.qtdePresencaStreak,
           t4.qtdeTrocaDePontosStreamElements,
           t4.qtdeReembolsoTrocaDePontosStreamElements,
           t4.qtdeRpg,
           t4.qtdeChurnModel

    FROM tb_agg_calc AS t1

    LEFT JOIN tb_hora_cliente AS t2
        ON t1.idCliente = t2.idCliente

    LEFT JOIN tb_intervalo_dias AS t3
        ON t1.idCliente = t3.idCliente

    LEFT JOIN tb_share_produtos AS t4
        ON t1.idCliente = t4.idCliente

)

-- Adiciona uma data de referência e seleciona as features dos clientes
SELECT DATE('{date}', '-1 day') AS dtRef,
       * 
FROM tb_join