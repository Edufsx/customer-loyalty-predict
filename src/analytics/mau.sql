WITH tb_daily AS (
    
    SELECT DISTINCT
        date(substr(DtCriacao, 0, 11)) AS dtDia,
        idCliente
    FROM transacoes
    ORDER BY dtDia
),

tb_distinct_day AS (
    SELECT 
            DISTINCT dtDia AS dtRef
    FROM tb_daily
)

SELECT t1.dtRef,
        count(DISTINCT idCliente) AS MAU,
        count(DISTINCT t2.dtDia) AS qtdDias
FROM tb_distinct_day AS t1

LEFT JOIN tb_daily AS t2
-- dtRef é meu dia 0
ON  t2.dtDia <= t1.dtRef
-- Por isso não é maior ou igual a 28
AND julianday(t1.dtRef) - julianday(t2.dtDia) < 28

GROUP BY t1.dtRef

ORDER BY t1.dtRef ASC