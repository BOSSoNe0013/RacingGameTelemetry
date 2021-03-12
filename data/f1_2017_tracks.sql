--
-- File generated with SQLiteStudio v3.0.6 on Sat Jul 18 16:47:56 2015
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: Tracks
CREATE TABLE Tracks (id INTEGER PRIMARY KEY UNIQUE, name text, length real, start_z real, laps real);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (1, 'Melbourne', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (2, 'Sepang', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (3, 'Shanghai', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (4, 'Sakhir (Bahrain)', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (5, 'Catalunya', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (6, 'Monaco', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (7, 'Montreal', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (8, 'Silverstone', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (9, 'Hockenheim', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (10, 'Hungaroring', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (11, 'Spa', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (12, 'Monza', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (13, 'Singapore', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (14, 'Suzuka', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (15, 'Abu Dhabi', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (16, 'Texas', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (17, 'Brazil', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (18, 'Austria', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (19, 'Sochi', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (20, 'Mexico', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (21, 'Baku (Azerbaijan)', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (22, 'Sakhir Short', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (23, 'Silverstone Short', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (24, 'Texas Short', 0, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (25, 'Suzuka Short', 0, 0, 0);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
