import pandas as pd
import sqlite3

# File paths
excel_file_path = 'ts_discography.xlsx'
db_file_path = 'taylor_swift.db'

# Connect to SQLite database
conn = sqlite3.connect(db_file_path)

# Load the Excel file
df = pd.read_excel(excel_file_path, sheet_name='ts_discography')

# Clean the specific columns by removing the first and last characters if they are '[' and ']'
def clean_column_values(column):
    """Remove leading and trailing brackets and quotes if they exist."""
    return column.apply(lambda x: str(x).strip("[]").replace("'", "").strip() if isinstance(x, str) else x)

# Clean the 'song_tags', 'song_writers', and 'song_producers' columns
df['song_tags'] = clean_column_values(df['song_tags'])
df['song_writers'] = clean_column_values(df['song_writers'])
df['song_producers'] = clean_column_values(df['song_producers'])
df['song_artists'] = clean_column_values(df['song_artists'])

# 1. Albums Table
albums = df[['album_title', 'album_url']].drop_duplicates().dropna()
albums.insert(0, 'AlbumId', range(1, len(albums) + 1))  # Generate AlbumId
albums.to_sql('Albums', conn, if_exists='replace', index=False)  # Use 'replace' to avoid duplicates
print("Inserted data into Album table.")

# 2. Songs Table
songs = df[['song_title', 'song_url', 'song_release_date', 'song_page_views', 'song_lyrics', 'category']].drop_duplicates()
songs.insert(0, 'SongId', range(1, len(songs) + 1))  # Generate SongId
songs.to_sql('Songs', conn, if_exists='replace', index=False)  # Use 'replace'
print("Inserted data into Songs table.")

# 3. Tags Table
tags_col = ['song_tags']

# Initialize an empty list to store tags and SongId associations
tags_data = []

# Iterate through each song in the df to extract tags and associate with SongId
for _, row in df.iterrows():
    # Split the tags (assumes tags are stored as a string like "tag1, tag2, tag3")
    song_tags = str(row['song_tags']).split(',')
    
    # Clean and strip whitespace from each tag
    song_tags = [tag.strip() for tag in song_tags if tag.strip()]  # Remove empty tags

    # For each tag, add a record to the tags_data list with the corresponding SongId
    for tag in song_tags:
        tags_data.append({'song_title': row['song_title'], 'tag_name': tag})

# Create a DataFrame from the tags_data list
tags_df = pd.DataFrame(tags_data)

# Drop duplicates to avoid inserting the same tag multiple times
tags_df = tags_df.drop_duplicates(subset=['song_title', 'tag_name'])

# Generate TagId
tags_df.insert(0, 'TagId', range(1, len(tags_df) + 1))

# Map song titles to SongIds using the existing Songs table (assuming you already have this data)
# Assuming 'songs' DataFrame exists and contains 'SongId' and 'song_title'
tag_song_mapping = {row['song_title']: row['SongId'] for _, row in songs.iterrows()}

# Map each tag to its corresponding SongId
tags_df['SongId'] = tags_df['song_title'].map(tag_song_mapping)

# Drop rows where SongId is None (invalid SongId mapping)
tags_df = tags_df.dropna(subset=['SongId'])

# Remove the 'song_title' column as we no longer need it
tags_df = tags_df.drop(columns=['song_title'])

# Insert into the Tags table in the database
tags_df.to_sql('Tags', conn, if_exists='replace', index=False)  # Use 'replace' to overwrite the table if it exists
print("Inserted cleaned data into Tags table.")


# 4. People Table
people_columns = ['song_writers', 'song_producers', 'song_artists']
people = pd.concat([df[col].dropna().str.split(',', expand=True).stack() for col in people_columns]).reset_index(drop=True)
people = pd.DataFrame({'person_name': people})  # Create DataFrame
people['person_name'] = people['person_name'].str.strip()  # Remove leading/trailing spaces
people = people.drop_duplicates()  # Drop duplicates after stripping
people.insert(0, 'PersonId', range(1, len(people) + 1))  # Generate PersonId
people.to_sql('People', conn, if_exists='replace', index=False)  # Use 'replace'
print("Inserted cleaned data into People table.")


