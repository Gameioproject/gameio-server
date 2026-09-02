-- MariaDB dump 10.19-11.3.2-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: romm
-- ------------------------------------------------------
-- Server version	11.3.2-MariaDB-1:11.3.2+maria~ubu2204

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `hashed_password` varchar(255) DEFAULT NULL,
  `enabled` tinyint(1) NOT NULL,
  `role` varchar(20) NOT NULL,
  `avatar_path` varchar(255) NOT NULL,
  `last_login` timestamp NULL DEFAULT NULL,
  `last_active` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `email` varchar(255) DEFAULT NULL,
  `ra_username` varchar(255) DEFAULT NULL,
  `ra_progression` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`ra_progression`)),
  `ui_settings` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`ui_settings`)),
  `permission_group_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_username` (`username`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `ix_users_permission_group_id` (`permission_group_id`),
  CONSTRAINT `fk_users_permission_group_id` FOREIGN KEY (`permission_group_id`) REFERENCES `permission_groups` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES
(1,'admin','$2b$12$ldjOP2oAZd0VTCe.dis.i.fp9N7zK8g3.3ka63VycecjNwxFdAInm',1,'admin','','2026-08-29 22:10:41','2026-08-31 23:20:06','2026-08-29 22:10:36','2026-08-31 23:20:06','naifalqarni.cs@gmail.com','','{}','{}',NULL),
(2,'claudetest','$2b$12$eOXran40zls.7ulj9cYy1OWVrj/iwfj/G9sT/Vdi860Buu.0N8MXy',1,'admin','','2026-08-29 23:15:40','2026-09-01 02:16:45','2026-08-29 23:15:33','2026-09-01 02:16:45',NULL,'','{}','{}',NULL),
(3,'naif','$2b$12$kuZPz3SghMpWJqjNXk4XWOcDv4AOD70kzzJ2.4wWPVkt5ro9wqW9q',1,'user','',NULL,'2026-09-02 21:24:00','2026-09-01 02:08:55','2026-09-02 21:24:00','naif@playgameio.com','','{}','{}',NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `game_hosts`
--

DROP TABLE IF EXISTS `game_hosts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `game_hosts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `kind` enum('INTERNET_ARCHIVE','HTTP') NOT NULL,
  `base` varchar(1000) NOT NULL,
  `platform_slug` varchar(100) DEFAULT NULL,
  `enabled` tinyint(1) NOT NULL DEFAULT 1,
  `index_started_at` timestamp NULL DEFAULT NULL,
  `last_indexed_at` timestamp NULL DEFAULT NULL,
  `last_index_stats` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`last_index_stats`)),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `game_hosts`
--

