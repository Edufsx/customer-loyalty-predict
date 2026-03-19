-- Verificação da Segmentação realizada dentro dos ciclos de vida
SELECT dtRef,
       descLifeCycle,
       cluster,
       -- Quantidade de clientes por segmento de cada estado do ciclo de vida
       COUNT(*) AS qtdeCliente
FROM life_cycle

-- Retira os Zumbis pois não foram segmentados 
WHERE descLifeCycle <> '05-ZUMBI'
-- Considera apenas a data mais recente
AND dtRef = (SELECT MAX(dtRef) FROM life_cycle)

GROUP BY dtRef, descLifeCycle, cluster
ORDER BY dtRef, descLifeCycle, cluster