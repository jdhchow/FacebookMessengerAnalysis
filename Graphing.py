import pandas as pd
from matplotlib import pyplot as plt


'''
Author: Jonathan Chow
Date Modified: 2020-01-20
Python Version: 3.7

Functions for graphing the conversation features
'''


# Graph data for two participant conversation
def graphTwoParticipantTimeSeries(featureDict, yAxisName, savePath):
    graphAssistantDF = pd.DataFrame()

    for participant in featureDict:
        temp = pd.DataFrame(featureDict[participant], index=[participant]).transpose()
        graphAssistantDF = pd.concat([graphAssistantDF, temp], sort=True, ignore_index=False, axis=1)

    # Add zeros for dates when one party sent no messages
    graphAssistantDF = graphAssistantDF.fillna(0)

    # Add missing dates as zeros for both parties
    idx = pd.date_range(list(graphAssistantDF.index)[0], list(graphAssistantDF.index)[-1])
    graphAssistantDF = graphAssistantDF.reindex(idx, fill_value=0)

    graphAssistantDF.iloc[:, 1] = -graphAssistantDF.iloc[:, 1]

    plt.figure(figsize=(12, 5), dpi=250)
    plt.xlabel('Date')
    plt.ylabel(yAxisName)
    plt.title('Analysis of Facebook Messages (2011-08-09 to 2020-01-20)')

    # # One style of plotting
    # plt.scatter(list(graphAssistantDF.index), graphAssistantDF.iloc[:, 0], color='darkblue', label=graphAssistantDF.columns[0], marker='.')
    # plt.scatter(list(graphAssistantDF.index), graphAssistantDF.iloc[:, 1], color='tomato', label=graphAssistantDF.columns[1], marker='.')

    plt.plot(list(graphAssistantDF.index), graphAssistantDF.iloc[:, 0], color='darkblue', label=graphAssistantDF.columns[0])
    plt.plot(list(graphAssistantDF.index), graphAssistantDF.iloc[:, 1], color='tomato', label=graphAssistantDF.columns[1])

    plt.grid(True)

    # Set the y axis such that the scale is the same for both +/-
    maxYAxis = max([abs(x) for x in plt.gca().get_ylim()])
    plt.ylim(-maxYAxis, maxYAxis)

    # Change the negative values to positive for aesthetics
    yLabels = [int(abs(x)) for x in plt.gca().get_yticks().tolist()]
    plt.gca().set_yticklabels(yLabels)

    handles, labels = plt.gca().get_legend_handles_labels()

    plt.legend(handles, labels, loc='upper left')
    plt.savefig(savePath + yAxisName + '.png')
