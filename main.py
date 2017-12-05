import numpy as np
from sklearn.neural_network import MLPRegressor
import json
import csv
import matplotlib.pyplot as plt
from sklearn.preprocessing import normalize
from sklearn.preprocessing import MinMaxScaler

class Main:
    @staticmethod
    def simulateData(season, dayType, appliances):
        filePath = '.\Preprocessed Data\\'

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

        for appliancesFolder in appliancesFolders:
            applianceFolderPath = filePath + appliancesFolder
            firstFileUrl = applianceFolderPath + '\\' + seasonAndDate.__str__()[2:16] + '\p-start-daily.csv'
            secondFileUrl = applianceFolderPath + '\\' + seasonAndDate.__str__()[2:16] + 'AVG-1min-interval.csv'
            thirdFileUrl = applianceFolderPath + '\\' + seasonAndDate.__str__()[2:16] + '-1min-interval.csv'

            time = np.arange(1, 1441)
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
                               hidden_layer_sizes=(3,3), random_state=1, max_iter=10000)
            print(np.size(Pstart.T), np.size(labels.T), np.size(time.T))
            print(Pstart, labels, time)
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
            print(min(labels), max(labels))
            clf.fit(features, labels)
            output = clf.predict(features)
            print(maxSca, minSca)
            output = maxSca*output
            labels = maxSca*labels
            print(max(output), max(labels))
            with open("jype.txt", "w") as outfile:
                json.dump(output.tolist(), outfile)
                outfile.close()
            output[output < 0] = 0
            print(output)
            plt.plot(time, output)
            plt.plot(time, oriLabels)
            plt.legend(['Predicted', 'Actual mean'])
            plt.xlabel('Time (1 minutes)')
            plt.ylabel('Energy')

        plt.show()

            # a = Pstart * Pmean.T