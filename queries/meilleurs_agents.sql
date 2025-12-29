-- Requête pour identifier les meilleurs agents commerciaux
SELECT 
    e.EmployeeId,
    e.FirstName || ' ' || e.LastName AS Nom_Employe,
    e.Title AS Poste,
    COUNT(i.InvoiceId) AS Nombre_Commandes,
    SUM(i.Total) AS Total_Ventes,
    e.HireDate AS Date_Embauche
FROM 
    Employee e
JOIN 
    Customer c ON e.EmployeeId = c.SupportRepId
JOIN 
    Invoice i ON c.CustomerId = i.CustomerId
WHERE 
    e.Title LIKE '%Sales%Agent%'
GROUP BY 
    e.EmployeeId, e.FirstName, e.LastName, e.Title
ORDER BY 
    Total_Ventes DESC;
