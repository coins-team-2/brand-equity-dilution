import sys
import os
import nltk
import re
import string
import random
import pymongo
import config
import statistics
import datetime
import collections
import json
import argparse

import matplotlib.pyplot as plt

from database_client import DatabaseClient

from nltk import FreqDist
from nltk import classify
from nltk import NaiveBayesClassifier

from nltk.tag import pos_tag

from nltk.corpus import stopwords
from nltk.corpus import subjectivity
from nltk.corpus import twitter_samples

from nltk.tokenize import word_tokenize

from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.util import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from nltk.stem.wordnet import WordNetLemmatizer

from pymongo import MongoClient

from wordcloud import WordCloud

from bson import json_util

from threading import Thread


def nltk_downloader():
    # downloads nltk packages
    nltk.download('twitter_samples')
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('stopwords')
    nltk.download('vader_lexicon')

def get_cloud_data(keyword):
    dbClient = DatabaseClient()

    tweets = list(dbClient.getAllDocuments(keyword))
    print("Currently there are %s tweets stored in the database collection '%s'." %(str(len(tweets)), keyword))

    max_id = max(list(map(lambda tweet: int(tweet['id_str']), tweets)))
    print("Id of latest fetched tweet is %s." %str(max_id))

    # print(type(tweets[0]))
    with open(keyword + '_data.json', 'w+') as f:
        # f.write(json.dumps(tweets, default=json_util.default, indent=4))
        json.dump(tweets, f, default=json_util.default, indent=4)
    return tweets

def get_tweets(keyword):
    # try:
    with open(keyword + '_data.json', 'r') as f:
        tweets = json.load(f)

    return tweets
    # except:
    #     print("No Data Stored. Start Script with '-o'-option to receive data from Cloud-DB.")
    #     return "No Data"    


