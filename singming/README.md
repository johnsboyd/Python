# Sing(le) Ming(le) - A Song Singles Mingler
 
Notes:

This flask app uses the Markov Chain algorithm to mashup song lyrics and create cutups based on word sequences.
Every word that follows another actually occurred somewhere in the original lyrics.  Any words in one song that
also appear in other songs allow crossovers into the various other song lyrics.  

The application uses redis with the RedisJSON module.  The python web scraping tools allow song lyrics to be 
displayed but the original lyrics are not really stored in the database intact, they are only stored as markov 
indexes. 

Installation:
```
  $ sudo apt-get install redis
  $ sudo apt-get install build-essential
  $ git clone https://github.com/RedisJSON/RedisJSON.git
  $ cd RedisJSON
  $ make
  $ cd src
  $ sudo cp rejson.so /var/lib/redis/
  $ sudo echo "loadmodule /var/lib/redis/rejson.so" >> /etc/redis/redis.conf
  $ service redis-server restart
  
  $ git clone https://github.com/johnsboyd/Python.git
  $ cd Python/singming
  $ pipenv install # (or use virtualenv and pip)
  $ source .venv/bin/activate
  $ python app.py
```

Using the application:
1) using Search form, type in the song title and artist name and hit return (lyrics should appear on screen)
2) click the 'Add-Song' to add your song to the list of indexed songs
3) repeat above steps to add in several songs
4) at 'Select Songs' screen check several radio buttons to select songs to be merged
5) click 'mingle-it' to see Markov (mashup) results
