DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS comic;

CREATE TABLE user (user_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, username VARCHAR(20) UNIQUE NOT NULL, password VARCHAR(255) NOT NULL, full_name VARCHAR(255) NOT NULL, join_date DATE, email VARCHAR(255) NOT NULL, meta JSON, user_group VARCHAR(20) DEFAULT 'user');

CREATE TABLE comic (comic_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, author_id INTEGER NOT NULL, posted TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, title VARCHAR(255) NOT NULL, body JSON, draft TINYINT(1) DEFAULT 0, FOREIGN KEY (author_id) REFERENCES user (user_id));

CREATE TABLE tag (tag_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, author_id INTEGER NOT NULL, post_id INTEGER NOT NULL, name VARCHAR(20), FOREIGN KEY (author_id) REFERENCES user (user_id), FOREIGN KEY (post_id) REFERENCES comic (comic_id));

CREATE TABLE collection (collection_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, author_id INT NOT NULL, posted TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, title VARCHAR(255) NOT NULL, meta JSON, members JSON, FOREIGN KEY (author_id) REFERENCES user (user_id));

CREATE TABLE lucaflect (name VARCHAR(20) NOT NULL, shortvalue VARCHAR(20), longvalue json);