def remove_noise(tweet_tokens, stop_words):

    cleaned_tokens = []

    for token, tag in pos_tag(tweet_tokens):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        token = re.sub("(@[A-Za-z0-9_]+)","", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        token = lemmatizer.lemmatize(token, pos)

        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            cleaned_tokens.append(str(token.lower()))
    return cleaned_tokens


def get_sentiment_of_tweet(tweet, neg, neu, pos):

    stop_words = stopwords.words('english')

    cleaned_tweet = remove_noise(word_tokenize(tweet), stop_words)
    

    ss = sid.polarity_scores(u" ".join(cleaned_tweet))

    neg.append(ss['neg'])
    neu.append(ss['neu'])
    pos.append(ss['pos'])

    return cleaned_tweet, neg, neu, pos

def converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def get_sentiment_results(b, keywords):
    results = dict()
    wc_results = dict()
    for kw in keywords:
        if b in kw:
            wc_results[kw] = collections.Counter({})
            print("Sentiment Intensity Analysis with noise removal for \"%s\": poitive, negative, neutral percentages" %kw)
            tweets = False

            results[kw] = dict()
            
            # while not tweets:
            #     try:
            tweets = get_tweets(kw)
                # except:
                #     tweets = False

            if tweets == "No Data":
                sys.exit()
            neg, neu, pos = list(), list(), list()

            print('Starting Analysis for %s' %kw)
            for tweet in tweets:
                if tweet['lang'] == 'en':
                    date = str(datetime.datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S %z %Y").date())
                    try:
                        x = results[kw][date]
                    except KeyError:
                        results[kw][date] = dict()
                        results[kw][date]['neg'] = list()
                        results[kw][date]['neu'] = list()
                        results[kw][date]['pos'] = list()
                    cleaned_tweet, results[kw][date]['neg'], results[kw][date]['neu'], results[kw][date]['pos'] = get_sentiment_of_tweet(tweet['full_text'], results[kw][date]['neg'], results[kw][date]['neu'], results[kw][date]['pos'])

                    # # print(cleaned_tweet)
                    # cleaned_tweet = [x for x in cleaned_tweet if x != 'http']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != 'https']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != 'rt']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != ',']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '0']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '\'s']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '´´']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '``']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '\'\'']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '.']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '..']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '...']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '=']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != ':']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != ';']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '?']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '!']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '\'']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '"']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '""']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '(']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != ')']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '>']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '<']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '/']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '`']
                    # cleaned_tweet = [x for x in cleaned_tweet if x != '´']
                    # if b == 'audi':
                    #     cleaned_tweet = [x for x in cleaned_tweet if x != 'audi']
                    #     cleaned_tweet = [x for x in cleaned_tweet if x != 'e-tron']
                    #     cleaned_tweet = [x for x in cleaned_tweet if x != 'etron']
                    # if b == 'volkswagen':
                    #     cleaned_tweet = [x for x in cleaned_tweet if x != 'volkswagen']
                    #     cleaned_tweet = [x for x in cleaned_tweet if x != 'vw']
                    #     cleaned_tweet = [x for x in cleaned_tweet if x != 'id3']
                    #     cleaned_tweet = [x for x in cleaned_tweet if x != 'id.3']
                    #     cleaned_tweet = [x for x in cleaned_tweet if x != 'vwid3']
                    #     cleaned_tweet = [x for x in cleaned_tweet if x != 'vwid.3']
                    # if b == 'mercedes':
                    #     cleaned_tweet = [x for x in cleaned_tweet if x != 'mercedes']
                    #     cleaned_tweet = [x for x in cleaned_tweet if x != 'mercedes-benz']
                    #     cleaned_tweet = [x for x in cleaned_tweet if x != 'mercedesbenz']
                    #     cleaned_tweet = [x for x in cleaned_tweet if x != 'benz']
                    #     cleaned_tweet = [x for x in cleaned_tweet if x != 'eqc']
                    
                    # wc_results[kw] += collections.Counter(cleaned_tweet)




    # x_axis_vals = dict()
    # y_axis_vals = dict()
    for kw in results:
        for date in sorted(results[kw]):
            print((sum(results[kw][date]['pos']) / len(results[kw][date]['pos'])) - (sum(results[kw][date]['neg']) / len(results[kw][date]['neg'])))
            results[kw][date]['len'] = len(results[kw][date]['pos'])
            results[kw][date]['pos_avg'] = sum(results[kw][date]['pos']) / len(results[kw][date]['pos'])
            results[kw][date]['neu_avg'] = sum(results[kw][date]['neu']) / len(results[kw][date]['neu'])
            results[kw][date]['neg_avg'] = sum(results[kw][date]['neg']) / len(results[kw][date]['neg'])
            results[kw][date]['value'] = (sum(results[kw][date]['pos']) / len(results[kw][date]['pos'])) - (sum(results[kw][date]['neg']) / len(results[kw][date]['neg']))
            del results[kw][date]['pos']
            del results[kw][date]['neu']
            del results[kw][date]['neg']

    #     wordcloud = WordCloud()
    #     wordcloud.generate_from_frequencies(frequencies=wc_results[kw])
    #     plt.figure()
    #     plt.imshow(wordcloud, interpolation="bilinear")
    #     plt.axis("off")
    #     plt.show()

    #     x_axis_vals[kw] = list()
    #     y_axis_vals[kw] = list()

    #     for date in sorted(results[kw]):
    #         neg_avg = sum(results[kw][date]['neg']) / len(results[kw][date]['neg'])
    #         print(neg_avg)
    #         if len(results[kw][date]['neg']) > 0:
    #             y_axis_vals[kw].append(neg_avg)
    #         x_axis_vals[kw].append(str(date))

    # print(x_axis_vals[list(x_axis_vals.keys())[0]])
    # print(y_axis_vals[list(y_axis_vals.keys())[0]])
    # print(x_axis_vals[list(x_axis_vals.keys())[1]])
    # print(y_axis_vals[list(y_axis_vals.keys())[1]])


    # plt.plot(x_axis_vals[list(x_axis_vals.keys())[0]], y_axis_vals[list(y_axis_vals.keys())[0]], 'r--', x_axis_vals[list(x_axis_vals.keys())[1]], y_axis_vals[list(y_axis_vals.keys())[1]], 'b--')
    # plt.show()


    print(results)
    with open('results_%s_%s.json' %(b, datetime.datetime.now().strftime("%Y%m%d%H%M%S")), 'w+') as f:
        # f.write(json.dumps(tweets, default=json_util.default, indent=4))
        json.dump(results, f, default=converter, indent=4)

def main():
    # nltk_downloader()
    brands = ['audi', 'volkswagen', 'mercedes']
    keywords = ['audi_etron', 'audi', 'volkswagen_id3', 'volkswagen', 'mercedes_eqc', 'mercedes']
    # keywords = ['audi_etron', 'volkswagen_id3', 'mercedes_eqc']
    # keywords = ['audi', 'volkswagen', 'mercedes']
    # keywords = ['mercedes']
    # keywords = ['audi_etron']#, 'audi']

    if args.online:
        for b in brands:
            for kw in keywords:
                if b in kw:
                    get_cloud_data(kw)
                    print('Fetched and saved data of "%s' %kw)

        print('Successfully fetched and saved cloud data to JSON Files')

        exit()


    for b in brands:
        get_sentiment_results(b, keywords)
        # t = Thread(target=get_sentiment_results, args=(b, keywords))
        # t.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Offline or Online Data')
    parser.add_argument("-o", "--online", help="Get Online Data", action="store_true")

    args = parser.parse_args()

    sid = SentimentIntensityAnalyzer()
    lemmatizer = WordNetLemmatizer()

    main()