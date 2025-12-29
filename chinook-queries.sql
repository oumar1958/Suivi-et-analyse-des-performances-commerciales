-- Projet : Automatisation des rapports de ventes avec SQL
-- Base de données : Chinook
-- Auteur : [Votre nom]
-- Date : 2025-12-26

-- 1. Clients non américains
SELECT 
    CustomerId,
    FirstName || ' ' || LastName AS NomComplet,
    Country AS Pays
FROM 
    Customer
WHERE 
    Country != 'USA';

-- 2. Clients brésiliens
SELECT 
    CustomerId,
    FirstName || ' ' || LastName AS NomComplet,
    Country AS Pays
FROM 
    Customer
WHERE 
    Country = 'Brazil';

-- 3. Factures des clients brésiliens
SELECT 
    c.FirstName || ' ' || c.LastName AS NomClient,
    i.InvoiceId,
    i.InvoiceDate,
    i.BillingCountry AS PaysFacturation
FROM 
    Invoice i
JOIN 
    Customer c ON i.CustomerId = c.CustomerId
WHERE 
    c.Country = 'Brazil';

-- 4. Agents de vente
SELECT 
    EmployeeId,
    FirstName || ' ' || LastName AS NomComplet,
    Title AS Poste
FROM 
    Employee
WHERE 
    Title LIKE '%Sales%' 
    AND Title LIKE '%Agent%';

-- 5. Pays uniques dans les factures
SELECT DISTINCT 
    BillingCountry AS PaysFacturation
FROM 
    Invoice
ORDER BY 
    BillingCountry;

-- 6. Factures par agent de vente
SELECT 
    e.FirstName || ' ' || e.LastName AS AgentVente,
    i.*
FROM 
    Invoice i
JOIN 
    Customer c ON i.CustomerId = c.CustomerId
JOIN 
    Employee e ON c.SupportRepId = e.EmployeeId
WHERE 
    e.Title LIKE '%Sales%' 
    AND e.Title LIKE '%Agent%';

-- 7. Détails des factures avec totaux
SELECT 
    c.FirstName || ' ' || c.LastName AS Client,
    i.InvoiceId,
    i.InvoiceDate,
    i.BillingCountry AS PaysFacturation,
    e.FirstName || ' ' || e.LastName AS AgentVente,
    SUM(il.UnitPrice * il.Quantity) AS TotalFacture
FROM 
    Invoice i
JOIN 
    Customer c ON i.CustomerId = c.CustomerId
JOIN 
    Employee e ON c.SupportRepId = e.EmployeeId
JOIN 
    InvoiceLine il ON i.InvoiceId = il.InvoiceId
GROUP BY 
    i.InvoiceId;

-- 8. Ventes par année (2009 et 2011)
SELECT 
    strftime('%Y', InvoiceDate) AS Annee,
    COUNT(*) AS NombreFactures,
    SUM(Total) AS MontantTotal
FROM 
    Invoice
WHERE 
    strftime('%Y', InvoiceDate) IN ('2009', '2011')
GROUP BY 
    strftime('%Y', InvoiceDate);

-- 9. Articles pour la facture 37
SELECT 
    COUNT(*) AS NombreArticles
FROM 
    InvoiceLine
WHERE 
    InvoiceId = 37;

-- 10. Articles par facture
SELECT 
    InvoiceId,
    COUNT(*) AS NombreArticles
FROM 
    InvoiceLine
GROUP BY 
    InvoiceId;

-- 11. Noms des morceaux pour chaque ligne de facture
SELECT 
    il.InvoiceLineId,
    t.Name AS Morceau
FROM 
    InvoiceLine il
JOIN 
    Track t ON il.TrackId = t.TrackId;

-- 12. Morceaux et artistes par ligne de facture
SELECT 
    il.InvoiceLineId,
    t.Name AS Morceau,
    ar.Name AS Artiste
FROM 
    InvoiceLine il
JOIN 
    Track t ON il.TrackId = t.TrackId
JOIN 
    Album al ON t.AlbumId = al.AlbumId
JOIN 
    Artist ar ON al.ArtistId = ar.ArtistId;

-- 13. Nombre de factures par pays
SELECT 
    BillingCountry AS Pays,
    COUNT(*) AS NombreFactures
FROM 
    Invoice
GROUP BY 
    BillingCountry
ORDER BY 
    NombreFactures DESC;

-- 14. Nombre de morceaux par playlist
SELECT 
    p.Name AS Playlist,
    COUNT(pt.TrackId) AS NombreMorceaux
FROM 
    Playlist p
JOIN 
    PlaylistTrack pt ON p.PlaylistId = pt.PlaylistId
GROUP BY 
    p.PlaylistId
ORDER BY 
    NombreMorceaux DESC;

-- 15. Liste des morceaux sans IDs
SELECT 
    t.Name AS Morceau,
    al.Title AS Album,
    mt.Name AS TypeMedia,
    g.Name AS Genre
FROM 
    Track t
JOIN 
    Album al ON t.AlbumId = al.AlbumId
JOIN 
    MediaType mt ON t.MediaTypeId = mt.MediaTypeId
JOIN 
    Genre g ON t.GenreId = g.GenreId;

-- 16. Factures avec nombre d'articles
SELECT 
    i.InvoiceId,
    i.InvoiceDate,
    COUNT(il.InvoiceLineId) AS NombreArticles,
    SUM(il.UnitPrice * il.Quantity) AS MontantTotal
FROM 
    Invoice i
JOIN 
    InvoiceLine il ON i.InvoiceId = il.InvoiceId
GROUP BY 
    i.InvoiceId, i.InvoiceDate;

