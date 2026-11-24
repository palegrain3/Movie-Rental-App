DROP DATABASE IF EXISTS movie_rental;
CREATE DATABASE movie_rental;
USE movie_rental;

CREATE TABLE Customer (
  customer_id  INT AUTO_INCREMENT PRIMARY KEY,
  customer_name VARCHAR(100) NOT NULL,
  customer_email VARCHAR(255) NOT NULL UNIQUE,
  customer_phone VARCHAR(12) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  signup_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Movie (
  movie_id          INT AUTO_INCREMENT PRIMARY KEY,
  movie_name        VARCHAR(60) NOT NULL UNIQUE,
  release_year      INT NOT NULL,
  age_rating        ENUM('G', 'PG', 'PG-13', 'R', 'N/A') NOT NULL,
  movie_length      INT NOT NULL,
  imdb_rating       DECIMAL(3,1) CHECK (imdb_rating BETWEEN 0 AND 10),
  movie_description VARCHAR(500) NOT NULL
);

CREATE TABLE Genre (
  genre_id   INT AUTO_INCREMENT PRIMARY KEY,
  genre_name VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE Movie_Genre (
  movie_id INT,
  genre_id INT,
  PRIMARY KEY (movie_id, genre_id),
  FOREIGN KEY (movie_id) REFERENCES movie(movie_id),
  FOREIGN KEY (genre_id) REFERENCES genre(genre_id)
);

CREATE TABLE Rental (  -- one row per checkout
  rental_id   INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  movie_id    INT NOT NULL,
  rent_date   DATE NOT NULL,
  expire_date DATE NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES Customer(customer_id) ON DELETE CASCADE,
  FOREIGN KEY (movie_id)    REFERENCES movie(movie_id),
  CHECK (expire_date >= rent_date)
);

CREATE TABLE Actor (
  actor_id INT PRIMARY KEY,
  name     VARCHAR(40) NOT NULL,
  gender   VARCHAR(10) NOT NULL
);

CREATE TABLE Movie_Cast (
  movie_id  INT NOT NULL,
  actor_id  INT NOT NULL,
  role_name VARCHAR(25),
  PRIMARY KEY (actor_id, movie_id),
  FOREIGN KEY (movie_id) REFERENCES movie(movie_id),
  FOREIGN KEY (actor_id) REFERENCES actor(actor_id)
);

-- ---------- Data ----------
-- Customer table starts empty; add customers through the app.

INSERT INTO Movie (movie_id, movie_name, movie_length, release_year, age_rating, imdb_rating, movie_description) VALUES
(1, 'Pulp Fiction', 149, 1994, 'R', 8.9, 'The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.'),
(2, 'Avatar', 162, 2009, 'PG-13', 7.9, 'In the 22nd century, a paraplegic Marine is dispatched to the moon Pandora on a unique mission, but becomes torn between following orders and protecting an alien civilization.'),
(3, 'Deliverance', 150, 1972, 'R', 7.6, 'Outdoor fanatic Lewis Medlock takes his friends on a journey through the Georgia wilderness, on the Cahulawassee river, turning into a dangerous expedition into the American backcountry'),
(4, 'Space Balls', 96, 1987, 'PG', 7.1, 'A star-pilot for hire and his trusty half-dog sidekick must come to the rescue of a spoiled princess and save Planet Druidia from the clutches of the evil Spaceballs.'),
(5, 'Gladiator', 155, 2000, 'R', 8.5, 'A betrayed Roman general fights as a gladiator to avenge his murdered family.'),
(6, 'Spider-man 3', 139, 2007, 'PG-13', 6.3, 'The seemingly invincible Spider-Man goes up against an all-new crop of villain – including the shape-shifting Sandman. While Spider-Man''s superpowers are altered by an alien organism, his alter ego, Peter Parker, deals with nemesis Eddie Brock and gets caught up in a love triangle.'),
(7, 'Toy Story', 81, 1995, 'G', 8.3, 'A cowboy doll is threatened when a new space ranger toy arrives in his owner''s room.'),
(8, 'Bolt', 132, 2008, 'PG', 6.8, 'a tv-star dog who believes he has superpowers goes on a cross-country trek when he thinks she''s in real danger.'),
(9, 'Niu Lai', 86, 2026, 'N/A', 6.0, 'Adventure about a young cow named Niu Lai growing up to be a warrior.'),
(10, 'El Camino: A Breaking Bad Movie', 122, 2019, 'R', 7.3, 'Fugitive Jesse Pinkman runs from his captors, the law, and his past.');

INSERT INTO Genre (genre_name) VALUES
('Action'),
('Adventure'),
('Comedy'),
('Crime and Mystery'),
('Drama'),
('Fantasy'),
('Horror'),
('Romance'),
('Science Fiction'),
('Thriller'),
('Western');

-- Rental table starts empty (rentals need customers); add them through the app.

INSERT INTO Actor (actor_id, name, gender) VALUES
(23, 'Tim Roth',        'male'),
(24, 'Amanda Plummer',  'female'),
(25, 'Laura Lovelace',  'female'),
(26, 'John Travolta',   'male'),
(27, 'Sam Worthington', 'male'),
(28, 'Zoe Saldana',     'female'),
(29, 'Stephen Lang',    'male'),
(30, 'Ronny Cox',       'male'),
(31, 'Mel Brooks',      'male'),
(32, 'Rick Moranis',    'male'),
(33, 'Bill Pullman',    'male'),
(34, 'John Candy',      'male'),
(35, 'Daphne Zuniga',   'female'),
(36, 'Russell Crowe',   'male'),
(37, 'Joaquin Phoenix', 'male'),
(38, 'Connie Nielsen',  'female'),
(39, 'Tobey Maguire',   'male'),
(40, 'Kirsten Dunst',   'female'),
(41, 'Topher Grace',    'male'),
(42, 'Thomas Haden Church', 'male'),
(43, 'Tom Hanks',       'male'),
(44, 'Tim Allen',       'male'),
(45, 'Miley Cyrus',     'female'),
(46, 'Susie Essman',    'female'),
(47, 'Aaron Paul',      'male'),
(48, 'Jesse Plemons',   'male');

-- Movie <-> genre links (genre_id order: 1 Action, 2 Adventure, 3 Comedy, 4 Crime and Mystery,
-- 5 Drama, 6 Fantasy, 7 Horror, 8 Romance, 9 Science Fiction, 10 Thriller, 11 Western)
INSERT INTO Movie_Genre (movie_id, genre_id) VALUES
(1, 4), (1, 5), (1, 10),            -- Pulp Fiction
(2, 1), (2, 2), (2, 6), (2, 9),     -- Avatar
(3, 2), (3, 5), (3, 10),            -- Deliverance
(4, 2), (4, 3), (4, 9),             -- Space Balls
(5, 1), (5, 2), (5, 5),             -- Gladiator
(6, 1), (6, 2), (6, 9),             -- Spider-man 3
(7, 2), (7, 3), (7, 6),             -- Toy Story
(8, 2), (8, 3),                     -- Bolt
(9, 2), (9, 6),                     -- Niu Lai
(10, 4), (10, 5), (10, 10);         -- El Camino

-- Cast links
INSERT INTO Movie_Cast (movie_id, actor_id, role_name) VALUES
(1, 23, 'Pumpkin'), (1, 24, 'Honey Bunny'), (1, 25, 'Waitress'), (1, 26, 'Vincent Vega'),
(2, 27, 'Jake Sully'), (2, 28, 'Neytiri'), (2, 29, 'Col. Quaritch'),
(3, 30, 'Drew Ballinger'),
(4, 31, 'President Skroob'), (4, 32, 'Dark Helmet'), (4, 33, 'Lone Starr'), (4, 34, 'Barf'), (4, 35, 'Princess Vespa'),
(5, 36, 'Maximus'), (5, 37, 'Commodus'), (5, 38, 'Lucilla'),
(6, 39, 'Peter Parker'), (6, 40, 'Mary Jane Watson'), (6, 41, 'Eddie Brock'), (6, 42, 'Sandman'),
(7, 43, 'Woody'), (7, 44, 'Buzz Lightyear'),
(8, 26, 'Bolt'), (8, 45, 'Penny'), (8, 46, 'Mittens'),
(10, 47, 'Jesse Pinkman'), (10, 48, 'Todd Alquist');

-- Check that everything joins: every movie with its genres and cast
-- SELECT m.movie_name, GROUP_CONCAT(DISTINCT g.genre_name) AS genres, GROUP_CONCAT(DISTINCT a.name) AS cast_members
-- FROM movie m
-- LEFT JOIN MovieGenre mg ON mg.movie_id = m.movie_id LEFT JOIN genre g ON g.genre_id = mg.genre_id
-- LEFT JOIN movie_cast mc ON mc.movie_id = m.movie_id LEFT JOIN actor a ON a.actor_id = mc.actor_id
-- GROUP BY m.movie_id, m.movie_name;

/*
-- ---------- Searches ----------
-- Movies 2 hours or longer
SELECT movie_name, movie_length
FROM movie
WHERE movie_length >= 120;

-- Movies released before the year 2000
SELECT movie_name, release_year
FROM movie
WHERE release_year < 2000;

-- Movies rated R
SELECT movie_name, age_rating
FROM movie
WHERE age_rating = 'R';
*/

-- For checking to see if the tables work
/*
SELECT * FROM Customer;
SELECT * FROM Movie;
SELECT * FROM Genre;
SELECT * FROM Rental;
SELECT * FROM Movie_Genre;
SELECT * FROM Actor;
SELECT * FROM Movie_Cast;
*/