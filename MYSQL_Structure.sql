CREATE DATABASE `twintmysql` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

CREATE TABLE `followers` (
  `id` bigint(30) NOT NULL,
  `name` mediumtext,
  `username` text NOT NULL,
  `bio` longtext,
  `location` tinytext,
  `url` longtext,
  `join_date` tinytext NOT NULL,
  `join_time` tinytext NOT NULL,
  `tweets` int(11) DEFAULT NULL,
  `following` int(11) DEFAULT NULL,
  `followers` int(11) DEFAULT NULL,
  `likes` int(11) DEFAULT NULL,
  `media` int(11) DEFAULT NULL,
  `private` tinytext NOT NULL,
  `verified` tinytext NOT NULL,
  `avatar` longtext NOT NULL,
  `date_update` datetime NOT NULL,
  `follower` text NOT NULL,
  PRIMARY KEY (`follower`(255),`username`(255),`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `following_names` (
  `user` varchar(50) NOT NULL,
  `date_update` datetime NOT NULL,
  `follows` varchar(50) NOT NULL,
  PRIMARY KEY (`user`),
  KEY `follows_idx` (`follows`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `following` (
  `id` bigint(30) NOT NULL,
  `name` mediumtext,
  `username` text NOT NULL,
  `bio` longtext,
  `location` tinytext,
  `url` longtext,
  `join_date` tinytext NOT NULL,
  `join_time` tinytext NOT NULL,
  `tweets` int(11) DEFAULT NULL,
  `following` int(11) DEFAULT NULL,
  `followers` int(11) DEFAULT NULL,
  `likes` int(11) DEFAULT NULL,
  `media` int(11) DEFAULT NULL,
  `private` tinytext NOT NULL,
  `verified` tinytext NOT NULL,
  `avatar` longtext NOT NULL,
  `date_update` datetime NOT NULL,
  `follows` text NOT NULL,
  PRIMARY KEY (`id`,`username`(255),`follows`(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `following_names` (
  `user` varchar(50) NOT NULL,
  `date_update` datetime NOT NULL,
  `follows` varchar(50) NOT NULL,
  PRIMARY KEY (`user`),
  KEY `follows_idx` (`follows`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `tweets` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `id_str` varchar(30) DEFAULT NULL,
  `tweet` text,
  `conversation_id` text,
  `created_at` varchar(40) DEFAULT NULL,
  `date` text,
  `time` text,
  `timezone` text,
  `place` text,
  `replies_count` int(11) DEFAULT NULL,
  `likes_count` int(11) DEFAULT NULL,
  `retweets_count` int(11) DEFAULT NULL,
  `user_id` varchar(30) DEFAULT NULL,
  `user_id_str` text,
  `screen_name` text NOT NULL,
  `name` text,
  `link` text,
  `mentions` text,
  `hashtags` text,
  `cashtags` text,
  `urls` text,
  `photos` text,
  `quote_url` text,
  `video` int(11) DEFAULT NULL,
  `geo` text,
  `near` text,
  `source` text,
  `time_update` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1620 DEFAULT CHARSET=utf8mb4;


CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_str` varchar(40) NOT NULL,
  `name` text CHARACTER SET utf8mb4,
  `user` varchar(50) DEFAULT NULL,
  `private` int(11) DEFAULT '0',
  `verified` int(11) DEFAULT '0',
  `bio` text CHARACTER SET utf8mb4,
  `location` text CHARACTER SET utf8mb4,
  `url` text,
  `joined` datetime DEFAULT NULL,
  `tweets` int(11) DEFAULT NULL,
  `following` int(11) DEFAULT NULL,
  `followers` int(11) DEFAULT NULL,
  `likes` int(11) DEFAULT NULL,
  `media` int(11) DEFAULT NULL,
  `avatar` varchar(300) DEFAULT 'null',
  `time_update` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `relevance` decimal(30,20) DEFAULT NULL,
  `keep` bit(1) DEFAULT b'0',
  `suspended` bit(1) DEFAULT b'0',
  `blocked` bit(1) DEFAULT b'0',
  `unfollow` bit(1) DEFAULT b'0',
  `username` varchar(50) DEFAULT NULL,
  `doesntexist` bit(1) DEFAULT b'0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `id_str_UNIQUE` (`id_str`),
  KEY `user` (`user`) USING BTREE,
  FULLTEXT KEY `bio` (`bio`)
) ENGINE=InnoDB AUTO_INCREMENT=787914 DEFAULT CHARSET=latin1;


