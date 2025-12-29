-- Requête pour obtenir le nombre de clients par pays
SELECT 
    Country AS Pays,
    COUNT(*) AS Nombre_Clients
FROM 
    Customer
WHERE 
    Country IS NOT NULL
GROUP BY 
    Country
ORDER BY 
    Nombre_Clients DESC;
