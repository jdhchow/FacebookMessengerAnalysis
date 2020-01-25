import datetime
import pandas as pd
from Graphing import *


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
    return datetime.datetime.fromtimestamp(s)


def featureDict2DF(featureDict, self):
    featureDF = pd.DataFrame()

    for participant in featureDict:
        temp = pd.DataFrame(featureDict[participant], index=[participant]).transpose()
        featureDF = pd.concat([featureDF, temp], sort=True, ignore_index=False, axis=1)

    otherParticipants = list(featureDF.columns)
    otherParticipants.remove(self)

    featureDF = featureDF[otherParticipants + [self]]

    return featureDF


# Construct timeseries of the number of messages sent per day for each participant
def messagesPerDay(conversationList, featureDict, outputPath, self, indOrGroup):
    for conversation in conversationList:
        for message in conversation['messages']:
            try:
                featureDict[message['sender_name']][ms2dt(message['timestamp_ms']).date()] += 1
            except KeyError:
                featureDict[message['sender_name']][ms2dt(message['timestamp_ms']).date()] = 1

    featureDF = featureDict2DF(featureDict, self)

    # Add zeros for dates when a party sent no messages
    featureDF = featureDF.fillna(0)

    # Add missing dates as zeros for all parties
    idx = pd.date_range(list(featureDF.index)[0], list(featureDF.index)[-1])
    featureDF = featureDF.reindex(idx, fill_value=0)

    if indOrGroup == 'Individual':
        graphReflectedTimeSeries(featureDF, 'Number of Messages', outputPath, self)
    else:
        graphOverlappingTimeSeries(featureDF, 'Number of Messages', outputPath)


# Make timeseries of the number of words sent per day for each participant
def wordsPerDay(conversationList, featureDict, outputPath, self, indOrGroup):
    for conversation in conversationList:
        for message in conversation['messages']:
            if 'content' in message:
                try:
                    featureDict[message['sender_name']][ms2dt(message['timestamp_ms']).date()] += len(message['content'].split(' '))
                except KeyError:
                    featureDict[message['sender_name']][ms2dt(message['timestamp_ms']).date()] = len(message['content'].split(' '))

    featureDF = featureDict2DF(featureDict, self)

    # Add zeros for dates when a party sent no messages
    featureDF = featureDF.fillna(0)

    # Add missing dates as zeros for all parties
    idx = pd.date_range(list(featureDF.index)[0], list(featureDF.index)[-1])
    featureDF = featureDF.reindex(idx, fill_value=0)

    if indOrGroup == 'Individual':
        graphReflectedTimeSeries(featureDF, 'Number of Words', outputPath, self)
    else:
        graphOverlappingTimeSeries(featureDF, 'Number of Words', outputPath)


# Make timeseries of the cumulative word difference between me and average words sent by other participants
def cumWordDiff(conversationList, featureDict, outputPath, self):
    for conversation in conversationList:
        for message in conversation['messages']:
            if 'content' in message:
                featureDict[message['sender_name']][ms2dt(message['timestamp_ms'])] = len(message['content'].split(' '))

    featureDF = featureDict2DF(featureDict, self)

    # Add zeros for dates when one party sent no messages
    featureDF = featureDF.fillna(0)
    featureDF['Average'] = featureDF.loc[:, featureDF.columns != self].mean(axis=1)
    featureDF = featureDF.cumsum()
    featureSeries = featureDF[self] - featureDF['Average']

    graphSeries(featureSeries, 'Cumulative Word Difference (Self - Other Participant(s) Average)', outputPath)


# Make timeseries of the cumulative message difference between me and average words sent by other participants
def cumMessageDiff(conversationList, featureDict, outputPath, self):
    for conversation in conversationList:
        for message in conversation['messages']:
            featureDict[message['sender_name']][ms2dt(message['timestamp_ms'])] = 1

    featureDF = featureDict2DF(featureDict, self)

    # Add zeros for dates when one party sent no messages
    featureDF = featureDF.fillna(0)
    featureDF['Average'] = featureDF.loc[:, featureDF.columns != self].mean(axis=1)
    featureDF = featureDF.cumsum()
    featureSeries = featureDF[self] - featureDF['Average']

    graphSeries(featureSeries, 'Cumulative Message Difference (Self - Other Participant(s) Average)', outputPath)


# Construct timeseries of the running average number of words per message sent for each participant
def avgWordsPerMessage(conversationList, featureDict, outputPath, self):
    for conversation in conversationList:
        for message in conversation['messages']:
            if 'content' in message:
                featureDict[message['sender_name']][ms2dt(message['timestamp_ms'])] = len(message['content'].split(' '))

    featureDF = featureDict2DF(featureDict, self)

    # Get the running average of words per message
    featureDF = featureDF.expanding().mean()

    graphOverlappingTimeSeries(featureDF, 'Running Average of Words Per Message', outputPath)
