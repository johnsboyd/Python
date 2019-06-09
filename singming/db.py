import json
import random
import redis
import re

r = redis.StrictRedis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)

def add(uri,lyric):
    lyric = lyric.replace('\n','; ')
    markov = {}
    lsplit = lyric.split()
    for x in range(len(lsplit)):
        if x == len(lsplit)-1:
            markov.setdefault(lsplit[x],[]).append(';')
        else:
            markov.setdefault(lsplit[x],[]).append(lsplit[x+1])
    r.execute_command('JSON.SET', uri, '.', json.dumps(markov))
    return 'https://genius.com/' + uri.replace('_','-') + '-lyrics'

def get_keys():
    cursor = 0
    cursor, linklist = r.scan(cursor, count=10000)
    linklist.sort()
    return linklist

def dict_concat(src, collector):
    for k in src:
        collector.setdefault(k, []).extend(src[k])
    return collector

def combine(songlist):
    coll = {}
    for s in songlist:
        songdict = json.loads(r.execute_command('JSON.GET', s))
        dict_concat(songdict, coll)
    return coll

def walk(all_dict):
    sentence = ''
    word = ';'
    while len(sentence) < 2000 and len(all_dict[word]) > 0:
        word = all_dict[word][random.randint(0,len(all_dict[word])-1)]
        parsed_word = word.replace(';','\n')
        sentence += parsed_word + ' '
    return sentence
