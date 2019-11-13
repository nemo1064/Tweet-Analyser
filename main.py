from flask import Flask,make_response,request,send_file,redirect,url_for,render_template
import os
from sys import *

import sys,tweepy,csv,re
from textblob import TextBlob
import matplotlib.pyplot as plt
import numpy as np
import re
from PIL import Image
from wordcloud import WordCloud, STOPWORDS
from IPython.display import Image as im


global pt,nt,a1,a2
app=Flask(__name__)
app.config["DEBUG"] = True
@app.route('/')
def form():
     return render_template("form.html")

@app.route('/process',methods=["POST"])
    

def DownloadData():
    a1=request.form["search_query"]
    a2=request.form["max_tweets"]
    tweets = []
    tweetText = []
    # authenticating
    consumerKey = 'heuaCDZJKfqi06JMB6aGGztSi'
    consumerSecret = 'JMJJ3JMzCzjMqXgE1i75x9rEMTIIFtSDoZEMVqTWTgzZh2Jn31'
    accessToken = '1027585656896147458-gNOwPZX0p9KKr9sFQYJoCwgSlcssh2'
    accessTokenSecret = '4GTxAn8UelzH9btznHM0fdP2riuFlfsPV9jDRZfNoJIyD'
    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(auth)

    # input for term to be searched and how many tweets to search
    searchTerm = a1
    NoOfTerms = int(a2)

    # searching for tweets
    tweets = tweepy.Cursor(api.search, q=searchTerm, lang = "en").items(NoOfTerms)

    #raw_Tweets
    raw_tweets = []
    ptweets= []
    ntweets=[]

    # creating some variables to store info
    polarity = 0
    positive = 0
    wpositive = 0
    spositive = 0
    negative = 0
    wnegative = 0
    snegative = 0
    neutral = 0

    def cleanTweet(tweet):
    # Remove Links, Special Characters etc from tweet
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweet).split())

    # function to calculate percentage
    def percentage(part, whole):
        temp = 100 * float(part) / float(whole)
        return format(temp, '.2f')

    # iterating through tweets fetched
    for tweet in tweets:
        #append to list to form word cloud
        raw_tweets.append(tweet.text)
        #Append to temp so that we can store in csv later. I use encode UTF-8
        tweetText.append(cleanTweet(tweet.text).encode('utf-8'))
        #print (self.tweetText)    #print tweet's text
        analysis = TextBlob(tweet.text)
        # print(analysis.sentiment)  # print tweet's polarity
        polarity += analysis.sentiment.polarity  # adding up polarities to find the average later

        if (analysis.sentiment.polarity == 0):  # adding reaction of how people are reacting to find average later
            neutral += 1
        elif (analysis.sentiment.polarity > 0 and analysis.sentiment.polarity <= 0.3):
            ptweets.append(tweet)
            wpositive += 1
        elif (analysis.sentiment.polarity > 0.3 and analysis.sentiment.polarity <= 0.6):
            ptweets.append(tweet)
            positive += 1
        elif (analysis.sentiment.polarity > 0.6 and analysis.sentiment.polarity <= 1):
            ptweets.append(tweet)
            spositive += 1
        elif (analysis.sentiment.polarity > -0.3 and analysis.sentiment.polarity <= 0):
            ntweets.append(tweet)
            wnegative += 1
        elif (analysis.sentiment.polarity > -0.6 and analysis.sentiment.polarity <= -0.3):
            ntweets.append(tweet)
            negative += 1
        elif (analysis.sentiment.polarity > -1 and analysis.sentiment.polarity <= -0.6):
            ntweets.append(tweet)
            snegative += 1
    

   


    # Write to csv and close csv file
    with open("results.csv",'w') as resultFile:
        tweets = csv.writer(resultFile)
        for row in tweetText:
            tweets.writerow([row])
            #csvWriter.writerow(self.tweetText)
            #csvFile.close()

    
    #for tweet in ptweets[:5]:
     #   pt=tweet.text

    # printing first 5 negative tweets
    #def negtweets():
        #print("\n\nNegative tweets:")
     #   neglist=ntweets[:5]
      #  return render_template('process.html', neglist=neglist)


    # finding average of how people are reacting
    positive = percentage(positive, NoOfTerms)
    wpositive =percentage(wpositive, NoOfTerms)
    spositive =percentage(spositive, NoOfTerms)
    negative = percentage(negative, NoOfTerms)
    wnegative =percentage(wnegative, NoOfTerms)
    snegative =percentage(snegative, NoOfTerms)
    neutral = percentage(neutral, NoOfTerms)

    # finding average reaction
    polarity = polarity / NoOfTerms

    # Pie chart
    # labels = ['Positive [' + str(positive) + '%]', 'Weakly Positive [' + str(wpositive) + '%]','Strongly Positive [' + str(spositive) + '%]', 'Neutral [' + str(neutral) + '%]','Negative [' + str(negative) + '%]', 'Weakly Negative [' + str(wnegative) + '%]', 'Strongly Negative [' + str(snegative) + '%]']
    # sizes = [positive, wpositive, spositive, neutral, negative, wnegative, snegative]
    # colors = ['yellowgreen','lightgreen','darkgreen', 'gold', 'red','lightsalmon','darkred']
    # patches, texts = plt.pie(sizes, colors=colors, shadow=True,startangle=90)
    # plt.legend(patches, labels, loc="best")
    # plt.title('How people are reacting on ' + searchTerm + ' by analyzing ' + str(NoOfTerms) + ' Tweets.')
    # plt.axis('equal')
    # plt.tight_layout()
    # plt.savefig('static/pies.png')

    #Create a string form of our list of text
    raw_string = ''.join(raw_tweets)
    no_links = re.sub(r'http\S+', '', raw_string)
    no_unicode = re.sub(r"\\[a-z][a-z]?[0-9]+", '', no_links)
    no_special_characters = re.sub('[^A-Za-z ]+', '', no_unicode)

    words = no_special_characters.split(" ")
    words = [w for w in words if len(w) > 2]  # ignore a, an, be, ...
    words = [w.lower() for w in words]
    words = [w for w in words if w not in STOPWORDS]

    mask = np.array(Image.open('/home/cpt-nemo/Downloads/twitter_logo.png'))
    wc = WordCloud(background_color="white", max_words=2000, mask=mask)
    clean_string = ','.join(words)
    wc.generate(clean_string)
    
    # Word Cloud
    f = plt.figure(figsize=(50,50))
    f.add_subplot(1,2, 1)
    plt.imshow(wc, interpolation='bilinear')
    plt.title('Twitter Generated Word Cloud', size=50)
    plt.axis("off")
    # plt.savefig('static/cloud.png')
    f.add_subplot(1,2,2)
    labels = ['Positive [' + str(positive) + '%]', 'Weakly Positive [' + str(wpositive) + '%]','Strongly Positive [' + str(spositive) + '%]', 'Neutral [' + str(neutral) + '%]','Negative [' + str(negative) + '%]', 'Weakly Negative [' + str(wnegative) + '%]', 'Strongly Negative [' + str(snegative) + '%]']
    sizes = [positive, wpositive, spositive, neutral, negative, wnegative, snegative]
    colors = ['yellowgreen','lightgreen','darkgreen', 'gold', 'red','lightsalmon','darkred']
    patches, texts = plt.pie(sizes, colors=colors, shadow=True,startangle=90)
    plt.legend(patches, labels, loc="best",  prop={'size': 20})
    plt.title('How people are reacting on ' + searchTerm + ' by analyzing ' + str(NoOfTerms) + ' Tweets.', size=50)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('static/final.png', bbox_inches='tight', pad_inches=1)

    # printing out data
    print("How people are reacting on " + searchTerm + " by analyzing " + str(NoOfTerms) + " tweets.")
    print()
    print("General Report: ")

    if (polarity == 0):
        senti="Neutral"
    elif (polarity > 0 and polarity <= 0.3):
        senti="Weakly Positive"
    elif (polarity > 0.3 and polarity <= 0.6):
        senti="Positive"
    elif (polarity > 0.6 and polarity <= 1):
        senti="Strongly Positive"
    elif (polarity > -0.3 and polarity <= 0):
        senti="Weakly Negative"
    elif (polarity > -0.6 and polarity <= -0.3):
        senti="Negative"
    elif (polarity > -1 and polarity <= -0.6):
        senti="Strongly Negative"

    report=("Detailed Report: ")
    pos=(str(positive) + "% people thought it was positive ")
    wpos=(str(wpositive) + "% people thought it was weakly positive")
    spos=(str(spositive) + "% people thought it was strongly positive")
    neg=(str(negative) + "% people thought it was negative")
    wneg=(str(wnegative) + "% people thought it was weakly negative")
    sneg=(str(snegative) + "% people thought it was strongly negative")
    neu=(str(neutral) + "% people thought it was neutral")
    gen="General Report"

    return render_template("process.html",t3=report,t4=pos,t5=wpos,t6=spos,t7=neg,t8=wneg,t9=sneg,t10=neu,t11=gen,t12=senti,poslist=ptweets[:5],neglist=ntweets[:5])

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=4000)