# 5. Discography Table
discography = []

for _, row in df.iterrows():
    # Get the SongId and AlbumId
    song_id = songs[songs['song_title'] == row['song_title']]['SongId'].values[0]
    album_id = albums[albums['album_title'] == row['album_title']]['AlbumId'].values[0] if pd.notna(row['album_title']) else None

    # Process song writers
    for writer in str(row['song_writers']).split(','):
        writer = writer.strip()  # Normalize name
        if writer:  # Check if the writer is non-empty
            person = people[people['person_name'].str.strip() == writer]
            if not person.empty:
                person_id = person['PersonId'].values[0]
                discography.append({'SongId': song_id, 'PersonId': person_id, 'AlbumId': album_id, 'role_name': 'Writer'})
            else:
                print(f"Writer '{writer}' not found in People table. Skipping...")

    # Process song producers
    for producer in str(row['song_producers']).split(','):
        producer = producer.strip()  # Normalize name
        if producer:  # Check if the producer is non-empty
            person = people[people['person_name'].str.strip() == producer]
            if not person.empty:
                person_id = person['PersonId'].values[0]
                discography.append({'SongId': song_id, 'PersonId': person_id, 'AlbumId': album_id, 'role_name': 'Producer'})
            else:
                print(f"Producer '{producer}' not found in People table. Skipping...")
        
    # Process song artists
    for artist in str(row['song_artists']).split(','):
        artist = artist.strip()  # Normalize name
        if artist:  # Check if the writer is non-empty
            person = people[people['person_name'].str.strip() == artist]
            if not person.empty:
                person_id = person['PersonId'].values[0]
                discography.append({'SongId': song_id, 'PersonId': person_id, 'AlbumId': album_id, 'role_name': 'Artist'})
            else:
                print(f"Artist '{artist}' not found in People table. Skipping...")


# Convert to DataFrame and remove duplicates
discography_df = pd.DataFrame(discography).drop_duplicates()
discography_df.to_sql('Discography', conn, if_exists='replace', index=False)  # Use 'replace'
print("Inserted data into Discography table.")

# 6. Tracks Table
tracks = df[['song_title', 'album_title', 'album_track_number']].drop_duplicates()  # Include track_number from the Excel file

# Map SongId based on song_title and AlbumId based on album_title
tracks['SongId'] = tracks['song_title'].map(lambda x: songs[songs['song_title'] == x]['SongId'].values[0])
tracks['AlbumId'] = tracks['album_title'].map(lambda x: albums[albums['album_title'] == x]['AlbumId'].values[0] if pd.notna(x) else None)

# Drop song_title and album_title as they are no longer needed
tracks = tracks.drop(columns=['song_title', 'album_title']).drop_duplicates()

# No need to assign track_number sequentially, use the track_number from the Excel file directly
# Ensure the track_number column exists in the dataframe and is properly aligned
tracks['album_track_number'] = tracks['album_track_number'].astype(int)  # Ensure track_number is of integer type

# Insert into Tracks table in the database
tracks.to_sql('Tracks', conn, if_exists='replace', index=False)  # Use 'replace' to overwrite the table if it exists
print("Inserted data into Tracks table.")

# Print the column names to verify if 'track_number' exists
print(df.columns)

# If 'track_number' exists, proceed as before. Otherwise, print a message.
if 'album_track_number' in df.columns:
    tracks = df[['song_title', 'album_title', 'album_track_number']].drop_duplicates()
    tracks['SongId'] = tracks['song_title'].map(lambda x: songs[songs['song_title'] == x]['SongId'].values[0])
    tracks['AlbumId'] = tracks['album_title'].map(lambda x: albums[albums['album_title'] == x]['AlbumId'].values[0] if pd.notna(x) else None)
    tracks = tracks.drop(columns=['song_title', 'album_title']).drop_duplicates()
    tracks['album_track_number'] = tracks['album_track_number'].astype(int)
    tracks.to_sql('Tracks', conn, if_exists='replace', index=False)
    print("Inserted data into Tracks table.")
else:
    print("track_number column is missing in the input DataFrame.")



conn.close()
print("All data imported successfully :)!")
