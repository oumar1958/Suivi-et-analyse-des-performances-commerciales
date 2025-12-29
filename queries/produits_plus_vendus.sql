-- Requête pour identifier les produits les plus vendus
SELECT 
    t.TrackId,
    t.Name AS Nom_Produit,
    ar.Name AS Artiste,
    g.Name AS Genre,
    COUNT(il.InvoiceLineId) AS Nombre_Ventes,
    SUM(il.Quantity) AS Quantite_Vendue,
    ROUND(SUM(il.UnitPrice * il.Quantity), 2) AS Chiffre_Affaires
FROM 
    Track t
JOIN 
    Album al ON t.AlbumId = al.AlbumId
JOIN 
    Artist ar ON al.ArtistId = ar.ArtistId
JOIN 
    Genre g ON t.GenreId = g.GenreId
JOIN 
    InvoiceLine il ON t.TrackId = il.TrackId
GROUP BY 
    t.TrackId, t.Name, ar.Name, g.Name
ORDER BY 
    Quantite_Vendue DESC
LIMIT 50;
