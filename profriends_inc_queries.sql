-- SIMPLE QUERIES

-- #1 Display the buyer id, name, citizenship and birthplace of all buyers whose citizenship is Filipino
SELECT Buyerid, BuyerName, Citizenship
FROM profriends_inc.buyer
WHERE Citizenship = 'Filipino';

-- #2 Display the buyer name, gender, and civil status of buyers born in Manila.
SELECT BuyerName,  Gender, Civil_Status
FROM profriends_inc.buyer
WHERE Birthplace LIKE '%Manila%';

-- #3 List all beneficiary records who was born during years 2016 to 2020
SELECT *
FROM profriends_inc.beneficiary
WHERE YEAR(BenF_Bdate) BETWEEN 2016 AND 2020;

-- MODERATE QUERIES
-- #4 Display the buyer name, gender, civil status, and gross monthly income of married buyers 
-- whose gross monthly income ranges from 30,000 to 80,000.
SELECT BuyerName, Gender, Civil_Status, Gross_MonthlyIncome
FROM profriends_inc.buyer
WHERE (Gross_MonthlyIncome BETWEEN 50000 AND 90000) 
AND Civil_Status = 'M' ;

-- #5 Display each Finance_Type and the average LoanAmount. Show only finance types 
-- with an average loan amount greater than 1,000,000.
SELECT Finance_Type, AVG(LoanAmount) AS 'AVG Loan Amount'
FROM profriends_inc.loan
GROUP BY Finance_Type
HAVING AVG(LoanAmount) > 1000000;

-- #6 Display each Bank_Name and the total Gross_MonthlyIncome of buyers per bank. 
-- Sort from highest to lowest total income.
SELECT Bank_Name, SUM(Gross_MonthlyIncome) AS TotalIncome
FROM profriends_inc.buyer
GROUP BY Bank_Name
ORDER BY TotalIncome DESC;

-- #7 Determine the average and maximum Length_ofStay for each Home_Ownership type whose 
-- Length_ofStay is greater than or equal to 2 years. Display only groups with an average length of stay
--  greater than 3 years.
SELECT MAX(Length_ofStay) as 'Stay Length', 
AVG(Length_ofStay) AS 'AVG Stay', Home_Ownership
FROM profriends_inc.household
WHERE Length_ofStay >= 2
GROUP BY Home_Ownership
HAVING AVG(Length_ofStay) > 3;

-- DIFFICULT QUERIES

-- #8 Count how many buyers belong to each employment type whose civil status is either Single or Married. Also Tenure is 4 years above.
-- Provide only one total count per employment type.
SELECT Emp_Type, COUNT(*) AS TotalBuyers
FROM profriends_inc.employment e
JOIN profriends_inc.buyer b
	ON e.BuyerID = b.BuyerID
WHERE b.Civil_Status IN ('M','S') AND e.Tenure >= 4
GROUP BY Emp_Type;

-- #9 Display the BuyerName, Finance_Type, LoanAmount, Term, and computed yearly loan payment of buyers 
-- whose loan term is more than 5 years. Show only records where the yearly payment is greater than 200,000.
SELECT BuyerName, Finance_Type, LoanAmount, 
	   Loan_Term, (LoanAmount / Loan_Term) AS YearlyPayment
FROM profriends_inc.buyer b JOIN profriends_inc.loan l
	ON b.BuyerID = l.BuyerID
WHERE Loan_Term > 5 AND (LoanAmount / Loan_Term) > 200000;

-- #10 List each buyer’s name, count their total beneficiaries, and show the youngest beneficiary birthdate. 
-- Include only buyers with more than 1 beneficiary and sort from highest to lowest total beneficiaries.
SELECT BuyerName, COUNT(be.BeneficiaryID) AS TotalBeneficiaries,
	   MAX(BenF_Bdate) AS 'Youngest Beneficiary Bdate'
FROM profriends_inc.buyer b JOIN profriends_inc.beneficiary be
	ON b.BuyerID = be.BuyerID
GROUP BY b.BuyerName
HAVING COUNT(BeneficiaryID) > 1
ORDER BY TotalBeneficiaries DESC;