LOCK TABLES `game_hosts` WRITE;
/*!40000 ALTER TABLE `game_hosts` DISABLE KEYS */;
INSERT INTO `game_hosts` VALUES
(1,'n64-1','INTERNET_ARCHIVE','N64ROMsPACK','n64',1,NULL,'2026-08-30 22:47:02','{\"files_seen\": 304, \"files_skipped\": 8, \"matched\": 263, \"unmatched\": 33, \"created\": 0, \"updated\": 263, \"unmatched_sample\": [\"Battlezone - Rise of the Black Dogs (U) (!).n64\", \"Bust-A-Move _99 (U) [!].z64\", \"Castlevania - Legacy of Darkness (U) [!].z64\", \"Clay Fighter - Sculptor_s Cut (U) [!].z64\", \"Command and Conquer 3D (U) (!).n64\", \"Cruis_n World (U) [!].z64\", \"Elmo_s Letter Adventure (U) [!].z64\", \"Elmo_s Number Journey (U) [!].z64\", \"Fighter_s Destiny 2 (U) [!].z64\", \"Flying Dragon (U) [!].z64\", \"John Romero_s Daikatana (U) [!].z64\", \"Killer Instinct Gold (U) (V1.2) [!].z64\", \"King Hill 64 - Extreme Snowboarding (J) [!].v64\", \"Kobe Bryant_s NBA Courtside (U) [!].z64\", \"Madden 2000 (U) [!].z64\", \"Mario Golf 64 (English).v64\", \"Midway_s Greatest Arcade Hits Volume 1 (U) [!].z64\", \"Mortal Kombat Trilogy (U) (V1.2) [!].z64\", \"N64 1080 Snowboarding (JU).z64\", \"NFL Quarterback Club 2001 (U) [!].z64\", \"Nagano Olympic Hockey _98 (U) [!].z64\", \"Namco Museum 64 (U) [!].z64\", \"Olympic Hockey Nagano _98 (U) [!].v64\", \"Quake 64 (U) [!].z64\", \"RR64 - Ridge Racer 64 (U) [!].z64\"]}','2026-08-30 11:09:44','2026-08-30 22:47:02'),
(2,'ps1-1','INTERNET_ARCHIVE','ps1-rip-chd-ck','psx',1,NULL,'2026-08-30 11:10:40','{\"files_seen\": 1658, \"files_skipped\": 6, \"matched\": 1205, \"unmatched\": 447, \"created\": 1205, \"updated\": 0, \"unmatched_sample\": [\"\'98 Koushien - Koukou Yakyuu Simulation.chd\", \"100% Star.chd\", \"101 Best Games For Master System.chd\", \"10th Anniversary Memorial Save Data.chd\", \"19-ji 03-pun - Ueno-hatsu Yakou Ressha.chd\", \"1Xtreme.chd\", \"40 Winks - Conquer Your Dreams featuring Ruff Tumble.chd\", \"4x4 World Trophy.chd\", \"70\'s Robot Anime - Geppy-X - The Super Boosted Armor [Disc 3].chd\", \"70s Robot Anime - Geppy-X - The Super Boosted Armor [Disc 1].chd\", \"70s Robot Anime - Geppy-X - The Super Boosted Armor [Disc 2].chd\", \"70s Robot Anime - Geppy-X - The Super Boosted Armor [Disc 4].chd\", \"A Ressha de Ikou 4 - Evolution Global.chd\", \"A Ressha de Ikou 4 - Evolution.chd\", \"A Small Journey by Giuseppe Gatta.chd\", \"A-Train - Trains, Power, Money.chd\", \"A.IV - Evolution Global.chd\", \"A2 Racer - Europa Tour.chd\", \"AI Shougi 2 Deluxe.chd\", \"AI Shougi 2.chd\", \"Abe a GoGo.chd\", \"Ace Combat 1.chd\", \"Activision Classics.chd\", \"Actua Soccer - Club Edition.chd\", \"Actua Soccer.chd\"]}','2026-08-30 11:10:36','2026-08-30 11:10:40'),
(3,'ps2-1','INTERNET_ARCHIVE','playstation-2-games-iso','ps2',1,NULL,'2026-08-30 11:11:19','{\"files_seen\": 382, \"files_skipped\": 4, \"matched\": 278, \"unmatched\": 100, \"created\": 278, \"updated\": 0, \"unmatched_sample\": [\"Busin - Wizardry Alternative (Japan).iso\", \"Busou Renkin - Youkoso Papillon Park e (Japan).iso\", \"CSI - Crime Scene Investigation (Europe) (En,Fr,De,Es,It).iso\", \"Canis Canem Edit (Europe, Australia) (En,Fr,De,Es,It).iso\", \"Capcom Classics Collection (Europe).iso\", \"Capcom Classics Collection Vol. 2 (Europe).iso\", \"Castlevania (Europe) (En,Fr,De,Es,It).iso\", \"Castleween (Europe) (En,Fr,De,Es,It).iso\", \"Ce-Pa 2001 (Japan).iso\", \"Cel Damage Overdrive (Europe) (En,Fr,De,Es,It).iso\", \"Crashed (Europe) (En,Fr,De,Es,It).iso\", \"Crisis Zone (Europe, Australia) (En,Fr,De,Es,It).iso\", \"Dark Chronicle (Europe) (En,Fr,De,Es,It).iso\", \"Deus Ex (Germany).iso\", \"Disney-Pixar WALL-E - Der Letzte raeumt die Erde auf (Germany).iso\", \"Dot Hack G.U. Vol. 1 - Rebirth - Terminal Disc (USA).iso\", \"Dot Hack G.U. Vol. 2 - Reminisce (USA).iso\", \"Dot Hack G.U. Vol. 3 - Redemption (USA).iso\", \"Dot Hack Part 2 - Mutation (Europe) (En,Fr,De,Es,It).iso\", \"Dot Hack Part 3 - Outbreak (Europe) (En,Fr,De,Es,It).iso\", \"Dot Hack Part 4 - Quarantine (Europe) (En,Fr,De,Es,It).iso\", \"Driven to Destruction (Europe).iso\", \"Fahrenheit (Europe) (En,Fr,De,Es).iso\", \"Ford Street Racing (Europe) (En,Fr,De,Es,It).iso\", \"Genji (Europe, Australia) (En,Ja,Fr,De,Es,It).iso\"]}','2026-08-30 11:11:16','2026-08-30 11:11:19'),
(10,'gba','INTERNET_ARCHIVE','GameboyAdvanceRomCollectionByGhostware','gba',1,NULL,'2026-08-30 22:48:27','{\"files_seen\": 1671, \"files_skipped\": 5, \"matched\": 1136, \"unmatched\": 530, \"created\": 1136, \"updated\": 0, \"unmatched_sample\": [\"2 Games in 1 - Brother Bear & The Lion King.zip\", \"2 Games in 1 - Columns Crown & Chu Chu Rocket!.zip\", \"2 Games in 1 - Disney Princess & Lizzie McGuire.zip\", \"2 Games in 1 - Disney Princesse & Frere des Ours.zip\", \"2 Games in 1 - Disney\'s Finding Nemo & Finding Nemo - The Continuing Adventures.zip\", \"2 Games in 1 - Disney\'s Finding Nemo & The Incredibles.zip\", \"2 Games in 1 - Disney\'s Lion King & Disney Princess.zip\", \"2 Games in 1 - Disney\'s Sports Pack - Football & SkateBoarding.zip\", \"2 Games in 1 - GT Advance 3 & Moto GP.zip\", \"2 Games in 1 - Hugo - Bukkazoom! & Hugo - The Evil Mirror Advance.zip\", \"2 Games in 1 - Peter Pan & Lilo and Stitch 2.zip\", \"2 Games in 1 - Sonic Advance & Chu Chu Rocket!.zip\", \"2 Games in 1 - Sonic Advance & Sonic Pinball Party.zip\", \"2 Games in 1 - Sonic Battle & Chu Chu Rocket!.zip\", \"2 Games in 1 - Sonic Battle & Sonic Advance.zip\", \"2 Games in 1 - Sonic Pinball Party & Columns Crown.zip\", \"2 Games in 1 - Sonic Pinball Party & Sonic Battle.zip\", \"2 Games in 1 - SpongeBob SquarePants - Battle for Bikini Bottom & Jimmy Neutron - Boy Genius.zip\", \"2 Games in 1 - SpongeBob SquarePants - SuperSponge & Rugrats - Go Wild.zip\", \"2 Games in 1 - SpongeBob SquarePants - SuperSponge & SpongeBob SquarePants - Battle for Bikini Bottom.zip\", \"2 Games in 1 - Spyro - Season of Ice & Crash Bandicoot 2 - N-Tranced.zip\", \"2 Games in 1 - Spyro 2 - Season of Flame & Crash Nitro Kart.zip\", \"2 Games in 1 - Spyro Superpack - Spyro - Season of Ice & Spyro - Season of Flame.zip\", \"2 Games in 1 - The SpongeBob SquarePants Movie & SpongeBob and Friends - Freeze Frame Frenzy.zip\", \"2 Games in 1 - UbiSoft Gamepack - Prince of Persia & Tomb Raider.zip\"]}','2026-08-30 22:48:24','2026-08-30 22:48:27'),
(11,'gc-1','INTERNET_ARCHIVE','AsiaGamecubeCollectionByGhostware','ngc',1,NULL,'2026-08-30 22:49:28','{\"files_seen\": 308, \"files_skipped\": 5, \"matched\": 141, \"unmatched\": 162, \"created\": 141, \"updated\": 0, \"unmatched_sample\": [\"1080 Silver Storm.iso\", \"2002 FIFA World Cup Korea Japan.iso\", \"All-Star Baseball 2003 featuring Derek Jeter.iso\", \"Atsumare!! Made in Wario.iso\", \"Auto Modellista - U.S.-tuned.iso\", \"Bakuten Shoot Beyblade 2002 - Nettou! Magne Tag Battle!.iso\", \"Baseball 2003, The - Battle Ball Park Sengen Perfect Play Pro Yakyuu.iso\", \"Baten Kaitos - Owaranai Tsubasa to Ushinawareta Umi (Disc 1).iso\", \"Baten Kaitos - Owaranai Tsubasa to Ushinawareta Umi (Disc 2).iso\", \"Baten Kaitos II - Hajimari no Tsubasa to Kamigami no Shishi (Disc 1).iso\", \"Baten Kaitos II - Hajimari no Tsubasa to Kamigami no Shishi (Disc 2).iso\", \"Battle Houshin.iso\", \"Beach Spikers - Virtua Beach Volleyball.iso\", \"Biohazard (Disc 1).iso\", \"Biohazard (Disc 2).iso\", \"Biohazard - Code - Veronica - Kanzenban (Collector\'s Box) (Disc 1).iso\", \"Biohazard - Code - Veronica - Kanzenban (Collector\'s Box) (Disc 2).iso\", \"Biohazard 2 (Collector\'s Box).iso\", \"Biohazard 3 - Last Escape (Collector\'s Box).iso\", \"Biohazard 4 (Disc 1).iso\", \"Biohazard 4 (Disc 2).iso\", \"Biohazard Zero (Collector\'s Box) (Disc 1).iso\", \"Biohazard Zero (Collector\'s Box) (Disc 2).iso\", \"Bloody Roar - Extreme.iso\", \"Bokujou Monogatari - Shiawase no Uta for World.iso\"]}','2026-08-30 22:49:25','2026-08-30 22:49:28'),
(12,'wii-1','INTERNET_ARCHIVE','Wii_ISO','wii',1,NULL,'2026-08-30 22:50:51','{\"files_seen\": 115, \"files_skipped\": 5, \"matched\": 98, \"unmatched\": 12, \"created\": 98, \"updated\": 0, \"unmatched_sample\": [\"Fortune Street (USA).iso\", \"House of the Dead 2 and 3 Return, The (USA) (En,Fr,Es).iso\", \"Just Dance 3 (USA) (En,Fr,Es) (Rev 1).iso\", \"Kirby\'s Dream Collection - Special Edition (USA).iso\", \"Metroid Prime Trilogy (USA).iso\", \"New Play Control! Donkey Kong Jungle Beat (USA) (En,Fr,Es).iso\", \"New Play Control! Mario Power Tennis (USA) (En,Fr,Es).iso\", \"New Play Control! Pikmin (USA) (En,Fr,Es).iso\", \"Ookami (USA).iso\", \"Super Mario All-Stars (USA).iso\", \"Tatsunoko vs. Capcom - Ultimate All-Stars (USA).iso\", \"Wii Sports + Wii Sports Resort (USA) (En,Fr,Es).iso\"]}','2026-08-30 22:50:48','2026-08-30 22:50:51');
/*!40000 ALTER TABLE `game_hosts` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-02 22:39:44
