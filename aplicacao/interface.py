import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import render_template, Flask
import logging
import db

APP = Flask(__name__)

# Start page
@APP.route('/')
def index():
    stats = db.execute('''
    SELECT * FROM
        (SELECT COUNT(*) FROM Songs)
    JOIN
        (SELECT COUNT(*) FROM Albums)
    JOIN
        (SELECT COUNT(*) FROM People)
    JOIN
        (SELECT COUNT(DISTINCT tag_name) FROM Tags)
    ''').fetchone()
    logging.info(stats)
    return render_template('index.html', stats=stats)

#Songs
@APP.route('/songs/')
def list_songs():   #lista todas as músicas
    songs=db.execute('''
    SELECT SongId, song_title, song_release_date, song_page_views, category, song_url, song_lyrics
    FROM Songs
    ORDER BY SongId
    ''').fetchall()
    return render_template('songs-list.html',songs=songs)

@APP.route('/songs/<int:id>/')
def get_song(id):       #procura a song através do seu id
    song=db.execute('''
        SELECT SongId, song_title, song_release_date, song_page_views, category, song_url, song_lyrics
        FROM Songs
        WHERE SongId = ?
        ''',[id]).fetchone()
    
    #verifica se a song existe
    if song is None:
        abort(404, 'Song id {} does not exist.'.format(id))
        
    #devolve as tags de uma música
    tags = db.execute('''       
        SELECT tag_name
        FROM Tags
        WHERE SongId = ?
        ''',[id]).fetchall()
    
    #pessoas que participam na música
    people = db.execute('''     
        SELECT role_name, person_name
        FROM Discography
        JOIN People on Discography.PersonId=People.PersonId
        WHERE SongId = ? 
        ORDER BY person_name, role_name
        ''',[id]).fetchall()
        
    #número da track da música se pertencer a um álbum e nome do album
    tracks = db.execute('''
        SELECT album_title, album_track_number
        FROM Tracks
        JOIN Albums ON Albums.AlbumId = Tracks.AlbumId
        WHERE Tracks.SongId = ? AND Albums.AlbumId IS NOT NULL 
        ''',[id]).fetchall()
        
    return render_template('song.html',song=song, tags=tags, people=people,tracks=tracks)

#ver a letra da música
@APP.route('/songs/<int:id>/lyrics')
def get_song_lyrics(id):
    song = db.execute('''
        SELECT song_title, song_lyrics
        FROM Songs
        WHERE SongId = ?
    ''', [id]).fetchone()

    if song is None:
        abort(404, f'Song id {id} does not exist.')

    return render_template('song-lyrics.html', song=song)


@APP.route('/songs/search/<expr>/')
def search_song(expr):    #procura uma música/s através de um trecho da letra
    search = { 'expr' : expr}
    expr = '%' + expr + '%'
    songs = db.execute('''
        SELECT SongId, song_title, song_release_date, song_page_views, category,song_lyrics
        FROM Songs
        WHERE song_title LIKE ?
        ''',[expr]).fetchall()
    return render_template('song-search.html', search=search, songs=songs)

#Álbuns
@APP.route('/albuns/')
def list_albuns():   #lista todos os albuns
    albuns=db.execute('''
    SELECT *
    FROM Albums
    ORDER BY AlbumId
    ''').fetchall()
    
    return render_template('albuns-list.html',albuns=albuns)

@APP.route('/albuns/<int:id>/')
def get_album(id):   #procura o album pelo id
  album = db.execute(
    '''
    SELECT *
    FROM Albums 
    WHERE AlbumId = ?
    ''',[id]).fetchone()
  
  if album is None:
     abort(404, 'Album id {} does not exist.'.format(id))
     
  #devolver as tracks do album
  tracks = db.execute('''
      SELECT album_track_number, song_title
      FROM Tracks
      JOIN Songs ON Songs.SongId=Tracks.SongId
      WHERE AlbumId = ?
      ORDER BY album_track_number
      ''',[id]).fetchall()
  return render_template('album.html', album=album, tracks=tracks)

