SELECT dtRef,
        descLifeCycle,
        cluster,
        count(*) AS qtdeCliente
FROM life_cycle

WHERE descLifeCycle <> '05-ZUMBI'
AND dtRef = (SELECT max(dtRef) FROM life_cycle)

GROUP BY dtRef, descLifeCycle, cluster
ORDER BY dtRef, descLifeCycle, cluster