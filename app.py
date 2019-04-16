import os

import pandas as pd
import numpy as np

import sqlalchemy

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
        searchParam = request.args.to_dict()
        print(searchParam)
        # Query the Table
        airline= searchParam['airline']
        tweet=searchParam['tweet']
        # ----------------------------------
        if charttype=='none':
            query=db.session.query(Tweets)
            if airline!='All':
                query = query.filter(Tweets.airline==airline) 
            if tweet:
                query = query.filter(Tweets.text.contains(tweet))
        elif charttype=='pie':
            query=db.session.query(Tweets.airline_sentiment,func.count(Tweets.airline_sentiment)) 
            if airline!='All':
                query = query.filter(Tweets.airline==airline) 
            if tweet:
                query = query.filter(Tweets.text.contains(tweet))
            query=query.group_by(Tweets.airline_sentiment)
        elif charttype=='bar':
            query=db.session.query(Tweets.airline,Tweets.airline_sentiment,func.count(Tweets.airline_sentiment)) 
            if airline!='All':
                query = query.filter(Tweets.airline==airline) 
            if tweet:
                query = query.filter(Tweets.text.contains(tweet))
            query=query.group_by(Tweets.airline,Tweets.airline_sentiment)
    except:
        # Return some sample data in case of error
        query = db.session.query(Tweets).limit(25)
    return query
        
@app.route("/")
def index():
    return render_template("index.html")

@app.route('/api/search/', methods=['GET'])
def search():
    searchParam = request.args.to_dict()
    results=searchQuery(searchParam,'none').all()
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
    
    #Word Cloud
    wordcloud_data=wordCloud(tweet_words)
    #Pie chart
    piechart_data=searchQuery(searchParam,'pie').all()
    #Bar chart
    barchart_data=searchQuery(searchParam,'bar').all()
    
    # Format the data to send as json
    return jsonify(all_tweets=all_tweets,wordcloud_data=wordcloud_data,piechart_data=piechart_data,barchart_data=barchart_data)
     

@app.route("/about")
def names():
    return render_template("about.html")

if __name__ == "__main__":
    app.run()
