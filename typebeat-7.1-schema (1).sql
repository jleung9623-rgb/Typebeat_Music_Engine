-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: typebeat_ai_v7
-- ------------------------------------------------------
-- Server version	8.0.44

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
-- Table structure for table `artists`
--

DROP TABLE IF EXISTS `artists`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `artists` (
  `artist_id` int NOT NULL AUTO_INCREMENT,
  `artist_name` varchar(50) NOT NULL,
  `genre_id` int NOT NULL,
  PRIMARY KEY (`artist_id`),
  UNIQUE KEY `artist_name` (`artist_name`),
  KEY `genre_id` (`genre_id`),
  CONSTRAINT `artists_ibfk_1` FOREIGN KEY (`genre_id`) REFERENCES `genres` (`genre_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `chord_notes`
--

DROP TABLE IF EXISTS `chord_notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chord_notes` (
  `note_id` int NOT NULL AUTO_INCREMENT,
  `chord_id` int NOT NULL,
  PRIMARY KEY (`note_id`),
  KEY `chord_id` (`chord_id`),
  CONSTRAINT `chord_notes_ibfk_1` FOREIGN KEY (`chord_id`) REFERENCES `chords` (`chord_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `chords`
--

DROP TABLE IF EXISTS `chords`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chords` (
  `chord_id` int NOT NULL AUTO_INCREMENT,
  `chord_name` varchar(20) NOT NULL,
  `chord_class` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`chord_id`),
  UNIQUE KEY `chord_name` (`chord_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `compositions`
--

DROP TABLE IF EXISTS `compositions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compositions` (
  `comp_id` int NOT NULL AUTO_INCREMENT,
  `artist_id` int NOT NULL,
  `file_path` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `file_name` varchar(255) NOT NULL,
  PRIMARY KEY (`comp_id`),
  KEY `artist_id` (`artist_id`),
  CONSTRAINT `compositions_ibfk_1` FOREIGN KEY (`artist_id`) REFERENCES `artists` (`artist_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `genres`
--

DROP TABLE IF EXISTS `genres`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `genres` (
  `genre_id` int NOT NULL AUTO_INCREMENT,
  `genre_name` varchar(50) NOT NULL,
  `default_tempo` int DEFAULT '120',
  `time_signature` varchar(10) DEFAULT '4/4',
  `entropy_pivot_bar` int DEFAULT '8',
  PRIMARY KEY (`genre_id`),
  UNIQUE KEY `genre_name` (`genre_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `motif_notes`
--

DROP TABLE IF EXISTS `motif_notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `motif_notes` (
  `note_id` int NOT NULL AUTO_INCREMENT,
  `motif_id` int DEFAULT NULL,
  `pitch_value` int DEFAULT NULL,
  `chord_id` int DEFAULT NULL,
  `duration` float DEFAULT NULL,
  `beat_position` float DEFAULT NULL,
  `micro_offset` float DEFAULT '0',
  PRIMARY KEY (`note_id`),
  KEY `motif_id` (`motif_id`),
  KEY `chord_id` (`chord_id`),
  CONSTRAINT `motif_notes_ibfk_1` FOREIGN KEY (`motif_id`) REFERENCES `motifs` (`motif_id`) ON DELETE CASCADE,
  CONSTRAINT `motif_notes_ibfk_2` FOREIGN KEY (`chord_id`) REFERENCES `chords` (`chord_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `motifs`
--

DROP TABLE IF EXISTS `motifs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `motifs` (
  `motif_id` int NOT NULL AUTO_INCREMENT,
  `motif_name` varchar(50) DEFAULT NULL,
  `sequence_data` varchar(100) DEFAULT NULL,
  `phrase_latency` float DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `motif_weight` float DEFAULT '1',
  `occurrence_count` int DEFAULT '0',
  `motif_class` enum('Opening','Verse','Pre-Chorus','Chorus','Build','De-escalation','Bridge','Entropic','Rest','Outro') DEFAULT NULL,
  `track_id` int DEFAULT NULL,
  `motif_pivot_offset` float DEFAULT NULL,
  PRIMARY KEY (`motif_id`),
  UNIQUE KEY `sequence_data` (`sequence_data`),
  KEY `fk_track` (`track_id`),
  CONSTRAINT `fk_track` FOREIGN KEY (`track_id`) REFERENCES `tracks` (`track_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scales`
--

DROP TABLE IF EXISTS `scales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `scales` (
  `scale_id` int NOT NULL AUTO_INCREMENT,
  `scale_name` varchar(50) NOT NULL,
  `intervals` varchar(50) NOT NULL,
  `default_root_note` int DEFAULT '60',
  PRIMARY KEY (`scale_id`),
  UNIQUE KEY `scale_name` (`scale_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `song_blueprints`
--

DROP TABLE IF EXISTS `song_blueprints`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `song_blueprints` (
  `blueprint_id` int NOT NULL AUTO_INCREMENT,
  `genre_id` int NOT NULL,
  `block_position` int NOT NULL,
  `block_class` enum('Opening','Verse','Pre-Chorus','Chorus','Build','De-escalation','Bridge','Entropic','Rest','Outro') NOT NULL,
  PRIMARY KEY (`blueprint_id`),
  KEY `genre_id` (`genre_id`),
  CONSTRAINT `song_blueprints_ibfk_1` FOREIGN KEY (`genre_id`) REFERENCES `genres` (`genre_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tracks`
--

DROP TABLE IF EXISTS `tracks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tracks` (
  `track_id` int NOT NULL AUTO_INCREMENT,
  `track_name` varchar(50) NOT NULL,
  `midi_channel` int NOT NULL,
  `instrument_name` varchar(50) DEFAULT 'Acoustic Grand Piano',
  `patch_number` int DEFAULT '1',
  `genre_id` int DEFAULT NULL,
  `track_motif_limit` int DEFAULT '32',
  `scale_id` int DEFAULT NULL,
  PRIMARY KEY (`track_id`),
  KEY `fk_track_genre` (`genre_id`),
  KEY `fk_track_scale` (`scale_id`),
  CONSTRAINT `fk_track_genre` FOREIGN KEY (`genre_id`) REFERENCES `genres` (`genre_id`),
  CONSTRAINT `fk_track_scale` FOREIGN KEY (`scale_id`) REFERENCES `scales` (`scale_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `transitions`
--

DROP TABLE IF EXISTS `transitions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transitions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `from_motif_id` int NOT NULL,
  `to_motif_id` int NOT NULL,
  `weight` float DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `fk_from_motif` (`from_motif_id`),
  KEY `fk_to_motif` (`to_motif_id`),
  CONSTRAINT `fk_from_motif` FOREIGN KEY (`from_motif_id`) REFERENCES `motifs` (`motif_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_to_motif` FOREIGN KEY (`to_motif_id`) REFERENCES `motifs` (`motif_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_preferences`
--

DROP TABLE IF EXISTS `user_preferences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_preferences` (
  `pref_id` int NOT NULL AUTO_INCREMENT,
  `setting_key` varchar(50) DEFAULT NULL,
  `setting_value` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`pref_id`),
  UNIQUE KEY `setting_key` (`setting_key`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-06 15:04:18
