-- Segmentação de Marketing

-- Idade Base 
-- Recência: qtd de dias desde a ultima interação
-- PODERIA olhar para a curva de Recência
-- CRM no marketing (Customer Relationship Management)

-- CICLO DE VIDA DO USUÁRIO
-- Curiosa < 7 (Curiosa)
-- Recência < 7 dias AND Idade Base > 7 (Fiel)
-- 7 < Recência < 15 dias AND Idade Base > 7 (Turista)
-- 15 < Recência < 28 dias AND Idade Base > 7 (Desencantado)
-- Recência > 28 dias AND Idade Base > 7 (Zumbi - Churn)
-- Desencantado -> Fiel (Reconquistado)
-- Zumbi -> Fiel (Reborn)

-- Idade Base
-- Data Última Transação
-- Data Penúltima Transação

WITH tb_daily AS (
    SELECT  DISTINCT
            idCliente,
            substr(DtCriacao, 1, 10) as dtDia
    FROM transacoes
    WHERE dtDia < "{date}"
),

tb_idade AS (
    SELECT idCliente,
            CAST(julianday('{date}') - julianday(min(dtDia)) AS INT) AS qtdeDiasPrimTransacao,
            CAST(julianday('{date}') - julianday(max(dtDia)) AS INT) AS qtdeDiasUltimaAtivacao
    FROM tb_daily
    GROUP BY idCliente
),

tb_rn AS (
    SELECT *,
            row_number() OVER (PARTITION BY idCliente ORDER BY dtDia DESC) AS rnDia
    FROM tb_daily
),

tb_penultima_ativacao AS (
    SELECT *,
            CAST(julianday('{date}') - julianday(dtDia) AS INT) AS qtdeDiasPenultimaAtivacao
    FROM tb_rn
    WHERE rnDia = 2
),

tb_life_cycle AS (
    SELECT t1.*,
            t2.qtdeDiasPenultimaAtivacao,
            CASE
                WHEN qtdeDiasPrimTransacao <= 7 THEN "01-CURIOSO"
                WHEN qtdeDiasUltimaAtivacao <= 7 AND qtdeDiasPenultimaAtivacao - qtdeDiasUltimaAtivacao <= 14 THEN "02-FIEL"
                WHEN qtdeDiasUltimaAtivacao BETWEEN 8 AND 14  THEN "03-TURISTA"
                WHEN qtdeDiasUltimaAtivacao BETWEEN 15 AND 28 THEN "04-DESENCANTADO"
                WHEN qtdeDiasUltimaAtivacao > 28 THEN "05-ZUMBI" 
                WHEN qtdeDiasUltimaAtivacao <= 7 AND qtdeDiasPenultimaAtivacao - qtdeDiasUltimaAtivacao BETWEEN 15 AND 27 THEN "02-RECONQUISTADO"
                WHEN qtdeDiasUltimaAtivacao <= 7 AND qtdeDiasPenultimaAtivacao - qtdeDiasUltimaAtivacao >= 28 THEN "02-REBORN"
            END AS descLifeCycle
    FROM tb_idade AS t1
    LEFT JOIN tb_penultima_ativacao AS t2
    ON t1.idCliente = t2.idCliente
),

tb_freq_valor AS (
        SELECT idCliente,
                count(DISTINCT substr(DtCriacao, 0, 11)) AS  qtdeFrequencia,
                sum(CASE WHEN qtdePontos > 0 THEN qtdePontos ELSE 0 END) AS qtdePontosPos
        FROM transacoes
        WHERE DtCriacao < "{date}"
        AND DtCriacao >= date("{date}", "-28 day")
        GROUP BY 1
        ORDER BY qtdeFrequencia DESC
),

tb_cluster AS (
        SELECT *,
                CASE
                        WHEN qtdeFrequencia <= 10 AND qtdePontosPos >= 1500 THEN '12-HYPERS'
                        WHEN qtdeFrequencia > 10 AND qtdePontosPos >= 1500 THEN '22-EFICIENTES'
                        WHEN qtdeFrequencia <= 10 AND qtdePontosPos >= 750 THEN '10-INDECISOS'
                        WHEN qtdeFrequencia > 10 AND qtdePontosPos >= 750 THEN '21-ESFORCADOS'
                        WHEN qtdeFrequencia < 5  THEN '00-LURKER'
                        WHEN qtdeFrequencia <= 10  THEN '01-PREGUICOSO'
                        WHEN qtdeFrequencia > 10  THEN '20-POTENCIAL'
                END AS cluster
        FROM tb_freq_valor
)


SELECT date('{date}', '-1 day') AS dtRef,
        t1.*,
        t2.qtdeFrequencia,
        t2.qtdePontosPos,
        t2.cluster
FROM tb_life_cycle AS t1
LEFT JOIN tb_cluster AS t2
ON t1.idCliente = t2.idCliente