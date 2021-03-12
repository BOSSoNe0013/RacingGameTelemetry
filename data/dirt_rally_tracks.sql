--
-- File generated with SQLiteStudio v3.0.6 on Sat Jul 18 16:47:56 2015
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: Tracks
CREATE TABLE Tracks (id INTEGER PRIMARY KEY UNIQUE, name text, length real, start_z real, laps real);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (1, 'Ampelonas Ormi', 4860.19, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (2, 'Kathodo Leontiou', 9665.99, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (3, 'Pomono Ekrixi', 5086.83, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (4, 'Koryfi Dafni', 4582.01, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (5, 'Fourketa Kourva', 4515.4, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (6, 'Perasma Platani', 10688.1, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (7, 'Tsiristra Theo', 10357.9, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (8, 'Ourea Spevsi', 5739.1, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (9, 'Ypsna tou Dasos', 5383.01, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (10, 'Abies Koilada', 7089.41, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (11, 'Pedines Epidaxi', 6595.31, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (12, 'Anodou Farmakas', 9666.5, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (21, 'Waldaufstieg', 5393.22, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (22, 'Waldabstieg', 6015.08, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (23, 'Kreuzungsring', 6318.71, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (24, 'Kreuzungsring reverse', 5685.28, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (25, 'Ruschberg', 10700, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (26, 'Verbundsring', 5855.68, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (27, 'Verbundsring reverse', 5550.86, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (28, 'Flugzeugring', 4937.85, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (29, 'Flugzeugring Reverse', 5129.04, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (30, 'Oberstein', 11684.2, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (31, 'Hammerstein', 10805.2, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (32, 'Frauenberg', 11684.2, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (41, 'Route de Turini', 10805.2, 1290.45, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (42, 'Valee descendante', 10866.9, -2358.05, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (43, 'Col de Turini – Sprint en descente', 4730.02, 298.587, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (44, 'Col de Turini sprint en Montee', 4729.54, -209.405, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (45, 'Col de Turini – Descente', 5175.91, -120.206, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (46, 'Gordolon – Courte montee', 5175.91, -461.134, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (47, 'Route de Turini (Descente)', 4015.36, -1005.69, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (48, 'Approche du Col de Turini – Montee', 3952.15, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (49, 'Pra dAlart', 9831.45, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (50, 'Col de Turini Depart', 9831.97, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (51, 'Route de Turini (Montee)', 6843.32, -977.825, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (52, 'Col de Turini – Depart en descente', 6846.83, -2357.89, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (61, 'Pant Mawr Reverse', 4821.65, NULL, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (62, 'Bidno Moorland', 4993.26, 1928.69, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (63, 'Bidno Moorland Reverse', 5165.95, 2470.99, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (64, 'River Severn Valley', 11435.5, -553.109, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (65, 'Bronfelen', 11435.6, 11435.6, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (66, 'Fferm Wynt', 5717.4, -553.112, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (67, 'Fferm Wynt Reverse', 5717.39, -21.5283, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (68, 'Dyffryn Afon', 5718.1, -26.0434, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (69, 'Dyffryn Afon Reverse', 5718.1, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (70, 'Sweet Lamb', 9944.87, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (71, 'Geufron Forest', 10063.6, 0, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (72, 'Pant Mawr', 4788.67, NULL, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (1001, 'Pikes Peak - Full Course', 19476.5, -4701.25, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (1002, 'Pikes Peak - Sector 1', 6327.69, -4700.96, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (1003, 'Pikes Peak - Sector 2', 6456.36, -1122.07, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (1004, 'Pikes Peak - Sector 3', 7077.2, 1397.84, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (1005, 'Pikes Peak (Mixed Surface) - Full Course', 19476.5, -4701.11, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (1006, 'Pikes Peak (Mixed Surface) - Sector 1', 6327.7, -4700.94, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (1007, 'Pikes Peak (Mixed Surface) - Sector 2', 6456.37, -1122.23, 0);
INSERT INTO Tracks (id, name, length, start_z, laps) VALUES (1008, 'Pikes Peak (Mixed Surface) - Sector 3', 7077.21, 1397.82, 0);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