-- 17. Ventes totales par agent de vente
SELECT 
    e.EmployeeId,
    e.FirstName || ' ' || e.LastName AS AgentVente,
    ROUND(SUM(i.Total), 2) AS VentesTotales
FROM 
    Employee e
JOIN 
    Customer c ON e.EmployeeId = c.SupportRepId
JOIN 
    Invoice i ON c.CustomerId = i.CustomerId
WHERE 
    e.Title LIKE '%Sales%' 
    AND e.Title LIKE '%Agent%'
GROUP BY 
    e.EmployeeId, e.FirstName, e.LastName;

-- 18. Meilleur agent de vente en 2009
SELECT 
    e.FirstName || ' ' || e.LastName AS MeilleurVendeur2009,
    ROUND(SUM(i.Total), 2) AS MontantVentes
FROM 
    Employee e
JOIN 
    Customer c ON e.EmployeeId = c.SupportRepId
JOIN 
    Invoice i ON c.CustomerId = i.CustomerId
WHERE 
    strftime('%Y', i.InvoiceDate) = '2009'
    AND e.Title LIKE '%Sales%' 
    AND e.Title LIKE '%Agent%'
GROUP BY 
    e.EmployeeId
ORDER BY 
    MontantVentes DESC
LIMIT 1;

-- 19. Meilleur agent de vente en 2010
SELECT 
    e.FirstName || ' ' || e.LastName AS MeilleurVendeur2010,
    ROUND(SUM(i.Total), 2) AS MontantVentes
FROM 
    Employee e
JOIN 
    Customer c ON e.EmployeeId = c.SupportRepId
JOIN 
    Invoice i ON c.CustomerId = i.CustomerId
WHERE 
    strftime('%Y', i.InvoiceDate) = '2010'
    AND e.Title LIKE '%Sales%' 
    AND e.Title LIKE '%Agent%'
GROUP BY 
    e.EmployeeId
ORDER BY 
    MontantVentes DESC
LIMIT 1;

-- 20. Meilleur agent de vente global
SELECT 
    e.FirstName || ' ' || e.LastName AS MeilleurVendeurGlobal,
    ROUND(SUM(i.Total), 2) AS MontantVentesTotal
FROM 
    Employee e
JOIN 
    Customer c ON e.EmployeeId = c.SupportRepId
JOIN 
    Invoice i ON c.CustomerId = i.CustomerId
WHERE 
    e.Title LIKE '%Sales%' 
    AND e.Title LIKE '%Agent%'
GROUP BY 
    e.EmployeeId
ORDER BY 
    MontantVentesTotal DESC
LIMIT 1;

-- 21. Nombre de clients par agent de vente
SELECT 
    e.FirstName || ' ' || e.LastName AS AgentVente,
    COUNT(c.CustomerId) AS NombreClients
FROM 
    Employee e
LEFT JOIN 
    Customer c ON e.EmployeeId = c.SupportRepId
WHERE 
    e.Title LIKE '%Sales%' 
    AND e.Title LIKE '%Agent%'
GROUP BY 
    e.EmployeeId, e.FirstName, e.LastName;

-- 22. Ventes totales par pays
SELECT 
    i.BillingCountry AS Pays,
    ROUND(SUM(i.Total), 2) AS VentesTotales
FROM 
    Invoice i
GROUP BY 
    i.BillingCountry
ORDER BY 
    VentesTotales DESC;

-- 23. Morceau le plus acheté en 2013
SELECT 
    t.Name AS Morceau,
    ar.Name AS Artiste,
    COUNT(il.InvoiceLineId) AS NombreAchats
FROM 
    Track t
JOIN 
    InvoiceLine il ON t.TrackId = il.TrackId
JOIN 
    Invoice i ON il.InvoiceId = i.InvoiceId
JOIN 
    Album al ON t.AlbumId = al.AlbumId
JOIN 
    Artist ar ON al.ArtistId = ar.ArtistId
WHERE 
    strftime('%Y', i.InvoiceDate) = '2013'
GROUP BY 
    t.TrackId
ORDER BY 
    NombreAchats DESC
LIMIT 1;

-- 24. Top 5 des morceaux les plus achetés
SELECT 
    t.Name AS Morceau,
    ar.Name AS Artiste,
    COUNT(il.InvoiceLineId) AS NombreAchats
FROM 
    Track t
JOIN 
    InvoiceLine il ON t.TrackId = il.TrackId
JOIN 
    Album al ON t.AlbumId = al.AlbumId
JOIN 
    Artist ar ON al.ArtistId = ar.ArtistId
GROUP BY 
    t.TrackId
ORDER BY 
    NombreAchats DESC
LIMIT 5;

-- 25. Top 3 des artistes les plus vendus
SELECT 
    ar.Name AS Artiste,
    COUNT(il.InvoiceLineId) AS NombreVentes
FROM 
    Artist ar
JOIN 
    Album al ON ar.ArtistId = al.ArtistId
JOIN 
    Track t ON al.AlbumId = t.AlbumId
JOIN 
    InvoiceLine il ON t.TrackId = il.TrackId
GROUP BY 
    ar.ArtistId
ORDER BY 
    NombreVentes DESC
LIMIT 3;

-- 26. Type de média le plus acheté
SELECT 
    mt.Name AS TypeMedia,
    COUNT(il.InvoiceLineId) AS NombreAchats
FROM 
    MediaType mt
JOIN 
    Track t ON mt.MediaTypeId = t.MediaTypeId
JOIN 
    InvoiceLine il ON t.TrackId = il.TrackId
GROUP BY 
    mt.MediaTypeId
ORDER BY 
    NombreAchats DESC
LIMIT 1;
