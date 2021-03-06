import argparse
import numpy as np
from sklearn.neural_network import MLPRegressor
import json
import csv
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

import const
import generateLabel


class Main:
    @staticmethod
    def simulateData(season, dayType, appliances):
        filePath = '.\Preprocessed Data\\'
        dataPath = '.\Data\\'
        appliancesFolders = []
        for appliance in appliances:
            appliancesFolders.append({
                                         'Kettle': '04',
                                         'PC': '06',
                                         'Fridge': '01',
                                         'Washer': '05',
                                         'Freezer': '07',
                                         'Dryer': '02'
                                     }[appliance])

        seasonAndDate = {
            {
                True: 'weekend',
                False: 'weekday'
            }[dayType]
            + '-' +
            {
                True: 'winter',
                False: 'summer'
            }[season]
        }

        actualTotalEnergyConsumption = [float(0.0)] * 1440
        expectTotalEnergyConsumption = [float(0.0)] * 1440

        for appliancesFolder in appliancesFolders:
            applianceFolderPath = filePath + appliancesFolder
            dataForlderPath = dataPath + appliancesFolder
            generateLabel.generateLabel(dataForlderPath, seasonAndDate.__str__()[2:16], applianceFolderPath)
            firstFileUrl = applianceFolderPath + '\\' + seasonAndDate.__str__()[2:16] + '\p-start-daily.csv'
            secondFileUrl = applianceFolderPath + '\\' + seasonAndDate.__str__()[2:16] + 'AVG-1min-interval.csv'
            thirdFileUrl = applianceFolderPath + '\\' + seasonAndDate.__str__()[2:16] + '-1min-interval.csv'

            time = np.arange(1, 1441)
            if appliancesFolder == '04':
                Pstart = []
                output = []
                labels = []
                with open(firstFileUrl,
                          newline='') as csvfile:
                    dataReader = csv.reader(csvfile, delimiter=';')
                    for data in dataReader:
                        Pstart = np.append(Pstart, [float(i) for i in data])

                # poissonDistribution = np.random.poisson(lam=(100., 500.), size=(100, 2))

                powerOnConsumption = {
                    'weekend-summer': const.Const.KETTLE_WEEKEND_SUMMER_AVERAGE_DAILY_ON_POWER,
                    'weekend-winter': const.Const.KETTLE_WEEKEND_WINTER_AVERAGE_DAILY_ON_POWER,
                    'weekday-summer': const.Const.KETTLE_WEEKDAY_SUMMER_AVERAGE_DAILY_ON_POWER,
                    'weekday-winter': const.Const.KETTLE_WEEKDAY_WINTER_AVERAGE_DAILY_ON_POWER
                }[seasonAndDate.__str__()[2:16]]

                useFrequency = {
                    'weekend-summer': const.Const.KETTLE_WEEKEND_SUMMER_AVERAGE_DAILY_USE_TIME,
                    'weekend-winter': const.Const.KETTLE_WEEKEND_WINTER_AVERAGE_DAILY_USE_TIME,
                    'weekday-summer': const.Const.KETTLE_WEEKDAY_SUMMER_AVERAGE_DAILY_USE_TIME,
                    'weekday-winter': const.Const.KETTLE_WEEKDAY_WINTER_AVERAGE_DAILY_USE_TIME
                }[seasonAndDate.__str__()[2:16]]

                useTime = {
                    'weekend-summer': const.Const.KETTLE_WEEKEND_SUMMER_AVERAGE_DAILY_TIME_USE,
                    'weekend-winter': const.Const.KETTLE_WEEKEND_WINTER_AVERAGE_DAILY_TIME_USE,
                    'weekday-summer': const.Const.KETTLE_WEEKDAY_SUMMER_AVERAGE_DAILY_TIME_USE,
                    'weekday-winter': const.Const.KETTLE_WEEKDAY_WINTER_AVERAGE_DAILY_TIME_USE
                }[seasonAndDate.__str__()[2:16]]

                probeFactor = 1
                currentUseTime = 0
                for dailyminute in Pstart:
                    if currentUseTime > 0:
                        if currentUseTime > 60:
                            output.append(powerOnConsumption * 60)
                        else:
                            output.append(powerOnConsumption * currentUseTime)
                            probeFactor = 2
                        currentUseTime -= 60
                    else:
                        if probeFactor > 1:
                            probeFactor -= 0.01
                        randomProbabilityStart = probeFactor * np.random.uniform(0.8, 1)
                        if dailyminute > randomProbabilityStart:
                            if useFrequency > 0:
                                currentUseTime = useTime
                                if currentUseTime > 60:
                                    output.append(powerOnConsumption * 60)
                                else:
                                    output.append(powerOnConsumption * currentUseTime)
                                    probeFactor = 2
                                currentUseTime -= 60
                                useFrequency -= 1
                            else:
                                output.append(0)
                        else:
                            output.append(0)

                with open(thirdFileUrl,
                          newline='') as csvfile:
                    dataReader = csv.reader(csvfile, delimiter=';')
                    for data in dataReader:
                        labels = np.append(labels, np.array([[float(i) for i in data]]))
                    labels = np.array([labels])

                oriLabels = labels.T
                # print(output)
                # print(labels)
                # plt.plot(time, output)
                # plt.plot(time, labels)
                # plt.legend(['Predicted', 'Actual mean'])
                # plt.xlabel('Time (1 minutes)')
                # plt.ylabel('Energy')
                print(labels)
                expectTotalEnergyConsumption = [x + y for x, y in zip(expectTotalEnergyConsumption, output)]
                actualTotalEnergyConsumption = [x + y for x, y in zip(actualTotalEnergyConsumption, oriLabels)]

                # lamsaothilam
            else:
                Pmean = []

                Pstart = []

                labels = []
                with open(firstFileUrl,
                          newline='') as csvfile:
                    dataReader = csv.reader(csvfile, delimiter=';')
                    for data in dataReader:
                        Pstart = np.append(Pstart, [float(i) for i in data])
                        # Pstart = array([Pstart])
                with open(secondFileUrl,
                          newline='') as csvfile:
                    dataReader = csv.reader(csvfile, delimiter=';')
                    for data in dataReader:
                        Pmean = np.append(Pmean, [float(i) for i in data])
                    Pmean = np.array([Pmean])
                with open(thirdFileUrl,
                          newline='') as csvfile:
                    dataReader = csv.reader(csvfile, delimiter=';')
                    for data in dataReader:
                        labels = np.append(labels, np.array([[float(i) for i in data]]))
                    labels = np.array([labels])

                clf = MLPRegressor(solver='lbfgs', alpha=1e-5,
                                   hidden_layer_sizes=(7, 7), random_state=0, max_iter=20000)
                # print(np.size(Pstart.T), np.size(labels.T), np.size(time.T))
                # print(Pstart, labels, time)
                # temp = Pmean
                # Pmean = labels
                # labels = temp
                features = np.vstack((Pstart, Pmean, time))
                scaler = MinMaxScaler(feature_range=(0, 1))
                features = scaler.fit_transform(features.T)
                #   features = normalize(features.T, axis=0)
                oriLabels = labels.T
                maxSca = np.max(labels)
                minSca = np.min(labels)
                #    labels = normalize(labels.T, axis=0)
                labels = scaler.fit_transform(labels.T)
                # print(min(labels), max(labels))
                clf.fit(features, labels)
                output = clf.predict(features)
                # print(maxSca, minSca)
                output = maxSca * output
                labels = maxSca * labels
                # print(max(output), max(labels))
                with open("jype.txt", "w") as outfile:
                    json.dump(output.tolist(), outfile)
                    outfile.close()
                output[output < 0] = 0
                # print(output)
                # plt.plot(time, output)
                # plt.plot(time, oriLabels)
                # plt.legend(['Predicted', 'Actual mean'])
                # plt.xlabel('Time (1 minutes)')
                # plt.ylabel('Energy')

                expectTotalEnergyConsumption = [x + y for x, y in zip(expectTotalEnergyConsumption, output)]
                actualTotalEnergyConsumption = [x + y for x, y in zip(actualTotalEnergyConsumption, oriLabels)]

        # plt.subplot(211)
        plt.plot(time, expectTotalEnergyConsumption)
        # plt.subplot(212)
        plt.plot(time, actualTotalEnergyConsumption)
        plt.legend(['Simulated consumption', 'Actual consumption'])
        plt.xlabel('Time (minute)')
        plt.ylabel('Energy (W)')
        plt.show()

        # a = Pstart * Pmean.T


