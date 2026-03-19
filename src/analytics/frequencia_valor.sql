-- Calcula métricas de Frequência e Valor em janela móvel de 28 dias 
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
