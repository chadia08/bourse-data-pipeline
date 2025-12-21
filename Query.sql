CREATE DATABASE IF NOT EXISTS bourse;
USE bourse; 
CREATE TABLE IF NOT EXISTS bourse.company
(
    symbole String,
    nom String,
    secteur String,
    sous_secteur String,
    siege String,
    date_introduction DateTime64(3),
    cik String
)
ENGINE = MergeTree
ORDER BY symbole;

-- user: default
-- password: 8SM~VfR.4zCrC