def main():
    # create parser object
    parser = argparse.ArgumentParser(description="A command line interface for Energy Consumption Simulator")

    # defining arguments for parser object
    parser.add_argument("-season", type=str, nargs=1,
                        metavar="season", default=['winter'], choices={'summer', 'winter'},
                        help="Choose the appropriate season (winter or summer)")

    parser.add_argument("-daytype", type=str, nargs=1,
                        metavar="daytype", default=['weekdays'], choices={'weekdays', 'weekends'},
                        help="Choose the appropriate daytype (weekdays or weekends)")

    parser.add_argument('appliances', metavar='appliance', type=str, nargs='+',
                        help='Choose the list of appliances to simulate\n'
                             'all or the name of appliances (i.e. Fridge, Kettle, PC, Washer, Dryer, Freezer',
                        choices=['all', 'Fridge', 'Kettle', 'PC', 'Washer', 'Dryer', 'Freezer'])

    # parse the arguments from standard input
    args = parser.parse_args()
    if args.season == ['winter'] or args.season == 'winter':
        season = 1
    else:
        season = 0
    if args.daytype == ['weekdays'] or args.season == 'weekdays':
        dayType = 0
    else:
        dayType = 1
    if args.appliances == ['all']:
        appliances = ['Fridge', 'Kettle', 'PC', 'Washer', 'Dryer', 'Freezer']
    else:
        appliances = args.appliances

    Main.simulateData(season, dayType, appliances)


if __name__ == "__main__":
    # calling the main function
    main()
