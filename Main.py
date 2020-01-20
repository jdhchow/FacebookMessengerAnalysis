import zipfile
import json
from pathlib import Path
from Graphing import *
from FeatureExtraction import *
from BookmarkedConversations import *


'''
Author: Jonathan Chow
Date Modified: 2020-01-20
Python Version: 3.7

Data visualization/analysis of Facebook Messenger data from 2011-08-09 to 2020-01-20
'''


if __name__ == '__main__':
    print(str(datetime.datetime.now()) + ': Started')

    # The key for the individualConv or groupConv dictionaries storing the codes for my specific conversations
    name = 'Anonymous'
    outputDir = 'Output/' + name + '/'

    # Create output directory if it does not exist
    Path(outputDir).mkdir(parents=True, exist_ok=True)

    # Read .zip file of messages
    archive = zipfile.ZipFile('messages20200120.zip', 'r')

    # Open desired conversation as json
    jsonConvList = []
    convIndex = 1
    while convIndex > 0:
        try:
            convName = 'messages/inbox/' + individualConv[name] + '/message_' + str(convIndex) + '.json'
            convRaw = archive.open(convName).read()
            jsonConvList += [json.loads(convRaw)]
            convIndex += 1
        except KeyError:
            break

    # Create dictionary of all participants
    participantList = list(set(parDict['name'] for conversation in jsonConvList for parDict in conversation['participants']))
    participantDict = {participant: {} for participant in participantList}

    messagesPerDayDict = messagesPerDay(jsonConvList, participantDict.copy())
    graphTwoParticipantTimeSeries(messagesPerDayDict, 'Number of Messages', outputDir)

    wordsPerDayDict = wordsPerDay(jsonConvList, participantDict.copy())
    graphTwoParticipantTimeSeries(wordsPerDayDict, 'Number of Words', outputDir)

    print(str(datetime.datetime.now()) + ': Finished')
