-- Características (features) dos clientes relacionadas ao ciclo de vida

-- Frequência e Ciclo de Vida com cluster dos clientes em uma determinada data
WITH tb_life_cycle_atual AS (

    SELECT idCliente,
           qtdeFrequencia,
           descLifeCycle AS descLifeCycleAtual,
           cluster AS descClusterAtual 
    FROM life_cycle

    -- Filtra as informações considerando a data de referência
    WHERE dtRef = DATE('{date}', '-1 day')

),

-- Ciclo de vida dos clientes em uma janela móvel de 28 dias
tb_life_cycle_D28 AS (
    
    SELECT idCliente,
           descLifeCycle AS descLifeCycleD28,
           cluster AS descClusterD28
    FROM life_cycle

    WHERE dtRef = DATE('{date}', '-29 day')

),

-- Calcula o percentual que cada cliente passou nos estados do Ciclo de Vida
tb_share_ciclos AS (
 
    SELECT idCliente,
    
           1. * SUM(
                    CASE
                        WHEN descLifeCycle = '01-CURIOSO' THEN 1 
                        ELSE 0 
                    END
                ) / COUNT(*) AS pctCurioso,
          
           1. * SUM(
                    CASE
                        WHEN descLifeCycle = '02-FIEL' THEN 1 
                        ELSE 0 
                    END
                ) / COUNT(*) AS pctFiel,
          
           1. * SUM(
                    CASE
                        WHEN descLifeCycle = '03-TURISTA' THEN 1 
                        ELSE 0 
                    END
                ) / COUNT(*) AS pctTurista,
          
           1. * SUM(
                    CASE
                        WHEN descLifeCycle = '04-DESENCANTADO' THEN 1 
                        ELSE 0 
                    END
                ) / COUNT(*) AS pctDesencantado,
                    
           1. * SUM(
                    CASE
                        WHEN descLifeCycle = '05-ZUMBI' THEN 1 
                        ELSE 0 
                    END
                ) / COUNT(*) AS pctZumbi,
           
           1. * SUM(
                    CASE 
                        WHEN descLifeCycle = '02-RECONQUISTADO' THEN 1 
                        ELSE 0 
                    END
                ) / COUNT(*) AS pctReconquistado,
           
           1. * SUM(
                    CASE 
                        WHEN descLifeCycle = '02-REBORN' THEN 1 
                        ELSE 0 
                    END
                ) / COUNT(*) AS pctReborn
    
    FROM life_cycle

    WHERE dtRef < '{date}'

    GROUP BY idCliente

),

-- Calcula a média da Frequência de cada Grupo 
tb_avg_cycle AS (

    SELECT descLifeCycleAtual,
           AVG(qtdeFrequencia) AS avgFreqGrupo
    FROM tb_life_cycle_atual

    GROUP BY descLifeCycleAtual

),

-- Consolida as características (features) dos clientes
tb_join AS (
    SELECT t1.idCliente,
           t1.qtdeFrequencia,
           t1.descLifeCycleAtual,
           t1.descClusterAtual, 
           t2.descLifeCycleD28,
           t2.descClusterD28,
           t3.pctCurioso,
           t3.pctFiel,
           t3.pctTurista,
           t3.pctDesencantado,
           t3.pctZumbi,
           t3.pctReconquistado,
           t3.pctReborn,
           t4.avgFreqGrupo,
           -- Calcula a razão entre as frequência do cliente e do grupo
           1. * t1.qtdeFrequencia / t4.avgFreqGrupo AS ratioFreqGrupo

    FROM tb_life_cycle_atual AS t1

    LEFT JOIN tb_life_cycle_D28 AS t2
        ON t1.idCliente = t2.idCliente

    LEFT JOIN tb_share_ciclos AS t3
        ON t1.idCliente = t3.idCliente

    LEFT JOIN tb_avg_cycle AS t4
        ON t1.descLifeCycleAtual = t4.descLifeCycleAtual
)

-- Marca a data de Referência e seleciona as features dos clientes
SELECT DATE('{date}', '-1 day') AS dtRef,
       *
FROM tb_join

