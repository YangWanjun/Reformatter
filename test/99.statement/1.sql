USE AdventureWorks2012
GO

UPDATE Production.Product
SET Color = 'Metallic Red'
WHERE Name LIKE 'Road-250%' AND Color <> 'Red'
go