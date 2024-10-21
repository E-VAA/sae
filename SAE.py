# Importation des modules utilisés
import sqlite3
import pandas

# Création de la connexion
conn = sqlite3.connect("ClassicModel.sqlite")

# Récupération du contenu de Customers avec une requête SQL
pandas.read_sql_query("SELECT * FROM Customers;", conn)

# Fermeture de la connexion : IMPORTANT à faire dans un cadre professionnel
#conn.close()

###  ###
#1 - Lister les clients n’ayant jamais effecuté une commande
q1 = pandas.read_sql_query(
    """
    SELECT c.customerName, c.customerNumber
    FROM Customers c
    LEFT JOIN Orders o ON c.customerNumber = o.customerNumber
    Where o.orderNumber IS NULL;
    """,
    conn
)
print(q1)
print()

#2 - Pour chaque employé, le nombre de clients, le nombre de commandes et le montant total de celles-ci
q2 = pandas.read_sql_query(
    """
    SELECT
        e.employeeNumber,
        e.firstName,
        e.lastName,
        COUNT(DISTINCT c.customerNumber) AS numberofCustomers,
        COUNT(DISTINCT o.orderNumber) AS numberofOrders,
        SUM(p.amount) AS totalOrderAmont
    FROM Employees e
    LEFT JOIN Customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    LEFT JOIN Orders o ON c.customerNumber = o.customerNumber
    LEFT JOIN Payments p ON o.customerNumber = p.customerNumber
    GROUP BY e.employeeNumber, e.firstName, e.lastName;
    """,
    conn
)
print(q2)
print()

#3 - Idem pour chaque bureau (nombre de clients, nombre de commandes et montant total), avec en plus le nombre de clients d’un pays différent, s’il y en a :
q3 = pandas.read_sql_query(
    """
    SELECT
        b.officeCode,
        b.city,
        b.country AS officeCountry,
        COUNT(DISTINCT c.customerNumber) AS numberofCustomers,
        COUNT(DISTINCT o.orderNumber) AS numberofOrders,
        SUM(p.amount) AS totalOrderAmont,
        COUNT(DISTINCT CASE
            WHEN c.country != b.country THEN c.customerNumber
            ELSE NULL
        END) AS customersFromDifferentCountry
    FROM Offices b
    LEFT JOIN Employees e ON b.officeCode = e.officeCode
    LEFT JOIN Customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    LEFT JOIN Orders o ON c.customerNumber = o.customerNumber
    LEFT JOIN Payments p ON o.customerNumber = p.customerNumber
    GROUP BY b.officeCode, b.city, b.country;
    """,
    conn
)
print(q3)
print()

#4 - Pour chaque produit, donner le nombre de commandes, la quantité totale commandée, et le nombre de clients différents
q4 = pandas.read_sql_query(
    """
    SELECT
        p.productCode,
        COUNT(DISTINCT o.orderNumber) AS numberofOrders,
        SUM(od.quantityOrdered) AS totalQuantityOrdered,
        COUNT(DISTINCT o.customerNumber) AS numberofDistinctCustomers
    FROM Products p
    LEFT JOIN OrderDetails od ON p.productCode = od.productCode
    LEFT JOIN Orders o ON od.orderNumber = o.orderNumber
    GROUP BY p.productCode;
    """,
    conn
)
print(q4)
print()


#5 - Donner le nombre de commande pour chaque pays du client, ainsi que le montant total des commandes 
#et le montant total payé : on veut conserver les client n'ayant jamais commandé dans le résultat final
q5 = pandas.read_sql_query(
    """
    SELECT
    c.country,
    COUNT(DISTINCT o.orderNumber) AS numberOfOrders,
    SUM(od.quantityOrdered * od.priceEach) AS totalOrderAmount,
    SUM(pa.amount) AS totalPaidAmount
    FROM Customers c
    LEFT JOIN Orders o ON c.customerNumber = o.customerNumber
    LEFT JOIN OrderDetails od ON o.orderNumber = od.orderNumber
    LEFT JOIN Payments pa ON c.customerNumber = pa.customerNumber
    GROUP BY c.country;
    """, 
    conn
)
print(q5)
print()


#6 - On veut la table de contigence du nombre de commande entre la ligne de produits et le pays du client
q6 = pandas.read_sql_query(
    """
    SELECT
        p.productLine, 
        c.country, 
        COUNT(*) AS numberofOrder
    FROM Orders o
    JOIN OrderDetails od ON o.orderNumber = od.orderNumber
    JOIN Products p ON od.productCode = p.productCode
    JOIN Customers c ON o.customerNumber = c.customerNumber
    GROUP BY p.productLine, c.country;
    """,
    conn
)
print(q6)
print()

#7 - On veut la même table croisant la ligne de produits et le pays du client, mais avec le montant total payé dans chaque cellule ;
q7 = pandas.read_sql_query(
    """
    SELECT 
        p.productLine, 
        c.country, 
        SUM(od.quantityOrdered * od.priceEach) as montant_total_paye
    FROM Orders o
    JOIN OrderDetails od ON o.orderNumber = od.orderNumber
    JOIN Products p ON od.productCode = p.productCode
    JOIN Customers c ON o.customerNumber = c.customerNumber
    GROUP BY p.productLine, c.country
    ORDER BY p.productLine, c.country;
    """,
    conn
)
print(q7)
print()

#8 - Donner les 10 produits pour lesquels la marge moyenne est la plus importante (cf buyPrice et priceEach) ;
q8 = pandas.read_sql_query(
    """
    SELECT 
        p.productName, 
        AVG(od.priceEach - p.buyPrice) AS margeMoyenne 
    FROM OrderDetails od
    JOIN Products p ON od.productCode = p.productCode
    GROUP BY p.productName
    ORDER BY margeMoyenne DESC
    LIMIT 10;
    """,
    conn
)
print(q8)
print()

#9 - Lister les produits (avec le nom et le code du client) qui ont été vendus à perte :
#Si un produit a été dans cette situation plusieurs fois, il doit apparaître plusieurs fois,
#Une vente à perte arrive quand le prix de vente est inférieur au prix d’achat ;
q9 = pandas.read_sql_query(
    """
    SELECT 
        p.productName, 
        c.customerName,
        c.customerNumber,
        od.priceEach,
        p.buyPrice
    FROM OrderDetails od
    JOIN Products p ON od.productCode = p.productCode
    JOIN Orders o ON od.orderNumber = o.orderNumber
    JOIN Customers c ON o.customerNumber = c.customerNumber
    WHERE od.priceEach < p.buyPrice ;
    """,
    conn
)
print(q9)
print()

#10 - Lister les clients pour lesquels le montant total payé est inférieur aux montants totals des achats
q10 = pandas.read_sql_query(
    """
    SELECT 
        c.customerNumber,
        c.customerName,
        SUM(od.quantityOrdered * od.priceEach) AS totalMontantAchat,
        (SELECT SUM(amount) FROM Payments p WHERE p.customerNumber = c.customerNumber) AS totalAmountPaye
    FROM Customers c
    JOIN Orders o ON c.customerNumber = o.customerNumber
    JOIN OrderDetails od ON o.orderNumber = od.orderNumber
    GROUP BY c.customerNumber
    HAVING totalAmountPaye < totalMontantAchat;
    """,
    conn
)
print(q10)
print()