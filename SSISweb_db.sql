CREATE DATABASE  IF NOT EXISTS `ssisweb_db` 

--
-- Table structure for table `college`
--

DROP TABLE IF EXISTS `college`;

CREATE TABLE `college` (
  `code` varchar(8) NOT NULL,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- data for table `college`
--

LOCK TABLES `college` WRITE;
INSERT INTO `college` VALUES ('CCS','College of Computer Studies');
UNLOCK TABLES;

--
-- Table structure for table `course`
--

DROP TABLE IF EXISTS `course`;
CREATE TABLE `course` (
  `code` varchar(8) NOT NULL,
  `name` varchar(50) NOT NULL,
  `college` varchar(8) DEFAULT NULL,
  PRIMARY KEY (`code`),
  UNIQUE KEY `Course_UNIQUE` (`name`),
  KEY `college` (`college`),
  CONSTRAINT `college` FOREIGN KEY (`college`) REFERENCES `college` (`code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


--
-- data for table `course`
--

LOCK TABLES `course` WRITE;
INSERT INTO `course` VALUES ('BSCS','Bachelor of Science in Computer Science','CCS');
UNLOCK TABLES;

--
-- Table structure for table `student_info`
--

DROP TABLE IF EXISTS `student_info`;
CREATE TABLE `student_info` (
  `id` varchar(9) NOT NULL,
  `firstname` varchar(45) NOT NULL,
  `lastname` varchar(45) NOT NULL,
  `year` int NOT NULL,
  `gender` enum('Male','Female','Non-binary','Transgender','Prefer not to say','Not listed') NOT NULL,
  `course` varchar(8) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `Student ID_UNIQUE` (`id`),
  KEY `Course_idx` (`course`),
  CONSTRAINT `Course` FOREIGN KEY (`course`) REFERENCES `course` (`code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


--
-- data for table `student_info`
--

LOCK TABLES `student_info` WRITE;
INSERT INTO `student_info` VALUES ('2021-2362','Rhea','Guingao',3,'Female','BSCS');
UNLOCK TABLES;



