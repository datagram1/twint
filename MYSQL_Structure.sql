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

CREATE TABLE `followers_names` (
  `user` varchar(50) NOT NULL,
  `date_update` datetime NOT NULL,
  `follower` varchar(50) NOT NULL,
  PRIMARY KEY (`user`),
  KEY `follower` (`follower`) USING BTREE
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
  `id` bigint(30) NOT NULL,
  `user_id` bigint(30) DEFAULT NULL,
  `date` date NOT NULL,
  `time` time NOT NULL,
  `timezone` tinytext NOT NULL,
  `location` tinytext NOT NULL,
  `user` text NOT NULL,
  `tweet` longtext NOT NULL,
  `replies` int(11) DEFAULT NULL,
  `likes` int(11) DEFAULT NULL,
  `retweets` int(11) DEFAULT NULL,
  `hashtags` longtext,
  `link` longtext,
  `retweet` int(1) DEFAULT NULL,
  `user_rt` text,
  `mentions` longtext,
  `date_update` datetime NOT NULL,
  `search_name` mediumtext NOT NULL COMMENT 'user can use this field to know from which search the info comes. max 255 chars. if the user do not especify, it must be set to "-" ',
  PRIMARY KEY (`id`,`search_name`(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_str` varchar(40) NOT NULL,
  `name` text,
  `user` varchar(50) DEFAULT NULL,
  `private` int(11) DEFAULT '0',
  `verified` int(11) DEFAULT '0',
  `bio` text,
  `location` text,
  `url` text,
  `joined` datetime DEFAULT NULL,
  `tweets` int(11) DEFAULT NULL,
  `following` int(11) DEFAULT NULL,
  `followers` int(11) DEFAULT NULL,
  `likes` int(11) DEFAULT NULL,
  `media` int(11) DEFAULT NULL,
  `avatar` varchar(200) DEFAULT 'null',
  `time_update` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `relevance` decimal(30,20) DEFAULT NULL,
  `keep` bit(1) DEFAULT b'0',
  `suspended` bit(1) DEFAULT b'0',
  `blocked` bit(1) DEFAULT b'0',
  `unfollow` bit(1) DEFAULT b'0',
  `username` varchar(50) NOT NULL,
  `doesntexist` bit(1) DEFAULT b'0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `username_UNIQUE` (`username`),
  UNIQUE KEY `id_str_UNIQUE` (`id_str`),
  KEY `user` (`user`) USING BTREE,
  FULLTEXT KEY `bio` (`bio`)
) ENGINE=InnoDB AUTO_INCREMENT=722253 DEFAULT CHARSET=latin1;

