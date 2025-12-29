-- Requête pour obtenir le total des ventes par année
SELECT 
    strftime('%Y', InvoiceDate) AS Annee,
    COUNT(*) AS Nombre_Commandes,
    SUM(Total) AS Total_Ventes
FROM 
    Invoice
GROUP BY 
    strftime('%Y', InvoiceDate)
ORDER BY 
    Annee;
