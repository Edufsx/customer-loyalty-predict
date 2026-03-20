-- Remove a tabela anterior para evitar conflito na recriação
DROP TABLE IF EXISTS abt_fiel;

-- Criação da Tabela Base Analítica (ABT) utilizada no Treino do Modelo
CREATE TABLE IF NOT EXISTS abt_fiel AS

-- Prepara amostragem aleatória de cada cliente e define variável target
WITH tb_join AS (
    
    SELECT t1.dtRef,
           t1.idCliente,
           t1.descLifeCycle,
           t2.descLifeCycle,
           
           -- Target: Cliente será fiel depois de 28 dias? Se sim, atribui 1
           CASE 
               WHEN t2.descLifeCycle = '02-FIEL' THEN 1 
               ELSE 0
           END AS flFiel,
           
           -- Ordena linhas aleatoriamente por cliente (amostragem aleatória das datas)
           ROW_NUMBER() OVER (PARTITION BY t1.idCliente ORDER BY RANDOM()) AS randomCol

    FROM life_cycle AS t1

    LEFT JOIN life_cycle AS t2
        ON t1.idCliente = t2.idCliente
    AND DATE(t1.dtRef, '+28 day') = DATE(t2.dtRef)

    -- Filtra período para seleção da amostra 
    WHERE((t1.dtRef >= '2024-03-01' AND t1.dtRef <= '2025-09-01') 
            OR t1.dtRef = '2025-10-01' 
            OR t1.dtRef = '2025-11-01'
            OR t1.dtRef = '2025-12-01')
    -- Remove clientes zumbi para não distorcer o modelo de predições
    AND t1.descLifeCycle <> '05-ZUMBI'

),

-- Realiza amostragem aleatória das datas, selecionando duas datas por cliente
tb_cohort AS (

    SELECT dtRef,
           idCliente,
           flFiel
    FROM tb_join
   
    WHERE randomCol <= 2
    
    ORDER BY idCliente, dtRef

),

/*
Agrega todas as features dos clientes nas datas da amostragem aleatória:
- Features Transacionais;
- Features relacionadas ao Ciclo de Vida;
- Features relacionadas à Plataforma de Cursos.
*/
abt_final AS (
SELECT t1.*,
       t2.idadeDias,
       t2.qtdeAtivacaoVida,
       t2.qtdeAtivacaoD7,
       t2.qtdeAtivacaoD14,
       t2.qtdeAtivacaoD28,
       t2.qtdeAtivacaoD56,
       t2.qtdeTransacaoVida,
       t2.qtdeTransacaoD7,
       t2.qtdeTransacaoD14,
       t2.qtdeTransacaoD28, 
       t2.qtdeTransacaoD56,
       t2.saldoVida,
       t2.saldoD7,
       t2.saldoD14,
       t2.saldoD28,
       t2.saldoD56,
       t2.qtdePontosPosVida,
       t2.qtdePontosPosD7,
       t2.qtdePontosPosD14,
       t2.qtdePontosPosD28,
       t2.qtdePontosPosD56, 
       t2.qtdePontosNegVida,
       t2.qtdePontosNegD7,
       t2.qtdePontosNegD14,
       t2.qtdePontosNegD28,
       t2.qtdePontosNegD56,
       t2.qtdeTransacaoManha,
       t2.qtdeTransacaoTarde,
       t2.qtdeTransacaoNoite,
       t2.pctTransacaoManha, 
       t2.pctTransacaoTarde, 
       t2.pctTransacaoNoite, 
       t2.qtdeTransacaoDiaVida, 
       t2.qtdeTransacaoDiaD7, 
       t2.qtdeTransacaoDiaD14, 
       t2.qtdeTransacaoDiaD28, 
       t2.qtdeTransacaoDiaD56, 
       t2.pctAtivacaoMAU, 
       t2.qtdeHorasVida,
       t2.qtdeHorasD7,
       t2.qtdeHorasD14,
       t2.qtdeHorasD28,
       t2.qtdeHorasD56,
       t2.avgIntervaloDiasVida,
       t2.avgIntervaloDiasD28,
       t2.qtdeChatMessage,
       t2.qtdeAirflowLover,
       t2.qtdeRLover,
       t2.qtdeListaPresenca,
       t2.qtdePresencaStreak,
       t2.qtdeTrocaDePontosStreamElements,
       t2.qtdeReembolsoTrocaDePontosStreamElements,
       t2.qtdeRpg,
       t2.qtdeChurnModel,
       t3.qtdeFrequencia,
       t3.descLifeCycleAtual,
       t3.descClusterAtual,
       t3.descLifeCycleD28,
       t3.descClusterD28,
       t3.pctCurioso,
       t3.pctFiel,
       t3.pctTurista,
       t3.pctDesencantado,
       t3.pctZumbi,
       t3.pctReconquistado,
       t3.pctReborn,
       t3.avgFreqGrupo, 
       t3.ratioFreqGrupo,
       t4.qtdeCursosCompletos,
       t4.qtdeCursosIncompletos,
       t4.carreira,
       t4.coletaDados2024,
       t4.dsDatabricks2024,
       t4.dsPontos2024,
       t4.estatistica2024,
       t4.estatistica2025,
       t4.github2024,
       t4.github2025,
       t4.go2026,
       t4.iaCanal2025,
       t4.lagoMago2024,
       t4.loyaltyPredict2025 ,
       t4.machineLearning2025,
       t4.matchmakingTramparDeCasa2024,
       t4.ml2024,
       t4.mlflow2025,
       t4.nekt2025,
       t4.pandas2024,
       t4.pandas2025,
       t4.plataformaMl2026,
       t4.python2024,
       t4.python2025,
       t4.speedF1,
       t4.sql2020,
       t4.sql2025,
       t4.streamlit2025,
       t4.tramparLakehouse2024,
       t4.tseAnalytics2024,
       t4.qtdDiasUltimaAtiv 

FROM tb_cohort AS t1

LEFT JOIN fs_transacional AS t2
    ON t1.idCliente = t2.idCliente
AND t1.dtRef = t2.dtRef

LEFT JOIN fs_life_cycle AS t3
    ON t1.idCliente = t3.idCliente
AND t1.dtRef = t3.dtRef

LEFT JOIN fs_education AS t4
    ON t1.idCliente = t4.idCliente
AND t1.dtRef = t4.dtRef
)

SELECT *
FROM abt_final;