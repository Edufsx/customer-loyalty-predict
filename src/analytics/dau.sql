-- DAU: Daily Active Users

-- Seleciona uma coluna que contém apenas a data 
SELECT DATE(DtCriacao) as dtDia,

       -- Conta clientes distintos em uma data (DAU) 
       COUNT(DISTINCT idCliente) as DAU

-- Define a consulta na tabela transacoes 
FROM transacoes

-- Agrupa pela data
GROUP BY dtDia

-- Ordena pela data na ordem ascendente
ORDER BY dtDia