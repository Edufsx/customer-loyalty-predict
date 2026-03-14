-- Constrói tabela com datas e usuários distintos 
WITH tb_daily_users AS (
     
    SELECT DISTINCT 
        DATE(DtCriacao) AS dtDia,
        idCliente
    FROM transacoes

),

-- Constrói tabela com todos os dias da base
tb_reference_day AS (
    
    SELECT DISTINCT 
        dtDia AS dtRef
    FROM tb_daily_users

),

-- Calcula Usuários Mensais Ativos (MAU)
tb_mau AS (

    SELECT t1.dtRef,
           -- Usuários distintos ativos nos últimos 28 dias
           COUNT(DISTINCT t2.idCliente) AS MAU,
           -- Quantidade de dias observados nos últimos 28 dias
           COUNT(DISTINCT t2.dtDia) AS qtdDias
    FROM tb_reference_day AS t1

    LEFT JOIN tb_daily_users AS t2
    ON  t2.dtDia <= t1.dtRef
    AND (JULIANDAY(t1.dtRef) - JULIANDAY(t2.dtDia)) < 28

    -- Agrupa pela data de referência
    GROUP BY t1.dtRef

)

SELECT *
FROM tb_mau
ORDER BY dtRef