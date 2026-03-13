WITH tb_freq_valor AS (
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

SELECT *
FROM tb_cluster