@APP.route('/albuns/search/<expr>/')
def search_album(expr):
    search = {'expr' : expr }
    expr = '%' + expr + '%'
    albuns = db.execute('''
        SELECT *
        FROM Albums
        WHERE album_title LIKE ?
        ''',[expr]).fetchall()
    return render_template('album-search.html', search=search,albuns=albuns)

#People
@APP.route('/people/')
def list_people():
    people=db.execute('''
        SELECT People.PersonId, person_name, role_name, song_title
        FROM People
        JOIN Discography ON Discography.PersonId=People.PersonId
        JOIN Songs on Discography.SongId=Songs.SongId
        ORDER BY person_name
        ''').fetchall()
    return render_template('people-list.html', people=people)

#dá a pessoa pelo seu id
@APP.route('/people/<int:id>/')
def get_people(id):
  people = db.execute(
    '''
    SELECT People.person_name, Songs.song_title, Discography.role_name
    FROM People
    JOIN Discography ON Discography.PersonId=People.PersonId
    JOIN Songs on Discography.SongId=Songs.SongId
    WHERE People.PersonId= ?
    ORDER BY People.person_name
    ''', [id]).fetchall()
  
  if people is None:
     abort(404, 'Person id {} does not exist.'.format(id))
  return render_template('people.html', people=people) 
  
#Questions
@APP.route('/questions/')
def questions():
    #lista as perguntas
    questions = [
        "Question 1",
        "Question 2",
        "Question 3",
        "Question 4",
        "Question 5",
        "Question 6",
        "Question 7",
        "Question 8",
        "Question 9",
        "Question 10",
        "Question 11",
        "Question 12",
        "Question 13",
        "Question 14"
    ]
    return render_template('questions.html', questions=questions)

#cada pergunta
@APP.route('/questions/1')
def question_1():
    result = db.execute('''
    SELECT a.album_title, a.album_url
    FROM Albums a;
    ''').fetchall()
    return render_template('question_1.html', result=result)

@APP.route('/questions/2')
def question_2():
    result = db.execute('''
    SELECT s.song_title
    FROM Discography d
    NATURAL JOIN Songs s
    NATURAL JOIN Tags t
    WHERE s.song_title LIKE "%Taylor's Version%" and t.tag_name='Ballad'
    GROUP BY s.song_title
    ORDER BY s.song_title;
    ''').fetchall()
    return render_template('question_2.html', result=result)
    
@APP.route('/questions/3')
def question_3():
    result = db.execute('''
    SELECT DISTINCT s.song_title, s.song_url, s.song_release_date
    FROM Discography d
    NATURAL JOIN Songs s
    WHERE s.category='Non-Album Songs'
    ORDER BY s.song_release_date;
    ''').fetchall()
    return render_template('question_3.html', result=result)

@APP.route('/questions/4')
def question_4():
    result = db.execute('''
    SELECT DISTINCT s.song_title, a.album_title
    FROM Discography d
    NATURAL JOIN Tracks t
    NATURAL JOIN Songs s
    NATURAL JOIN Albums a
    WHERE t.album_track_number=13;
    ''').fetchall()
    return render_template('question_4.html', result=result)

@APP.route('/questions/5')
def question_5():
    result = db.execute('''
    SELECT s.song_title
    FROM Discography d
    NATURAL JOIN Songs s
    NATURAL JOIN People p
    NATURAL JOIN Albums a
    WHERE a.album_title='reputation' and p.person_name='Jack Antonoff'and d.role_name='Producer'
    ORDER BY s.song_title;
    ''').fetchall()
    return render_template('question_5.html', result=result)

@APP.route('/questions/6')
def question_6():
    result = db.execute('''
    SELECT DISTINCT s.song_title, p.person_name
    FROM Discography d
    NATURAL JOIN People p
    NATURAL JOIN Songs s
    WHERE d.role_name='Artist' AND p.person_name!='Taylor Swift'
    ORDER BY p.person_name;
    ''').fetchall()
    return render_template('question_6.html', result=result)

