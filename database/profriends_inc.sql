CREATE DATABASE  IF NOT EXISTS `profriends_inc` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `profriends_inc`;
-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: profriends_inc
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `beneficiary`
--

DROP TABLE IF EXISTS `beneficiary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `beneficiary` (
  `BeneficiaryID` varchar(15) NOT NULL,
  `BuyerID` varchar(15) DEFAULT NULL,
  `BenF_Name` varchar(50) NOT NULL,
  `BenF_Bdate` date DEFAULT NULL,
  `Relationship` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`BeneficiaryID`,`BenF_Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `beneficiary`
--

LOCK TABLES `beneficiary` WRITE;
/*!40000 ALTER TABLE `beneficiary` DISABLE KEYS */;
INSERT INTO `beneficiary` VALUES ('BEN-001','B-2023-001','Jemie Velasco','2016-06-17','Child'),('BEN-001','B-2023-001','Shawn Velasco','2019-11-23','Child'),('BEN-002','B-2024-002','Rosa Santos','1965-05-07','Parent'),('BEN-003','B-2024-003','Kyle Reyes','2018-01-06','Child'),('BEN-004','B-2025-004','Kiel Gomez','1962-04-14','Parent'),('BEN-004','B-2025-004','Mia Gomez','2013-05-16','Child'),('BEN-004','B-2025-004','Patrick Gomez','2015-12-23','Child'),('BEN-005','B-2026-005','Lily Tan','1960-08-25','Parent');
/*!40000 ALTER TABLE `beneficiary` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `buyer`
--

DROP TABLE IF EXISTS `buyer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `buyer` (
  `BuyerID` varchar(15) NOT NULL,
  `BuyerName` varchar(50) NOT NULL,
  `Birthdate` date NOT NULL,
  `Birthplace` varchar(100) NOT NULL,
  `GovID` varchar(20) NOT NULL,
  `TIN` varchar(15) NOT NULL,
  `Gender` char(1) NOT NULL,
  `Civil_Status` char(2) NOT NULL,
  `Address` varchar(100) NOT NULL,
  `Citizenship` varchar(20) NOT NULL,
  `Gross_MonthlyIncome` decimal(12,2) NOT NULL,
  `Tel_Num` varchar(15) DEFAULT NULL,
  `Mobile_Num` varchar(15) NOT NULL,
  `Personal_Email` varchar(50) NOT NULL,
  `Work_Email` varchar(50) DEFAULT NULL,
  `Account_Type` varchar(20) NOT NULL,
  `Bank_Name` varchar(50) NOT NULL,
  PRIMARY KEY (`BuyerID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `buyer`
--

LOCK TABLES `buyer` WRITE;
/*!40000 ALTER TABLE `buyer` DISABLE KEYS */;
INSERT INTO `buyer` VALUES ('B-2023-001','James Velasco','1995-05-03','Cebu City','Passport','123-456-789-000','M','M','#16 Mapayapa St., Cebu City','Filipino',85000.00,'(02)8123-4567','9171234567','jamesvelasco03@gmail.com','jvelasco8723@accenture.com','Savings','BDO'),('B-2024-002','Ana Santos','1993-10-02','Quezon City','Postal ID','222-333-444-000','F','S','#45 Aurora Blvd., QC','Filipino',74000.00,'(02)8555-1111','9192345678','santosana@gmail.com','anas92@ayala.com','Payroll','BPI'),('B-2024-003','Mark Reyes','1988-11-20','Manila','SSS','555-666-777-000','M','M','#78 Rizal St., Manila','Filipino',60000.00,'(02)8999-3333','9175678901','mark20@gmail.com','mark@biz.com','Checking','Metrobank'),('B-2025-004','Liza Gomez','1992-07-25','Laguna','Driver\'s License','111-222-333-000','F','M','#12 Sunset Ave., Laguna','Filipino',67000.00,'(049)555-7777','9193456789','lizagomez@gmail.com','liza@corp.com','Savings','Landbank'),('B-2026-005','Kevin Tan','1990-12-12','Manila','National ID','777-888-999-000','M','S','#89 Binondo, Manila','Filipino',70000.00,'(02)8333-9999','9176543210','kevintan@gmail.com','tankevin@global.com','Checking','Chinabank');
/*!40000 ALTER TABLE `buyer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employment`
--

DROP TABLE IF EXISTS `employment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employment` (
  `EmploymentID` varchar(15) NOT NULL,
  `BuyerID` varchar(15) NOT NULL,
  `Emp_Type` varchar(30) NOT NULL,
  `Emp_Name` varchar(50) NOT NULL,
  `Emp_Address` varchar(100) NOT NULL,
  `Emp_TelNum` varchar(15) DEFAULT NULL,
  `Emp_EmailAdd` varchar(50) DEFAULT NULL,
  `Occupation` varchar(30) NOT NULL,
  `Position` varchar(30) NOT NULL,
  `Tenure` int NOT NULL,
  `Occupation_rank` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`EmploymentID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employment`
--

LOCK TABLES `employment` WRITE;
/*!40000 ALTER TABLE `employment` DISABLE KEYS */;
INSERT INTO `employment` VALUES ('E-2023-001','B-2023-001','Employed','Accenture','Mandaue City','(02)8899-1234','careers.ph@accenture.com','Software Engineer','Specialist',3,'Rank & File'),('E-2024-002','B-2024-002','Employed','Ayala Corporation','Quezon City','(02)8777-2222','careers@ayala.com','Accountant','Staff',5,'Rank & File'),('E-2024-003','B-2024-003','Self Employed','Reyes Trading','Manila','(02)8222-4444','contact@reyes.com','Business Owner','Owner',6,'Business Owner'),('E-2025-004','B-2025-004','Employed','TechCorp','Laguna','(02)8609-3225','hr@techcorp.com','HR Manager','Manager',7,'Manager'),('E-2026-005','B-2026-005','OFW-Landbased','Global Co.','Dubai',NULL,'contact@global.com','Engineer','Supervisor',4,'Others');
/*!40000 ALTER TABLE `employment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `household`
--

DROP TABLE IF EXISTS `household`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `household` (
  `HouseholdID` varchar(15) NOT NULL,
  `BuyerID` varchar(15) NOT NULL,
  `Household_Details` varchar(50) DEFAULT NULL,
  `Num_children` int NOT NULL,
  `Num_parents` int NOT NULL,
  `Num_others` int NOT NULL,
  `Address` varchar(100) NOT NULL,
  `Home_Ownership` varchar(20) NOT NULL,
  `Length_ofStay` int DEFAULT NULL,
  PRIMARY KEY (`HouseholdID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `household`
--

LOCK TABLES `household` WRITE;
/*!40000 ALTER TABLE `household` DISABLE KEYS */;
INSERT INTO `household` VALUES ('H-2023-001','B-2023-001','With dependents',2,1,0,'145 Mango Grove St., Lahug, Cebu City, Cebu','Rented',3),('H-2024-002','B-2024-002','No dependents',0,0,0,'28 Sampaguita Ave., Brgy. Teachers Village East, Quezon City','Owned',6),('H-2024-003','B-2024-003','With dependents',1,0,1,'1028 Rizal St., Malate, Manila','Owned by Parents',8),('H-2025-004','B-2025-004','With dependents',3,0,0,'Block 5 Lot 9, Greenfields Village, Santa Rosa, Laguna','Owned',7),('H-2026-005','B-2026-005','No dependents',0,0,0,'45 San Andres Corner Quirino Ave., Paco, Manila','Rented',3);
/*!40000 ALTER TABLE `household` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loan`
--

DROP TABLE IF EXISTS `loan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `loan` (
  `LoanID` varchar(15) NOT NULL,
  `BuyerID` varchar(15) NOT NULL,
  `UnitID` varchar(15) NOT NULL,
  `Finance_Type` varchar(20) NOT NULL,
  `DP_Term` int NOT NULL,
  `Loan_Term` int NOT NULL,
  `Purchase_Purpose` varchar(15) NOT NULL,
  `Source_Funds` varchar(30) NOT NULL,
  `LoanAmount` decimal(12,2) NOT NULL,
  `Downpayment` decimal(12,2) NOT NULL,
  `ReservationFee` decimal(12,2) NOT NULL,
  `Sell_Price` decimal(12,2) NOT NULL,
  `OrPr_Num` varchar(30) NOT NULL,
  `OrPr_Date` date NOT NULL,
  `Booking_Officer` varchar(30) NOT NULL,
  `ProcessingFee` decimal(12,2) NOT NULL,
  PRIMARY KEY (`LoanID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loan`
--

LOCK TABLES `loan` WRITE;
/*!40000 ALTER TABLE `loan` DISABLE KEYS */;
INSERT INTO `loan` VALUES ('L-2023-001','B-2023-001','UNIT-A01','Bank',24,10,'Primary Home','Employment',2000000.00,400000.00,20000.00,2400000.00,'OR-10001','2023-04-09','Luis Remigio',5000.00),('L-2024-002','B-2024-002','UNIT-B02','Pag-IBIG',12,15,'Investment','Employment',1500000.00,300000.00,15000.00,1800000.00,'OR-10002','2024-03-15','Alice Cruz',4000.00),('L-2024-003','B-2024-003','UNIT-C03','Cash',6,5,'Primary Home','Business',1000000.00,200000.00,10000.00,1500000.00,'OR-10003','2024-11-20','John Lee',3000.00),('L-2025-004','B-2025-004','UNIT-D04','Bank',18,12,'Retirement','Employment',2500000.00,600000.00,25000.00,3100000.00,'OR-10004','2025-01-10','Sarah Lim',5500.00),('L-2026-005','B-2026-005','UNIT-E05','In-House',24,20,'Investment','Remittance',3000000.00,800000.00,30000.00,3800000.00,'OR-10005','2026-05-01','Mark Cruz',6000.00);
/*!40000 ALTER TABLE `loan` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `spouse`
--

DROP TABLE IF EXISTS `spouse`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `spouse` (
  `BuyerID` varchar(15) NOT NULL,
  `Sps_Name` varchar(50) DEFAULT NULL,
  `Sps_Bdate` date DEFAULT NULL,
  `Sps_Bplace` varchar(50) DEFAULT NULL,
  `Sps_Citizenship` varchar(20) DEFAULT NULL,
  `Sps_GovID` varchar(20) DEFAULT NULL,
  `Sps_TIN` varchar(15) DEFAULT NULL,
  `Sps_TelNum` varchar(15) DEFAULT NULL,
  `Sps_EmailAdd` varchar(50) DEFAULT NULL,
  `Sps_MobNum` varchar(15) DEFAULT NULL,
  `Sps_GrossMonthlyIncome` decimal(12,2) DEFAULT NULL,
  PRIMARY KEY (`BuyerID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `spouse`
--

LOCK TABLES `spouse` WRITE;
/*!40000 ALTER TABLE `spouse` DISABLE KEYS */;
INSERT INTO `spouse` VALUES ('B-2023-001','Levie Velasco','1997-03-07','Cebu City','Filipino','National ID','987-654-321-000','(02)8456-7890','velascolevie@gmail.com','9181234567',30000.00),('B-2024-002',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),('B-2024-003','Carla Reyes','1990-09-09','Manila','Filipino','Passport','888-999-000-000','(02)8111-2222','carlareyes@gmail.com','9184567890',28000.00),('B-2025-004','Carlo Gomez','1991-01-01','Laguna','Filipino','Postal ID','444-555-666-000','(02)8344-2672','gmzcarlo@gmail.com','9192349876',73000.00),('B-2026-005',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `spouse` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-28 19:25:14
