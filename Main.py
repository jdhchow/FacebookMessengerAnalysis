import zipfile
import json
import copy
from pathlib import Path
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
    convName = 'Anonymous'
    me = 'Jonathan Chow'
    convType = 'Individual'
    outputDir = 'Output/' + convName + '/'

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
            convID = 'messages/inbox/' + conversations[convType][convName] + '/message_' + str(convIndex) + '.json'
            convRaw = archive.open(convID).read()
            jsonConvList += [json.loads(convRaw)]
            convIndex += 1
        except KeyError:
            break

    # Create dictionary of all participants
    participantList = list(set(parDict['name'] for conversation in jsonConvList for parDict in conversation['participants']))
    participantDict = {participant: {} for participant in participantList}

    messagesPerDay(jsonConvList, copy.deepcopy(participantDict), outputDir, me, convType)
    wordsPerDay(jsonConvList, copy.deepcopy(participantDict), outputDir, me, convType)
    cumMessageDiff(jsonConvList, copy.deepcopy(participantDict), outputDir, me)
    cumWordDiff(jsonConvList, copy.deepcopy(participantDict), outputDir, me)
    avgWordsPerMessage(jsonConvList, copy.deepcopy(participantDict), outputDir, me, convType)

    print(str(datetime.datetime.now()) + ': Finished')
