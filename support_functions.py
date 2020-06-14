import numpy as np
import matplotlib.pyplot as plt


def enhance_for_plot(xarray, run_time, inplot, *plotarg):
    k = 0
    time = np.zeros(2*(run_time-1)+1)
    orray = np.zeros(2 * (run_time - 1) + 1)
    for i in range(run_time):
        if i == 0:
            time[k] = i
            orray[k] = xarray[i]
            k = k + 1
        else:
            time[k] = i
            orray[k] = xarray[i-1]
            time[k + 1] = i
            orray[k + 1] = xarray[i]
            k = k + 2
    plt.figure(inplot.number)
    if plotarg.__len__() == 1:
        plt.plot(time, orray, plotarg[0])
    else:
        plt.plot(time, orray)
