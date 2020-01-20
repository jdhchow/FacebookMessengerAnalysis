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

    # The key for the conversation dictionary storing the codes for my specific conversations
    name = 'Anonymous'
    convType = 'Individual'
    outputDir = 'Output/' + name + '/'

    # Make sure that the conversation type is correct
    assert convType == 'Individual' or convType == 'Group'

    # Create output directory if it does not exist
    Path(outputDir).mkdir(parents=True, exist_ok=True)

    # Read .zip file of messages
    archive = zipfile.ZipFile('messages20200120.zip', 'r')

    # Open desired conversation as json
    jsonConvList = []
    convIndex = 1
    while convIndex > 0:
        try:
            convName = 'messages/inbox/' + conversations[convType][name] + '/message_' + str(convIndex) + '.json'
            convRaw = archive.open(convName).read()
            jsonConvList += [json.loads(convRaw)]
            convIndex += 1
        except KeyError:
            break

    # Create dictionary of all participants
    participantList = list(set(parDict['name'] for conversation in jsonConvList for parDict in conversation['participants']))
    participantDict = {participant: {} for participant in participantList}

    messagesPerDayDict = messagesPerDay(jsonConvList, participantDict.copy())
    wordsPerDayDict = wordsPerDay(jsonConvList, participantDict.copy())

    if convType == 'Individual':
        graphIndividualConvTimeSeries(messagesPerDayDict, 'Number of Messages', outputDir)
        graphIndividualConvTimeSeries(wordsPerDayDict, 'Number of Words', outputDir)
    else:
        graphGroupConvTimeSeries(messagesPerDayDict, 'Number of Messages', outputDir)
        graphGroupConvTimeSeries(wordsPerDayDict, 'Number of Words', outputDir)

    print(str(datetime.datetime.now()) + ': Finished')
