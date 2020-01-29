import numpy as np
from matplotlib import pyplot as plt


'''
Author: Jonathan Chow
Date Modified: 2020-01-20
Python Version: 3.7

Functions for graphing conversation features
'''


# Get range of colours from 'darkblue' to 'tomato'
def list2Colour(listLen):
    startColour = (0.0, 0.0, 0.5450980392156862)
    endColour = (1.0, 0.38823529411764707, 0.2784313725490196)

    rgb = np.array([np.linspace(sc, ec, listLen) for sc, ec in zip(startColour, endColour)])

    return [tuple(rgb[:, cIndex]) for cIndex in range(0, listLen)]


# Graph two timeseries
def graphReflectedTimeSeries(featureDF, yAxisName, savePath, selfName):
    # Reflect the feature corresponding to me
    featureDF[selfName] = -featureDF[selfName]

    plt.figure(figsize=(12, 5), dpi=250)
    plt.xlabel('Date')
    plt.ylabel(yAxisName)
    plt.title('Analysis of Facebook Messages (2011-08-09 to 2020-01-20)')

    plt.plot(list(featureDF.index), featureDF.loc[:, featureDF.columns != selfName],
             color='darkblue', label=[x for x in featureDF.columns if x != selfName][0])
    plt.plot(list(featureDF.index), featureDF[selfName],
             color='tomato', label=selfName)

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


# Graph single timeseries
def graphSeries(featureSeries, yAxisName, savePath):
    plt.figure(figsize=(12, 5), dpi=250)
    plt.xlabel('Date')
    plt.ylabel(yAxisName)
    plt.title('Analysis of Facebook Messages (2011-08-09 to 2020-01-20)')
    plt.plot(list(featureSeries.index), featureSeries, color='darkblue')
    plt.grid(True)
    plt.savefig(savePath + yAxisName + '.png')


# Graph n overlapping timeseries
def graphOverlappingTimeSeries(featureDF, yAxisName, savePath):
    plt.figure(figsize=(12, 5), dpi=250)
    plt.xlabel('Date')
    plt.ylabel(yAxisName)
    plt.title('Analysis of Facebook Messages (2011-08-09 to 2020-01-20)')

    colourList = list2Colour(len(featureDF.columns))

    for participantIndex in range(0, len(featureDF.columns)):
        plt.plot(list(featureDF.index), featureDF.iloc[:, participantIndex],
                 color=colourList[participantIndex], label=featureDF.columns[participantIndex])

    plt.grid(True)

    handles, labels = plt.gca().get_legend_handles_labels()

    plt.legend(handles, labels, loc='upper left')
    plt.savefig(savePath + yAxisName + '.png')


# Graph n stacked timeseries
def graphStackedTimeSeries(featureDF, yAxisName, savePath):
    plt.figure(figsize=(12, 5), dpi=250)
    plt.xlabel('Date')
    plt.ylabel(yAxisName)
    plt.title('Analysis of Facebook Messages (2011-08-09 to 2020-01-20)')

    colourList = list2Colour(len(featureDF.columns))

    plt.stackplot(list(featureDF.index), featureDF.transpose().values.tolist(), colors=colourList, labels=featureDF.columns)

    plt.grid(True)

    handles, labels = plt.gca().get_legend_handles_labels()

    plt.legend(handles, labels, loc='upper left')
    plt.savefig(savePath + yAxisName + '.png')


# Graph n barcharts
def graphBarchart(featureDict, xAxisName, yAxisName, savePath, selfName):
    labels = list(range(1, len(featureDict[selfName]) + 1))
    x = np.arange(0, len(labels))
    width = 0.9 / len(featureDict)

    plt.figure(figsize=(12, 5), dpi=250)
    plt.xlabel(xAxisName)
    plt.ylabel(yAxisName)
    plt.title('Analysis of Facebook Messages (2011-08-09 to 2020-01-20)')

    colourList = list2Colour(len(featureDict))

    participantIndex = 0
    participantBars = []

    for participant in [part for part in featureDict if part != selfName]:
        participantBars += [(participant, plt.gca().bar(x + (width / 2) + (width * participantIndex),
                                                        [x[1] for x in featureDict[participant]],
                                                        width, color=colourList[participantIndex], label=participant))]
        participantIndex += 1

    participantBars += [(selfName, plt.gca().bar(x + (width / 2) + (width * participantIndex),
                                                    [x[1] for x in featureDict[selfName]],
                                                    width, color=colourList[participantIndex], label=selfName))]

    plt.gca().set_xticks(x)
    plt.gca().set_xticklabels(labels)

    handles, labels = plt.gca().get_legend_handles_labels()

    plt.legend(handles, labels, loc='upper right')

    for participant in participantBars:
        participantIndex = 0

        for rect in participant[1]:
            height = rect.get_height()

            plt.gca().annotate(featureDict[participant[0]][participantIndex][0],
                               xy=(rect.get_x() + rect.get_width() / 2, height),
                               xytext=(0, 1),  # 3 points vertical offset
                               textcoords='offset points',
                               ha='center', va='bottom', fontsize=5)

            participantIndex += 1

    plt.savefig(savePath + xAxisName + '.png')
