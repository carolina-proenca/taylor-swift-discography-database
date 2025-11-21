-- Create the Songs table
CREATE TABLE Songs (
    SongId INT PRIMARY KEY,
    song_title VARCHAR(255) NOT NULL,
    song_url VARCHAR(2083),
    song_release_date DATE,
    song_page_views INT DEFAULT 0,
    category VARCHAR(100),
    song_lyrics TEXT
);

CREATE TABLE Tags (
    TagId INT PRIMARY KEY,          -- Unique identifier for each tag
    SongId INT,                     -- References the Song that has the tag
    tag_name VARCHAR(100) NOT NULL, -- Name of the tag
    FOREIGN KEY (SongId) REFERENCES Songs(SongId) ON DELETE CASCADE -- Foreign Key to Songs table
);


-- Create the Album table
CREATE TABLE Albums (
    AlbumId INT PRIMARY KEY,
    album_title VARCHAR(255) NOT NULL,
    album_url VARCHAR(2083)
);

-- Create the People table
CREATE TABLE People (
    PersonId INT PRIMARY KEY,
    person_name VARCHAR(255) NOT NULL
);

-- Create the Tracks table
CREATE TABLE Tracks (
    SongId INT,
    AlbumId INT,
    album_track_number INT,
    PRIMARY KEY (SongId, AlbumId),
    FOREIGN KEY (SongId) REFERENCES Songs(SongId) ON DELETE CASCADE,
    FOREIGN KEY (AlbumId) REFERENCES Albums(AlbumId) ON DELETE CASCADE
);

-- Create the Discography table
CREATE TABLE Discography (
    SongId INT,
    PersonId INT,
    AlbumId INT,
    role_name VARCHAR(100),
    PRIMARY KEY (SongId, PersonId, AlbumId, role_name),
    FOREIGN KEY (SongId) REFERENCES Songs(SongId) ON DELETE CASCADE,
    FOREIGN KEY (PersonId) REFERENCES People(PersonId) ON DELETE CASCADE,
    FOREIGN KEY (AlbumId) REFERENCES Albums(AlbumId) ON DELETE CASCADE
);

