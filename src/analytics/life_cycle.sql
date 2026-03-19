-- Seleciona quais dias cada cliente esteve ativo
WITH tb_daily AS (

    SELECT DISTINCT
        idCliente,
        DATE(DtCriacao) as dtDia
    FROM transacoes

    -- Considera apenas histórico anterior à data de referência 
    WHERE dtDia < '{date}'

),

-- Calcula tabela com a Recência e Idade na base
tb_idade AS (

    SELECT idCliente,
           CAST(JULIANDAY('{date}') - JULIANDAY(min(dtDia)) AS INT) AS qtdeDiasPrimTransacao,
           CAST(JULIANDAY('{date}') - JULIANDAY(max(dtDia)) AS INT) AS qtdeDiasUltimaAtivacao
    FROM tb_daily
    
    GROUP BY idCliente
),

-- Tabela auxiliar para calcular a quantidade de dias desde a penúltima transação
tb_rn AS (
  
    SELECT *,
           -- Enumera ativações por cliente para permitir extração da última linha 
           ROW_NUMBER() OVER (PARTITION BY idCliente ORDER BY dtDia DESC) AS rnDia
    FROM tb_daily

),

-- Calcula a Recência desde a penúltima ativação 
tb_penultima_ativacao AS (

    SELECT *,
           CAST(JULIANDAY('{date}') - JULIANDAY(dtDia) AS INT) AS qtdeDiasPenultimaAtivacao
    FROM tb_rn
    
    WHERE rnDia = 2

),

-- Classifica clients em estágios do ciclo de vida com base na Recência
tb_life_cycle AS (
    
    SELECT t1.*,
           t2.qtdeDiasPenultimaAtivacao,
           
           -- Regras de classificação do ciclo de vida:
           CASE
               WHEN t1.qtdeDiasPrimTransacao <= 7 THEN 
                        '01-CURIOSO'
                
               WHEN t1.qtdeDiasUltimaAtivacao <= 7 
               AND t2.qtdeDiasPenultimaAtivacao - t1.qtdeDiasUltimaAtivacao <= 14 THEN 
                        '02-FIEL'
                
               WHEN t1.qtdeDiasUltimaAtivacao BETWEEN 8 AND 14 THEN 
                        '03-TURISTA'
                
               WHEN t1.qtdeDiasUltimaAtivacao BETWEEN 15 AND 28 THEN 
                        '04-DESENCANTADO'
                
               WHEN t1.qtdeDiasUltimaAtivacao > 28 THEN 
                        '05-ZUMBI' 
                
               WHEN t1.qtdeDiasUltimaAtivacao <= 7 
               AND t2.qtdeDiasPenultimaAtivacao - t1.qtdeDiasUltimaAtivacao BETWEEN 15 AND 27 THEN 
                        '02-RECONQUISTADO'
                
               WHEN t1.qtdeDiasUltimaAtivacao <= 7 
               AND t2.qtdeDiasPenultimaAtivacao - t1.qtdeDiasUltimaAtivacao >= 28 THEN
                        '02-REBORN'
           END AS descLifeCycle
    
    FROM tb_idade AS t1

    LEFT JOIN tb_penultima_ativacao AS t2
        ON t1.idCliente = t2.idCliente

),

-- Calcula métricas de Frequência e Valor em janela móvel de 28 dias 
tb_freq_valor AS (
    
    SELECT idCliente,
           -- Frequência: números de dias ativos na janela
           COUNT(DISTINCT DATE(DtCriacao)) AS qtdeFrequencia,
        
           -- Valor: quantidade de pontos positivos na janela
           SUM(
               CASE 
                    WHEN qtdePontos > 0 THEN qtdePontos
                    ELSE 0 
               END
           ) AS qtdePontosPos

    FROM transacoes

    -- Define janela móvel de 28 dias anterior a data de referência
    WHERE DtCriacao < '{date}'
    AND DtCriacao >= date('{date}', '-28 day')

    GROUP BY idCliente

    ORDER BY qtdeFrequencia DESC

),

-- Segmentação dos usuários com base em Frequência e Valor (inspirado na RFV)
tb_cluster AS (
        SELECT *,

               -- Regras manuais definidas a partir da distribuição observada
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

-- Consolida ciclo de vida e segmentação RFV 
tb_join AS(

    SELECT DATE('{date}', '-1 day') AS dtRef,
           t1.*,
           t2.qtdeFrequencia,
           t2.qtdePontosPos,
           t2.cluster
    FROM tb_life_cycle AS t1
    
    LEFT JOIN tb_cluster AS t2
        ON t1.idCliente = t2.idCliente
)

SELECT * 
FROM tb_join