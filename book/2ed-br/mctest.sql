-- MySQL dump 10.13  Distrib 8.0.33, for macos12.6 (x86_64)
--
-- Host: localhost    Database: DB_MCTest
-- ------------------------------------------------------
-- Server version	8.0.21

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `account_user`
--

DROP TABLE IF EXISTS `account_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(15) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(255) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `is_trusty` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=108 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_user`
--

LOCK TABLES `account_user` WRITE;
/*!40000 ALTER TABLE `account_user` DISABLE KEYS */;
INSERT INTO `account_user` VALUES (1,'pbkdf2_sha256$150000$4zxBrMk9MeNY$0s4uwkF2IE8LZCNLZQUV2jhnp+BZjx0AuhooEkpzyDg=','2023-12-07 17:27:40.098976',1,'fzampirolli','Francisco','Zampirolli','fzampirolli@ufabc.edu.br',1,1,'2019-01-14 18:03:04.000000',0),(53,'pbkdf2_sha256$600000$ZI9m2tjIBRzu1ErAOkJQjm$5ebijVAQZuPGJx8mpiF3B8GPqVJyqzuc8GymsEjRbiw=','2022-05-26 17:03:49.359608',0,'fzstudent','Francisco','Estudante','fzstudent@ufabc.edu.br',0,1,'2019-01-31 07:27:04.065858',0),(65,'pbkdf2_sha256$600000$o50RY7ieNBhOjl7Uq5EJmN$S8zQK1gi875c+TQYYLZG51s7Q3wQAwYGPOZxWSdzd2c=','2022-07-12 22:54:55.679807',0,'fzprof','Francisco','Professor','fzprof@ufabc.edu.br',0,1,'2019-09-02 20:48:18.000000',0),(66,'pbkdf2_sha256$600000$2fc5ARaUAsn5yimb26laij$KA3BvUBxbGbARHnXel4amkgkysr8YWCYUZnM22aUEss=','2022-05-26 17:12:07.229064',0,'fzcoord','Francisco','Coordenador','fzcoord@ufabc.edu.br',0,1,'2019-09-02 20:49:06.000000',0);
/*!40000 ALTER TABLE `account_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_user_groups`
--

DROP TABLE IF EXISTS `account_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_user_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `account_user_groups_user_id_group_id_4d09af3e_uniq` (`user_id`,`group_id`),
  KEY `account_user_groups_group_id_6c71f749_fk_auth_group_id` (`group_id`),
  CONSTRAINT `account_user_groups_group_id_6c71f749_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `account_user_groups_user_id_14345e7b_fk_account_user_id` FOREIGN KEY (`user_id`) REFERENCES `account_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=108 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_user_groups`
--

LOCK TABLES `account_user_groups` WRITE;
/*!40000 ALTER TABLE `account_user_groups` DISABLE KEYS */;
INSERT INTO `account_user_groups` VALUES (4,1,2),(71,65,2),(70,66,2);
/*!40000 ALTER TABLE `account_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_user_user_permissions`
--

DROP TABLE IF EXISTS `account_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_user_user_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `account_user_user_permis_user_id_permission_id_48bdd28b_uniq` (`user_id`,`permission_id`),
  KEY `account_user_user_pe_permission_id_66c44191_fk_auth_perm` (`permission_id`),
  CONSTRAINT `account_user_user_pe_permission_id_66c44191_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `account_user_user_pe_user_id_cc42d270_fk_account_u` FOREIGN KEY (`user_id`) REFERENCES `account_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_user_user_permissions`
--

LOCK TABLES `account_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `account_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `account_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
INSERT INTO `auth_group` VALUES (1,'coordenador'),(2,'professor');
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=78 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
INSERT INTO `auth_group_permissions` VALUES (38,1,21),(39,1,22),(40,1,23),(1,1,24),(2,1,25),(3,1,26),(4,1,27),(5,1,28),(6,1,29),(7,1,30),(8,1,31),(9,1,32),(10,1,33),(34,1,35),(11,1,37),(12,1,41),(35,1,42),(36,1,43),(37,1,44),(13,1,45),(14,1,46),(15,1,47),(16,1,48),(17,1,49),(18,1,50),(19,1,51),(20,1,52),(21,1,53),(22,1,54),(23,1,55),(24,1,56),(25,1,57),(26,1,58),(27,1,59),(28,1,60),(29,1,61),(30,1,62),(31,1,63),(32,1,64),(33,1,65),(74,2,17),(75,2,18),(76,2,19),(77,2,20),(41,2,24),(42,2,25),(43,2,26),(44,2,27),(45,2,28),(46,2,29),(47,2,30),(48,2,31),(49,2,32),(50,2,33),(51,2,37),(52,2,41),(53,2,45),(54,2,46),(55,2,47),(56,2,48),(57,2,49),(58,2,50),(59,2,51),(60,2,52),(61,2,53),(62,2,54),(63,2,55),(64,2,56),(65,2,57),(66,2,58),(67,2,59),(68,2,60),(69,2,61),(70,2,62),(71,2,63),(72,2,64),(73,2,65);
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=78 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add topic',6,'add_topic'),(22,'Can change topic',6,'change_topic'),(23,'Can delete topic',6,'delete_topic'),(24,'Can view topic',6,'view_topic'),(25,'Can add question',7,'add_question'),(26,'Can change question',7,'change_question'),(27,'Can delete question',7,'delete_question'),(28,'Can view question',7,'view_question'),(29,'Set question as validated',7,'can_mark_update'),(30,'Can add answer',8,'add_answer'),(31,'Can change answer',8,'change_answer'),(32,'Can delete answer',8,'delete_answer'),(33,'Can view answer',8,'view_answer'),(34,'Can add course',9,'add_course'),(35,'Can change course',9,'change_course'),(36,'Can delete course',9,'delete_course'),(37,'Can view course',9,'view_course'),(38,'Can add institute',10,'add_institute'),(39,'Can change institute',10,'change_institute'),(40,'Can delete institute',10,'delete_institute'),(41,'Can view institute',10,'view_institute'),(42,'Can add discipline',11,'add_discipline'),(43,'Can change discipline',11,'change_discipline'),(44,'Can delete discipline',11,'delete_discipline'),(45,'Can view discipline',11,'view_discipline'),(46,'Can add classroom',12,'add_classroom'),(47,'Can change classroom',12,'change_classroom'),(48,'Can delete classroom',12,'delete_classroom'),(49,'Can view classroom',12,'view_classroom'),(50,'Can add exam',13,'add_exam'),(51,'Can change exam',13,'change_exam'),(52,'Can delete exam',13,'delete_exam'),(53,'Can view exam',13,'view_exam'),(54,'Can add student exam',14,'add_studentexam'),(55,'Can change student exam',14,'change_studentexam'),(56,'Can delete student exam',14,'delete_studentexam'),(57,'Can view student exam',14,'view_studentexam'),(58,'Can add student exam question',15,'add_studentexamquestion'),(59,'Can change student exam question',15,'change_studentexamquestion'),(60,'Can delete student exam question',15,'delete_studentexamquestion'),(61,'Can view student exam question',15,'view_studentexamquestion'),(62,'Can add student',16,'add_student'),(63,'Can change student',16,'change_student'),(64,'Can delete student',16,'delete_student'),(65,'Can view student',16,'view_student'),(66,'Can add user',17,'add_user'),(67,'Can change user',17,'change_user'),(68,'Can delete user',17,'delete_user'),(69,'Can view user',17,'view_user'),(70,'Can add classroom exam',18,'add_classroomexam'),(71,'Can change classroom exam',18,'change_classroomexam'),(72,'Can delete classroom exam',18,'delete_classroomexam'),(73,'Can view classroom exam',18,'view_classroomexam'),(74,'Can add variation exam',19,'add_variationexam'),(75,'Can change variation exam',19,'change_variationexam'),(76,'Can delete variation exam',19,'delete_variationexam'),(77,'Can view variation exam',19,'view_variationexam');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_classroom`
--

DROP TABLE IF EXISTS `course_classroom`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_classroom` (
  `id` int NOT NULL AUTO_INCREMENT,
  `classroom_code` varchar(20) NOT NULL,
  `classroom_room` varchar(20) NOT NULL,
  `classroom_days` varchar(20) NOT NULL,
  `classroom_type` varchar(6) NOT NULL,
  `discipline_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `course_classroom_discipline_id_6c1c6c02_fk_course_discipline_id` (`discipline_id`),
  CONSTRAINT `course_classroom_discipline_id_6c1c6c02_fk_course_discipline_id` FOREIGN KEY (`discipline_id`) REFERENCES `course_discipline` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=671 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_classroom`
--

LOCK TABLES `course_classroom` WRITE;
/*!40000 ALTER TABLE `course_classroom` DISABLE KEYS */;
INSERT INTO `course_classroom` VALUES (670,'fzTurmaTeste','virtual','2023.3','PClass',51);
/*!40000 ALTER TABLE `course_classroom` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_classroom_classroom_profs`
--

DROP TABLE IF EXISTS `course_classroom_classroom_profs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_classroom_classroom_profs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `classroom_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `course_classroom_classro_classroom_id_user_id_da4a3ce2_uniq` (`classroom_id`,`user_id`),
  KEY `course_classroom_cla_user_id_3d589b69_fk_account_u` (`user_id`),
  CONSTRAINT `course_classroom_cla_classroom_id_f7438abe_fk_course_cl` FOREIGN KEY (`classroom_id`) REFERENCES `course_classroom` (`id`),
  CONSTRAINT `course_classroom_cla_user_id_3d589b69_fk_account_u` FOREIGN KEY (`user_id`) REFERENCES `account_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_classroom_classroom_profs`
--

LOCK TABLES `course_classroom_classroom_profs` WRITE;
/*!40000 ALTER TABLE `course_classroom_classroom_profs` DISABLE KEYS */;
INSERT INTO `course_classroom_classroom_profs` VALUES (3,670,1);
/*!40000 ALTER TABLE `course_classroom_classroom_profs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_classroom_students`
--

DROP TABLE IF EXISTS `course_classroom_students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_classroom_students` (
  `id` int NOT NULL AUTO_INCREMENT,
  `classroom_id` int NOT NULL,
  `student_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `course_classroom_students_classroom_id_student_id_08ea9b73_uniq` (`classroom_id`,`student_id`),
  KEY `course_classroom_stu_student_id_4e5d6532_fk_student_s` (`student_id`),
  CONSTRAINT `course_classroom_stu_classroom_id_63b3b2e3_fk_course_cl` FOREIGN KEY (`classroom_id`) REFERENCES `course_classroom` (`id`),
  CONSTRAINT `course_classroom_stu_student_id_4e5d6532_fk_student_s` FOREIGN KEY (`student_id`) REFERENCES `student_student` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_classroom_students`
--

LOCK TABLES `course_classroom_students` WRITE;
/*!40000 ALTER TABLE `course_classroom_students` DISABLE KEYS */;
/*!40000 ALTER TABLE `course_classroom_students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_course`
--

DROP TABLE IF EXISTS `course_course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_course` (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_name` varchar(100) NOT NULL,
  `course_code` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_course`
--

LOCK TABLES `course_course` WRITE;
/*!40000 ALTER TABLE `course_course` DISABLE KEYS */;
INSERT INTO `course_course` VALUES (12,'Curso Exemplo','CE');
/*!40000 ALTER TABLE `course_course` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_course_course_coords`
--

DROP TABLE IF EXISTS `course_course_course_coords`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_course_course_coords` (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `course_course_course_coords_course_id_user_id_3c160231_uniq` (`course_id`,`user_id`),
  KEY `course_course_course_coords_user_id_53b67b4c_fk_account_user_id` (`user_id`),
  CONSTRAINT `course_course_course_coords_user_id_53b67b4c_fk_account_user_id` FOREIGN KEY (`user_id`) REFERENCES `account_user` (`id`),
  CONSTRAINT `course_course_course_course_id_27d06245_fk_course_co` FOREIGN KEY (`course_id`) REFERENCES `course_course` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_course_course_coords`
--

LOCK TABLES `course_course_course_coords` WRITE;
/*!40000 ALTER TABLE `course_course_course_coords` DISABLE KEYS */;
/*!40000 ALTER TABLE `course_course_course_coords` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_course_course_profs`
--

DROP TABLE IF EXISTS `course_course_course_profs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_course_course_profs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `course_course_course_profs_course_id_user_id_ae382174_uniq` (`course_id`,`user_id`),
  KEY `course_course_course_profs_user_id_0905c765_fk_account_user_id` (`user_id`),
  CONSTRAINT `course_course_course_course_id_413fe2f9_fk_course_co` FOREIGN KEY (`course_id`) REFERENCES `course_course` (`id`),
  CONSTRAINT `course_course_course_profs_user_id_0905c765_fk_account_user_id` FOREIGN KEY (`user_id`) REFERENCES `account_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_course_course_profs`
--

LOCK TABLES `course_course_course_profs` WRITE;
/*!40000 ALTER TABLE `course_course_course_profs` DISABLE KEYS */;
/*!40000 ALTER TABLE `course_course_course_profs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_course_institutes`
--

DROP TABLE IF EXISTS `course_course_institutes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_course_institutes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_id` int NOT NULL,
  `institute_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `course_course_institutes_course_id_institute_id_b41037d4_uniq` (`course_id`,`institute_id`),
  KEY `course_course_instit_institute_id_9fa7b95c_fk_course_in` (`institute_id`),
  CONSTRAINT `course_course_instit_institute_id_9fa7b95c_fk_course_in` FOREIGN KEY (`institute_id`) REFERENCES `course_institute` (`id`),
  CONSTRAINT `course_course_institutes_course_id_4721f5a6_fk_course_course_id` FOREIGN KEY (`course_id`) REFERENCES `course_course` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_course_institutes`
--

LOCK TABLES `course_course_institutes` WRITE;
/*!40000 ALTER TABLE `course_course_institutes` DISABLE KEYS */;
INSERT INTO `course_course_institutes` VALUES (12,12,3);
/*!40000 ALTER TABLE `course_course_institutes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_discipline`
--

DROP TABLE IF EXISTS `course_discipline`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_discipline` (
  `id` int NOT NULL AUTO_INCREMENT,
  `discipline_name` varchar(100) NOT NULL,
  `discipline_code` varchar(20) NOT NULL,
  `discipline_objective` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_discipline`
--

LOCK TABLES `course_discipline` WRITE;
/*!40000 ALTER TABLE `course_discipline` DISABLE KEYS */;
INSERT INTO `course_discipline` VALUES (51,'Disciplina Exemplo','DE','');
/*!40000 ALTER TABLE `course_discipline` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_discipline_courses`
--

DROP TABLE IF EXISTS `course_discipline_courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_discipline_courses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `discipline_id` int NOT NULL,
  `course_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `course_discipline_courses_discipline_id_course_id_ae298cd6_uniq` (`discipline_id`,`course_id`),
  KEY `course_discipline_courses_course_id_9b08f936_fk_course_course_id` (`course_id`),
  CONSTRAINT `course_discipline_co_discipline_id_58803173_fk_course_di` FOREIGN KEY (`discipline_id`) REFERENCES `course_discipline` (`id`),
  CONSTRAINT `course_discipline_courses_course_id_9b08f936_fk_course_course_id` FOREIGN KEY (`course_id`) REFERENCES `course_course` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_discipline_courses`
--

LOCK TABLES `course_discipline_courses` WRITE;
/*!40000 ALTER TABLE `course_discipline_courses` DISABLE KEYS */;
INSERT INTO `course_discipline_courses` VALUES (1,51,12);
/*!40000 ALTER TABLE `course_discipline_courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_discipline_discipline_coords`
--

DROP TABLE IF EXISTS `course_discipline_discipline_coords`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_discipline_discipline_coords` (
  `id` int NOT NULL AUTO_INCREMENT,
  `discipline_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `course_discipline_discip_discipline_id_user_id_b9c7dd19_uniq` (`discipline_id`,`user_id`),
  KEY `course_discipline_di_user_id_1b546641_fk_account_u` (`user_id`),
  CONSTRAINT `course_discipline_di_discipline_id_dffbcc8f_fk_course_di` FOREIGN KEY (`discipline_id`) REFERENCES `course_discipline` (`id`),
  CONSTRAINT `course_discipline_di_user_id_1b546641_fk_account_u` FOREIGN KEY (`user_id`) REFERENCES `account_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_discipline_discipline_coords`
--

LOCK TABLES `course_discipline_discipline_coords` WRITE;
/*!40000 ALTER TABLE `course_discipline_discipline_coords` DISABLE KEYS */;
INSERT INTO `course_discipline_discipline_coords` VALUES (1,51,1);
/*!40000 ALTER TABLE `course_discipline_discipline_coords` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_discipline_discipline_profs`
--

DROP TABLE IF EXISTS `course_discipline_discipline_profs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_discipline_discipline_profs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `discipline_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `course_discipline_discip_discipline_id_user_id_d73b9cdc_uniq` (`discipline_id`,`user_id`),
  KEY `course_discipline_di_user_id_af64824b_fk_account_u` (`user_id`),
  CONSTRAINT `course_discipline_di_discipline_id_8f7f8690_fk_course_di` FOREIGN KEY (`discipline_id`) REFERENCES `course_discipline` (`id`),
  CONSTRAINT `course_discipline_di_user_id_af64824b_fk_account_u` FOREIGN KEY (`user_id`) REFERENCES `account_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_discipline_discipline_profs`
--

LOCK TABLES `course_discipline_discipline_profs` WRITE;
/*!40000 ALTER TABLE `course_discipline_discipline_profs` DISABLE KEYS */;
INSERT INTO `course_discipline_discipline_profs` VALUES (2,51,1),(1,51,65),(3,51,66);
/*!40000 ALTER TABLE `course_discipline_discipline_profs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_institute`
--

DROP TABLE IF EXISTS `course_institute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_institute` (
  `id` int NOT NULL AUTO_INCREMENT,
  `institute_name` varchar(50) NOT NULL,
  `institute_code` varchar(20) NOT NULL,
  `institute_logo` varchar(20) NOT NULL,
  `institute_url` varchar(20) NOT NULL,
  `institute_exams_generated` int NOT NULL,
  `institute_exams_corrected` int NOT NULL,
  `institute_questions_corrected` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_institute`
--

LOCK TABLES `course_institute` WRITE;
/*!40000 ALTER TABLE `course_institute` DISABLE KEYS */;
INSERT INTO `course_institute` VALUES (3,'Instituto Exemplo','IE','logo','www.ufabc.edu.br',6,0,0);
/*!40000 ALTER TABLE `course_institute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_institute_institute_coords`
--

DROP TABLE IF EXISTS `course_institute_institute_coords`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_institute_institute_coords` (
  `id` int NOT NULL AUTO_INCREMENT,
  `institute_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `course_institute_institu_institute_id_user_id_0b9d4aa2_uniq` (`institute_id`,`user_id`),
  KEY `course_institute_ins_user_id_f3a649aa_fk_account_u` (`user_id`),
  CONSTRAINT `course_institute_ins_institute_id_c82b8224_fk_course_in` FOREIGN KEY (`institute_id`) REFERENCES `course_institute` (`id`),
  CONSTRAINT `course_institute_ins_user_id_f3a649aa_fk_account_u` FOREIGN KEY (`user_id`) REFERENCES `account_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_institute_institute_coords`
--

LOCK TABLES `course_institute_institute_coords` WRITE;
/*!40000 ALTER TABLE `course_institute_institute_coords` DISABLE KEYS */;
/*!40000 ALTER TABLE `course_institute_institute_coords` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_institute_institute_profs`
--

DROP TABLE IF EXISTS `course_institute_institute_profs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_institute_institute_profs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `institute_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `course_institute_institu_institute_id_user_id_93b32325_uniq` (`institute_id`,`user_id`),
  KEY `course_institute_ins_user_id_f4e4ff24_fk_account_u` (`user_id`),
  CONSTRAINT `course_institute_ins_institute_id_b610787d_fk_course_in` FOREIGN KEY (`institute_id`) REFERENCES `course_institute` (`id`),
  CONSTRAINT `course_institute_ins_user_id_f4e4ff24_fk_account_u` FOREIGN KEY (`user_id`) REFERENCES `account_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_institute_institute_profs`
--

LOCK TABLES `course_institute_institute_profs` WRITE;
/*!40000 ALTER TABLE `course_institute_institute_profs` DISABLE KEYS */;
/*!40000 ALTER TABLE `course_institute_institute_profs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_account_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_account_user_id` FOREIGN KEY (`user_id`) REFERENCES `account_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1198 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2019-01-22 19:23:32.936912','1','coordenador',1,'[{\"added\": {}}]',3,1),(2,'2019-01-22 19:24:16.435423','1','coordenador',2,'[{\"changed\": {\"fields\": [\"permissions\"]}}]',3,1),(3,'2019-01-22 19:25:07.076121','2','professor',1,'[{\"added\": {}}]',3,1),(4,'2019-01-22 19:25:20.297401','2','rafaela.rocha@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(5,'2019-01-22 19:25:32.975848','1','fzampirolli@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(6,'2019-01-22 19:25:43.488692','2','rafaela.rocha@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(7,'2019-01-22 19:28:34.037321','4','fzcoord@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(8,'2019-01-24 13:02:05.530940','5','fzstudent@ufabc.edu.br',3,'',17,1),(9,'2019-01-24 13:02:05.560157','51','fzstudent1@ufabc.edu.br',3,'',17,1),(10,'2019-01-24 14:02:05.888518','2','rafaela.rocha@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(11,'2019-01-24 18:25:59.327593','4','BCM0505 - 08h-SA-DA1,10h-SB-DA2 - teste1',3,'',13,1),(12,'2019-01-24 18:25:59.362338','5','BCM0505 - 08h-SA-DA1,10h-SB-DA2 - teste2',3,'',13,1),(13,'2019-01-24 18:25:59.446145','4','BCM0505 - 08h-SA-DA1,10h-SB-DA2 - teste1',3,'',13,1),(14,'2019-01-24 18:25:59.522979','5','BCM0505 - 08h-SA-DA1,10h-SB-DA2 - teste2',3,'',13,1),(15,'2019-01-24 19:12:40.362145','8','BCM0505 - 08h-SA-DA1,10h-SB-DA2 - Prova 1',3,'',13,1),(16,'2019-01-24 19:12:40.418037','8','BCM0505 - 08h-SA-DA1,10h-SB-DA2 - Prova 1',3,'',13,1),(17,'2019-01-30 17:20:49.242258','52','aline.lima@mj.gov.br',2,'[{\"changed\": {\"fields\": [\"groups\", \"last_login\"]}}]',17,1),(18,'2019-01-30 18:20:32.423858','52','aline.lima@mj.gov.br',2,'[{\"changed\": {\"fields\": [\"first_name\", \"last_name\"]}}]',17,1),(19,'2019-01-31 07:47:32.415595','52','aline.lima@mj.gov.br',2,'[{\"changed\": {\"fields\": [\"first_name\", \"last_name\"]}}]',17,1),(20,'2019-02-08 15:41:19.643541','9','BCM0505 - teste_teo - Prova 1',3,'',13,1),(21,'2019-02-15 09:29:46.933262','2','rafaela.rocha@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(22,'2019-02-15 09:30:53.816549','52','aline.lima@mj.gov.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(23,'2019-02-15 18:45:46.958843','56','sandra.trevisan@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"last_name\", \"groups\"]}}]',17,1),(24,'2019-02-15 18:46:35.130867','55','steil@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"last_name\", \"groups\"]}}]',17,1),(25,'2019-02-15 18:56:29.867630','56','sandra.trevisan@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(26,'2019-02-15 19:48:47.789421','1','fzampirolli@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"last_name\"]}}]',17,1),(27,'2019-02-15 20:08:36.803986','77','EP-sel - A101_0',3,'',12,1),(28,'2019-02-15 20:08:36.833140','78','EP-sel - A102_0',3,'',12,1),(29,'2019-02-15 20:08:36.907370','79','EP-sel - A103_0',3,'',12,1),(30,'2019-02-15 20:08:36.934386','80','EP-sel - A104_0',3,'',12,1),(31,'2019-02-15 20:08:36.959398','81','EP-sel - A105_0',3,'',12,1),(32,'2019-02-15 20:08:36.984403','82','EP-sel - A106_0',3,'',12,1),(33,'2019-02-15 20:08:37.009643','83','EP-sel - A107_0',3,'',12,1),(34,'2019-02-15 20:08:37.034791','84','EP-sel - A108_0',3,'',12,1),(35,'2019-02-15 20:08:37.059953','85','EP-sel - A109_0',3,'',12,1),(36,'2019-02-15 20:08:37.085045','86','EP-sel - A110_0',3,'',12,1),(37,'2019-02-15 20:08:37.110298','87','EP-sel - A113_0',3,'',12,1),(38,'2019-02-15 20:08:37.136677','88','EP-sel - A114_0',3,'',12,1),(39,'2019-02-15 20:08:37.170114','89','EP-sel - A211_0',3,'',12,1),(40,'2019-02-15 20:08:37.203358','90','EP-sel - A212_0',3,'',12,1),(41,'2019-02-15 20:08:37.237182','91','EP-sel - L407_2',3,'',12,1),(42,'2019-02-15 20:08:37.270679','76','EP-sel - S006_0',3,'',12,1),(43,'2019-02-15 20:10:06.938040','92','EP-sel - S204_0',3,'',12,1),(44,'2019-02-15 20:10:06.971833','93','EP-sel - S205_0',3,'',12,1),(45,'2019-02-15 20:10:07.005895','94','EP-sel - S206_0',3,'',12,1),(46,'2019-02-15 20:10:07.039355','95','EP-sel - S207_0',3,'',12,1),(47,'2019-02-15 20:10:07.072883','96','EP-sel - S208_0',3,'',12,1),(48,'2019-02-15 20:10:07.106354','97','EP-sel - S209_0',3,'',12,1),(49,'2019-02-15 20:10:07.205222','98','EP-sel - S210_0',3,'',12,1),(50,'2019-02-15 20:10:07.240315','99','EP-sel - S213_0',3,'',12,1),(51,'2019-02-15 20:10:07.273834','100','EP-sel - S214_0',3,'',12,1),(52,'2019-02-15 20:10:07.307455','101','EP-sel - S301_1',3,'',12,1),(53,'2019-02-15 20:10:07.332730','102','EP-sel - S301_2',3,'',12,1),(54,'2019-02-15 20:10:07.357921','103','EP-sel - S302_1',3,'',12,1),(55,'2019-02-15 20:10:07.383048','104','EP-sel - S302_2',3,'',12,1),(56,'2019-02-15 20:10:07.408181','105','EP-sel - S305_1',3,'',12,1),(57,'2019-02-15 20:10:07.433367','106','EP-sel - S305_2',3,'',12,1),(58,'2019-02-15 20:10:07.458545','107','EP-sel - S306_1',3,'',12,1),(59,'2019-02-15 20:10:07.483667','108','EP-sel - S307_1',3,'',12,1),(60,'2019-02-15 20:10:07.508831','109','EP-sel - S307_2',3,'',12,1),(61,'2019-02-15 20:10:07.534002','110','EP-sel - S308_1',3,'',12,1),(62,'2019-02-15 20:10:07.559525','111','EP-sel - S311_1',3,'',12,1),(63,'2019-02-15 20:10:07.584245','112','EP-sel - S311_2',3,'',12,1),(64,'2019-02-15 20:15:28.304630','56','sandra.trevisan@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(65,'2019-02-15 20:16:00.801282','56','sandra.trevisan@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(66,'2019-02-18 10:58:51.380289','56','sandra.trevisan@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(67,'2019-02-18 10:59:16.292014','55','steil@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(68,'2019-02-18 10:59:34.612433','1','fzampirolli@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"last_name\"]}}]',17,1),(69,'2019-03-14 23:54:46.882266','57','',1,'[{\"added\": {}}]',17,1),(70,'2019-03-14 23:55:31.595784','57','luciana.milena@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"first_name\", \"last_name\", \"email\", \"groups\"]}}]',17,1),(71,'2019-03-15 18:42:54.887408','58','ana.muta@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"last_name\"]}}]',17,1),(72,'2019-03-15 19:02:05.860439','3','fzprof@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"last_name\"]}}]',17,1),(73,'2019-03-15 20:44:40.419255','58','ana.muta@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(74,'2019-03-15 21:20:22.208327','6905','Nathalia Florencio Peres-nathaliafperes@gmail.com',1,'[{\"added\": {}}]',16,1),(75,'2019-03-15 21:22:37.366841','155','CLIP - A-101-0',2,'[{\"changed\": {\"fields\": [\"students\"]}}]',12,1),(76,'2019-03-15 23:08:02.648837','163','MCTA033 - NA2',2,'[{\"changed\": {\"fields\": [\"classroom_profs\"]}}]',12,1),(77,'2019-04-08 13:18:01.049208','3','fzprof@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"last_name\"]}}]',17,1),(78,'2019-05-21 10:06:11.081053','60','',1,'[{\"added\": {}}]',17,1),(79,'2019-05-21 10:06:33.798719','60','guiou@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"first_name\", \"last_name\", \"email\", \"groups\"]}}]',17,1),(80,'2019-05-21 10:07:30.677483','61','',1,'[{\"added\": {}}]',17,1),(81,'2019-05-21 10:07:52.547935','61','ercilio.silva@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"first_name\", \"last_name\", \"email\", \"groups\"]}}]',17,1),(82,'2019-05-21 10:08:42.624964','62','',1,'[{\"added\": {}}]',17,1),(83,'2019-05-21 10:08:55.897412','62','joao.moreira@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"first_name\", \"last_name\", \"email\", \"groups\"]}}]',17,1),(84,'2019-05-21 10:09:41.490384','63','',1,'[{\"added\": {}}]',17,1),(85,'2019-05-21 10:09:57.324343','63','jorge.tomioka@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"first_name\", \"last_name\", \"email\", \"groups\"]}}]',17,1),(86,'2019-05-21 10:40:11.681851','45','[BCM0505]<repeticao>',2,'[{\"changed\": {\"fields\": [\"discipline\"]}}]',6,1),(87,'2019-05-21 10:42:14.840986','45','[BCM0505]<repeticao>',3,'',6,1),(88,'2019-05-22 12:17:03.128571','20','BCM0505 - test-teo - Prova 1 teo3a08h',2,'[{\"changed\": {\"fields\": [\"classrooms\"]}}]',13,1),(89,'2019-05-22 12:19:02.357147','55','BCM0505 - test-lab - P2-B3B4-SB',2,'[{\"changed\": {\"fields\": [\"classrooms\"]}}]',13,1),(90,'2019-05-22 12:34:55.425091','11',' -  - Ciclo 45',3,'',13,1),(91,'2019-05-22 12:36:46.565051','35',' -  - Nivelamento',3,'',13,1),(92,'2019-05-22 12:43:11.370550','28','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 1 lab10h',3,'',13,1),(93,'2019-05-22 12:43:11.418738','65','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 2',3,'',13,1),(94,'2019-05-22 12:43:11.468597','28','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 1 lab10h',3,'',13,1),(95,'2019-05-22 12:43:11.511198','65','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 2',3,'',13,1),(96,'2019-05-22 12:43:11.551911','28','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 1 lab10h',3,'',13,1),(97,'2019-05-22 12:43:11.593804','65','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 2',3,'',13,1),(98,'2019-05-22 12:43:11.658753','28','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 1 lab10h',3,'',13,1),(99,'2019-05-22 12:43:11.711856','65','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 2',3,'',13,1),(100,'2019-05-22 12:43:11.752903','28','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 1 lab10h',3,'',13,1),(101,'2019-05-22 12:43:11.795100','65','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 2',3,'',13,1),(102,'2019-05-22 12:43:11.836464','28','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 1 lab10h',3,'',13,1),(103,'2019-05-22 12:43:11.879955','65','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 2',3,'',13,1),(104,'2019-05-22 12:43:11.921421','28','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 1 lab10h',3,'',13,1),(105,'2019-05-22 12:43:11.962955','65','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 2',3,'',13,1),(106,'2019-05-22 12:43:12.005240','28','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 1 lab10h',3,'',13,1),(107,'2019-05-22 12:43:12.046910','65','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 2',3,'',13,1),(108,'2019-05-22 12:43:12.089301','28','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 1 lab10h',3,'',13,1),(109,'2019-05-22 12:43:12.131792','65','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 2',3,'',13,1),(110,'2019-05-22 12:43:12.173089','28','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 1 lab10h',3,'',13,1),(111,'2019-05-22 12:43:12.214520','65','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 2',3,'',13,1),(112,'2019-05-22 12:43:12.256641','28','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 1 lab10h',3,'',13,1),(113,'2019-05-22 12:43:12.298554','65','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 2',3,'',13,1),(114,'2019-05-22 12:43:12.340281','28','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 1 lab10h',3,'',13,1),(115,'2019-05-22 12:43:12.381534','65','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 2',3,'',13,1),(116,'2019-05-22 12:43:12.423527','28','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 1 lab10h',3,'',13,1),(117,'2019-05-22 12:43:12.465622','65','BCM0505 - 10-DA1-SA,10-DA1-SB,10-DA2-SA,10-DA2-SB,10-DA3-SA,10-DA3-SB,10-DA4-SA,10-DA4-SB,10-DA5-SA,10-DA6-SA,10-DA7-SA,10-DA8-SA,10-DA9-SA - Prova 2',3,'',13,1),(118,'2019-05-22 12:43:12.502693','29','BCM0505 - 19-NB1-SA,19-NB1-SB,19-NB2-SB,19-NB4-SA,19-NB5-SA,19-NB7-SA,19-NB8-SA,19-NB9-SA - Prova 1 lab19h',3,'',13,1),(119,'2019-05-22 12:43:12.545017','29','BCM0505 - 19-NB1-SA,19-NB1-SB,19-NB2-SB,19-NB4-SA,19-NB5-SA,19-NB7-SA,19-NB8-SA,19-NB9-SA - Prova 1 lab19h',3,'',13,1),(120,'2019-05-22 12:43:12.581387','22','BCM0505 - 19-NB12-SB,19-NB145-SA,19-NB789-SA - Prova 1 teo3a19h',3,'',13,1),(121,'2019-05-22 12:43:12.617103','22','BCM0505 - 19-NB12-SB,19-NB145-SA,19-NB789-SA - Prova 1 teo3a19h',3,'',13,1),(122,'2019-05-22 12:43:12.664531','29','BCM0505 - 19-NB1-SA,19-NB1-SB,19-NB2-SB,19-NB4-SA,19-NB5-SA,19-NB7-SA,19-NB8-SA,19-NB9-SA - Prova 1 lab19h',3,'',13,1),(123,'2019-05-22 12:43:12.703648','29','BCM0505 - 19-NB1-SA,19-NB1-SB,19-NB2-SB,19-NB4-SA,19-NB5-SA,19-NB7-SA,19-NB8-SA,19-NB9-SA - Prova 1 lab19h',3,'',13,1),(124,'2019-05-22 12:43:12.745340','29','BCM0505 - 19-NB1-SA,19-NB1-SB,19-NB2-SB,19-NB4-SA,19-NB5-SA,19-NB7-SA,19-NB8-SA,19-NB9-SA - Prova 1 lab19h',3,'',13,1),(125,'2019-05-22 12:43:12.787300','29','BCM0505 - 19-NB1-SA,19-NB1-SB,19-NB2-SB,19-NB4-SA,19-NB5-SA,19-NB7-SA,19-NB8-SA,19-NB9-SA - Prova 1 lab19h',3,'',13,1),(126,'2019-05-22 12:43:12.824384','22','BCM0505 - 19-NB12-SB,19-NB145-SA,19-NB789-SA - Prova 1 teo3a19h',3,'',13,1),(127,'2019-05-22 12:43:12.864908','29','BCM0505 - 19-NB1-SA,19-NB1-SB,19-NB2-SB,19-NB4-SA,19-NB5-SA,19-NB7-SA,19-NB8-SA,19-NB9-SA - Prova 1 lab19h',3,'',13,1),(128,'2019-05-22 12:43:12.904489','29','BCM0505 - 19-NB1-SA,19-NB1-SB,19-NB2-SB,19-NB4-SA,19-NB5-SA,19-NB7-SA,19-NB8-SA,19-NB9-SA - Prova 1 lab19h',3,'',13,1),(129,'2019-05-22 12:43:13.035817','30','BCM0505 - 21-NA1-SA,21-NA1-SB,21-NA2-SA,21-NA2-SB,21-NA3-SA,21-NA3-SB,21-NA4-SA,21-NA4-SB,21-NA5-SA,21-NA6-SA,21-NA7-SA,21-NA8-SA,21-NA9-SA - Prova 1 lab21h',3,'',13,1),(130,'2019-05-22 12:43:13.084158','30','BCM0505 - 21-NA1-SA,21-NA1-SB,21-NA2-SA,21-NA2-SB,21-NA3-SA,21-NA3-SB,21-NA4-SA,21-NA4-SB,21-NA5-SA,21-NA6-SA,21-NA7-SA,21-NA8-SA,21-NA9-SA - Prova 1 lab21h',3,'',13,1),(131,'2019-05-22 12:43:13.134671','30','BCM0505 - 21-NA1-SA,21-NA1-SB,21-NA2-SA,21-NA2-SB,21-NA3-SA,21-NA3-SB,21-NA4-SA,21-NA4-SB,21-NA5-SA,21-NA6-SA,21-NA7-SA,21-NA8-SA,21-NA9-SA - Prova 1 lab21h',3,'',13,1),(132,'2019-05-22 12:43:13.184835','30','BCM0505 - 21-NA1-SA,21-NA1-SB,21-NA2-SA,21-NA2-SB,21-NA3-SA,21-NA3-SB,21-NA4-SA,21-NA4-SB,21-NA5-SA,21-NA6-SA,21-NA7-SA,21-NA8-SA,21-NA9-SA - Prova 1 lab21h',3,'',13,1),(133,'2019-05-22 12:43:13.234396','30','BCM0505 - 21-NA1-SA,21-NA1-SB,21-NA2-SA,21-NA2-SB,21-NA3-SA,21-NA3-SB,21-NA4-SA,21-NA4-SB,21-NA5-SA,21-NA6-SA,21-NA7-SA,21-NA8-SA,21-NA9-SA - Prova 1 lab21h',3,'',13,1),(134,'2019-05-22 12:43:13.284270','30','BCM0505 - 21-NA1-SA,21-NA1-SB,21-NA2-SA,21-NA2-SB,21-NA3-SA,21-NA3-SB,21-NA4-SA,21-NA4-SB,21-NA5-SA,21-NA6-SA,21-NA7-SA,21-NA8-SA,21-NA9-SA - Prova 1 lab21h',3,'',13,1),(135,'2019-05-22 12:43:13.334680','30','BCM0505 - 21-NA1-SA,21-NA1-SB,21-NA2-SA,21-NA2-SB,21-NA3-SA,21-NA3-SB,21-NA4-SA,21-NA4-SB,21-NA5-SA,21-NA6-SA,21-NA7-SA,21-NA8-SA,21-NA9-SA - Prova 1 lab21h',3,'',13,1),(136,'2019-05-22 12:43:13.384620','30','BCM0505 - 21-NA1-SA,21-NA1-SB,21-NA2-SA,21-NA2-SB,21-NA3-SA,21-NA3-SB,21-NA4-SA,21-NA4-SB,21-NA5-SA,21-NA6-SA,21-NA7-SA,21-NA8-SA,21-NA9-SA - Prova 1 lab21h',3,'',13,1),(137,'2019-05-22 12:43:13.435239','30','BCM0505 - 21-NA1-SA,21-NA1-SB,21-NA2-SA,21-NA2-SB,21-NA3-SA,21-NA3-SB,21-NA4-SA,21-NA4-SB,21-NA5-SA,21-NA6-SA,21-NA7-SA,21-NA8-SA,21-NA9-SA - Prova 1 lab21h',3,'',13,1),(138,'2019-05-22 12:43:13.485211','30','BCM0505 - 21-NA1-SA,21-NA1-SB,21-NA2-SA,21-NA2-SB,21-NA3-SA,21-NA3-SB,21-NA4-SA,21-NA4-SB,21-NA5-SA,21-NA6-SA,21-NA7-SA,21-NA8-SA,21-NA9-SA - Prova 1 lab21h',3,'',13,1),(139,'2019-05-22 12:43:13.538301','30','BCM0505 - 21-NA1-SA,21-NA1-SB,21-NA2-SA,21-NA2-SB,21-NA3-SA,21-NA3-SB,21-NA4-SA,21-NA4-SB,21-NA5-SA,21-NA6-SA,21-NA7-SA,21-NA8-SA,21-NA9-SA - Prova 1 lab21h',3,'',13,1),(140,'2019-05-22 12:43:13.577346','30','BCM0505 - 21-NA1-SA,21-NA1-SB,21-NA2-SA,21-NA2-SB,21-NA3-SA,21-NA3-SB,21-NA4-SA,21-NA4-SB,21-NA5-SA,21-NA6-SA,21-NA7-SA,21-NA8-SA,21-NA9-SA - Prova 1 lab21h',3,'',13,1),(141,'2019-05-22 12:43:13.627637','30','BCM0505 - 21-NA1-SA,21-NA1-SB,21-NA2-SA,21-NA2-SB,21-NA3-SA,21-NA3-SB,21-NA4-SA,21-NA4-SB,21-NA5-SA,21-NA6-SA,21-NA7-SA,21-NA8-SA,21-NA9-SA - Prova 1 lab21h',3,'',13,1),(142,'2019-05-22 19:06:27.652279','53','BCM0505 - 08-DB1-SA',3,'',12,1),(143,'2019-05-22 19:06:27.682203','54','BCM0505 - 08-DB1-SB',3,'',12,1),(144,'2019-05-22 19:06:27.707490','20','BCM0505 - 08-DB12-SB',3,'',12,1),(145,'2019-05-22 19:06:27.732893','19','BCM0505 - 08-DB123-SA',3,'',12,1),(146,'2019-05-22 19:06:27.757914','57','BCM0505 - 08-DB2-SA',3,'',12,1),(147,'2019-05-22 19:06:27.783016','58','BCM0505 - 08-DB2-SB',3,'',12,1),(148,'2019-05-22 19:06:27.816616','60','BCM0505 - 08-DB3-SA',3,'',12,1),(149,'2019-05-22 19:06:27.850182','61','BCM0505 - 08-DB3-SB',3,'',12,1),(150,'2019-05-22 19:06:27.883671','185','BCM0505 - 08-DB34-SB',3,'',12,1),(151,'2019-05-22 19:06:27.917255','62','BCM0505 - 08-DB4-SA',3,'',12,1),(152,'2019-05-22 19:06:27.950728','63','BCM0505 - 08-DB4-SB',3,'',12,1),(153,'2019-05-22 19:06:27.984130','24','BCM0505 - 08-DB458-SA',3,'',12,1),(154,'2019-05-22 19:06:28.017581','65','BCM0505 - 08-DB5-SA',3,'',12,1),(155,'2019-05-22 19:06:28.051096','68','BCM0505 - 08-DB8-SA',3,'',12,1),(156,'2019-05-22 19:06:28.084646','27','BCM0505 - 10-DA1-SA',3,'',12,1),(157,'2019-05-22 19:06:28.118057','28','BCM0505 - 10-DA1-SB',3,'',12,1),(158,'2019-05-22 19:06:28.151581','10','BCM0505 - 10-DA12-SB',3,'',12,1),(159,'2019-05-22 19:06:28.233317','9','BCM0505 - 10-DA123-SA',3,'',12,1),(160,'2019-05-22 19:06:28.269066','31','BCM0505 - 10-DA2-SA',3,'',12,1),(161,'2019-05-22 19:06:28.302614','32','BCM0505 - 10-DA2-SB',3,'',12,1),(162,'2019-05-22 19:06:28.335932','35','BCM0505 - 10-DA3-SA',3,'',12,1),(163,'2019-05-22 19:06:28.369317','36','BCM0505 - 10-DA3-SB',3,'',12,1),(164,'2019-05-22 19:06:28.403773','13','BCM0505 - 10-DA34-SB',3,'',12,1),(165,'2019-05-22 19:06:28.436706','39','BCM0505 - 10-DA4-SA',3,'',12,1),(166,'2019-05-22 19:06:28.469766','40','BCM0505 - 10-DA4-SB',3,'',12,1),(167,'2019-05-22 19:06:28.503210','15','BCM0505 - 10-DA456-SA',3,'',12,1),(168,'2019-05-22 19:06:28.536679','43','BCM0505 - 10-DA5-SA',3,'',12,1),(169,'2019-05-22 19:06:28.570198','45','BCM0505 - 10-DA6-SA',3,'',12,1),(170,'2019-05-22 19:06:28.603672','47','BCM0505 - 10-DA7-SA',3,'',12,1),(171,'2019-05-22 19:06:28.637215','17','BCM0505 - 10-DA789-SA',3,'',12,1),(172,'2019-05-22 19:06:28.670678','49','BCM0505 - 10-DA8-SA',3,'',12,1),(173,'2019-05-22 19:06:28.704191','51','BCM0505 - 10-DA9-SA',3,'',12,1),(174,'2019-05-22 19:06:28.737741','55','BCM0505 - 19-NB1-SA',3,'',12,1),(175,'2019-05-22 19:06:28.771127','56','BCM0505 - 19-NB1-SB',3,'',12,1),(176,'2019-05-22 19:06:28.805705','22','BCM0505 - 19-NB12-SB',3,'',12,1),(177,'2019-05-22 19:06:28.839333','21','BCM0505 - 19-NB145-SA',3,'',12,1),(178,'2019-05-22 19:06:28.872837','59','BCM0505 - 19-NB2-SB',3,'',12,1),(179,'2019-05-22 19:06:28.906316','64','BCM0505 - 19-NB4-SA',3,'',12,1),(180,'2019-05-22 19:06:28.931479','66','BCM0505 - 19-NB5-SA',3,'',12,1),(181,'2019-05-22 19:06:28.956523','67','BCM0505 - 19-NB7-SA',3,'',12,1),(182,'2019-05-22 19:06:28.981806','25','BCM0505 - 19-NB789-SA',3,'',12,1),(183,'2019-05-22 19:06:29.006957','69','BCM0505 - 19-NB8-SA',3,'',12,1),(184,'2019-05-22 19:06:29.032087','70','BCM0505 - 19-NB9-SA',3,'',12,1),(185,'2019-05-22 19:06:29.057196','29','BCM0505 - 21-NA1-SA',3,'',12,1),(186,'2019-05-22 19:06:29.082382','30','BCM0505 - 21-NA1-SB',3,'',12,1),(187,'2019-05-22 19:06:29.107553','12','BCM0505 - 21-NA12-SB',3,'',12,1),(188,'2019-05-22 19:06:29.132721','11','BCM0505 - 21-NA123-SA',3,'',12,1),(189,'2019-05-22 19:06:29.157831','33','BCM0505 - 21-NA2-SA',3,'',12,1),(190,'2019-05-22 19:06:29.182809','34','BCM0505 - 21-NA2-SB',3,'',12,1),(191,'2019-05-22 19:06:29.208073','37','BCM0505 - 21-NA3-SA',3,'',12,1),(192,'2019-05-22 19:06:29.233242','38','BCM0505 - 21-NA3-SB',3,'',12,1),(193,'2019-05-22 19:06:29.292202','14','BCM0505 - 21-NA34-SB',3,'',12,1),(194,'2019-05-22 19:06:29.325706','41','BCM0505 - 21-NA4-SA',3,'',12,1),(195,'2019-05-22 19:06:29.359117','42','BCM0505 - 21-NA4-SB',3,'',12,1),(196,'2019-05-22 19:06:29.392705','18','BCM0505 - 21-NA789-SA',3,'',12,1),(197,'2019-05-22 19:06:29.426830','50','BCM0505 - 21-NA8-SA',3,'',12,1),(198,'2019-05-22 19:06:29.459730','52','BCM0505 - 21-NA9-SA',3,'',12,1),(199,'2019-05-22 19:06:29.493234','26','BCM0505 - DEaD-SA-SB',3,'',12,1),(200,'2019-05-22 19:06:29.526703','165','BCM0505 - NA2BCM0505',3,'',12,1),(201,'2019-05-22 19:06:29.560104','187','BCM0505 - NA4BCM0505-15SA',3,'',12,1),(202,'2019-05-22 19:06:29.593585','176','BCM0505 - PI-EaD-SA',3,'',12,1),(203,'2019-05-22 19:06:29.627085','71','BCM0505 - PI-EaD-SA-212',3,'',12,1),(204,'2019-05-22 19:06:29.660490','151','BCM0505 - PI-EaD-SA-213',3,'',12,1),(205,'2019-05-22 19:06:29.694107','179','BCM0505 - PI-EaD-SA-L404',3,'',12,1),(206,'2019-05-22 19:06:29.727538','180','BCM0505 - PI-EaD-SA-L407',3,'',12,1),(207,'2019-05-22 19:06:29.761155','181','BCM0505 - PI-EaD-SA-L409',3,'',12,1),(208,'2019-05-22 19:06:29.794511','72','BCM0505 - PI-EaD-SB',3,'',12,1),(209,'2019-05-22 19:06:29.828075','182','BCM0505 - PI-EaD-SB-A1L102',3,'',12,1),(210,'2019-05-22 19:08:15.100044','68',' -  - BCM0505-10-NA3-SB',3,'',13,1),(211,'2019-05-22 19:08:15.127453','69',' -  - BCM0505-21-NA3-SB',3,'',13,1),(212,'2019-05-22 19:08:15.152982','67',' -  - BCM0505-DB4SB-Pratic',3,'',13,1),(213,'2019-05-22 19:08:15.178902','42',' -  - P1-DA1-SB',3,'',13,1),(214,'2019-05-22 19:08:15.212478','39',' -  - P1-DB1-SB',3,'',13,1),(215,'2019-05-22 19:08:15.246071','44',' -  - P1-NA1-SB',3,'',13,1),(216,'2019-05-22 19:08:15.279530','43',' -  - P1-NB1-SB',3,'',13,1),(217,'2019-05-22 19:08:15.313015','60',' -  - P2-DA1-SB',3,'',13,1),(218,'2019-05-22 19:08:15.346213','62',' -  - P2-DB1-SB',3,'',13,1),(219,'2019-05-22 19:08:15.377782','63',' -  - P2-NA1-SB',3,'',13,1),(220,'2019-05-22 19:08:15.402867','61',' -  - P2-NB1-SB',3,'',13,1),(221,'2019-05-22 19:08:15.428010','47',' -  - Prova 1',3,'',13,1),(222,'2019-05-22 19:08:15.453180','46',' -  - Prova 1',3,'',13,1),(223,'2019-05-22 19:08:15.478275','27',' -  - Prova 1 lab08h',3,'',13,1),(224,'2019-05-22 19:08:15.503467','21',' -  - Prova 1 teo3a10h',3,'',13,1),(225,'2019-05-22 19:08:15.528649','19',' -  - Prova 1 teo3a21hquiz',3,'',13,1),(226,'2019-05-22 19:08:15.553754','13',' -  - Prova 1 teo4a17h',3,'',13,1),(227,'2019-05-22 19:08:15.578899','32',' -  - Prova 1 teoSA17h',3,'',13,1),(228,'2019-05-22 19:08:15.604060','58',' -  - Prova 2',3,'',13,1),(229,'2019-05-22 19:08:15.637541','54',' -  - Prova 2',3,'',13,1),(230,'2019-05-22 19:08:15.662736','53',' -  - Prova 2',3,'',13,1),(231,'2019-05-22 19:08:15.696238','51',' -  - Prova 2',3,'',13,1),(232,'2019-05-22 19:08:15.730932','56',' -  - Prova 2 lab19h',3,'',13,1),(233,'2019-05-22 19:08:15.764444','57',' -  - Prova 2 lab21h',3,'',13,1),(234,'2019-05-22 19:08:15.797890','66',' -  - REC-PI-2019',3,'',13,1),(235,'2019-05-26 10:23:43.890253','65',' -  - teste2',3,'',13,1),(236,'2019-05-31 22:11:36.884097','18',' -  - Simulado 2a',3,'',13,1),(237,'2019-06-01 12:51:09.381924','52','aline.lima@mj.gov.br',2,'[{\"changed\": {\"fields\": [\"last_name\"]}}]',17,1),(238,'2019-06-01 12:51:35.156476','58','ana.muta@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"last_name\"]}}]',17,1),(239,'2019-06-01 12:52:00.549952','57','luciana.milena@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"last_name\"]}}]',17,1),(240,'2019-06-01 12:52:14.690788','56','sandra.trevisan@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"last_name\"]}}]',17,1),(241,'2019-06-01 12:52:30.878745','55','steil@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"last_name\"]}}]',17,1),(242,'2019-06-01 17:37:21.270013','64','leandro.teodoro@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(243,'2019-06-08 12:20:09.750787','4','fzcoord@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(244,'2019-06-08 15:21:45.900938','5','[BCM0505]<matriz>',2,'[{\"changed\": {\"fields\": [\"discipline\"]}}]',6,1),(245,'2019-06-10 11:18:17.272940','1','fzampirolli@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(246,'2019-06-27 21:34:54.271540','65','fz1@ufabc.edu.br',3,'',17,1),(247,'2019-07-12 15:01:38.113174','77','EE - DAESTO013-17SA - P1',3,'',13,1),(248,'2019-07-19 19:35:40.811259','2','professor',2,'[{\"changed\": {\"fields\": [\"permissions\"]}}]',3,1),(249,'2019-07-19 19:54:29.008045','10','gabriel.santiago@ufabc.edu.br',3,'',17,1),(250,'2019-07-19 19:55:20.055646','45','ronaldo.prati@ufabc.edu.br',3,'',17,1),(251,'2019-07-19 19:58:28.893230','8','aline.panazio@ufabc.edu.br',3,'',17,1),(252,'2019-07-19 19:58:28.923986','9','ana.simoes@ufabc.edu.br',3,'',17,1),(253,'2019-07-19 19:58:28.957460','11','aritanan.gruber@ufabc.edu.br',3,'',17,1),(254,'2019-07-19 19:58:28.990949','15','c.sato@ufabc.edu.br',3,'',17,1),(255,'2019-07-19 19:58:29.024415','12','carla.negri@ufabc.edu.br',3,'',17,1),(256,'2019-07-19 19:58:29.057899','13','carlos.ssantos@ufabc.edu.br',3,'',17,1),(257,'2019-07-19 19:58:29.091428','18','daniel.martin@ufabc.edu.br',3,'',17,1),(258,'2019-07-19 19:58:29.124897','24','francisco.massetto@ufabc.edu.br',3,'',17,1),(259,'2019-07-19 19:58:29.158372','37','graca.marietto@ufabc.edu.br',3,'',17,1),(260,'2019-07-19 19:58:29.191891','27','itana.stiubiener@ufabc.edu.br',3,'',17,1),(261,'2019-07-19 19:58:29.226606','30','joao.gois@ufabc.edu.br',3,'',17,1),(262,'2019-07-19 19:58:29.251755','28','joao.kleinschmidt@ufabc.edu.br',3,'',17,1),(263,'2019-07-19 19:58:29.276894','32','juliana.braga@ufabc.edu.br',3,'',17,1),(264,'2019-07-19 19:58:29.302001','26','manic.gordana@ufabc.edu.br',3,'',17,1),(265,'2019-07-19 19:58:29.327188','43','paulo.joia@ufabc.edu.br',3,'',17,1),(266,'2019-07-19 19:58:29.352319','19','santana.martins@ufabc.edu.br',3,'',17,1),(267,'2019-07-19 19:58:29.377456','46','saul.leite@ufabc.edu.br',3,'',17,1),(268,'2019-07-19 19:58:29.402610','47','thiago.covoes@ufabc.edu.br',3,'',17,1),(269,'2019-07-19 19:58:29.427723','50','wagner.tanaka@ufabc.edu.br',3,'',17,1),(270,'2019-07-19 19:59:43.589006','16','cristiane.salum@ufabc.edu.br',3,'',17,1),(271,'2019-07-19 19:59:43.623621','21','elizabeth.teodorov@ufabc.edu.br',3,'',17,1),(272,'2019-07-19 19:59:43.657088','38','mario.gazziro@ufabc.edu.br',3,'',17,1),(273,'2019-07-19 19:59:43.690591','44','ricardo.suyama@ufabc.edu.br',3,'',17,1),(274,'2019-07-19 20:00:18.416246','35','magda.miyashiro@ufabc.edu.br',3,'',17,1),(275,'2019-07-19 20:00:18.448048','29','marcelo.josko@ufabc.edu.br',3,'',17,1),(276,'2019-07-19 20:00:18.481526','40','ribeiro.pinheiro@ufabc.edu.br',3,'',17,1),(277,'2019-07-30 19:09:58.300978','79',' -  - Prova 1 SL108',3,'',13,1),(278,'2019-07-30 19:09:58.335992','80',' -  - Prova 1 SL212',3,'',13,1),(279,'2019-07-30 19:45:59.799132','7223','-',3,'',16,1),(280,'2019-07-30 19:48:17.157291','12682','11122215-Leandro Teodoro-teoolt.bio@gmail.com',2,'[{\"changed\": {\"fields\": [\"student_ID\", \"student_email\"]}}]',16,1),(281,'2019-07-30 19:48:25.564468','12681','31201910037-Artur Teles Barbosa-arturtelesbarbosa@gmail.com',2,'[{\"changed\": {\"fields\": [\"student_ID\", \"student_email\"]}}]',16,1),(282,'2019-07-30 19:57:08.316176','13642','111; nome 111; ufabc.tomioka@gmail.com',2,'[{\"changed\": {\"fields\": [\"student_name\", \"student_ID\"]}}]',16,1),(283,'2019-07-30 19:57:20.325771','13643','222; nome 222; ufabc.tomioka@gmail.com',2,'[{\"changed\": {\"fields\": [\"student_name\", \"student_ID\"]}}]',16,1),(284,'2019-07-30 19:59:29.820344','13642','111; 111 nome; ufabc.tomioka@gmail.com',2,'[{\"changed\": {\"fields\": [\"student_name\"]}}]',16,1),(285,'2019-07-30 19:59:48.143850','13644','111; 111 nome; ufabc.tomioka@gmail.com',2,'[{\"changed\": {\"fields\": [\"student_name\"]}}]',16,1),(286,'2019-07-30 20:00:17.180130','13643','222; 222 nome; ufabc.tomioka@gmail.com',2,'[{\"changed\": {\"fields\": [\"student_name\"]}}]',16,1),(287,'2019-07-30 20:00:25.017534','13645','222; 222 nome; ufabc.tomioka@gmail.com',2,'[{\"changed\": {\"fields\": [\"student_name\"]}}]',16,1),(288,'2019-07-30 20:00:34.679186','13645','222; 222 nome; ufabc.tomioka@gmail.com',2,'[]',16,1),(289,'2019-07-30 20:01:23.332128','13642','111; 111 nome; ufabc.tomioka@gmail.com',3,'',16,1),(290,'2019-07-30 20:01:23.356365','13643','222; 222 nome; ufabc.tomioka@gmail.com',3,'',16,1),(291,'2019-07-30 20:02:06.322293','13644','01; 01 nome; ufabc.tomioka@gmail.com',2,'[{\"changed\": {\"fields\": [\"student_name\", \"student_ID\"]}}]',16,1),(292,'2019-07-30 20:02:15.206635','13645','02; 02 nome; ufabc.tomioka@gmail.com',2,'[{\"changed\": {\"fields\": [\"student_name\", \"student_ID\"]}}]',16,1),(293,'2019-08-01 11:17:30.835134','1','ClassroomExam object (1)',1,'[{\"added\": {}}]',18,1),(294,'2019-08-02 22:39:33.118452','64','[BIJ0207]<SistemasEnergia>',2,'[{\"changed\": {\"fields\": [\"topic_text\"]}}]',6,1),(295,'2019-08-16 20:03:04.869184','17',' -  - EP2019 - Sim 1',3,'',13,1),(296,'2019-08-16 20:03:04.906468','71',' -  - Simulado 1 teste2',3,'',13,1),(297,'2019-08-16 20:03:04.940817','50',' -  - test',3,'',13,1),(298,'2019-08-16 20:03:04.974817','75',' -  - test-coord',3,'',13,1),(299,'2019-08-16 20:03:05.008217','72',' -  - test2',3,'',13,1),(300,'2019-08-16 20:03:05.041651','83',' -  - teste4',3,'',13,1),(301,'2019-09-02 15:23:07.181675','4','fzcoord@ufabc.edu.br',3,'',17,1),(302,'2019-09-02 15:23:07.183747','3','fzprof@ufabc.edu.br',3,'',17,1),(303,'2019-09-02 20:49:29.124744','66','fzcoord@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(304,'2019-09-02 20:49:38.734116','65','fzprof@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(305,'2019-09-10 16:57:09.324219','60','guiou.kobayashi@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"email\"]}}]',17,1),(306,'2019-10-08 12:07:17.669713','67','g.aldeia@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(307,'2019-10-09 20:22:16.478531','68','renato.coutinho@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(308,'2019-10-19 14:41:43.753581','23','Prova 1 teo3a21h',3,'',13,1),(309,'2019-10-19 14:52:45.367296','97','P1-2019.Q3',2,'[{\"changed\": {\"fields\": [\"classrooms\"]}}]',13,1),(310,'2019-10-19 14:54:46.936902','76','P1 EaD - 19.2',2,'[{\"changed\": {\"fields\": [\"classrooms\"]}}]',13,1),(311,'2019-10-19 14:58:43.000524','49','Prova 2 teo3a21hquiz',2,'[{\"changed\": {\"fields\": [\"classrooms\"]}}]',13,1),(312,'2019-10-22 18:01:25.674736','203','EE - teste2alunos',2,'[{\"changed\": {\"fields\": [\"students\"]}}]',12,1),(313,'2019-10-23 20:45:17.758291','100','P1',3,'',13,1),(314,'2019-10-23 20:45:17.792677','99','P1',3,'',13,1),(315,'2019-10-31 13:56:05.038064','38','Prova 1',3,'',13,1),(316,'2019-11-22 12:04:58.960241','72','wcosta@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(317,'2019-11-22 12:08:49.322189','73','aldeia@ufabc.edu.br',3,'',17,1),(318,'2020-02-14 12:27:08.950536','114','EP-sel - A101-0',3,'',12,1),(319,'2020-02-14 12:27:08.961045','115','EP-sel - A102-0',3,'',12,1),(320,'2020-02-14 12:27:08.969801','116','EP-sel - A103-0',3,'',12,1),(321,'2020-02-14 12:27:08.978110','117','EP-sel - A104-0',3,'',12,1),(322,'2020-02-14 12:27:08.985993','118','EP-sel - A105-0',3,'',12,1),(323,'2020-02-14 12:27:08.993717','119','EP-sel - A106-0',3,'',12,1),(324,'2020-02-14 12:27:09.001642','120','EP-sel - A107-0',3,'',12,1),(325,'2020-02-14 12:27:09.009000','121','EP-sel - A108-0',3,'',12,1),(326,'2020-02-14 12:27:09.016316','122','EP-sel - A109-0',3,'',12,1),(327,'2020-02-14 12:27:09.023805','123','EP-sel - A110-0',3,'',12,1),(328,'2020-02-14 12:27:09.031351','292','EP-sel - A111-0',3,'',12,1),(329,'2020-02-14 12:27:09.038943','293','EP-sel - A112-0',3,'',12,1),(330,'2020-02-14 12:27:09.046650','124','EP-sel - A113-0',3,'',12,1),(331,'2020-02-14 12:27:09.054271','125','EP-sel - A114-0',3,'',12,1),(332,'2020-02-14 12:27:09.062007','126','EP-sel - A211-0',3,'',12,1),(333,'2020-02-14 12:27:09.069472','127','EP-sel - A212-0',3,'',12,1),(334,'2020-02-14 12:27:09.077157','128','EP-sel - L407-2',3,'',12,1),(335,'2020-02-14 12:27:09.084702','113','EP-sel - S006-0',3,'',12,1),(336,'2020-02-14 12:27:09.092292','291','EP-sel - S008-0',3,'',12,1),(337,'2020-02-14 12:27:09.099694','129','EP-sel - S204-0',3,'',12,1),(338,'2020-02-14 12:27:09.107377','130','EP-sel - S205-0',3,'',12,1),(339,'2020-02-14 12:27:09.115106','131','EP-sel - S206-0',3,'',12,1),(340,'2020-02-14 12:27:09.122898','132','EP-sel - S207-0',3,'',12,1),(341,'2020-02-14 12:27:09.130509','133','EP-sel - S208-0',3,'',12,1),(342,'2020-02-14 12:27:09.138006','134','EP-sel - S209-0',3,'',12,1),(343,'2020-02-14 12:27:09.145688','135','EP-sel - S210-0',3,'',12,1),(344,'2020-02-14 12:27:09.153272','136','EP-sel - S213-0',3,'',12,1),(345,'2020-02-14 12:27:09.160929','137','EP-sel - S214-0',3,'',12,1),(346,'2020-02-14 12:27:09.168587','138','EP-sel - S301-1',3,'',12,1),(347,'2020-02-14 12:27:09.176068','139','EP-sel - S301-2',3,'',12,1),(348,'2020-02-14 12:27:09.183618','140','EP-sel - S302-1',3,'',12,1),(349,'2020-02-14 12:27:09.191388','141','EP-sel - S302-2',3,'',12,1),(350,'2020-02-14 12:27:09.199159','142','EP-sel - S305-1',3,'',12,1),(351,'2020-02-14 12:27:09.207055','143','EP-sel - S305-2',3,'',12,1),(352,'2020-02-14 12:27:09.214818','144','EP-sel - S306-1',3,'',12,1),(353,'2020-02-14 12:27:09.222337','145','EP-sel - S307-1',3,'',12,1),(354,'2020-02-14 12:27:09.230052','146','EP-sel - S307-2',3,'',12,1),(355,'2020-02-14 12:27:09.239434','147','EP-sel - S308-1',3,'',12,1),(356,'2020-02-14 12:27:09.248496','148','EP-sel - S311-1',3,'',12,1),(357,'2020-02-14 12:27:09.256273','149','EP-sel - S311-2',3,'',12,1),(358,'2020-02-14 15:20:56.835545','17','[]<6 - Contra Inteligência>',3,'',6,1),(359,'2020-02-14 15:29:58.680723','1','ClassroomExam object (1)',1,'[{\"added\": {}}]',18,1),(360,'2020-02-14 15:31:15.026413','90','CE-exame teste',3,'',13,1),(361,'2020-02-14 15:31:15.030474','95','Exam Test',3,'',13,1),(362,'2020-02-14 15:31:15.033246','14','RECUPERAÇÃO',3,'',13,1),(363,'2020-02-14 15:31:15.035080','96','teste',3,'',13,1),(364,'2020-02-14 15:31:15.037918','107','teste-vcpi',3,'',13,1),(365,'2020-02-18 17:43:10.913004','75','heitor.rodrigues@aluno.ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"username\", \"email\"]}}]',17,1),(366,'2020-02-18 17:43:32.177026','75','heitor.rodrigues@aluno.ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(367,'2020-02-18 17:57:08.474604','126','exame - heitor',3,'',13,1),(368,'2020-02-19 23:29:51.964594','77','joao.gois@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"first_name\"]}}]',17,1),(369,'2020-02-19 23:37:13.030548','64','BCM0505-15-SBC',3,'',13,1),(370,'2020-02-19 23:37:13.036494','73','P1 EaD',3,'',13,1),(371,'2020-02-19 23:37:13.040261','76','P1 EaD - 19.2',3,'',13,1),(372,'2020-02-19 23:37:13.044066','74','P2 EaD',3,'',13,1),(373,'2020-02-19 23:37:13.047514','20','Prova 1 2020',3,'',13,1),(374,'2020-02-19 23:37:13.050859','102','PI-EAD-2019-Q3- P1',3,'',13,1),(375,'2020-02-19 23:37:13.054300','102','PI-EAD-2019-Q3- P1',3,'',13,1),(376,'2020-02-19 23:41:02.687822','55','P2-B3B4-SB',3,'',13,1),(377,'2020-02-19 23:41:02.693392','36','Prova 1 lab10.b',3,'',13,1),(378,'2020-02-19 23:41:02.697752','15','Prova 1 quiz',3,'',13,1),(379,'2020-02-19 23:41:02.701769','49','Prova 2 teo3a21hquiz',3,'',13,1),(380,'2020-02-19 23:41:02.705769','123','teste',3,'',13,1),(381,'2020-02-19 23:41:02.710608','127','exame-test-heitor',3,'',13,1),(382,'2020-03-07 11:20:38.550073','23','fernando.teubl@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"first_name\", \"last_name\"]}}]',17,1),(383,'2020-03-10 22:45:37.126735','78','edson.iriarte@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(384,'2020-03-12 16:35:20.278694','79','denise.goya@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(385,'2020-03-19 20:58:30.544149','80','ugo.ibusuki@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(386,'2020-04-15 17:02:11.947711','21075','11020215; Mauro Mascarenhas; mauro.mascarenhas@aluno.ufabc.edu.br',1,'[{\"added\": {}}]',16,1),(387,'2020-06-01 18:39:44.106979','65','fzprof@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"password\"]}}]',17,1),(388,'2020-06-01 18:40:12.813602','66','fzcoord@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"password\"]}}]',17,1),(389,'2020-06-01 18:40:39.284694','53','fzstudent@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"password\"]}}]',17,1),(390,'2020-06-19 12:48:47.435640','78','edson.iriarte@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"password\"]}}]',17,1),(391,'2020-08-21 12:18:51.914556','84','peter.claessens@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(392,'2020-08-26 14:00:41.306706','537','BC0005; top 02-Bases de Dados; typ QM; dif 5; gro e; par no; #0537; des dados15',2,'[{\"changed\": {\"fields\": [\"question_text\", \"question_who_created\"]}}]',7,1),(393,'2020-08-26 14:01:14.983583','535','BC0005; top 02-Bases de Dados; typ QM; dif 5; gro e; par no; #0535; des dados13',2,'[{\"changed\": {\"fields\": [\"question_text\", \"question_who_created\"]}}]',7,1),(394,'2020-08-26 14:01:24.780638','536','BC0005; top 02-Bases de Dados; typ QM; dif 5; gro e; par no; #0536; des dados14',2,'[{\"changed\": {\"fields\": [\"question_text\", \"question_who_created\"]}}]',7,1),(395,'2020-08-26 14:01:38.500367','538','BC0005; top 02-Bases de Dados; typ QM; dif 5; gro e; par no; #0538; des dados16',2,'[{\"changed\": {\"fields\": [\"question_text\", \"question_who_created\"]}}]',7,1),(396,'2020-09-16 12:10:43.658541','91','r.sadao@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"first_name\"]}}]',17,1),(397,'2020-09-24 18:58:39.152274','75','heitor.rodrigues@aluno.ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(398,'2020-09-24 18:58:53.209193','96','ricardo.liang@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(399,'2020-09-24 18:59:54.345972','75','heitor.rodrigues@aluno.ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(400,'2020-12-15 18:53:32.857432','33','luiz.rozante@gmail.com',2,'[{\"changed\": {\"fields\": [\"email\"]}}]',17,1),(401,'2020-12-19 22:18:38.488782','197','Rozante teste exame1',3,'',13,1),(402,'2020-12-19 22:18:38.493884','198','Rozante teste exame2',3,'',13,1),(403,'2020-12-19 22:20:51.971628','199','Rozante lista p Goca',3,'',13,1),(404,'2020-12-23 12:51:28.800668','22878','12342134; asdfsadf; asdf@asfd',3,'',16,1),(405,'2021-01-29 11:39:39.599674','99','',1,'[{\"added\": {}}]',17,1),(406,'2021-01-29 11:40:14.199742','99','renato.watanabe@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"first_name\", \"last_name\", \"email\", \"groups\"]}}]',17,1),(407,'2021-02-23 12:08:48.612488','100','jair.donadelli@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(408,'2021-03-19 12:43:11.626325','100','jair.donadelli@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"password\"]}}]',17,1),(409,'2021-03-19 12:44:23.503385','100','jair.donadelli@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"password\"]}}]',17,1),(410,'2021-05-19 17:58:46.426722','67','g.aldeia@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(411,'2021-05-19 17:59:04.501628','67','g.aldeia@ufabc.edu.br',3,'',17,1),(412,'2021-05-19 17:59:21.294910','72','wcosta@ufabc.edu.br',3,'',17,1),(413,'2021-05-19 17:59:34.287557','75','heitor.rodrigues@aluno.ufabc.edu.br',3,'',17,1),(414,'2021-06-09 09:20:00.235668','484','BCM0505',3,'',12,1),(415,'2021-09-13 20:58:21.469141','24517','3002; Victor Hugo Zaninette Bernardino; hugo.bernardino@aluno.ufabc.edu.br',3,'',16,1),(416,'2021-09-13 20:58:21.474662','23501','1012; Victor Hugo Zaninette Bernardino; hugo.bernardino@aluno.ufabc.edu.br',3,'',16,1),(417,'2021-09-13 20:58:55.665518','24516','3001; Fernando G. Chacon F. Teruel; gabriel.chacon@aluno.ufabc.edu.br',3,'',16,1),(418,'2021-09-13 20:58:55.670250','23455','1008; Fernando G. Chacon F. Teruel; gabriel.chacon@aluno.ufabc.edu.br',3,'',16,1),(419,'2021-09-13 21:21:05.723189','24520','3005; Lucas David Vadilho; lucas.david@aluno.ufabc.edu.br',3,'',16,1),(420,'2021-09-13 21:21:05.726792','24468','1015; Lucas David Vadilho; lucas.david@aluno.ufabc.edu.br',3,'',16,1),(421,'2021-09-13 21:23:04.403652','24521','3006; Renato de Avila Lopes; renato.avila@aluno.ufabc.edu.br',3,'',16,1),(422,'2021-09-13 21:23:04.410234','24469','1016; Renato de Avila Lopes; renato.avila@aluno.ufabc.edu.br',3,'',16,1),(423,'2021-09-13 21:23:49.252480','24518','3003; Guilherme Melo da Silva; melo.guilherme@aluno.ufabc.edu.br',3,'',16,1),(424,'2021-09-13 21:23:49.257471','24466','1013; Guilherme Melo da Silva; melo.guilherme@aluno.ufabc.edu.br',3,'',16,1),(425,'2021-09-13 21:25:52.918408','24519','3004; Hugo Bento de Assis Silva; hugo.bento@aluno.ufabc.edu.br',3,'',16,1),(426,'2021-09-13 21:25:52.922871','24467','1014; Hugo Bento de Assis Silva; hugo.bento@aluno.ufabc.edu.br',3,'',16,1),(427,'2021-09-14 09:23:43.607322','101','paulo.meirelles@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(428,'2022-04-30 13:16:28.784648','102','graca.marietto@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(429,'2022-05-17 21:27:24.096261','335','pi-SUB-REC-21h',2,'[{\"changed\": {\"fields\": [\"exam_who_created\"]}}]',13,1),(430,'2022-05-23 16:34:23.290357','103','david.martins@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(431,'2022-06-01 11:06:56.688721','104','pedro.autreto@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(432,'2022-06-28 10:59:00.676840','79','denise.goya@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"password\"]}}]',17,1),(433,'2022-07-07 21:31:27.586724','105','',1,'[{\"added\": {}}]',17,1),(434,'2022-07-07 21:31:55.918140','105','marcelo.reyes@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"first_name\", \"last_name\", \"email\", \"groups\"]}}]',17,1),(435,'2022-09-12 14:33:44.858545','106','geiza.silva@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(436,'2022-10-10 21:04:44.564630','606','dis Bases Computacionais da Ciência; cod guiou-bcc-NB3-19h; typ PClass; roo L503; day 2022.3; pro guiou.kobayashi; stu 1; id_606',3,'',12,1),(437,'2022-10-13 18:46:14.546451','90','wagner.tanaka@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"password\"]}}]',17,1),(438,'2022-11-16 11:14:04.241298','107','',1,'[{\"added\": {}}]',17,1),(439,'2022-11-16 11:15:19.396264','107','roberto.rodrigues@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"username\", \"first_name\", \"last_name\", \"email\", \"groups\"]}}]',17,1),(440,'2022-11-16 11:20:50.409189','418','TSI5-SisCom',2,'[{\"changed\": {\"fields\": [\"exam_who_created\"]}}]',13,1),(441,'2022-11-26 13:51:07.189758','69','irineu.antunes@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"password\"]}}]',17,1),(442,'2022-11-26 13:51:22.969786','69','irineu.antunes@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"groups\"]}}]',17,1),(443,'2022-11-26 13:53:17.821072','69','irineu.antunes@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"password\"]}}]',17,1),(444,'2023-04-17 19:53:10.835454','43','[BC0005]<02-Manipulação de Dados>',3,'',6,1),(445,'2023-04-17 19:53:29.963193','40','[BC0005]<03-Gráficos de Funções>',3,'',6,1),(446,'2023-04-17 19:53:29.966624','42','[BC0005]<04-Estatística Descritiva>',3,'',6,1),(447,'2023-04-17 19:53:29.969209','164','[BC0005]<05-Correlação e Regressão>',3,'',6,1),(448,'2023-04-17 19:53:29.971847','166','[BC0005,BCM0505]<06-Lógica de Programação: sequencial>',3,'',6,1),(449,'2023-04-17 19:53:29.974652','44','[BC0005,BCM0505]<07-Lógica de Programação: condicionais>',3,'',6,1),(450,'2023-04-17 19:53:29.977303','46','[BC0005,BCM0505]<08-Lógica de Programação: repetição>',3,'',6,1),(451,'2023-04-17 19:53:29.980009','158','[BC0005,BCM0505]<09-Modelagem e Simulação>',3,'',6,1),(452,'2023-04-17 19:53:29.982444','41','[BC0005]<99-Medidas.old>',3,'',6,1),(453,'2023-04-17 19:53:29.985119','159','[BC0005]<99-Variáveis.old>',3,'',6,1),(454,'2023-04-17 19:53:29.987805','62','[BCM0504]<natinf>',3,'',6,1),(455,'2023-04-17 19:53:29.990294','63','[BCM0504]<NI>',3,'',6,1),(456,'2023-04-17 19:53:29.992870','231','[BCM0504]<NI-01 Dados, Informação e Conhecimento>',3,'',6,1),(457,'2023-04-17 19:53:29.995372','232','[BCM0504]<NI-02 Mundo Digital>',3,'',6,1),(458,'2023-04-17 19:53:29.997930','233','[BCM0504]<NI-03 Teoria da Informação>',3,'',6,1),(459,'2023-04-17 19:53:30.000732','234','[BCM0504]<NI-04 Códigos e Codificação>',3,'',6,1),(460,'2023-04-17 19:53:30.003302','235','[BCM0504]<NI-05 Códigos de Tratamento de Erros>',3,'',6,1),(461,'2023-04-17 19:53:30.005980','236','[BCM0504]<NI-06 Compressão de Dados>',3,'',6,1),(462,'2023-04-17 19:53:30.008910','166','[BC0005,BCM0505]<06-Lógica de Programação: sequencial>',3,'',6,1),(463,'2023-04-17 19:53:30.011758','44','[BC0005,BCM0505]<07-Lógica de Programação: condicionais>',3,'',6,1),(464,'2023-04-17 19:53:30.014668','46','[BC0005,BCM0505]<08-Lógica de Programação: repetição>',3,'',6,1),(465,'2023-04-17 19:53:30.018551','158','[BC0005,BCM0505]<09-Modelagem e Simulação>',3,'',6,1),(466,'2023-04-17 19:53:30.022328','1','[BCM0505]<1-sequencial>',3,'',6,1),(467,'2023-04-17 19:53:30.024813','133','[BCM0505]<2-módulo-parte1>',3,'',6,1),(468,'2023-04-17 19:53:30.027165','2','[BCM0505]<3-condicional>',3,'',6,1),(469,'2023-04-17 19:53:30.029689','3','[BCM0505]<4-repetição>',3,'',6,1),(470,'2023-04-17 19:53:30.032159','4','[BCM0505]<5-vetor>',3,'',6,1),(471,'2023-04-17 19:53:30.034671','6','[BCM0505]<6-módulo-parte2>',3,'',6,1),(472,'2023-04-17 19:53:30.037390','5','[BCM0505]<7-matriz>',3,'',6,1),(473,'2023-04-17 19:53:30.039915','229','[BCM0505]<mini-tópico>',3,'',6,1),(474,'2023-04-17 19:53:30.042348','188','[BCM0506]<1a. Prova BCM0506 2022 Q1>',3,'',6,1),(475,'2023-04-17 19:53:30.044936','186','[BCM0506]<1o. Teste BCM0506 2022 Q1>',3,'',6,1),(476,'2023-04-17 19:53:30.047602','190','[BCM0506]<2a. Prova BCM0506 2022 Q1>',3,'',6,1),(477,'2023-04-17 19:53:30.050097','189','[BCM0506]<2o. Teste BCM0506 2022 Q1>',3,'',6,1),(478,'2023-04-17 19:53:30.052667','162','[BCM0506]<BCM0506-quiz1>',3,'',6,1),(479,'2023-04-17 19:53:30.055176','165','[BCM0506]<BCM0506-quiz2>',3,'',6,1),(480,'2023-04-17 19:53:30.057844','179','[BCM0506]<BCM0506-quiz3>',3,'',6,1),(481,'2023-04-17 19:53:30.060363','170','[BCM0506]<BCM0506-quiz6>',3,'',6,1),(482,'2023-04-17 19:53:30.063955','161','[BCM0506]<Classes>',3,'',6,1),(483,'2023-04-17 19:53:30.067676','160','[BCM0506]<Declaração>',3,'',6,1),(484,'2023-04-17 19:53:30.070506','172','[BCM0506]<Exame2>',3,'',6,1),(485,'2023-04-17 19:53:30.073286','173','[BCM0506]<Geral>',3,'',6,1),(486,'2023-04-17 19:53:30.076051','174','[BCM0506]<Grafos>',3,'',6,1),(487,'2023-04-17 19:53:30.078588','175','[BCM0506]<Leis de Potência>',3,'',6,1),(488,'2023-04-17 19:53:30.081327','191','[BCM0506]<mini_turma>',3,'',6,1),(489,'2023-04-17 19:53:30.084243','220','[BCM0506]<P1_Q3_22>',3,'',6,1),(490,'2023-04-17 19:53:30.087792','168','[BCM0506]<quiz4>',3,'',6,1),(491,'2023-04-17 19:53:30.090844','169','[BCM0506]<quiz5>',3,'',6,1),(492,'2023-04-17 19:53:30.093869','171','[BCM0506]<quiz7>',3,'',6,1),(493,'2023-04-17 19:53:30.096813','176','[BCM0506]<Roteamento>',3,'',6,1),(494,'2023-04-17 19:53:30.099333','182','[BCM0506]<Teste1>',3,'',6,1),(495,'2023-04-17 19:53:30.102011','181','[BCM0506]<teste1>',3,'',6,1),(496,'2023-04-17 19:53:30.104727','187','[BCM0506]<Teste2>',3,'',6,1),(497,'2023-04-17 19:53:30.107364','183','[BCM0506]<teste2>',3,'',6,1),(498,'2023-04-17 19:53:30.110003','55','[BCN0402]<ABERTAS>',3,'',6,1),(499,'2023-04-17 19:53:30.112742','49','[BCN0402]<APROXIMAÇÃO LINEAR>',3,'',6,1),(500,'2023-04-17 19:53:30.115457','138','[BCN0402]<Edson-Derivada>',3,'',6,1),(501,'2023-04-17 19:53:30.118209','139','[BCN0402]<Edson-Integral>',3,'',6,1),(502,'2023-04-17 19:53:30.121023','52','[BCN0402]<GRÁFICO>',3,'',6,1),(503,'2023-04-17 19:53:30.123854','51','[BCN0402]<L\'HOSPITA>',3,'',6,1),(504,'2023-04-17 19:53:30.126365','53','[BCN0402]<MÁXIMOS/MÍNIMOS>',3,'',6,1),(505,'2023-04-17 19:53:30.129073','59','[BCN0402]<P2-INTEGRAL-ÁREA>',3,'',6,1),(506,'2023-04-17 19:53:30.131799','58','[BCN0402]<P2-INTEGRAL-POR PARTES>',3,'',6,1),(507,'2023-04-17 19:53:30.134364','56','[BCN0402]<P2-INTEGRAL-SUBSTITUIÇÃO>',3,'',6,1),(508,'2023-04-17 19:53:30.137251','61','[BCN0402]<P2-INTEGRAL-SUBSTITUIÇÃO TRIGONOMÉTRICA>',3,'',6,1),(509,'2023-04-17 19:53:30.140257','60','[BCN0402]<P2-INTEGRAL-VOLUME>',3,'',6,1),(510,'2023-04-17 19:53:30.143964','57','[BCN0402]<P2-TFC-PARTE 1>',3,'',6,1),(511,'2023-04-17 19:53:30.147032','54','[BCN0402]<PROBLEMAS DE OTIMIZAÇÃO>',3,'',6,1),(512,'2023-04-17 19:53:30.150529','48','[BCN0402]<RDA1P>',3,'',6,1),(513,'2023-04-17 19:53:30.155578','47','[BCN0402]<RETA TANGENTE>',3,'',6,1),(514,'2023-04-17 19:53:30.159426','50','[BCN0402]<TAXAS RELACIONADAS>',3,'',6,1),(515,'2023-04-17 19:53:30.162836','112','[BIJ0207]<SistemasEnergia>',3,'',6,1),(516,'2023-04-17 19:53:30.165618','64','[BIJ0207]<SistemasEnergia.old>',3,'',6,1),(517,'2023-04-17 19:53:30.168496','19','[CIP]<nível 1>',3,'',6,1),(518,'2023-04-17 19:53:30.171578','20','[CLIP]<nível 1>',3,'',6,1),(519,'2023-04-17 19:53:30.174867','128','[CN]<Sistemas Lineares>',3,'',6,1),(520,'2023-04-17 19:53:30.177862','129','[CN]<zeros de funções>',3,'',6,1),(521,'2023-04-17 19:53:30.181785','114','[Comp]<comp-topic1>',3,'',6,1),(522,'2023-04-17 19:53:30.185092','113','[Comp]<UFABC - TSI - Compiladores>',3,'',6,1),(523,'2023-04-17 19:53:30.188249','94','[CompMov]<CompMov1>',3,'',6,1),(524,'2023-04-17 19:53:30.191319','95','[CompMov]<CompMov2>',3,'',6,1),(525,'2023-04-17 19:53:30.194244','96','[CompMov]<CompMov3>',3,'',6,1),(526,'2023-04-17 19:53:30.197131','97','[CompMov]<CompMov4>',3,'',6,1),(527,'2023-04-17 19:53:30.200036','98','[CompMov]<CompMov5>',3,'',6,1),(528,'2023-04-17 19:53:30.202790','99','[CompMov]<CompMov6>',3,'',6,1),(529,'2023-04-17 19:53:30.205619','101','[CompMov]<CompMov7>',3,'',6,1),(530,'2023-04-17 19:53:30.208512','237','[CompMov]<TSI5-ComMov-Diogo>',3,'',6,1),(531,'2023-04-17 19:53:30.211274','21','[CPE]<nível 1>',3,'',6,1),(532,'2023-04-17 19:53:30.214251','111','[EESTO013-17]<Alternativa de Investimento>',3,'',6,1),(533,'2023-04-17 19:53:30.217292','185','[EESTO013-17]<Depreciação>',3,'',6,1),(534,'2023-04-17 19:53:30.220153','110','[EESTO013-17]<ESTO013-17 Juros>',3,'',6,1),(535,'2023-04-17 19:53:30.223037','122','[EESTO013-17]<ESTO013-17 Juros e Conceitos>',3,'',6,1),(536,'2023-04-17 19:53:30.225959','115','[EESTO013-17]<ESTO013-17 VPL Conceitos>',3,'',6,1),(537,'2023-04-17 19:53:30.229304','184','[EESTO013-17]<Inflação em Projetos>',3,'',6,1),(538,'2023-04-17 19:53:30.233505','178','[EP2021]<Selecao2021>',3,'',6,1),(539,'2023-04-17 19:53:30.237438','227','[EP2023]<seleção2023>',3,'',6,1),(540,'2023-04-17 19:53:30.240200','38','[ESTG010-17]<IT-2018-3Q>',3,'',6,1),(541,'2023-04-17 19:53:30.243167','39','[ESTG010-17]<IT-2018-3QP2>',3,'',6,1),(542,'2023-04-17 19:53:30.246444','153','[ESTG016-17]<QS-01-introducao>',3,'',6,1),(543,'2023-04-17 19:53:30.250945','134','[ESTG025-17]<Desenho Autor Marca>',3,'',6,1),(544,'2023-04-17 19:53:30.255049','135','[ESTG025-17]<Indicação Cultivar Geral>',3,'',6,1),(545,'2023-04-17 19:54:15.304762','40','[BC0005]<03-Gráficos de Funções>',3,'',6,1),(546,'2023-04-17 19:54:15.308867','42','[BC0005]<04-Estatística Descritiva>',3,'',6,1),(547,'2023-04-17 19:54:15.311778','164','[BC0005]<05-Correlação e Regressão>',3,'',6,1),(548,'2023-04-17 19:54:15.316224','166','[BC0005,BCM0505]<06-Lógica de Programação: sequencial>',3,'',6,1),(549,'2023-04-17 19:54:15.319192','166','[BC0005,BCM0505]<06-Lógica de Programação: sequencial>',3,'',6,1),(550,'2023-04-17 19:54:28.481136','44','[BC0005,BCM0505]<07-Lógica de Programação: condicionais>',3,'',6,1),(551,'2023-04-17 19:54:28.485322','46','[BC0005,BCM0505]<08-Lógica de Programação: repetição>',3,'',6,1),(552,'2023-04-17 19:54:28.488455','158','[BC0005,BCM0505]<09-Modelagem e Simulação>',3,'',6,1),(553,'2023-04-17 19:54:28.491489','41','[BC0005]<99-Medidas.old>',3,'',6,1),(554,'2023-04-17 19:54:28.494545','159','[BC0005]<99-Variáveis.old>',3,'',6,1),(555,'2023-04-17 19:54:28.497520','62','[BCM0504]<natinf>',3,'',6,1),(556,'2023-04-17 19:54:28.500622','63','[BCM0504]<NI>',3,'',6,1),(557,'2023-04-17 19:54:28.503801','44','[BC0005,BCM0505]<07-Lógica de Programação: condicionais>',3,'',6,1),(558,'2023-04-17 19:54:28.506972','46','[BC0005,BCM0505]<08-Lógica de Programação: repetição>',3,'',6,1),(559,'2023-04-17 19:54:28.510165','158','[BC0005,BCM0505]<09-Modelagem e Simulação>',3,'',6,1),(560,'2023-04-17 19:54:46.315294','231','[BCM0504]<NI-01 Dados, Informação e Conhecimento>',3,'',6,1),(561,'2023-04-17 19:54:46.318683','232','[BCM0504]<NI-02 Mundo Digital>',3,'',6,1),(562,'2023-04-17 19:54:46.321910','233','[BCM0504]<NI-03 Teoria da Informação>',3,'',6,1),(563,'2023-04-17 19:54:46.325041','234','[BCM0504]<NI-04 Códigos e Codificação>',3,'',6,1),(564,'2023-04-17 19:54:46.327800','235','[BCM0504]<NI-05 Códigos de Tratamento de Erros>',3,'',6,1),(565,'2023-04-17 19:54:46.331230','236','[BCM0504]<NI-06 Compressão de Dados>',3,'',6,1),(566,'2023-04-17 19:54:46.334258','1','[BCM0505]<1-sequencial>',3,'',6,1),(567,'2023-04-17 19:54:46.337451','133','[BCM0505]<2-módulo-parte1>',3,'',6,1),(568,'2023-04-17 19:54:46.340317','2','[BCM0505]<3-condicional>',3,'',6,1),(569,'2023-04-17 19:54:46.343394','3','[BCM0505]<4-repetição>',3,'',6,1),(570,'2023-04-17 19:55:09.982039','231','[BCM0504]<NI-01 Dados, Informação e Conhecimento>',3,'',6,1),(571,'2023-04-17 19:55:09.986715','232','[BCM0504]<NI-02 Mundo Digital>',3,'',6,1),(572,'2023-04-17 19:55:09.990698','233','[BCM0504]<NI-03 Teoria da Informação>',3,'',6,1),(573,'2023-04-17 19:55:09.993681','234','[BCM0504]<NI-04 Códigos e Codificação>',3,'',6,1),(574,'2023-04-17 19:55:23.448372','235','[BCM0504]<NI-05 Códigos de Tratamento de Erros>',3,'',6,1),(575,'2023-04-17 19:55:23.452022','236','[BCM0504]<NI-06 Compressão de Dados>',3,'',6,1),(576,'2023-04-17 19:55:23.455235','1','[BCM0505]<1-sequencial>',3,'',6,1),(577,'2023-04-17 19:55:35.925548','235','[BCM0504]<NI-05 Códigos de Tratamento de Erros>',3,'',6,1),(578,'2023-04-17 19:55:45.092375','236','[BCM0504]<NI-06 Compressão de Dados>',3,'',6,1),(579,'2023-04-17 19:55:53.975919','1','[BCM0505]<1-sequencial>',3,'',6,1),(580,'2023-04-17 19:56:17.543890','133','[BCM0505]<2-módulo-parte1>',3,'',6,1),(581,'2023-04-17 19:56:30.244451','2','[BCM0505]<3-condicional>',3,'',6,1),(582,'2023-04-17 19:56:30.247200','3','[BCM0505]<4-repetição>',3,'',6,1),(583,'2023-04-17 19:56:30.249461','4','[BCM0505]<5-vetor>',3,'',6,1),(584,'2023-04-17 19:56:30.252947','6','[BCM0505]<6-módulo-parte2>',3,'',6,1),(585,'2023-04-17 19:56:30.256058','5','[BCM0505]<7-matriz>',3,'',6,1),(586,'2023-04-17 19:56:30.259314','229','[BCM0505]<mini-tópico>',3,'',6,1),(587,'2023-04-17 19:56:30.261855','188','[BCM0506]<1a. Prova BCM0506 2022 Q1>',3,'',6,1),(588,'2023-04-17 19:56:30.264362','186','[BCM0506]<1o. Teste BCM0506 2022 Q1>',3,'',6,1),(589,'2023-04-17 19:56:30.266591','190','[BCM0506]<2a. Prova BCM0506 2022 Q1>',3,'',6,1),(590,'2023-04-17 19:56:30.268946','189','[BCM0506]<2o. Teste BCM0506 2022 Q1>',3,'',6,1),(591,'2023-04-17 19:56:30.271299','162','[BCM0506]<BCM0506-quiz1>',3,'',6,1),(592,'2023-04-17 19:56:30.273645','165','[BCM0506]<BCM0506-quiz2>',3,'',6,1),(593,'2023-04-17 19:56:30.275916','179','[BCM0506]<BCM0506-quiz3>',3,'',6,1),(594,'2023-04-17 19:56:30.278222','170','[BCM0506]<BCM0506-quiz6>',3,'',6,1),(595,'2023-04-17 19:56:30.280592','161','[BCM0506]<Classes>',3,'',6,1),(596,'2023-04-17 19:56:30.283166','160','[BCM0506]<Declaração>',3,'',6,1),(597,'2023-04-17 19:56:30.285763','172','[BCM0506]<Exame2>',3,'',6,1),(598,'2023-04-17 19:56:30.288127','173','[BCM0506]<Geral>',3,'',6,1),(599,'2023-04-17 19:56:30.290337','174','[BCM0506]<Grafos>',3,'',6,1),(600,'2023-04-17 19:56:30.292655','175','[BCM0506]<Leis de Potência>',3,'',6,1),(601,'2023-04-17 19:56:30.294989','191','[BCM0506]<mini_turma>',3,'',6,1),(602,'2023-04-17 19:56:30.297235','220','[BCM0506]<P1_Q3_22>',3,'',6,1),(603,'2023-04-17 19:56:30.299566','168','[BCM0506]<quiz4>',3,'',6,1),(604,'2023-04-17 19:56:30.301779','169','[BCM0506]<quiz5>',3,'',6,1),(605,'2023-04-17 19:56:30.304077','171','[BCM0506]<quiz7>',3,'',6,1),(606,'2023-04-17 19:56:30.306286','176','[BCM0506]<Roteamento>',3,'',6,1),(607,'2023-04-17 19:56:30.308736','182','[BCM0506]<Teste1>',3,'',6,1),(608,'2023-04-17 19:56:30.311058','181','[BCM0506]<teste1>',3,'',6,1),(609,'2023-04-17 19:56:30.313491','187','[BCM0506]<Teste2>',3,'',6,1),(610,'2023-04-17 19:56:30.315784','183','[BCM0506]<teste2>',3,'',6,1),(611,'2023-04-17 19:56:30.318106','55','[BCN0402]<ABERTAS>',3,'',6,1),(612,'2023-04-17 19:56:30.320472','49','[BCN0402]<APROXIMAÇÃO LINEAR>',3,'',6,1),(613,'2023-04-17 19:56:30.322743','138','[BCN0402]<Edson-Derivada>',3,'',6,1),(614,'2023-04-17 19:56:30.325111','139','[BCN0402]<Edson-Integral>',3,'',6,1),(615,'2023-04-17 19:56:30.327405','52','[BCN0402]<GRÁFICO>',3,'',6,1),(616,'2023-04-17 19:56:30.329937','51','[BCN0402]<L\'HOSPITA>',3,'',6,1),(617,'2023-04-17 19:56:30.332305','53','[BCN0402]<MÁXIMOS/MÍNIMOS>',3,'',6,1),(618,'2023-04-17 19:56:30.334477','59','[BCN0402]<P2-INTEGRAL-ÁREA>',3,'',6,1),(619,'2023-04-17 19:56:30.337178','58','[BCN0402]<P2-INTEGRAL-POR PARTES>',3,'',6,1),(620,'2023-04-17 19:56:30.339444','56','[BCN0402]<P2-INTEGRAL-SUBSTITUIÇÃO>',3,'',6,1),(621,'2023-04-17 19:56:30.341617','61','[BCN0402]<P2-INTEGRAL-SUBSTITUIÇÃO TRIGONOMÉTRICA>',3,'',6,1),(622,'2023-04-17 19:56:30.344042','60','[BCN0402]<P2-INTEGRAL-VOLUME>',3,'',6,1),(623,'2023-04-17 19:56:30.346251','57','[BCN0402]<P2-TFC-PARTE 1>',3,'',6,1),(624,'2023-04-17 19:56:30.348651','54','[BCN0402]<PROBLEMAS DE OTIMIZAÇÃO>',3,'',6,1),(625,'2023-04-17 19:56:30.350933','48','[BCN0402]<RDA1P>',3,'',6,1),(626,'2023-04-17 19:56:30.353292','47','[BCN0402]<RETA TANGENTE>',3,'',6,1),(627,'2023-04-17 19:56:30.355657','50','[BCN0402]<TAXAS RELACIONADAS>',3,'',6,1),(628,'2023-04-17 19:56:30.357895','112','[BIJ0207]<SistemasEnergia>',3,'',6,1),(629,'2023-04-17 19:56:30.360250','64','[BIJ0207]<SistemasEnergia.old>',3,'',6,1),(630,'2023-04-17 19:56:30.362497','19','[CIP]<nível 1>',3,'',6,1),(631,'2023-04-17 19:56:30.364885','20','[CLIP]<nível 1>',3,'',6,1),(632,'2023-04-17 19:56:30.367360','128','[CN]<Sistemas Lineares>',3,'',6,1),(633,'2023-04-17 19:56:30.369664','129','[CN]<zeros de funções>',3,'',6,1),(634,'2023-04-17 19:56:30.372036','114','[Comp]<comp-topic1>',3,'',6,1),(635,'2023-04-17 19:56:30.374308','113','[Comp]<UFABC - TSI - Compiladores>',3,'',6,1),(636,'2023-04-17 19:56:30.376756','94','[CompMov]<CompMov1>',3,'',6,1),(637,'2023-04-17 19:56:30.378979','95','[CompMov]<CompMov2>',3,'',6,1),(638,'2023-04-17 19:56:30.381380','96','[CompMov]<CompMov3>',3,'',6,1),(639,'2023-04-17 19:56:30.383696','97','[CompMov]<CompMov4>',3,'',6,1),(640,'2023-04-17 19:56:30.385968','98','[CompMov]<CompMov5>',3,'',6,1),(641,'2023-04-17 19:56:30.388296','99','[CompMov]<CompMov6>',3,'',6,1),(642,'2023-04-17 19:56:30.390770','101','[CompMov]<CompMov7>',3,'',6,1),(643,'2023-04-17 19:56:30.393088','237','[CompMov]<TSI5-ComMov-Diogo>',3,'',6,1),(644,'2023-04-17 19:56:30.395372','21','[CPE]<nível 1>',3,'',6,1),(645,'2023-04-17 19:56:30.397793','111','[EESTO013-17]<Alternativa de Investimento>',3,'',6,1),(646,'2023-04-17 19:56:30.400057','185','[EESTO013-17]<Depreciação>',3,'',6,1),(647,'2023-04-17 19:56:30.402262','110','[EESTO013-17]<ESTO013-17 Juros>',3,'',6,1),(648,'2023-04-17 19:56:30.404621','122','[EESTO013-17]<ESTO013-17 Juros e Conceitos>',3,'',6,1),(649,'2023-04-17 19:56:30.406977','115','[EESTO013-17]<ESTO013-17 VPL Conceitos>',3,'',6,1),(650,'2023-04-17 19:56:30.409470','184','[EESTO013-17]<Inflação em Projetos>',3,'',6,1),(651,'2023-04-17 19:56:30.411836','178','[EP2021]<Selecao2021>',3,'',6,1),(652,'2023-04-17 19:56:30.414041','227','[EP2023]<seleção2023>',3,'',6,1),(653,'2023-04-17 19:56:30.416342','38','[ESTG010-17]<IT-2018-3Q>',3,'',6,1),(654,'2023-04-17 19:56:30.418516','39','[ESTG010-17]<IT-2018-3QP2>',3,'',6,1),(655,'2023-04-17 19:56:30.421049','153','[ESTG016-17]<QS-01-introducao>',3,'',6,1),(656,'2023-04-17 19:56:30.423501','134','[ESTG025-17]<Desenho Autor Marca>',3,'',6,1),(657,'2023-04-17 19:56:30.425825','135','[ESTG025-17]<Indicação Cultivar Geral>',3,'',6,1),(658,'2023-04-17 19:56:30.428351','136','[ESTG025-17]<Marcas>',3,'',6,1),(659,'2023-04-17 19:56:30.430681','130','[ESTG025-17]<Patentes>',3,'',6,1),(660,'2023-04-17 19:56:30.433135','11','[Ex]<template>',3,'',6,1),(661,'2023-04-17 19:56:30.435719','12','[Ex]<template-equação-paramétrica>',3,'',6,1),(662,'2023-04-17 19:56:30.438318','13','[Ex]<template-figura>',3,'',6,1),(663,'2023-04-17 19:56:30.440964','14','[Ex]<template-integral>',3,'',6,1),(664,'2023-04-17 19:56:30.443507','15','[Ex]<template-integral-fig>',3,'',6,1),(665,'2023-04-17 19:56:30.445842','16','[Ex]<template-mru>',3,'',6,1),(666,'2023-04-17 19:56:30.448301','192','[FEMEC]<FEMEC-Introdução>',3,'',6,1),(667,'2023-04-17 19:56:30.450704','65','[GA]<Vetores>',3,'',6,1),(668,'2023-04-17 19:56:30.453401','7','[GestGovTI]<Aula01>',3,'',6,1),(669,'2023-04-17 19:56:30.455903','8','[GestGovTI]<Aula02>',3,'',6,1),(670,'2023-04-17 19:56:30.458257','9','[GestGovTI]<Aula03>',3,'',6,1),(671,'2023-04-17 19:56:30.461795','10','[GestGovTI]<Aula04>',3,'',6,1),(672,'2023-04-17 19:56:30.464183','66','[GestPQSw]<PMBOK>',3,'',6,1),(673,'2023-04-17 19:56:30.466642','157','[IPE]<01-Introdução>',3,'',6,1),(674,'2023-04-17 19:56:30.469486','163','[IPE]<Tópico Exemplo>',3,'',6,1),(675,'2023-04-17 19:56:30.472135','67','[ITW]<internet>',3,'',6,1),(676,'2023-04-17 19:56:30.474653','225','[MCTA004-17]<Aula>',3,'',6,1),(677,'2023-04-17 19:56:30.477204','35','[MCTA004-17]<introducao>',3,'',6,1),(678,'2023-04-17 19:56:30.479632','222','[MCTA004-17]<introducao2>',3,'',6,1),(679,'2023-04-17 19:56:30.482024','36','[MCTA004-17]<introducaoP2>',3,'',6,1),(680,'2023-04-17 20:00:24.367799','4','[BCM0505]<5-vetor>',3,'',6,1),(681,'2023-04-17 20:00:24.372430','6','[BCM0505]<6-módulo-parte2>',3,'',6,1),(682,'2023-04-17 20:00:24.375570','5','[BCM0505]<7-matriz>',3,'',6,1),(683,'2023-04-17 20:00:24.379715','229','[BCM0505]<mini-tópico>',3,'',6,1),(684,'2023-04-17 20:00:24.383192','186','[BCM0506]<1o. Teste BCM0506 2022 Q1>',3,'',6,1),(685,'2023-04-17 20:00:24.386521','189','[BCM0506]<2o. Teste BCM0506 2022 Q1>',3,'',6,1),(686,'2023-04-17 20:05:59.610374','162','[BCM0506]<BCM0506-quiz1>',3,'',6,1),(687,'2023-04-17 20:05:59.620958','165','[BCM0506]<BCM0506-quiz2>',3,'',6,1),(688,'2023-04-17 20:05:59.624510','179','[BCM0506]<BCM0506-quiz3>',3,'',6,1),(689,'2023-04-17 20:05:59.628053','170','[BCM0506]<BCM0506-quiz6>',3,'',6,1),(690,'2023-04-17 20:06:19.323407','229','[BCM0505]<mini-tópico>',3,'',6,1),(691,'2023-04-17 20:06:19.326934','161','[BCM0506]<Classes>',3,'',6,1),(692,'2023-04-17 20:06:19.329959','160','[BCM0506]<Declaração>',3,'',6,1),(693,'2023-04-17 20:06:19.332993','172','[BCM0506]<Exame2>',3,'',6,1),(694,'2023-04-17 20:06:19.335911','173','[BCM0506]<Geral>',3,'',6,1),(695,'2023-04-17 20:06:19.338867','174','[BCM0506]<Grafos>',3,'',6,1),(696,'2023-04-17 20:06:19.342114','175','[BCM0506]<Leis de Potência>',3,'',6,1),(697,'2023-04-17 20:06:19.345242','191','[BCM0506]<mini_turma>',3,'',6,1),(698,'2023-04-17 20:06:19.348534','220','[BCM0506]<P1_Q3_22>',3,'',6,1),(699,'2023-04-17 20:06:38.859637','168','[BCM0506]<quiz4>',3,'',6,1),(700,'2023-04-17 20:06:38.863084','169','[BCM0506]<quiz5>',3,'',6,1),(701,'2023-04-17 20:06:38.865939','171','[BCM0506]<quiz7>',3,'',6,1),(702,'2023-04-17 20:06:38.869090','176','[BCM0506]<Roteamento>',3,'',6,1),(703,'2023-04-17 20:06:38.872059','182','[BCM0506]<Teste1>',3,'',6,1),(704,'2023-04-17 20:06:38.875009','181','[BCM0506]<teste1>',3,'',6,1),(705,'2023-04-17 20:06:38.878088','187','[BCM0506]<Teste2>',3,'',6,1),(706,'2023-04-17 20:06:38.881946','183','[BCM0506]<teste2>',3,'',6,1),(707,'2023-04-17 20:06:38.885301','138','[BCN0402]<Edson-Derivada>',3,'',6,1),(708,'2023-04-17 20:06:38.888319','139','[BCN0402]<Edson-Integral>',3,'',6,1),(709,'2023-04-17 20:07:03.155984','52','[BCN0402]<GRÁFICO>',3,'',6,1),(710,'2023-04-17 20:07:03.159699','51','[BCN0402]<L\'HOSPITA>',3,'',6,1),(711,'2023-04-17 20:07:03.162697','53','[BCN0402]<MÁXIMOS/MÍNIMOS>',3,'',6,1),(712,'2023-04-17 20:07:03.165669','59','[BCN0402]<P2-INTEGRAL-ÁREA>',3,'',6,1),(713,'2023-04-17 20:07:03.168747','58','[BCN0402]<P2-INTEGRAL-POR PARTES>',3,'',6,1),(714,'2023-04-17 20:07:03.172754','56','[BCN0402]<P2-INTEGRAL-SUBSTITUIÇÃO>',3,'',6,1),(715,'2023-04-17 20:07:03.176712','61','[BCN0402]<P2-INTEGRAL-SUBSTITUIÇÃO TRIGONOMÉTRICA>',3,'',6,1),(716,'2023-04-17 20:07:03.180072','60','[BCN0402]<P2-INTEGRAL-VOLUME>',3,'',6,1),(717,'2023-04-17 20:07:03.182879','57','[BCN0402]<P2-TFC-PARTE 1>',3,'',6,1),(718,'2023-04-17 20:07:03.185992','54','[BCN0402]<PROBLEMAS DE OTIMIZAÇÃO>',3,'',6,1),(719,'2023-04-17 20:07:03.189101','48','[BCN0402]<RDA1P>',3,'',6,1),(720,'2023-04-17 20:07:03.192145','47','[BCN0402]<RETA TANGENTE>',3,'',6,1),(721,'2023-04-17 20:07:03.195126','50','[BCN0402]<TAXAS RELACIONADAS>',3,'',6,1),(722,'2023-04-17 20:07:26.470786','112','[BIJ0207]<SistemasEnergia>',3,'',6,1),(723,'2023-04-17 20:07:26.474331','64','[BIJ0207]<SistemasEnergia.old>',3,'',6,1),(724,'2023-04-17 20:07:26.477516','19','[CIP]<nível 1>',3,'',6,1),(725,'2023-04-17 20:07:26.480813','20','[CLIP]<nível 1>',3,'',6,1),(726,'2023-04-17 20:07:26.483740','128','[CN]<Sistemas Lineares>',3,'',6,1),(727,'2023-04-17 20:07:26.486877','129','[CN]<zeros de funções>',3,'',6,1),(728,'2023-04-17 20:07:26.489857','114','[Comp]<comp-topic1>',3,'',6,1),(729,'2023-04-17 20:07:26.493029','113','[Comp]<UFABC - TSI - Compiladores>',3,'',6,1),(730,'2023-04-17 20:07:26.496200','94','[CompMov]<CompMov1>',3,'',6,1),(731,'2023-04-17 20:07:26.499128','95','[CompMov]<CompMov2>',3,'',6,1),(732,'2023-04-17 20:07:26.502188','96','[CompMov]<CompMov3>',3,'',6,1),(733,'2023-04-17 20:07:26.505402','97','[CompMov]<CompMov4>',3,'',6,1),(734,'2023-04-17 20:07:26.508388','98','[CompMov]<CompMov5>',3,'',6,1),(735,'2023-04-17 20:07:26.511440','99','[CompMov]<CompMov6>',3,'',6,1),(736,'2023-04-17 20:07:26.514840','101','[CompMov]<CompMov7>',3,'',6,1),(737,'2023-04-17 20:07:26.517806','237','[CompMov]<TSI5-ComMov-Diogo>',3,'',6,1),(738,'2023-04-17 20:07:52.320889','21','[CPE]<nível 1>',3,'',6,1),(739,'2023-04-17 20:07:52.324013','185','[EESTO013-17]<Depreciação>',3,'',6,1),(740,'2023-04-17 20:07:52.326682','110','[EESTO013-17]<ESTO013-17 Juros>',3,'',6,1),(741,'2023-04-17 20:07:52.329336','122','[EESTO013-17]<ESTO013-17 Juros e Conceitos>',3,'',6,1),(742,'2023-04-17 20:07:52.331999','115','[EESTO013-17]<ESTO013-17 VPL Conceitos>',3,'',6,1),(743,'2023-04-17 20:07:52.334521','184','[EESTO013-17]<Inflação em Projetos>',3,'',6,1),(744,'2023-04-17 20:07:52.337272','178','[EP2021]<Selecao2021>',3,'',6,1),(745,'2023-04-17 20:07:52.339879','227','[EP2023]<seleção2023>',3,'',6,1),(746,'2023-04-17 20:07:52.342490','38','[ESTG010-17]<IT-2018-3Q>',3,'',6,1),(747,'2023-04-17 20:07:52.345222','39','[ESTG010-17]<IT-2018-3QP2>',3,'',6,1),(748,'2023-04-17 20:07:52.347843','153','[ESTG016-17]<QS-01-introducao>',3,'',6,1),(749,'2023-04-17 20:07:52.350339','134','[ESTG025-17]<Desenho Autor Marca>',3,'',6,1),(750,'2023-04-17 20:07:52.353301','135','[ESTG025-17]<Indicação Cultivar Geral>',3,'',6,1),(751,'2023-04-17 20:07:52.356032','136','[ESTG025-17]<Marcas>',3,'',6,1),(752,'2023-04-17 20:07:52.358659','130','[ESTG025-17]<Patentes>',3,'',6,1),(753,'2023-04-17 20:08:10.189780','11','[Ex]<template>',3,'',6,1),(754,'2023-04-17 20:08:10.192705','12','[Ex]<template-equação-paramétrica>',3,'',6,1),(755,'2023-04-17 20:08:10.195119','13','[Ex]<template-figura>',3,'',6,1),(756,'2023-04-17 20:08:10.197738','14','[Ex]<template-integral>',3,'',6,1),(757,'2023-04-17 20:08:10.201051','15','[Ex]<template-integral-fig>',3,'',6,1),(758,'2023-04-17 20:08:10.204670','16','[Ex]<template-mru>',3,'',6,1),(759,'2023-04-17 20:08:10.208188','192','[FEMEC]<FEMEC-Introdução>',3,'',6,1),(760,'2023-04-17 20:08:10.210847','65','[GA]<Vetores>',3,'',6,1),(761,'2023-04-17 20:08:10.213688','7','[GestGovTI]<Aula01>',3,'',6,1),(762,'2023-04-17 20:08:10.216291','8','[GestGovTI]<Aula02>',3,'',6,1),(763,'2023-04-17 20:08:10.219134','9','[GestGovTI]<Aula03>',3,'',6,1),(764,'2023-04-17 20:08:10.221894','10','[GestGovTI]<Aula04>',3,'',6,1),(765,'2023-04-17 20:08:10.225030','66','[GestPQSw]<PMBOK>',3,'',6,1),(766,'2023-04-17 20:08:10.228704','157','[IPE]<01-Introdução>',3,'',6,1),(767,'2023-04-17 20:08:10.232021','163','[IPE]<Tópico Exemplo>',3,'',6,1),(768,'2023-04-17 20:08:10.235295','67','[ITW]<internet>',3,'',6,1),(769,'2023-04-17 20:08:10.237925','35','[MCTA004-17]<introducao>',3,'',6,1),(770,'2023-04-17 20:08:10.240340','222','[MCTA004-17]<introducao2>',3,'',6,1),(771,'2023-04-17 20:08:10.242628','36','[MCTA004-17]<introducaoP2>',3,'',6,1),(772,'2023-04-17 20:08:10.245330','37','[MCTA004-17]<IntroducaoREC>',3,'',6,1),(773,'2023-04-17 20:08:10.248072','150','[MCTA023-13]<SD-10certificado>',3,'',6,1),(774,'2023-04-17 20:08:10.250760','151','[MCTA023-13]<SD-11cifrasclassicas1>',3,'',6,1),(775,'2023-04-17 20:08:10.253654','152','[MCTA023-13]<SD-12integridade>',3,'',6,1),(776,'2023-04-17 20:08:10.256447','140','[MCTA023-13]<SD-1fundamentos1>',3,'',6,1),(777,'2023-04-17 20:08:10.260302','141','[MCTA023-13]<SD-2fundamentos2>',3,'',6,1),(778,'2023-04-17 20:08:10.263461','143','[MCTA023-13]<SD-3cifrasclassicas2>',3,'',6,1),(779,'2023-04-17 20:08:10.266090','144','[MCTA023-13]<SD-4cifrasbloco>',3,'',6,1),(780,'2023-04-17 20:08:10.268676','145','[MCTA023-13]<SD-5hash>',3,'',6,1),(781,'2023-04-17 20:08:10.271272','146','[MCTA023-13]<SD-6chavepublica>',3,'',6,1),(782,'2023-04-17 20:08:10.273791','147','[MCTA023-13]<SD-7controleacesso1>',3,'',6,1),(783,'2023-04-17 20:08:10.276356','148','[MCTA023-13]<SD-8controleacesso2>',3,'',6,1),(784,'2023-04-17 20:08:10.280233','149','[MCTA023-13]<SD-9assinatura>',3,'',6,1),(785,'2023-04-17 20:08:10.284334','210','[MCTA028-15]<PE-01-introdução>',3,'',6,1),(786,'2023-04-17 20:08:10.287132','221','[MCTA028-15]<PE-01-recursão>',3,'',6,1),(787,'2023-04-17 20:08:10.289943','211','[MCTA028-15]<PE-02-vetor>',3,'',6,1),(788,'2023-04-17 20:08:10.292516','212','[MCTA028-15]<PE-03-matriz>',3,'',6,1),(789,'2023-04-17 20:08:10.295192','215','[MCTA028-15]<PE-04-arquivo>',3,'',6,1),(790,'2023-04-17 20:08:10.297967','214','[MCTA028-15]<PE-04-registro>',3,'',6,1),(791,'2023-04-17 20:08:10.300613','213','[MCTA028-15]<PE-05-ponteiro>',3,'',6,1),(792,'2023-04-17 20:08:10.303143','223','[MCTA028-15]<PE-06-Lista-Fila-Pilha>',3,'',6,1),(793,'2023-04-17 20:08:10.305527','28','[MCTA033]<APF>',3,'',6,1),(794,'2023-04-17 20:08:10.308040','22','[MCTA033]<CMMI>',3,'',6,1),(795,'2023-04-17 20:08:10.310531','34','[MCTA033]<ES>',3,'',6,1),(796,'2023-04-17 20:08:10.314286','30','[MCTA033]<Modelagem>',3,'',6,1),(797,'2023-04-17 20:08:10.317428','23','[MCTA033]<OO>',3,'',6,1),(798,'2023-04-17 20:08:10.320346','24','[MCTA033]<Padrão>',3,'',6,1),(799,'2023-04-17 20:08:10.323082','33','[MCTA033]<Processo>',3,'',6,1),(800,'2023-04-17 20:08:10.325718','32','[MCTA033]<Requisito>',3,'',6,1),(801,'2023-04-17 20:08:10.328251','27','[MCTA033]<RUP>',3,'',6,1),(802,'2023-04-17 20:08:10.330644','31','[MCTA033]<SI>',3,'',6,1),(803,'2023-04-17 20:08:10.333248','29','[MCTA033]<Teste>',3,'',6,1),(804,'2023-04-17 20:08:10.336690','25','[MCTA033]<UML>',3,'',6,1),(805,'2023-04-17 20:08:10.339652','85','[MetCient]<MetCient>',3,'',6,1),(806,'2023-04-17 20:08:10.342533','86','[ModDad]<ModDad>',3,'',6,1),(807,'2023-04-17 20:08:10.345645','180','[NHI2049]<LB-Lógica Proposicional>',3,'',6,1),(808,'2023-04-17 20:08:10.348605','177','[PDI]<im1-Introdução>',3,'',6,1),(809,'2023-04-17 20:08:10.351385','137','[PDI]<im2-Operadores Morfológicos>',3,'',6,1),(810,'2023-04-17 20:08:10.354289','68','[ProjSis]<projeto>',3,'',6,1),(811,'2023-04-17 20:08:10.356786','92','[SegInfo]<SegInfo1>',3,'',6,1),(812,'2023-04-17 20:08:10.359280','91','[SegInfo]<SegInfo2p1>',3,'',6,1),(813,'2023-04-17 20:08:10.361911','93','[SegInfo]<SegInfo2p2>',3,'',6,1),(814,'2023-04-17 20:08:10.364481','90','[SegInfo]<SegInfo3>',3,'',6,1),(815,'2023-04-17 20:08:10.366941','89','[SegInfo]<SegInfo4>',3,'',6,1),(816,'2023-04-17 20:08:10.369702','88','[SegInfo]<SegInfoFixas>',3,'',6,1),(817,'2023-04-17 20:08:10.372525','228','[Seleção]<guiou>',3,'',6,1),(818,'2023-04-17 20:08:10.375150','193','[Seleção]<OLD-sel>',3,'',6,1),(819,'2023-04-17 20:08:10.377748','203','[Seleção]<sel-Arquitetura>',3,'',6,1),(820,'2023-04-17 20:08:10.380420','205','[Seleção]<sel-Compilador>',3,'',6,1),(821,'2023-04-17 20:08:10.383746','204','[Seleção]<sel-Linguagens>',3,'',6,1),(822,'2023-04-17 20:08:10.387194','207','[Seleção]<sel-Memória>',3,'',6,1),(823,'2023-04-17 20:08:10.389855','202','[Seleção]<sel-Operações>',3,'',6,1),(824,'2023-04-17 20:08:10.392405','208','[Seleção]<sel-Redes>',3,'',6,1),(825,'2023-04-17 20:08:10.394836','209','[Seleção]<sel-SI>',3,'',6,1),(826,'2023-04-17 20:08:10.397431','206','[Seleção]<sel-SO>',3,'',6,1),(827,'2023-04-17 20:08:10.399994','69','[SisCom]<SisCom-Geral>',3,'',6,1),(828,'2023-04-17 20:08:10.402422','224','[SisCom]<TSI5-SisCom>',3,'',6,1),(829,'2023-04-17 20:08:10.404889','77','[SisCor]<SisCor01>',3,'',6,1),(830,'2023-04-17 20:08:10.407436','78','[SisCor]<SisCor02>',3,'',6,1),(831,'2023-04-17 20:08:10.409969','79','[SisCor]<SisCor03>',3,'',6,1),(832,'2023-04-17 20:08:10.412487','80','[SisCor]<SisCor04>',3,'',6,1),(833,'2023-04-17 20:08:10.414918','81','[SisCor]<SisCor05>',3,'',6,1),(834,'2023-04-17 20:08:10.417472','82','[SisCor]<SisCor06>',3,'',6,1),(835,'2023-04-17 20:08:10.420058','83','[SisCor]<SisCor07>',3,'',6,1),(836,'2023-04-17 20:08:10.423658','84','[SisCor]<SisCor08>',3,'',6,1),(837,'2023-04-17 20:08:10.427579','87','[SoftLivre]<SoftLivre>',3,'',6,1),(838,'2023-04-17 20:08:10.430523','226','[SoftLivre]<tsi5-Jorge>',3,'',6,1),(839,'2023-04-17 20:08:10.433389','70','[TecMult]<TecMult01>',3,'',6,1),(840,'2023-04-17 20:08:10.436014','71','[TecMult]<TecMult02>',3,'',6,1),(841,'2023-04-17 20:08:10.438799','72','[TecMult]<TecMult03>',3,'',6,1),(842,'2023-04-17 20:08:10.441530','73','[TecMult]<TecMult04>',3,'',6,1),(843,'2023-04-17 20:08:10.444213','74','[TecMult]<TecMult05>',3,'',6,1),(844,'2023-04-17 20:08:10.446788','75','[TecMult]<TecMult06>',3,'',6,1),(845,'2023-04-17 20:08:10.449583','76','[TecMult]<TecMult07>',3,'',6,1),(846,'2023-04-17 20:08:10.452225','216','[TSI-fase2]<Dado, Informação e Conhecimento>',3,'',6,1),(847,'2023-04-17 20:08:30.666301','6','[BCM0505]<6-módulo-parte2>',3,'',6,1),(848,'2023-04-17 20:08:30.669769','5','[BCM0505]<7-matriz>',3,'',6,1),(849,'2023-04-17 20:08:30.672530','11','[Ex]<template>',3,'',6,1),(850,'2023-04-17 20:08:30.675281','12','[Ex]<template-equação-paramétrica>',3,'',6,1),(851,'2023-04-17 20:08:30.678008','13','[Ex]<template-figura>',3,'',6,1),(852,'2023-04-17 20:08:30.680841','14','[Ex]<template-integral>',3,'',6,1),(853,'2023-04-17 20:08:30.683615','15','[Ex]<template-integral-fig>',3,'',6,1),(854,'2023-04-17 20:08:30.686676','16','[Ex]<template-mru>',3,'',6,1),(855,'2023-04-17 20:08:30.689551','192','[FEMEC]<FEMEC-Introdução>',3,'',6,1),(856,'2023-04-17 20:08:30.692333','65','[GA]<Vetores>',3,'',6,1),(857,'2023-04-17 20:08:45.962758','11','[Ex]<template>',3,'',6,1),(858,'2023-04-17 20:09:06.462434','192','[FEMEC]<FEMEC-Introdução>',3,'',6,1),(859,'2023-04-17 20:09:06.465832','65','[GA]<Vetores>',3,'',6,1),(860,'2023-04-17 20:09:06.468651','7','[GestGovTI]<Aula01>',3,'',6,1),(861,'2023-04-17 20:09:06.471572','8','[GestGovTI]<Aula02>',3,'',6,1),(862,'2023-04-17 20:09:06.474505','9','[GestGovTI]<Aula03>',3,'',6,1),(863,'2023-04-17 20:09:06.477340','10','[GestGovTI]<Aula04>',3,'',6,1),(864,'2023-04-17 20:09:06.480061','66','[GestPQSw]<PMBOK>',3,'',6,1),(865,'2023-04-17 20:09:06.482845','157','[IPE]<01-Introdução>',3,'',6,1),(866,'2023-04-17 20:09:06.485562','163','[IPE]<Tópico Exemplo>',3,'',6,1),(867,'2023-04-17 20:09:06.488239','67','[ITW]<internet>',3,'',6,1),(868,'2023-04-17 20:09:21.181274','65','[GA]<Vetores>',3,'',6,1),(869,'2023-04-17 20:09:32.282524','192','[FEMEC]<FEMEC-Introdução>',3,'',6,1),(870,'2023-04-17 20:09:43.821948','7','[GestGovTI]<Aula01>',3,'',6,1),(871,'2023-04-17 20:10:08.199563','66','[GestPQSw]<PMBOK>',2,'[]',6,1),(872,'2023-04-17 20:10:29.895766','66','[GestPQSw]<PMBOK>',3,'',6,1),(873,'2023-04-17 20:10:52.241449','157','[IPE]<01-Introdução>',3,'',6,1),(874,'2023-04-17 20:10:52.244645','163','[IPE]<Tópico Exemplo>',3,'',6,1),(875,'2023-04-17 20:10:52.247340','67','[ITW]<internet>',3,'',6,1),(876,'2023-04-17 20:10:52.250172','35','[MCTA004-17]<introducao>',3,'',6,1),(877,'2023-04-17 20:10:52.253387','222','[MCTA004-17]<introducao2>',3,'',6,1),(878,'2023-04-17 20:10:52.256464','36','[MCTA004-17]<introducaoP2>',3,'',6,1),(879,'2023-04-17 20:10:52.259378','37','[MCTA004-17]<IntroducaoREC>',3,'',6,1),(880,'2023-04-17 20:11:14.992281','150','[MCTA023-13]<SD-10certificado>',3,'',6,1),(881,'2023-04-17 20:11:14.995445','151','[MCTA023-13]<SD-11cifrasclassicas1>',3,'',6,1),(882,'2023-04-17 20:11:14.998145','152','[MCTA023-13]<SD-12integridade>',3,'',6,1),(883,'2023-04-17 20:11:15.000818','140','[MCTA023-13]<SD-1fundamentos1>',3,'',6,1),(884,'2023-04-17 20:11:15.004588','141','[MCTA023-13]<SD-2fundamentos2>',3,'',6,1),(885,'2023-04-17 20:11:15.008558','143','[MCTA023-13]<SD-3cifrasclassicas2>',3,'',6,1),(886,'2023-04-17 20:11:15.011875','144','[MCTA023-13]<SD-4cifrasbloco>',3,'',6,1),(887,'2023-04-17 20:11:15.014799','145','[MCTA023-13]<SD-5hash>',3,'',6,1),(888,'2023-04-17 20:11:15.017755','146','[MCTA023-13]<SD-6chavepublica>',3,'',6,1),(889,'2023-04-17 20:11:15.020756','147','[MCTA023-13]<SD-7controleacesso1>',3,'',6,1),(890,'2023-04-17 20:11:15.024089','148','[MCTA023-13]<SD-8controleacesso2>',3,'',6,1),(891,'2023-04-17 20:11:15.027292','149','[MCTA023-13]<SD-9assinatura>',3,'',6,1),(892,'2023-04-17 20:11:47.955647','210','[MCTA028-15]<PE-01-introdução>',3,'',6,1),(893,'2023-04-17 20:11:47.958994','221','[MCTA028-15]<PE-01-recursão>',3,'',6,1),(894,'2023-04-17 20:11:47.962062','211','[MCTA028-15]<PE-02-vetor>',3,'',6,1),(895,'2023-04-17 20:11:47.964925','212','[MCTA028-15]<PE-03-matriz>',3,'',6,1),(896,'2023-04-17 20:11:47.967741','215','[MCTA028-15]<PE-04-arquivo>',3,'',6,1),(897,'2023-04-17 20:11:47.970771','214','[MCTA028-15]<PE-04-registro>',3,'',6,1),(898,'2023-04-17 20:11:47.973522','213','[MCTA028-15]<PE-05-ponteiro>',3,'',6,1),(899,'2023-04-17 20:11:47.976281','223','[MCTA028-15]<PE-06-Lista-Fila-Pilha>',3,'',6,1),(900,'2023-04-17 20:11:47.978900','28','[MCTA033]<APF>',3,'',6,1),(901,'2023-04-17 20:11:47.981603','22','[MCTA033]<CMMI>',3,'',6,1),(902,'2023-04-17 20:11:47.984293','34','[MCTA033]<ES>',3,'',6,1),(903,'2023-04-17 20:11:47.986953','30','[MCTA033]<Modelagem>',3,'',6,1),(904,'2023-04-17 20:11:47.989692','23','[MCTA033]<OO>',3,'',6,1),(905,'2023-04-17 20:11:47.992669','24','[MCTA033]<Padrão>',3,'',6,1),(906,'2023-04-17 20:11:47.995348','33','[MCTA033]<Processo>',3,'',6,1),(907,'2023-04-17 20:11:47.998204','32','[MCTA033]<Requisito>',3,'',6,1),(908,'2023-04-17 20:11:48.001816','27','[MCTA033]<RUP>',3,'',6,1),(909,'2023-04-17 20:11:48.004497','31','[MCTA033]<SI>',3,'',6,1),(910,'2023-04-17 20:11:48.007194','29','[MCTA033]<Teste>',3,'',6,1),(911,'2023-04-17 20:11:48.010158','25','[MCTA033]<UML>',3,'',6,1),(912,'2023-04-17 20:12:18.278314','177','[PDI]<im1-Introdução>',3,'',6,1),(913,'2023-04-17 20:12:18.281726','137','[PDI]<im2-Operadores Morfológicos>',3,'',6,1),(914,'2023-04-17 20:12:18.284530','68','[ProjSis]<projeto>',3,'',6,1),(915,'2023-04-17 20:12:18.287208','92','[SegInfo]<SegInfo1>',3,'',6,1),(916,'2023-04-17 20:12:18.290319','91','[SegInfo]<SegInfo2p1>',3,'',6,1),(917,'2023-04-17 20:12:18.293339','93','[SegInfo]<SegInfo2p2>',3,'',6,1),(918,'2023-04-17 20:12:18.296015','90','[SegInfo]<SegInfo3>',3,'',6,1),(919,'2023-04-17 20:12:18.298825','89','[SegInfo]<SegInfo4>',3,'',6,1),(920,'2023-04-17 20:12:18.302658','88','[SegInfo]<SegInfoFixas>',3,'',6,1),(921,'2023-04-17 20:12:18.306619','228','[Seleção]<guiou>',3,'',6,1),(922,'2023-04-17 20:12:18.309724','193','[Seleção]<OLD-sel>',3,'',6,1),(923,'2023-04-17 20:12:18.312421','203','[Seleção]<sel-Arquitetura>',3,'',6,1),(924,'2023-04-17 20:12:18.315159','205','[Seleção]<sel-Compilador>',3,'',6,1),(925,'2023-04-17 20:12:18.319050','204','[Seleção]<sel-Linguagens>',3,'',6,1),(926,'2023-04-17 20:12:18.322018','207','[Seleção]<sel-Memória>',3,'',6,1),(927,'2023-04-17 20:12:18.325320','202','[Seleção]<sel-Operações>',3,'',6,1),(928,'2023-04-17 20:12:18.328694','208','[Seleção]<sel-Redes>',3,'',6,1),(929,'2023-04-17 20:12:18.331577','209','[Seleção]<sel-SI>',3,'',6,1),(930,'2023-04-17 20:12:18.334310','206','[Seleção]<sel-SO>',3,'',6,1),(931,'2023-04-17 20:12:52.013475','85','[MetCient]<MetCient>',3,'',6,1),(932,'2023-04-17 20:12:52.016571','86','[ModDad]<ModDad>',3,'',6,1),(933,'2023-04-17 20:12:52.019100','180','[NHI2049]<LB-Lógica Proposicional>',3,'',6,1),(934,'2023-04-17 20:12:52.021669','69','[SisCom]<SisCom-Geral>',3,'',6,1),(935,'2023-04-17 20:12:52.024216','224','[SisCom]<TSI5-SisCom>',3,'',6,1),(936,'2023-04-17 20:12:52.026708','77','[SisCor]<SisCor01>',3,'',6,1),(937,'2023-04-17 20:12:52.029323','78','[SisCor]<SisCor02>',3,'',6,1),(938,'2023-04-17 20:12:52.031799','79','[SisCor]<SisCor03>',3,'',6,1),(939,'2023-04-17 20:12:52.034124','80','[SisCor]<SisCor04>',3,'',6,1),(940,'2023-04-17 20:12:52.036594','81','[SisCor]<SisCor05>',3,'',6,1),(941,'2023-04-17 20:12:52.038985','82','[SisCor]<SisCor06>',3,'',6,1),(942,'2023-04-17 20:12:52.041498','83','[SisCor]<SisCor07>',3,'',6,1),(943,'2023-04-17 20:12:52.043974','84','[SisCor]<SisCor08>',3,'',6,1),(944,'2023-04-17 20:12:52.046370','87','[SoftLivre]<SoftLivre>',3,'',6,1),(945,'2023-04-17 20:12:52.048930','226','[SoftLivre]<tsi5-Jorge>',3,'',6,1),(946,'2023-04-17 20:12:52.051499','70','[TecMult]<TecMult01>',3,'',6,1),(947,'2023-04-17 20:12:52.054092','71','[TecMult]<TecMult02>',3,'',6,1),(948,'2023-04-17 20:12:52.056750','72','[TecMult]<TecMult03>',3,'',6,1),(949,'2023-04-17 20:12:52.059366','73','[TecMult]<TecMult04>',3,'',6,1),(950,'2023-04-17 20:12:52.062031','74','[TecMult]<TecMult05>',3,'',6,1),(951,'2023-04-17 20:12:52.065092','75','[TecMult]<TecMult06>',3,'',6,1),(952,'2023-04-17 20:12:52.067592','76','[TecMult]<TecMult07>',3,'',6,1),(953,'2023-04-17 20:13:02.604692','216','[TSI-fase2]<Dado, Informação e Conhecimento>',3,'',6,1),(954,'2023-04-17 20:13:02.607855','217','[TSI-fase2]<Mundo Digital>',3,'',6,1),(955,'2023-04-17 20:13:02.610775','218','[TSI-fase2]<Teoria da Informação>',3,'',6,1),(956,'2023-04-17 20:13:02.613551','219','[TSI-fase3]<fase3>',3,'',6,1),(957,'2023-04-17 20:13:10.139904','10','[GestGovTI]<Aula04>',3,'',6,1),(958,'2023-04-17 20:13:38.459985','1','[Ex]<1-sequencial>',2,'[{\"changed\": {\"fields\": [\"Disciplines\"]}}]',6,1),(959,'2023-04-17 20:13:51.329721','1','[Ex]<1-sequencial>',3,'',6,1),(960,'2023-04-17 20:14:35.378841','3','IE - CE - Disciplina Exemplo',3,'',11,1),(961,'2023-04-17 20:14:35.384740','11','UFABC - ARI - Curso de Italiano Presencial',3,'',11,1),(962,'2023-04-17 20:14:35.389934','12','UFABC - ARI - Curso de Língua Inglesa Presencial',3,'',11,1),(963,'2023-04-17 20:14:35.395288','13','UFABC - ARI - Curso Presencial de Espanhol',3,'',11,1),(964,'2023-04-17 20:14:35.400838','15','UFABC - BCC - Arquitetura de Computadores',3,'',11,1),(965,'2023-04-17 20:14:35.406334','34','UFABC - BCC - Compiladores',3,'',11,1),(966,'2023-04-17 20:14:35.411541','14','UFABC - BCC - Engenharia de Software',3,'',11,1),(967,'2023-04-17 20:14:35.416648','38','UFABC - BCC - Processamento Digital de Imagens',3,'',11,1),(968,'2023-04-17 20:14:35.421752','46','UFABC - BCC - Programação Estruturada',3,'',11,1),(969,'2023-04-17 20:14:35.426870','39','UFABC - BCC - Segurança de Dados',3,'',11,1),(970,'2023-04-17 20:14:35.431833','31','UFABC - BCC - Segurança de Dados',3,'',11,1),(971,'2023-04-17 20:14:35.437100','17','UFABC - BCT-H-Lic - Bases Computacionais da Ciência',3,'',11,1),(972,'2023-04-17 20:14:35.442241','42','UFABC - BCT-H-Lic - Comunicação e Redes',3,'',11,1),(973,'2023-04-17 20:14:35.447376','45','UFABC - BCT-H-Lic - Fenômenos Mecânicos',3,'',11,1),(974,'2023-04-17 20:14:35.453209','18','UFABC - BCT-H-Lic - Funções de Uma Variável',3,'',11,1),(975,'2023-04-17 20:14:35.459570','21','UFABC - BCT-H-Lic - Geometria Analítica',3,'',11,1),(976,'2023-04-17 20:14:35.464699','41','UFABC - BCT-H-Lic - Introdução à Probabilidade e à Estatística',3,'',11,1),(977,'2023-04-17 20:14:35.469843','44','UFABC - BCT-H-Lic - Lógica Básica',3,'',11,1),(978,'2023-04-17 20:14:35.474942','19','UFABC - BCT-H-Lic - Natureza da Informação',3,'',11,1),(979,'2023-04-17 20:14:35.480074','1','UFABC - BCT-H-Lic - Processamento da Informação',3,'',11,1),(980,'2023-04-17 20:14:35.485260','36','UFABC - BMat - Cálculo Numérico',3,'',11,1),(981,'2023-04-17 20:14:35.490504','20','UFABC - EE - Bases Conceituais da Energia',3,'',11,1),(982,'2023-04-17 20:14:35.495727','33','UFABC - EG - Engenharia Econômica',3,'',11,1),(983,'2023-04-17 20:14:35.500691','16','UFABC - EG - Inovação Tecnológica',3,'',11,1),(984,'2023-04-17 20:14:35.505752','37','UFABC - EG - Propriedade Intelectual',3,'',11,1),(985,'2023-04-17 20:14:35.510961','40','UFABC - EG - Qualidade em Sistemas',3,'',11,1),(986,'2023-04-17 20:14:35.516672','43','UFABC - EP - Processo seletivo 2021',3,'',11,1),(987,'2023-04-17 20:14:35.521855','50','UFABC - EP - Processo seletivo 2023',3,'',11,1),(988,'2023-04-17 20:14:35.527067','5','UFABC - EP - PROVA DE SELEÇÃO DE 2020',3,'',11,1),(989,'2023-04-17 20:14:35.532399','6','UFABC - EP - Simulados',3,'',11,1),(990,'2023-04-17 20:14:35.537619','32','UFABC - TSI - Computação Móvel',3,'',11,1),(991,'2023-04-17 20:14:35.543255','22','UFABC - TSI - Gestão de Projetos e Qualidade de Software',3,'',11,1),(992,'2023-04-17 20:14:35.548371','2','UFABC - TSI - Gestão e Governança de TI',3,'',11,1),(993,'2023-04-17 20:14:35.553577','23','UFABC - TSI - Internet e Tecnologias Web',3,'',11,1),(994,'2023-04-17 20:14:35.559846','28','UFABC - TSI - Metodologia Científica',3,'',11,1),(995,'2023-04-17 20:14:35.565611','29','UFABC - TSI - Modelagem de Dados',3,'',11,1),(996,'2023-04-17 20:14:35.570836','47','UFABC - TSI - Processo Seletivo',3,'',11,1),(997,'2023-04-17 20:14:35.575816','48','UFABC - TSI - Processo Seletivo - Fase 2',3,'',11,1),(998,'2023-04-17 20:14:35.580942','49','UFABC - TSI - Processo Seletivo - Fase 3',3,'',11,1),(999,'2023-04-17 20:14:35.585910','24','UFABC - TSI - Projeto de Sistemas',3,'',11,1),(1000,'2023-04-17 20:14:35.590881','25','UFABC - TSI - Sistemas Computacionais',3,'',11,1),(1001,'2023-04-17 20:14:35.595941','27','UFABC - TSI - Sistemas Corporativos da Informação',3,'',11,1),(1002,'2023-04-17 20:14:35.600880','30','UFABC - TSI - Software Livre',3,'',11,1),(1003,'2023-04-17 20:14:35.605886','26','UFABC - TSI - Tecnologias Multimídia',3,'',11,1),(1004,'2023-04-17 20:14:57.679582','3','IE - CE - Disciplina Exemplo',3,'',11,1),(1005,'2023-04-17 20:15:10.843929','11','UFABC - ARI - Curso de Italiano Presencial',3,'',11,1),(1006,'2023-04-17 20:15:10.850365','12','UFABC - ARI - Curso de Língua Inglesa Presencial',3,'',11,1),(1007,'2023-04-17 20:15:10.856593','13','UFABC - ARI - Curso Presencial de Espanhol',3,'',11,1),(1008,'2023-04-17 20:15:22.011828','15','UFABC - BCC - Arquitetura de Computadores',3,'',11,1),(1009,'2023-04-17 20:15:22.017477','34','UFABC - BCC - Compiladores',3,'',11,1),(1010,'2023-04-17 20:15:22.022979','14','UFABC - BCC - Engenharia de Software',3,'',11,1),(1011,'2023-04-17 20:15:22.027799','38','UFABC - BCC - Processamento Digital de Imagens',3,'',11,1),(1012,'2023-04-17 20:15:35.558924','46','UFABC - BCC - Programação Estruturada',3,'',11,1),(1013,'2023-04-17 20:15:35.566017','39','UFABC - BCC - Segurança de Dados',3,'',11,1),(1014,'2023-04-17 20:15:35.572714','31','UFABC - BCC - Segurança de Dados',3,'',11,1),(1015,'2023-04-17 20:15:35.578034','17','UFABC - BCT-H-Lic - Bases Computacionais da Ciência',3,'',11,1),(1016,'2023-04-17 20:15:35.583101','42','UFABC - BCT-H-Lic - Comunicação e Redes',3,'',11,1),(1017,'2023-04-17 20:15:49.840934','45','UFABC - BCT-H-Lic - Fenômenos Mecânicos',3,'',11,1),(1018,'2023-04-17 20:15:49.846860','18','UFABC - BCT-H-Lic - Funções de Uma Variável',3,'',11,1),(1019,'2023-04-17 20:15:49.852284','21','UFABC - BCT-H-Lic - Geometria Analítica',3,'',11,1),(1020,'2023-04-17 20:15:49.857445','41','UFABC - BCT-H-Lic - Introdução à Probabilidade e à Estatística',3,'',11,1),(1021,'2023-04-17 20:15:49.862820','44','UFABC - BCT-H-Lic - Lógica Básica',3,'',11,1),(1022,'2023-04-17 20:15:49.867948','19','UFABC - BCT-H-Lic - Natureza da Informação',3,'',11,1),(1023,'2023-04-17 20:15:49.872900','1','UFABC - BCT-H-Lic - Processamento da Informação',3,'',11,1),(1024,'2023-04-17 20:16:04.945143','45','UFABC - BCT-H-Lic - Fenômenos Mecânicos',3,'',11,1),(1025,'2023-04-17 20:16:04.950825','18','UFABC - BCT-H-Lic - Funções de Uma Variável',3,'',11,1),(1026,'2023-04-17 20:16:04.957485','21','UFABC - BCT-H-Lic - Geometria Analítica',3,'',11,1),(1027,'2023-04-17 20:16:04.963839','41','UFABC - BCT-H-Lic - Introdução à Probabilidade e à Estatística',3,'',11,1),(1028,'2023-04-17 20:16:22.192462','44','UFABC - BCT-H-Lic - Lógica Básica',3,'',11,1),(1029,'2023-04-17 20:16:22.198396','19','UFABC - BCT-H-Lic - Natureza da Informação',3,'',11,1),(1030,'2023-04-17 20:16:22.203581','36','UFABC - BMat - Cálculo Numérico',3,'',11,1),(1031,'2023-04-17 20:16:22.209912','20','UFABC - EE - Bases Conceituais da Energia',3,'',11,1),(1032,'2023-04-17 20:16:22.215895','33','UFABC - EG - Engenharia Econômica',3,'',11,1),(1033,'2023-04-17 20:16:37.754675','16','UFABC - EG - Inovação Tecnológica',3,'',11,1),(1034,'2023-04-17 20:16:37.760069','37','UFABC - EG - Propriedade Intelectual',3,'',11,1),(1035,'2023-04-17 20:16:37.765293','40','UFABC - EG - Qualidade em Sistemas',3,'',11,1),(1036,'2023-04-17 20:16:37.770435','43','UFABC - EP - Processo seletivo 2021',3,'',11,1),(1037,'2023-04-17 20:16:37.775449','50','UFABC - EP - Processo seletivo 2023',3,'',11,1),(1038,'2023-04-17 20:16:37.780377','5','UFABC - EP - PROVA DE SELEÇÃO DE 2020',3,'',11,1),(1039,'2023-04-17 20:16:37.785820','6','UFABC - EP - Simulados',3,'',11,1),(1040,'2023-04-17 20:16:37.790562','32','UFABC - TSI - Computação Móvel',3,'',11,1),(1041,'2023-04-17 20:16:37.795410','22','UFABC - TSI - Gestão de Projetos e Qualidade de Software',3,'',11,1),(1042,'2023-04-17 20:16:37.800816','2','UFABC - TSI - Gestão e Governança de TI',3,'',11,1),(1043,'2023-04-17 20:16:37.805803','23','UFABC - TSI - Internet e Tecnologias Web',3,'',11,1),(1044,'2023-04-17 20:16:37.812099','28','UFABC - TSI - Metodologia Científica',3,'',11,1),(1045,'2023-04-17 20:16:37.818500','29','UFABC - TSI - Modelagem de Dados',3,'',11,1),(1046,'2023-04-17 20:16:37.823520','47','UFABC - TSI - Processo Seletivo',3,'',11,1),(1047,'2023-04-17 20:16:37.828523','48','UFABC - TSI - Processo Seletivo - Fase 2',3,'',11,1),(1048,'2023-04-17 20:16:37.833794','49','UFABC - TSI - Processo Seletivo - Fase 3',3,'',11,1),(1049,'2023-04-17 20:16:37.841142','24','UFABC - TSI - Projeto de Sistemas',3,'',11,1),(1050,'2023-04-17 20:16:37.847070','25','UFABC - TSI - Sistemas Computacionais',3,'',11,1),(1051,'2023-04-17 20:16:37.852157','27','UFABC - TSI - Sistemas Corporativos da Informação',3,'',11,1),(1052,'2023-04-17 20:16:37.859300','30','UFABC - TSI - Software Livre',3,'',11,1),(1053,'2023-04-17 20:16:37.865375','26','UFABC - TSI - Tecnologias Multimídia',3,'',11,1),(1054,'2023-04-17 20:16:52.750206','16','UFABC - EG - Inovação Tecnológica',3,'',11,1),(1055,'2023-04-17 20:16:52.757602','37','UFABC - EG - Propriedade Intelectual',3,'',11,1),(1056,'2023-04-17 20:16:52.763340','40','UFABC - EG - Qualidade em Sistemas',3,'',11,1),(1057,'2023-04-17 20:16:52.771273','43','UFABC - EP - Processo seletivo 2021',3,'',11,1),(1058,'2023-04-17 20:16:52.776534','50','UFABC - EP - Processo seletivo 2023',3,'',11,1),(1059,'2023-04-17 20:16:52.781765','5','UFABC - EP - PROVA DE SELEÇÃO DE 2020',3,'',11,1),(1060,'2023-04-17 20:17:09.686955','6','UFABC - EP - Simulados',3,'',11,1),(1061,'2023-04-17 20:17:09.692599','32','UFABC - TSI - Computação Móvel',3,'',11,1),(1062,'2023-04-17 20:17:09.698076','22','UFABC - TSI - Gestão de Projetos e Qualidade de Software',3,'',11,1),(1063,'2023-04-17 20:17:09.703784','2','UFABC - TSI - Gestão e Governança de TI',3,'',11,1),(1064,'2023-04-17 20:17:09.709268','23','UFABC - TSI - Internet e Tecnologias Web',3,'',11,1),(1065,'2023-04-17 20:17:09.714343','28','UFABC - TSI - Metodologia Científica',3,'',11,1),(1066,'2023-04-17 20:17:23.113517','6','UFABC - EP - Simulados',3,'',11,1),(1067,'2023-04-17 20:17:30.848542','32','UFABC - TSI - Computação Móvel',3,'',11,1),(1068,'2023-04-17 20:17:45.226107','24','UFABC - TSI - Projeto de Sistemas',3,'',11,1),(1069,'2023-04-17 20:17:45.232039','25','UFABC - TSI - Sistemas Computacionais',3,'',11,1),(1070,'2023-04-17 20:17:45.237358','27','UFABC - TSI - Sistemas Corporativos da Informação',3,'',11,1),(1071,'2023-04-17 20:17:45.244858','30','UFABC - TSI - Software Livre',3,'',11,1),(1072,'2023-04-17 20:17:45.249967','26','UFABC - TSI - Tecnologias Multimídia',3,'',11,1),(1073,'2023-04-17 20:17:55.360620','29','UFABC - TSI - Modelagem de Dados',3,'',11,1),(1074,'2023-04-17 20:17:55.365974','47','UFABC - TSI - Processo Seletivo',3,'',11,1),(1075,'2023-04-17 20:17:55.371093','48','UFABC - TSI - Processo Seletivo - Fase 2',3,'',11,1),(1076,'2023-04-17 20:17:55.376175','49','UFABC - TSI - Processo Seletivo - Fase 3',3,'',11,1),(1077,'2023-04-17 20:18:04.649250','2','UFABC - TSI - Gestão e Governança de TI',3,'',11,1),(1078,'2023-04-17 20:18:04.655177','23','UFABC - TSI - Internet e Tecnologias Web',3,'',11,1),(1079,'2023-04-17 20:18:04.660446','28','UFABC - TSI - Metodologia Científica',3,'',11,1),(1080,'2023-04-17 20:18:14.990849','23','UFABC - TSI - Internet e Tecnologias Web',3,'',11,1),(1081,'2023-04-17 20:18:14.996387','28','UFABC - TSI - Metodologia Científica',3,'',11,1),(1082,'2023-04-17 20:18:25.624709','22','UFABC - TSI - Gestão de Projetos e Qualidade de Software',3,'',11,1),(1083,'2023-04-17 20:18:51.417875','2','UFABC - TSI - Gestão e Governança de TI',2,'[{\"changed\": {\"fields\": [\"Discipline professors\", \"Discipline coordinators\"]}}]',11,1),(1084,'2023-04-17 20:19:00.416321','2','UFABC - TSI - Gestão e Governança de TI',3,'',11,1),(1085,'2023-04-17 20:19:23.117470','2','IE - CE - Gestão e Governança de TI',2,'[{\"changed\": {\"fields\": [\"Discipline course\"]}}]',11,1),(1086,'2023-04-17 20:19:33.812397','2','IE - CE - Gestão e Governança de TI',3,'',11,1),(1087,'2023-04-17 20:20:04.659958','10','UFABC - Bacharelado em Matemática',3,'',9,1),(1088,'2023-04-17 20:20:04.663128','9','UFABC - Engenharia de Energia',3,'',9,1),(1089,'2023-04-17 20:20:04.665817','5','UFABC - Escola Preparatória',3,'',9,1),(1090,'2023-04-17 20:20:04.668429','11','UFABC - Pós-Graduação em Ciência da Computação',3,'',9,1),(1091,'2023-04-17 20:20:04.671063','6','UFABC - Relações Internacionais',3,'',9,1),(1092,'2023-04-17 20:20:13.208967','2','UFABC - Tecnologias e Sistemas de Informação',3,'',9,1),(1093,'2023-04-17 20:20:19.326699','8','UFABC - Engenharia de Gestão',3,'',9,1),(1094,'2023-04-17 20:20:28.042777','1','UFABC - Bacharelado em Ciência e Tec./Hum. e Licenciaturas',3,'',9,1),(1095,'2023-04-17 20:20:34.911433','7','UFABC - Bacharelado em Ciência da Computação',3,'',9,1),(1096,'2023-04-17 20:20:51.608890','1','Universidade Federal do ABC',3,'',10,1),(1097,'2023-04-17 20:21:23.104294','6','alexandre.donizeti@ufabc.edu.br',3,'',17,1),(1098,'2023-04-17 20:21:23.106265','7','alexandre.noma@ufabc.edu.br',3,'',17,1),(1099,'2023-04-17 20:21:23.107604','52','aline.lima@mj.gov.br',3,'',17,1),(1100,'2023-04-17 20:21:23.108778','58','ana.muta@ufabc.edu.br',3,'',17,1),(1101,'2023-04-17 20:21:23.110002','95','ana.simoes@ufabc.edu.br',3,'',17,1),(1102,'2023-04-17 20:21:23.111259','85','andre.cravo@ufabc.edu.br',3,'',17,1),(1103,'2023-04-17 20:21:23.112378','86','andre.t@ufabc.edu.br',3,'',17,1),(1104,'2023-04-17 20:21:23.113671','82','angelica.lima@ufabc.edu.br',3,'',17,1),(1105,'2023-04-17 20:21:23.114776','87','c.sato@ufabc.edu.br',3,'',17,1),(1106,'2023-04-17 20:21:23.115989','14','celso.kurashima@ufabc.edu.br',3,'',17,1),(1107,'2023-04-17 20:21:23.117155','93','claudio.meneses@ufabc.edu.br',3,'',17,1),(1108,'2023-04-17 20:21:23.118281','88','cristiane.salum@ufabc.edu.br',3,'',17,1),(1109,'2023-04-17 20:21:23.119529','17','daniel.boari@ufabc.edu.br',3,'',17,1),(1110,'2023-04-17 20:21:23.120854','103','david.martins@ufabc.edu.br',3,'',17,1),(1111,'2023-04-17 20:21:23.122335','79','denise.goya@ufabc.edu.br',3,'',17,1),(1112,'2023-04-17 20:21:23.123573','81','diego.ferruzzo@ufabc.edu.br',3,'',17,1),(1113,'2023-04-17 20:21:23.124829','78','edson.iriarte@ufabc.edu.br',3,'',17,1),(1114,'2023-04-17 20:21:23.126192','20','edson.pimentel@ufabc.edu.br',3,'',17,1),(1115,'2023-04-17 20:21:23.127365','61','ercilio.silva@ufabc.edu.br',3,'',17,1),(1116,'2023-04-17 20:21:23.128541','54','fabio.souza@ufabc.edu.br',3,'',17,1),(1117,'2023-04-17 20:21:23.129656','23','fernando.teubl@ufabc.edu.br',3,'',17,1),(1118,'2023-04-17 20:21:23.130854','22','folivetti@ufabc.edu.br',3,'',17,1),(1119,'2023-04-17 20:21:23.131985','25','francisco.fraga@ufabc.edu.br',3,'',17,1),(1120,'2023-04-17 20:21:23.133118','98','fzampirolli3@ufabc.edu.br',3,'',17,1),(1121,'2023-04-17 20:21:23.134230','83','fzprof1@ufabc.edu.br',3,'',17,1),(1122,'2023-04-17 20:21:23.137893','106','geiza.silva@ufabc.edu.br',3,'',17,1),(1123,'2023-04-17 20:21:23.139259','102','graca.marietto@ufabc.edu.br',3,'',17,1),(1124,'2023-04-17 20:21:23.140639','60','guiou.kobayashi@ufabc.edu.br',3,'',17,1),(1125,'2023-04-17 20:21:23.141872','89','harlen.batagelo@ufabc.edu.br',3,'',17,1),(1126,'2023-04-17 20:21:23.143119','69','irineu.antunes@ufabc.edu.br',3,'',17,1),(1127,'2023-04-17 20:21:23.144388','76','itana@ufabc.edu.br',3,'',17,1),(1128,'2023-04-17 20:21:23.145902','107','roberto.rodrigues@ufabc.edu.br',3,'',17,1),(1129,'2023-04-17 20:21:23.147872','100','jair.donadelli@ufabc.edu.br',3,'',17,1),(1130,'2023-04-17 20:21:23.149585','77','joao.gois@ufabc.edu.br',3,'',17,1),(1131,'2023-04-17 20:21:23.151056','62','joao.moreira@ufabc.edu.br',3,'',17,1),(1132,'2023-04-17 20:21:23.152426','31','john.sims@ufabc.edu.br',3,'',17,1),(1133,'2023-04-17 20:21:23.153516','63','jorge.tomioka@ufabc.edu.br',3,'',17,1),(1134,'2023-04-17 20:21:23.154708','70','juliana.braga@ufabc.edu.br',3,'',17,1),(1135,'2023-04-17 20:21:23.155853','64','leandro.teodoro@ufabc.edu.br',3,'',17,1),(1136,'2023-04-17 20:21:23.157106','57','luciana.milena@ufabc.edu.br',3,'',17,1),(1137,'2023-04-17 20:21:23.158157','94','luiz.bonani@ufabc.edu.br',3,'',17,1),(1138,'2023-04-17 20:21:23.159260','33','luiz.rozante@gmail.com',3,'',17,1),(1139,'2023-04-17 20:21:23.160313','34','luneque.junior@ufabc.edu.br',3,'',17,1),(1140,'2023-04-17 20:21:23.161323','71','manic.gordana@ufabc.edu.br',3,'',17,1),(1141,'2023-04-17 20:21:23.162823','105','marcelo.reyes@ufabc.edu.br',3,'',17,1),(1142,'2023-04-17 20:21:23.163897','36','marcio.oikawa@ufabc.edu.br',3,'',17,1),(1143,'2023-04-17 20:21:23.164979','39','mirtha.lina@ufabc.edu.br',3,'',17,1),(1144,'2023-04-17 20:21:23.166041','97','muhsen.hammoud@ufabc.edu.br',3,'',17,1),(1145,'2023-04-17 20:21:23.167329','41','natalia.emelianova@ufabc.edu.br',3,'',17,1),(1146,'2023-04-17 20:21:23.168413','101','paulo.meirelles@ufabc.edu.br',3,'',17,1),(1147,'2023-04-17 20:21:23.169622','42','paulo.pisani@ufabc.edu.br',3,'',17,1),(1148,'2023-04-17 20:21:23.170806','104','pedro.autreto@ufabc.edu.br',3,'',17,1),(1149,'2023-04-17 20:21:23.172101','84','peter.claessens@ufabc.edu.br',3,'',17,1),(1150,'2023-04-17 20:21:23.173292','59','r.fernando@ufabc.edu.br',3,'',17,1),(1151,'2023-04-17 20:21:23.174375','91','r.sadao@ufabc.edu.br',3,'',17,1),(1152,'2023-04-17 20:21:23.175648','2','rafaela.rocha@ufabc.edu.br',3,'',17,1),(1153,'2023-04-17 20:21:23.176789','68','renato.coutinho@ufabc.edu.br',3,'',17,1),(1154,'2023-04-17 20:21:23.178108','99','renato.watanabe@ufabc.edu.br',3,'',17,1),(1155,'2023-04-17 20:21:23.179450','96','ricardo.liang@ufabc.edu.br',3,'',17,1),(1156,'2023-04-17 20:21:23.180556','92','ronaldo.prati@ufabc.edu.br',3,'',17,1),(1157,'2023-04-17 20:21:23.181642','56','sandra.trevisan@ufabc.edu.br',3,'',17,1),(1158,'2023-04-17 20:21:23.182755','55','steil@ufabc.edu.br',3,'',17,1),(1159,'2023-04-17 20:21:23.184021','74','thiago.covoes@ufabc.edu.br',3,'',17,1),(1160,'2023-04-17 20:21:23.185154','80','ugo.ibusuki@ufabc.edu.br',3,'',17,1),(1161,'2023-04-17 20:21:23.186438','48','valerio.batista@ufabc.edu.br',3,'',17,1),(1162,'2023-04-17 20:21:23.187630','49','vera.nagamuta@ufabc.edu.br',3,'',17,1),(1163,'2023-04-17 20:21:23.188986','90','wagner.tanaka@ufabc.edu.br',3,'',17,1),(1164,'2023-04-17 20:21:53.587786','1',' -  - Processamento da Informação',3,'',11,1),(1165,'2023-04-17 20:22:13.649027','1',' -  - Processamento da Informação',2,'[{\"changed\": {\"fields\": [\"Discipline professors\", \"Discipline coordinators\"]}}]',11,1),(1166,'2023-04-17 20:22:22.660209','1',' -  - Processamento da Informação',3,'',11,1),(1168,'2023-04-17 20:22:56.152527','1','[]<1-sequencial>',3,'',6,1),(1169,'2023-04-17 20:24:09.252550','1','IE - CE - Processamento da Informação',2,'[{\"changed\": {\"fields\": [\"Discipline course\"]}}]',11,1),(1170,'2023-04-17 20:24:30.774516','1','IE - CE - Processamento da Informação',3,'',11,1),(1171,'2023-04-17 20:24:58.098133','2','Instituto Exemplo',3,'',10,1),(1172,'2023-04-17 20:25:17.397742','2',' - CE - Gestão e Governança de TI',3,'',11,1),(1173,'2023-04-17 20:25:58.502795','1','[]<1-sequencial>',3,'',6,1),(1174,'2023-04-17 20:38:33.768947','1',' -  - Processamento da Informação',3,'',11,1),(1175,'2023-04-17 20:38:40.965183','2',' -  - Gestão e Governança de TI',3,'',11,1),(1176,'2023-04-17 20:41:04.370405','1','[]<1-sequencial>',3,'',6,1),(1177,'2023-04-17 20:41:14.608974','2','[]<3-condicional>',3,'',6,1),(1178,'2023-04-17 20:41:14.612228','3','[]<4-repetição>',3,'',6,1),(1179,'2023-04-17 20:41:14.615025','4','[]<5-vetor>',3,'',6,1),(1180,'2023-04-17 20:41:14.618412','6','[]<6-módulo-parte2>',3,'',6,1),(1181,'2023-04-17 20:41:14.621889','5','[]<7-matriz>',3,'',6,1),(1182,'2023-04-17 20:41:14.625798','7','[]<Aula01>',3,'',6,1),(1183,'2023-04-17 20:41:14.628613','8','[]<Aula02>',3,'',6,1),(1184,'2023-04-17 20:41:14.631292','9','[]<Aula03>',3,'',6,1),(1185,'2023-04-17 20:41:14.634115','10','[]<Aula04>',3,'',6,1),(1186,'2023-04-17 20:41:14.637023','11','[]<template>',3,'',6,1),(1187,'2023-04-17 20:41:14.640026','12','[]<template-equação-paramétrica>',3,'',6,1),(1188,'2023-04-17 20:41:14.642954','13','[]<template-figura>',3,'',6,1),(1189,'2023-04-17 20:41:14.647211','14','[]<template-integral>',3,'',6,1),(1190,'2023-04-17 20:41:14.651322','15','[]<template-integral-fig>',3,'',6,1),(1191,'2023-04-17 20:41:14.654270','16','[]<template-mru>',3,'',6,1),(1192,'2023-04-17 20:44:26.557999','238','[DE]<Topico Exemplo>',1,'[{\"added\": {}}]',6,1),(1193,'2023-04-17 20:46:48.086717','2443','oi_d_lento; top Topico Exemplo; typ QM; dif 1; gro Questao Exemplo; par no; #2443; ans 5; des QE',1,'[{\"added\": {}}, {\"added\": {\"name\": \"answer\", \"object\": \"Answer object (8930)\"}}, {\"added\": {\"name\": \"answer\", \"object\": \"Answer object (8931)\"}}, {\"added\": {\"name\": \"answer\", \"object\": \"Answer object (8932)\"}}, {\"added\": {\"name\": \"answer\", \"object\": \"Answer object (8933)\"}}, {\"added\": {\"name\": \"answer\", \"object\": \"Answer object (8934)\"}}]',7,1),(1194,'2023-04-18 19:22:12.539157','1','fzampirolli@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"password\"]}}]',17,1),(1195,'2023-04-18 19:22:48.113585','66','fzcoord@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"password\"]}}]',17,1),(1196,'2023-04-18 19:23:12.199786','65','fzprof@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"password\"]}}]',17,1),(1197,'2023-04-18 19:23:37.931394','53','fzstudent@ufabc.edu.br',2,'[{\"changed\": {\"fields\": [\"password\"]}}]',17,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (17,'account','user'),(1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'contenttypes','contenttype'),(12,'course','classroom'),(9,'course','course'),(11,'course','discipline'),(10,'course','institute'),(18,'exam','classroomexam'),(13,'exam','exam'),(14,'exam','studentexam'),(15,'exam','studentexamquestion'),(19,'exam','variationexam'),(5,'sessions','session'),(16,'student','student'),(8,'topic','answer'),(7,'topic','question'),(6,'topic','topic');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2019-01-14 18:01:58.050393'),(2,'contenttypes','0002_remove_content_type_name','2019-01-14 18:01:58.807552'),(3,'auth','0001_initial','2019-01-14 18:02:01.560553'),(4,'auth','0002_alter_permission_name_max_length','2019-01-14 18:02:01.644818'),(5,'auth','0003_alter_user_email_max_length','2019-01-14 18:02:01.674140'),(6,'auth','0004_alter_user_username_opts','2019-01-14 18:02:01.708541'),(7,'auth','0005_alter_user_last_login_null','2019-01-14 18:02:01.741010'),(8,'auth','0006_require_contenttypes_0002','2019-01-14 18:02:01.770593'),(9,'auth','0007_alter_validators_add_error_messages','2019-01-14 18:02:01.799339'),(10,'auth','0008_alter_user_username_max_length','2019-01-14 18:02:01.833219'),(11,'auth','0009_alter_user_last_name_max_length','2019-01-14 18:02:01.866606'),(12,'account','0001_initial','2019-01-14 18:02:04.996024'),(13,'admin','0001_initial','2019-01-14 18:02:06.435302'),(14,'admin','0002_logentry_remove_auto_add','2019-01-14 18:02:06.475307'),(15,'admin','0003_logentry_add_action_flag_choices','2019-01-14 18:02:06.510048'),(16,'student','0001_initial','2019-01-14 18:02:06.748331'),(17,'course','0001_initial','2019-01-14 18:02:23.528385'),(18,'topic','0001_initial','2019-01-14 18:02:27.206037'),(19,'exam','0001_initial','2019-01-14 18:02:34.008320'),(20,'sessions','0001_initial','2019-01-14 18:02:34.430247'),(21,'exam','0002_auto_20190516_1209','2019-05-16 15:10:06.040410'),(22,'exam','0003_auto_20190516_1212','2019-05-16 15:13:03.506141'),(23,'exam','0004_auto_20190516_1218','2019-05-16 15:18:27.574141'),(24,'exam','0005_auto_20190516_1221','2019-05-16 15:21:24.027940'),(25,'exam','0006_auto_20190516_1225','2019-05-16 15:25:54.076721'),(26,'exam','0007_auto_20190516_1701','2019-05-16 20:01:41.733709'),(27,'auth','0010_alter_group_name_max_length','2019-09-02 13:17:15.440985'),(28,'auth','0011_update_proxy_permissions','2019-09-02 13:17:15.486559'),(29,'account','0001_squashed_0001_initial','2019-09-02 13:17:15.489816'),(30,'auth','0012_alter_user_first_name_max_length','2023-04-16 21:38:05.056043');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('6bkvenjhpms5t5hqtj0osp64qrv4qoia','.eJxVjDsOgzAQBe-ydWSxxsnalOk5g2Uv6-B8jIQhTZS7J0g0tG9m3gfK-vLvXPNSoTMn8GFdRr9WmX0eoAOEwxYDP6RsYLiHcpsUT2WZc1SbonZaVT8N8rzu7uFgDHX81-GsbQpBrGgm7YjYkTOEbbKSWkJjG-s4xUsUagSN00mcIBM3WiMjfH-JIDzr:1poAUi:_IGXUfTlb-Ww6B8ClQKfAbz0Z-WqHEIF4a1mEzeH6ms','2023-04-30 22:05:12.566797'),('8pmhspw3qtni8aplahikuydegnc30064','.eJxVjEsOwjAMBe_iNYrqtOCkS_acIXJch4ZPKjUtG8TdAambbt_MvDeU9RleuealQk8HCLwuY1irziEP0APCbossdy1_MNy4XCcjU1nmHM1fMRut5jIN-jhv7u5g5Dr-aj5al5jVqRWynkg8-Y6wTU5TS9i5xnlJ8RSVGsXO26ReUUgaa1EQPl-LJDzu:1poWaI:0rHZEv7HsdgaKvgofiPBVNnJjUV8FdKMwQZiT7IlBQU','2023-05-01 21:40:26.251775'),('abkr7xgenau6xyxog5ojhqmkxckvzs4a','eyJudW1fdmlzaXRzIjoxfQ:1poWz4:Ag8M9PXeqeyAnzU84KKFjEYsSawk1iDelVoaL3t2NMM','2023-05-01 22:06:02.104105'),('f8446tksu730gajit317ukfizdveq8ny','eyJudW1fdmlzaXRzIjoxfQ:1poqve:TT6bDKl7Ji5SIRPUE8UpMFoqZ0tqYh7m4TUEz__rHpw','2023-05-02 19:23:50.998501'),('lf0cqwqml0ozbloigke66e82n9v3yc4d','.eJxVjEsOwjAMBe_iNYrqtOCkS_acIXJch4ZPKjUtG8TdAambbt_MvDeU9RleuealQu8PEHhdxrBWnUMeoAeE3RZZ7lr-YLhxuU5GprLMOZq_YjZazWUa9HHe3N3ByHX81Xy0LjGrUytkPZF48h1hm5ymlrBzjfOS4ikqNYqdt0m9opA01qIgfL6MfDzw:1poPEP:R_Q96IddxIzaaDwk0V6d9r5DfJBEqa7Z9Khx5pLuhS0','2023-05-01 13:49:21.369099'),('lsqa9d8ms1uzt5x1ptpo9wyia2tdg1ne','NWNmNzBlOWMyOTBjZDE0MTE3YTFkNDhlYjU5YmZkZDAzYTBhZGQwNTp7Im51bV92aXNpdHMiOjMsIl9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiIzOGNjNTlmYzMwMmFkMWMyZmE2ZWY0ODdmNzAxODJlMDU5Yjg0Nzc1In0=','2023-12-21 17:27:40.203130'),('rgys2ur51zdn7svn2uk81wcgal1niy3t','eyJudW1fdmlzaXRzIjoyfQ:1poPLQ:bWcFBpV8OSIBo9alTqGLqM9LvI7yD8TylMJpFx_MIlU','2023-05-01 13:56:36.550054');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exam_classroomexam`
--

DROP TABLE IF EXISTS `exam_classroomexam`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_classroomexam` (
  `id` int NOT NULL AUTO_INCREMENT,
  `grade` varchar(20) NOT NULL,
  `exam_id` int DEFAULT NULL,
  `classroom_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `exam_id` (`exam_id`),
  KEY `classroom_id` (`classroom_id`),
  CONSTRAINT `exam_classroomexam_ibfk_1` FOREIGN KEY (`exam_id`) REFERENCES `exam_exam` (`id`),
  CONSTRAINT `exam_classroomexam_ibfk_2` FOREIGN KEY (`classroom_id`) REFERENCES `course_classroom` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_classroomexam`
--

LOCK TABLES `exam_classroomexam` WRITE;
/*!40000 ALTER TABLE `exam_classroomexam` DISABLE KEYS */;
/*!40000 ALTER TABLE `exam_classroomexam` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exam_exam`
--

DROP TABLE IF EXISTS `exam_exam`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_exam` (
  `id` int NOT NULL AUTO_INCREMENT,
  `exam_name` varchar(20) DEFAULT NULL,
  `exam_number_of_questions_var1` varchar(3) NOT NULL,
  `exam_number_of_questions_var2` varchar(3) NOT NULL,
  `exam_number_of_questions_var3` varchar(3) NOT NULL,
  `exam_number_of_questions_var4` varchar(3) NOT NULL,
  `exam_number_of_questions_var5` varchar(3) NOT NULL,
  `exam_number_of_anwsers_question` varchar(2) NOT NULL,
  `exam_number_of_questions_text` varchar(3) NOT NULL,
  `exam_variations` varchar(3) NOT NULL,
  `exam_max_questions_square` varchar(2) NOT NULL,
  `exam_max_squares_horizontal` varchar(2) NOT NULL,
  `exam_stylesheet` varchar(3) NOT NULL,
  `exam_print` varchar(4) NOT NULL,
  `exam_print_eco` varchar(3) NOT NULL,
  `exam_student_feedback` varchar(3) NOT NULL,
  `exam_room` varchar(20) DEFAULT NULL,
  `exam_hour` datetime(6) NOT NULL,
  `exam_term` varchar(2) NOT NULL,
  `exam_instructions` longtext NOT NULL,
  `exam_who_created_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `exam_exam_exam_who_created_id_de138c84_fk_account_user_id` (`exam_who_created_id`),
  CONSTRAINT `exam_exam_exam_who_created_id_de138c84_fk_account_user_id` FOREIGN KEY (`exam_who_created_id`) REFERENCES `account_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=477 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_exam`
--

LOCK TABLES `exam_exam` WRITE;
/*!40000 ALTER TABLE `exam_exam` DISABLE KEYS */;
INSERT INTO `exam_exam` VALUES (476,'exameTesteQR-QM','20','0','0','0','0','5','0','2','10','1','Hor','answ','yes','no',NULL,'2023-12-07 05:00:00.000000','t1','\\item desligar o celular',1);
/*!40000 ALTER TABLE `exam_exam` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exam_exam_classrooms`
--

DROP TABLE IF EXISTS `exam_exam_classrooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_exam_classrooms` (
  `id` int NOT NULL AUTO_INCREMENT,
  `exam_id` int NOT NULL,
  `classroom_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `exam_exam_classrooms_exam_id_classroom_id_c4ecc31d_uniq` (`exam_id`,`classroom_id`),
  KEY `exam_exam_classrooms_classroom_id_6435a4cf_fk_course_cl` (`classroom_id`),
  CONSTRAINT `exam_exam_classrooms_classroom_id_6435a4cf_fk_course_cl` FOREIGN KEY (`classroom_id`) REFERENCES `course_classroom` (`id`),
  CONSTRAINT `exam_exam_classrooms_exam_id_edf09d98_fk_exam_exam_id` FOREIGN KEY (`exam_id`) REFERENCES `exam_exam` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9429 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_exam_classrooms`
--

LOCK TABLES `exam_exam_classrooms` WRITE;
/*!40000 ALTER TABLE `exam_exam_classrooms` DISABLE KEYS */;
INSERT INTO `exam_exam_classrooms` VALUES (9428,476,670);
/*!40000 ALTER TABLE `exam_exam_classrooms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exam_exam_questions`
--

DROP TABLE IF EXISTS `exam_exam_questions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_exam_questions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `exam_id` int NOT NULL,
  `question_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `exam_exam_questions_exam_id_question_id_fb2c5892_uniq` (`exam_id`,`question_id`),
  KEY `exam_exam_questions_question_id_cc6e86f0_fk_topic_question_id` (`question_id`),
  CONSTRAINT `exam_exam_questions_exam_id_74f97ebb_fk_exam_exam_id` FOREIGN KEY (`exam_id`) REFERENCES `exam_exam` (`id`),
  CONSTRAINT `exam_exam_questions_question_id_cc6e86f0_fk_topic_question_id` FOREIGN KEY (`question_id`) REFERENCES `topic_question` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41088 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_exam_questions`
--

LOCK TABLES `exam_exam_questions` WRITE;
/*!40000 ALTER TABLE `exam_exam_questions` DISABLE KEYS */;
/*!40000 ALTER TABLE `exam_exam_questions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exam_exam_topics`
--

DROP TABLE IF EXISTS `exam_exam_topics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_exam_topics` (
  `id` int NOT NULL AUTO_INCREMENT,
  `exam_id` int NOT NULL,
  `topic_id` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_exam_topics`
--

LOCK TABLES `exam_exam_topics` WRITE;
/*!40000 ALTER TABLE `exam_exam_topics` DISABLE KEYS */;
INSERT INTO `exam_exam_topics` VALUES (1,561,11);
/*!40000 ALTER TABLE `exam_exam_topics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exam_studentexam`
--

DROP TABLE IF EXISTS `exam_studentexam`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_studentexam` (
  `id` int NOT NULL AUTO_INCREMENT,
  `grade` varchar(20) NOT NULL,
  `exam_id` int DEFAULT NULL,
  `student_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `exam_studentexam_exam_id_b33d0b66_fk_exam_exam_id` (`exam_id`),
  KEY `exam_studentexam_student_id_b67a86ca_fk_student_student_id` (`student_id`),
  CONSTRAINT `exam_studentexam_exam_id_b33d0b66_fk_exam_exam_id` FOREIGN KEY (`exam_id`) REFERENCES `exam_exam` (`id`),
  CONSTRAINT `exam_studentexam_student_id_b67a86ca_fk_student_student_id` FOREIGN KEY (`student_id`) REFERENCES `student_student` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2803 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_studentexam`
--

LOCK TABLES `exam_studentexam` WRITE;
/*!40000 ALTER TABLE `exam_studentexam` DISABLE KEYS */;
/*!40000 ALTER TABLE `exam_studentexam` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exam_studentexamquestion`
--

DROP TABLE IF EXISTS `exam_studentexamquestion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_studentexamquestion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `studentAnswer` varchar(2) NOT NULL,
  `answersOrder` varchar(10) NOT NULL,
  `question_id` int DEFAULT NULL,
  `studentExam_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `exam_studentexamques_question_id_f120cc5c_fk_topic_que` (`question_id`),
  KEY `exam_studentexamques_studentExam_id_0fcf82a2_fk_exam_stud` (`studentExam_id`),
  CONSTRAINT `exam_studentexamques_question_id_f120cc5c_fk_topic_que` FOREIGN KEY (`question_id`) REFERENCES `topic_question` (`id`),
  CONSTRAINT `exam_studentexamques_studentExam_id_0fcf82a2_fk_exam_stud` FOREIGN KEY (`studentExam_id`) REFERENCES `exam_studentexam` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31323 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_studentexamquestion`
--

LOCK TABLES `exam_studentexamquestion` WRITE;
/*!40000 ALTER TABLE `exam_studentexamquestion` DISABLE KEYS */;
/*!40000 ALTER TABLE `exam_studentexamquestion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exam_variationexam`
--

DROP TABLE IF EXISTS `exam_variationexam`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_variationexam` (
  `id` int NOT NULL AUTO_INCREMENT,
  `variation` longtext NOT NULL,
  `exam_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `exam_variationexam_exam_id_ba3b75d0_fk_exam_exam_id` (`exam_id`),
  CONSTRAINT `exam_variationexam_exam_id_ba3b75d0_fk_exam_exam_id` FOREIGN KEY (`exam_id`) REFERENCES `exam_exam` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=60968 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_variationexam`
--

LOCK TABLES `exam_variationexam` WRITE;
/*!40000 ALTER TABLE `exam_variationexam` DISABLE KEYS */;
/*!40000 ALTER TABLE `exam_variationexam` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_student`
--

DROP TABLE IF EXISTS `student_student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_student` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_name` varchar(50) NOT NULL,
  `student_ID` varchar(20) NOT NULL,
  `student_email` varchar(254) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=28518 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_student`
--

LOCK TABLES `student_student` WRITE;
/*!40000 ALTER TABLE `student_student` DISABLE KEYS */;
/*!40000 ALTER TABLE `student_student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `topic_answer`
--

DROP TABLE IF EXISTS `topic_answer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `topic_answer` (
  `id` int NOT NULL AUTO_INCREMENT,
  `answer_text` longtext NOT NULL,
  `answer_feedback` longtext NOT NULL,
  `question_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `topic_answer_question_id_9112ef5a_fk_topic_question_id` (`question_id`),
  CONSTRAINT `topic_answer_question_id_9112ef5a_fk_topic_question_id` FOREIGN KEY (`question_id`) REFERENCES `topic_question` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8945 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `topic_answer`
--

LOCK TABLES `topic_answer` WRITE;
/*!40000 ALTER TABLE `topic_answer` DISABLE KEYS */;
INSERT INTO `topic_answer` VALUES (8930,'1a alternativa criada','',2443),(8931,'2a alternativa criada','',2443),(8932,'3a alternativa criada','',2443),(8933,'4a alternativa criada','',2443),(8934,'5a alternativa criada','',2443),(8935,'1a alternativa criada','',2444),(8936,'2a alternativa criada','',2444),(8937,'3a alternativa criada','',2444),(8938,'4a alternativa criada','',2444),(8939,'5a alternativa criada','',2444),(8940,'1a alternativa criada','',2445),(8941,'2a alternativa criada','',2445),(8942,'3a alternativa criada','',2445),(8943,'4a alternativa criada','',2445),(8944,'5a alternativa criada','',2445);
/*!40000 ALTER TABLE `topic_answer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `topic_question`
--

DROP TABLE IF EXISTS `topic_question`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `topic_question` (
  `id` int NOT NULL AUTO_INCREMENT,
  `question_group` varchar(50) NOT NULL,
  `question_short_description` varchar(50) NOT NULL,
  `question_text` longtext NOT NULL,
  `question_type` varchar(2) NOT NULL,
  `question_difficulty` varchar(2) NOT NULL,
  `question_bloom_taxonomy` varchar(10) NOT NULL,
  `question_parametric` varchar(3) NOT NULL,
  `question_last_update` date DEFAULT NULL,
  `question_who_created_id` int DEFAULT NULL,
  `topic_id` int DEFAULT NULL,
  `question_correction_count` int DEFAULT '0',
  `question_correct_count` int DEFAULT '0',
  `question_IRT_a_discrimination` double DEFAULT '0',
  `question_IRT_b_ability` double DEFAULT '0',
  `question_IRT_c_guessing` double DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `topic_question_question_who_created_0b2f6e68_fk_account_u` (`question_who_created_id`),
  KEY `topic_question_topic_id_aa9661f2_fk_topic_topic_id` (`topic_id`),
  CONSTRAINT `topic_question_question_who_created_0b2f6e68_fk_account_u` FOREIGN KEY (`question_who_created_id`) REFERENCES `account_user` (`id`),
  CONSTRAINT `topic_question_topic_id_aa9661f2_fk_topic_topic_id` FOREIGN KEY (`topic_id`) REFERENCES `topic_topic` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2447 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `topic_question`
--

LOCK TABLES `topic_question` WRITE;
/*!40000 ALTER TABLE `topic_question` DISABLE KEYS */;
INSERT INTO `topic_question` VALUES (2443,'','QE1','Primeira Questao - Sempre a primeira alternativa criada eh a correta.','QM','1','remember','no','2023-04-17',1,238,0,0,0,0,0),(2444,'','QE2','Segunda Questao','QM','1','remember','no','2023-04-17',1,238,0,0,0,0,0),(2445,'','QE3','Terceira questao','QM','1','remember','no','2023-04-17',1,238,0,0,0,0,0),(2446,'','QE 4','Quarta questão.','QM','1','remember','no','2023-12-07',1,238,0,0,0,0,0);
/*!40000 ALTER TABLE `topic_question` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `topic_topic`
--

DROP TABLE IF EXISTS `topic_topic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `topic_topic` (
  `id` int NOT NULL AUTO_INCREMENT,
  `topic_text` varchar(50) NOT NULL,
  `topic_description` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=239 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `topic_topic`
--

LOCK TABLES `topic_topic` WRITE;
/*!40000 ALTER TABLE `topic_topic` DISABLE KEYS */;
INSERT INTO `topic_topic` VALUES (238,'Topico Exemplo','');
/*!40000 ALTER TABLE `topic_topic` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `topic_topic_course`
--

DROP TABLE IF EXISTS `topic_topic_course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `topic_topic_course` (
  `id` int NOT NULL AUTO_INCREMENT,
  `topic_id` int NOT NULL,
  `discipline_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `topic_topic_course_topic_id_discipline_id_1242b109_uniq` (`topic_id`,`discipline_id`),
  KEY `topic_topic_course_discipline_id_921e41cb_fk_course_di` (`discipline_id`),
  CONSTRAINT `topic_topic_course_discipline_id_921e41cb_fk_course_di` FOREIGN KEY (`discipline_id`) REFERENCES `course_discipline` (`id`),
  CONSTRAINT `topic_topic_course_topic_id_2b0bcc7c_fk_topic_topic_id` FOREIGN KEY (`topic_id`) REFERENCES `topic_topic` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `topic_topic_course`
--

LOCK TABLES `topic_topic_course` WRITE;
/*!40000 ALTER TABLE `topic_topic_course` DISABLE KEYS */;
/*!40000 ALTER TABLE `topic_topic_course` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `topic_topic_discipline`
--

DROP TABLE IF EXISTS `topic_topic_discipline`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `topic_topic_discipline` (
  `id` int NOT NULL AUTO_INCREMENT,
  `topic_id` int NOT NULL,
  `discipline_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `topic_topic_discipline_topic_id_discipline_id_2180320d_uniq` (`topic_id`,`discipline_id`),
  KEY `topic_topic_discipli_discipline_id_7980c44d_fk_course_di` (`discipline_id`),
  CONSTRAINT `topic_topic_discipli_discipline_id_7980c44d_fk_course_di` FOREIGN KEY (`discipline_id`) REFERENCES `course_discipline` (`id`),
  CONSTRAINT `topic_topic_discipline_topic_id_80b689ef_fk_topic_topic_id` FOREIGN KEY (`topic_id`) REFERENCES `topic_topic` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `topic_topic_discipline`
--

LOCK TABLES `topic_topic_discipline` WRITE;
/*!40000 ALTER TABLE `topic_topic_discipline` DISABLE KEYS */;
INSERT INTO `topic_topic_discipline` VALUES (1,238,51);
/*!40000 ALTER TABLE `topic_topic_discipline` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-12-07 18:11:19
