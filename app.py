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
        
@app.route("/")
def index():
    return render_template("index.html")

@app.route('/api/search/', methods=['GET'])
def search():
    try:
        searchParam = request.args.to_dict()
        print(searchParam)
        # Query the Tables
        airline= searchParam['airline']
        
        tweet=searchParam['tweet']
        tweetfrom= searchParam['tweetfrom']
        tweetto=searchParam['tweetto']
        # ----------------------------------
        query=db.session.query(Tweets)
        if airline!='All':
             query = query.filter(Tweets.airline==airline) 
        if tweet:
            query = query.filter(Tweets.text.contains(tweet))
        #print(query)
    except:
        # Return some sample data in case of error
        query = db.session.query(Tweets).limit(25)
    
    query2=query
    results=query.all()
    all_tweets = []
    tweet_words=''
    for result in results:
        tweet= {}
        tweet["sentiment"] = result.airline_sentiment
        tweet["airline"] = result.airline
        tweet["tweet"] = result.text
        tweet["date"] = result.tweet_date
        tweet["lat"] = 1#float(result.lat) 
        tweet["lng"] = 2#float(result.lng) 
        tweet_words+=result.text
        all_tweets.append(tweet)
    
    #Tokenize the words of each tweet to generate Word Cloud 
    #Word Cloud
    wordcloud_data=wordCloud(tweet_words)
    
    #Pie chart
    piechart_data=db.session.query(Tweets.airline_sentiment,func.count(Tweets.airline_sentiment)) \
        .group_by(Tweets.airline_sentiment).all()
    print(piechart_data)
    
    # Format the data to send as json
    return jsonify(all_tweets=all_tweets,wordcloud_data=wordcloud_data,piechart_data=piechart_data)
     

@app.route("/about")
def names():
    return render_template("about.html")

if __name__ == "__main__":
    app.run()
