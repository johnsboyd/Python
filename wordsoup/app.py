from db import add, get_keys, dict_concat, combine, walk
from flask import Flask, render_template, request, session, redirect, url_for, current_app
from getlyric import fetch_results, parse_results, parse_lyric, print_lyric
import os
import re
import sys

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def home():
    linklist = get_keys()
    return render_template('home.html', linklist = linklist)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/query', methods=['GET', 'POST'])
def query():
    try:
        if request.method == 'POST':
            search = request.form['search']  
            info, lyric = print_lyric(search)
            info = info[:-7] # truncate -lyrics
            info = info.replace('-','_').title() # capitalize all and use underbar
            session['info'] = info 
            session['lyric'] = lyric 
            songinfo = info.replace('_',' ') # use spaces in song title
            return render_template('query.html', lyric = lyric, songinfo = songinfo )
        return render_template('query.html', lyric = lyric, songinfo = songinfo )
    except Exception as e:
        return render_template("500.html", error = str(e))
    
@app.route('/addsong')
def addsong():
    info = session.get('info', None)
    lyric = session.get('lyric', None)
    url = add(info,lyric)
    return redirect(url_for('home'))

@app.route('/output/<keylink>')
def output(keylink):
    keylink = keylink.replace('_','-')
    lyric = parse_lyric('https://genius.com/' + keylink + '-lyrics')
    songinfo = keylink.replace('-',' ')
    return render_template('output.html', lyric = lyric, songinfo = songinfo ) 

@app.route('/markov', methods=['POST'])
def markov():
    checked_songs = request.form.getlist('check')
    all_dict = combine(checked_songs)
    lyrics = walk(all_dict)
    return render_template('markov.html', lyrics = lyrics) 

#@app.errorhandler(500)
#def internal_server_error(error):
#    app.logger.error('Server Error: %s', (error))
#    return render_template('500.html'), 500
#
#@app.errorhandler(Exception)
#def unhandled_exception(e):
#    app.logger.error('Unhandled Exception: %s', (e))
#    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)