@APP.route('/questions/7')
def question_7():
    result = db.execute('''
    WITH tab AS(SELECT DISTINCT s.song_title, s.song_page_views
    FROM Discography d
    NATURAL JOIN Songs s
    NATURAL JOIN Albums a
    WHERE a.album_title='folklore (deluxe version)')
    SELECT SUM(tab.song_page_views) num
    FROM tab;
    ''').fetchall()
    return render_template('question_7.html', result=result)

@APP.route('/questions/8')
def question_8():
    result = db.execute('''
    WITH tab AS(SELECT DISTINCT s.song_title, s.song_page_views
    FROM Discography d
    NATURAL JOIN Songs s
    NATURAL JOIN Albums a
    WHERE a.album_title='Speak Now (Deluxe)')
    SELECT AVG(tab.song_page_views) num
    FROM tab;
    ''').fetchall()
    return render_template('question_8.html', result=result)

@APP.route('/questions/9')
def question_9():
    result = db.execute('''
    WITH tab AS(SELECT s.song_title
    FROM Discography d
    NATURAL JOIN Songs s
    WHERE s.song_release_date NOT LIKE '200%'
    GROUP BY s.song_title)
    SELECT COUNT(*) num FROM tab;
    ''').fetchall()
    return render_template('question_9.html', result=result)

@APP.route('/questions/10')
def question_10():
    result = db.execute('''
    WITH tab AS(SELECT s.song_title
    FROM Discography d
    NATURAL JOIN Songs s
    WHERE s.song_lyrics LIKE '%night%'
    GROUP BY s.song_title)
    SELECT COUNT(*) num FROM tab;
    ''').fetchall()
    return render_template('question_10.html', result=result)

@APP.route('/questions/11')
def question_11():
    result = db.execute('''
    SELECT DISTINCT s.song_title, s.song_page_views
    FROM Discography d
    NATURAL JOIN People p
    NATURAL JOIN Songs s
    WHERE s.song_title NOT IN(SELECT DISTINCT s.song_title
    FROM Discography d
    NATURAL JOIN People p
    NATURAL JOIN Songs s
    WHERE s.song_release_date LIKE '200%' AND d.role_name='Producer' AND p.person_name='Taylor Swift')
    ORDER BY s.song_page_views DESC;
    ''').fetchall()
    return render_template('question_11.html', result=result)

@APP.route('/questions/12')
def question_12():
    result = db.execute('''
    WITH tab AS(SELECT a.album_title, s.song_title
    FROM Discography d
    NATURAL JOIN Songs s
    NATURAL JOIN Albums a
    GROUP BY a.album_title, s.song_title
    ORDER BY a.album_title)
    SELECT tab.album_title, COUNT(tab.song_title) num
    FROM tab
    GROUP BY tab.album_title
    ORDER BY num DESC
    LIMIT 3;
    ''').fetchall()
    return render_template('question_12.html', result=result)

@APP.route('/questions/13')
def question_13():
    result = db.execute('''
    SELECT DISTINCT s.song_title
    FROM Discography d
    NATURAL JOIN Songs s
    NATURAL JOIN Albums a
    NATURAL JOIN People p
    WHERE d.role_name='Writer' AND p.person_name='Taylor Swift' AND s.song_title NOT IN (SELECT DISTINCT s.song_title
    FROM Discography d
    NATURAL JOIN Songs s
    NATURAL JOIN Albums a
    NATURAL JOIN People p
    WHERE d.role_name='Writer' and p.person_name!='Taylor Swift');
    ''').fetchall()
    return render_template('question_13.html', result=result)

@APP.route('/questions/14')
def question_14():
    result = db.execute('''
    SELECT DISTINCT s.song_title, s.category
    FROM Discography d
    NATURAL JOIN Songs s
    NATURAL JOIN Tags t
    WHERE s.song_title IN (SELECT DISTINCT s.song_title
    FROM Discography d
    NATURAL JOIN Songs s
    NATURAL JOIN Tags t
    WHERE t.tag_name='Rock') AND s.song_title IN (SELECT DISTINCT s.song_title
    FROM Discography d
    NATURAL JOIN Songs s
    NATURAL JOIN Tags t
    WHERE t.tag_name='Orchestral');
    ''').fetchall()
    return render_template('question_14.html', result=result)
    



