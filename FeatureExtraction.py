import datetime
import pandas as pd
import re
from Graphing import *


'''
Author: Jonathan Chow
Date Modified: 2020-01-20
Python Version: 3.7

Functions for extracting features from conversation data

Note that all times are GMT. However, conversation participants are not in consistent timezones (and change timezones).
Some of the code is redundant and could be cleaned up.
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
    otherParticipants.sort(key=str.lower)

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


# Construct timeseries of proportion of messages to specific participants
# Messages sent to group chats are equivalent to sending a message to each person in the chat
def messagesSentPerDay(conversationList, featureDict, outputPath, self):
    for conversation in conversationList:
        for message in conversation['messages']:
            if message['sender_name'] == self:
                for participant in conversation['participants']:
                    try:
                        featureDict[participant['name']][ms2dt(message['timestamp_ms']).date()] += 1
                    except KeyError:
                        featureDict[participant['name']][ms2dt(message['timestamp_ms']).date()] = 1

    featureDF = featureDict2DF(featureDict, self)

    # Add zeros for dates when a party sent no messages
    featureDF = featureDF.fillna(0)

    # Remove total number of messages sent
    featureDF = featureDF.drop(self, 1)

    # Create dataframe of percent of messages sent to each participant
    percentFeatureDF = featureDF.div(featureDF.sum(axis=1), axis=0)

    # Add missing dates as zeros for all parties
    idx = pd.date_range(list(featureDF.index)[0], list(featureDF.index)[-1])
    featureDF = featureDF.reindex(idx, fill_value=0)

    graphStackedTimeSeries(featureDF, 'Messages Sent Per Day (Nominal)', outputPath)
    graphStackedTimeSeries(percentFeatureDF, 'Messages Sent Per Day (Percent)', outputPath)


# Construct timeseries of the cumulative number of words I use across all conversations
def cumWordUse(conversationList, outputPath, self):
    wordsOfInterestDict = {'interesting': {},
                           'nice': {},
                           'sorry': {},
                           'lol': {},
                           'lmao': {},
                           'neat': {},
                           'omg': {},
                           'hmm': {},
                           'fair': {},
                           'yeah': {}}

    for conversation in conversationList:
        for message in conversation['messages']:
            if message['sender_name'] == self and 'content' in message:
                for word in [re.sub(r'[^\w\s]', '', rawWord.lower()) for rawWord in message['content'].split(' ')]:
                    if word in wordsOfInterestDict:
                        try:
                            wordsOfInterestDict[word][ms2dt(message['timestamp_ms']).date()] += 1
                        except KeyError:
                            wordsOfInterestDict[word][ms2dt(message['timestamp_ms']).date()] = 1

    wordsOfInterestDF = pd.DataFrame()

    for word in wordsOfInterestDict:
        temp = pd.DataFrame(wordsOfInterestDict[word], index=[word]).transpose()
        wordsOfInterestDF = pd.concat([wordsOfInterestDF, temp], sort=True, ignore_index=False, axis=1)

    # Add missing dates as zeros for all parties
    idx = pd.date_range(list(wordsOfInterestDF.index)[0], list(wordsOfInterestDF.index)[-1])
    wordsOfInterestDF = wordsOfInterestDF.reindex(idx, fill_value=0)

    # Take the sum of word usage
    wordsOfInterestDF = wordsOfInterestDF.cumsum()

    # Fill from above for dates when no messages sent
    wordsOfInterestDF = wordsOfInterestDF.fillna(method='ffill')

    wordsOfInterestDF = wordsOfInterestDF[wordsOfInterestDF.columns.sort_values()]

    graphOverlappingTimeSeries(wordsOfInterestDF, 'Cumulative Word Usage (Common Responses)', outputPath)


# Construct timeseries of breaks between messages sent across all conversations
# TODO: The visualization of this function needs work
def breakLength(conversationList, outputPath, self):
    sentTimes = []

    for conversation in conversationList:
        messageList = [mssg for mssg in conversation['messages'] if mssg['sender_name'] == self]

        for message in messageList:
            sentTimes.append(message['timestamp_ms'])

    sentTimes.sort()

    featureSeries = pd.Series([(sentTimes[sentIndex] - sentTimes[sentIndex - 1]) / 60000 for sentIndex in range(1, len(sentTimes))], sentTimes[:-1])
    featureSeries.index = list(map(lambda x: ms2dt(x), featureSeries.index))

    graphSeries(featureSeries, 'Time Between Sent Messages (Minutes)', outputPath)


# Construct timeseries of the cumulative nominal and relative use of words 'i' and 'you' by all participants in a conversation
def convInterest(conversationList, featureDict, outputPath):
    wordList = ['i', 'you']
    featureWordDict = {}

    for participant in featureDict:
        for word in wordList:
            featureWordDict[participant + '_' + word] = {}

    for conversation in conversationList:
        for message in conversation['messages']:
            if 'content' in message:
                for word in [re.sub(r'[^\w\s]', '', rawWord.lower()) for rawWord in message['content'].split(' ')]:
                    if word in wordList:
                        try:
                            featureWordDict[message['sender_name'] + '_' + word][ms2dt(message['timestamp_ms']).date()] += 1
                        except KeyError:
                            featureWordDict[message['sender_name'] + '_' + word][ms2dt(message['timestamp_ms']).date()] = 1

    featureDF = pd.DataFrame()

    for participant in featureWordDict:
        temp = pd.DataFrame(featureWordDict[participant], index=[participant]).transpose()
        featureDF = pd.concat([featureDF, temp], sort=True, ignore_index=False, axis=1)

    # Add missing dates as zeros for all parties
    idx = pd.date_range(list(featureDF.index)[0], list(featureDF.index)[-1])
    featureDF = featureDF.reindex(idx, fill_value=0)

    # Get the running average of words per message
    featureDF = featureDF.cumsum()

    # Fill from above for dates when no messages sent
    featureDF = featureDF.fillna(method='ffill')

    featureRelativeDF = pd.DataFrame()

    for participant in featureDict:
        currWordUse = 0

        for word in wordList:
            currWordUse += featureDF[participant + '_' + word]

        for word in wordList:
            featureRelativeDF[participant + '_' + word] = featureDF[participant + '_' + word] / currWordUse

    featureDF = featureDF[featureDF.columns.sort_values()]
    featureRelativeDF = featureRelativeDF[featureRelativeDF.columns.sort_values()]

    graphOverlappingTimeSeries(featureDF, 'Cumulative Nominal Word Usage (Pronouns as Interest Proxy)', outputPath)
    graphOverlappingTimeSeries(featureRelativeDF, 'Cumulative Relative Word Usage (Pronouns as Interest Proxy)', outputPath)


# Construct barchart of common words used by participants in a conversations
def commonWords(conversationList, featureDict, outputPath, self):
    for conversation in conversationList:
        for message in conversation['messages']:
            if 'content' in message:
                for word in [re.sub(r'[^\w\s]', '', rawWord.lower()) for rawWord in message['content'].split(' ')]:
                    try:
                        featureDict[message['sender_name']][word] += 1.0
                    except KeyError:
                        featureDict[message['sender_name']][word] = 1.0

    wordList = {}

    for participant in featureDict:
        totalWords = 0

        for word, frequency in featureDict[participant].items():
            totalWords += frequency

        for word, frequency in featureDict[participant].items():
            featureDict[participant][word] /= totalWords

        wordList[participant] = [(word, frequency) for word, frequency in featureDict[participant].items() if len(word) > 0]
        wordList[participant].sort(key=lambda x: x[1], reverse=True)
        # wordList[participant] = [tup for tup in wordList[participant] if len(tup[0]) >= 4]
        wordList[participant] = wordList[participant][:20]

    graphBarchart(wordList, 'Most Common Words', 'Frequency', outputPath, self)
