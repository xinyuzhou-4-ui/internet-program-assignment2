-- MySQL dump 10.13  Distrib 8.0.45, for macos15 (arm64)
--
-- Host: localhost    Database: expense_tracker
-- ------------------------------------------------------
-- Server version	8.4.8

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
-- Table structure for table `user_activities`
--

DROP TABLE IF EXISTS `user_activities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_activities` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `action` varchar(50) NOT NULL,
  `detail` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_user_activities_user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_activities`
--

LOCK TABLES `user_activities` WRITE;
/*!40000 ALTER TABLE `user_activities` DISABLE KEYS */;
INSERT INTO `user_activities` VALUES (1,2,'login','User logged in.','2026-05-08 23:13:39'),(2,2,'login','User logged in.','2026-05-08 23:14:19'),(3,2,'update_user','Updated user 1: role=user, is_active=False','2026-05-08 23:17:06'),(4,3,'login','User logged in.','2026-05-09 00:06:37'),(5,3,'create_expense','Created expense 26: Train','2026-05-09 00:08:52'),(6,2,'login','User logged in.','2026-05-09 02:10:44'),(7,2,'login','User logged in.','2026-05-09 02:31:29'),(8,2,'login','User logged in.','2026-05-09 02:32:37'),(9,2,'login','User logged in.','2026-05-09 02:38:40'),(10,2,'deactivate_user','Deactivated user 3: zhouxinyu@gg.com','2026-05-09 02:39:41'),(11,2,'deactivate_user','Deactivated user 3: zhouxinyu@gg.com','2026-05-09 02:39:45'),(12,2,'deactivate_user','Deactivated user 2: logincheck@example.com','2026-05-09 02:39:51'),(13,2,'login','User logged in.','2026-05-09 02:45:17'),(19,2,'update_user','Updated user id 8','2026-05-09 15:31:58'),(20,2,'deactivate_user','Deactivated user id 8','2026-05-09 15:31:58'),(21,2,'login','User logged in.','2026-05-20 02:10:19'),(22,2,'login','User logged in.','2026-05-20 02:26:58'),(23,2,'update_user','Updated user 1: role=user, is_active=True','2026-05-20 02:27:06'),(24,2,'update_user','Updated user 3: role=user, is_active=True','2026-05-20 02:27:08'),(25,3,'login','User logged in.','2026-05-20 02:27:38'),(26,3,'create_expense','Created expense 30: Movie','2026-05-20 02:28:16'),(27,2,'login','User logged in.','2026-05-20 02:34:48'),(28,2,'logout','User logged out.','2026-05-20 02:36:45'),(29,2,'login','User logged in.','2026-05-20 02:36:49');
/*!40000 ALTER TABLE `user_activities` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-20  3:13:12
