import os
import json

import pandas as pd
import numpy as np
import sqlalchemy
from datetime import datetime

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, render_template
from flask import request
import re

from wordcloud import STOPWORDS
import collections
stopwords = set(STOPWORDS)

app = Flask(__name__)

#################################################
# Database Setup
#################################################
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:mysql57515c@localhost:3306/airlinetwitter"
print(app.config['SQLALCHEMY_DATABASE_URI'])

db = SQLAlchemy(app)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(db.engine, reflect=True)

# Save references to each table
Tweets = Base.classes.tweets

def wordCloud(tweet_words):
    '''
    Tokenize the words of each tweet to generate Word Cloud 
    '''
    word_tokens = tweet_words.split()
    filtered_sentence = [w for w in word_tokens if not w.lower() in stopwords]
    wordcount=[]
    myWord= {}
    for word in filtered_sentence:
        if re.match(r'^\w+$', word) and not word.isdigit():
            if word.lower() in myWord:
                myWord[word.lower()] += 1
            else:
                myWord[word.lower()] = 1 
    for k,v in myWord.items():
        item={} 
        item['text']=k
        item['weight']=v
        wordcount.append(item)
    return wordcount
 
def searchQuery(searchParam,charttype):
    '''
     Create search query based on chart type
    '''
    try:
        # Query the Table
        airline= searchParam['airline']
        tweet=searchParam['tweet']
        # ----------------------------------
        if charttype=='data':
            query=db.session.query(Tweets)
            if airline!='All':
                query = query.filter(Tweets.airline==airline) 
            if tweet:
                query = query.filter(Tweets.text.contains(tweet))
        elif charttype=='wordcloud':
            query=db.session.query(Tweets.text)
            if airline!='All':
                query = query.filter(Tweets.airline==airline) 
            if tweet:
                query = query.filter(Tweets.text.contains(tweet))      
        elif charttype=='pie':
            query=db.session.query(Tweets.airline_sentiment,func.count(Tweets.airline_sentiment).label('count')) 
            if airline!='All':
                query = query.filter(Tweets.airline==airline) 
            if tweet:
                query = query.filter(Tweets.text.contains(tweet))
            query=query.group_by(Tweets.airline_sentiment)
        elif charttype=='bar':
            query=db.session.query(Tweets.airline,Tweets.airline_sentiment,
                            func.count(Tweets.airline_sentiment).label('count')) 
            if airline!='All':
                query = query.filter(Tweets.airline==airline) 
            if tweet:
                query = query.filter(Tweets.text.contains(tweet))
            query=query.group_by(Tweets.airline,Tweets.airline_sentiment)
        elif charttype=='line':     
            query=db.session.query(Tweets.airline,Tweets.airline_sentiment,Tweets.tweet_date,
                                                           func.count(Tweets.airline_sentiment).label('count')) 
            if airline!='All':
                query=query.filter(Tweets.airline==airline) 
            if tweet:
                query = query.filter(Tweets.text.contains(tweet))
            query=query.group_by(Tweets.tweet_date,Tweets.airline_sentiment,Tweets.airline)
            query=query.order_by(Tweets.tweet_date.desc())
    except:
        # Return some sample data in case of error
        query = db.session.query(Tweets).limit(25)
    return query

'''
Data
'''
@app.route('/api/data', methods=['GET'])
def data():
    searchParam = request.args.to_dict()
    #Data
    results=searchQuery(searchParam,'data').all()
    all_tweets = []
    tweet_words=''
    for result in results:
        tweet= {}
        tweet["sentiment"] = result.airline_sentiment
        tweet["airline"] = result.airline
        tweet["tweet"] = result.text
        tweet["date"] = result.tweet_date
        tweet["lat"] = float(result.lat) 
        tweet["lng"] = float(result.lng) 
        tweet_words+=result.text
        all_tweets.append(tweet)
    # Format the data to send as json
    return jsonify(all_tweets=all_tweets)

'''
Word Cloud
'''
@app.route('/api/wordcloud', methods=['GET'])
def wordcloud():
    searchParam = request.args.to_dict()
    #Word Cloud
    results=searchQuery(searchParam,'wordcloud').all()
    tweet_words=''.join([r.text for r in results])
    wordcloud_data=wordCloud(tweet_words)
    # Format the data to send as json
    return jsonify(wordcloud_data=wordcloud_data)

'''
Pie Chart
'''
@app.route('/api/pie', methods=['GET'])
def pie():
    searchParam = request.args.to_dict()
    print(searchParam)
    #Pie chart
    results=searchQuery(searchParam,'pie').all()
    piechart_data=[]
    for result in results:
        tweet= {}
        tweet["sentiment"] = result.airline_sentiment
        tweet["count"] = result.count
        piechart_data.append(tweet)
    # Format the data to send as json
    return jsonify(piechart_data=piechart_data)  
 
'''
Bar Chart
'''
@app.route('/api/bar', methods=['GET'])
def bar():  
    searchParam = request.args.to_dict()
    #Bar chart
    results=searchQuery(searchParam,'bar').all()
    barchart_data=[]
    for result in results:
        tweet= {}
        tweet["sentiment"] = result.airline_sentiment
        tweet["airline"] = result.airline
        tweet["count"] = result.count
        barchart_data.append(tweet)
    # Format the data to send as json
    return jsonify(barchart_data=barchart_data)
'''
Line Chart
'''
@app.route('/api/line', methods=['GET'])
def line():     
    searchParam = request.args.to_dict()
    #line chart
    results=searchQuery(searchParam,'line').all()
    linechart_data=[]
    for result in results:
        try:
            if datetime.strptime(str(result.tweet_date), '%m/%d/%Y'):
                tweet= {}
                tweet["sentiment"] = result.airline_sentiment
                tweet["airline"] = result.airline
                tweet["date"] = result.tweet_date
                tweet["count"] = result.count
                linechart_data.append(tweet)
        except ValueError:
             pass
    return jsonify(linechart_data=linechart_data)

'''
Map 
'''
@app.route('/api/map/', methods=['GET'])
def mapapi():
    #Map
    query=db.session.query(Tweets.airline,Tweets.airline_sentiment,Tweets.text,
                               Tweets.lat,Tweets.lng).filter(Tweets.lat!=0).filter(Tweets.lng!=0) 
    results=query.all()
    map_data = []
    for result in results:
        tweet= {}
        tweet["sentiment"] = result.airline_sentiment
        tweet["airline"] = result.airline
        tweet["text"] = result.text
        tweet["lat"] = float(result.lat) 
        tweet["lng"] = float(result.lng) 
        map_data.append(tweet)
    return jsonify(map_data=map_data)
 
            
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/map")
def map():
    return render_template("map.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run()
