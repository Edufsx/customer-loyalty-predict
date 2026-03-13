-- MAU: Monthly Active Users
-- Como aumentar o MAU? 
    -- 1. Trazer mais gente, adianta se o balde estiver furado?
    -- 2. Reter as pessoas que vem (Segurar o Churn)

-- 28 Dias pq são exatamente 4 semanas
-- No final de semana fica mais cagado

SELECT substr(DtCriacao, 0, 8) as dtMes,
        count(DISTINCT idCliente) as MAU
FROM transacoes
GROUP BY 1
ORDER BY dtMes