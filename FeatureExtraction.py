import datetime


'''
Author: Jonathan Chow
Date Modified: 2020-01-20
Python Version: 3.7

Functions for extracting features from the conversation data. Note that all the times will be in GMT but this is not
of concern. I and the people I message are not in consistent timezones so trying to define a day would be wasteful.
'''


# Convert milliseconds (from start of unix time) to date
def ms2dt(milliseconds):
    s = milliseconds / 1000.0
    return datetime.datetime.fromtimestamp(s).date()


# Construct timeseries of the number of messages sent per day for each participant
def messagesPerDay(conversationList, featureDict):
    for conversation in conversationList:
        for message in conversation['messages']:
            try:
                featureDict[message['sender_name']][ms2dt(message['timestamp_ms'])] += 1
            except KeyError:
                featureDict[message['sender_name']][ms2dt(message['timestamp_ms'])] = 1

    return featureDict


# Make timeseries of the number of words sent per day for each participant
def wordsPerDay(conversationList, featureDict):
    for conversation in conversationList:
        for message in conversation['messages']:
            if 'content' in message:
                try:
                    featureDict[message['sender_name']][ms2dt(message['timestamp_ms'])] += len(message['content'].split(' '))
                except KeyError:
                    featureDict[message['sender_name']][ms2dt(message['timestamp_ms'])] = len(message['content'].split(' '))

    return featureDict
