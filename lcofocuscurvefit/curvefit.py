import argparse
import sys
import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize
import logging
import json

_logger = logging.getLogger(__name__)

sqrtfit = lambda x, seeing, bestfocus, slope: (seeing ** 2 + (slope * (x - bestfocus)) ** 2) ** 0.5


def dofit(xdata, ydata, func=sqrtfit, plot=False):
    # TODO: Verification that we have enough points.

    for iter in range(2):
        (paramset, istat) = optimize.curve_fit(func, xdata, ydata)
        # TODO: Verification that fit succeeded

        if len(paramset) == 3:
            fit = func(xdata, paramset[0], paramset[1], paramset[2])
        elif len(paramset) == 2:
            fit = func(xdata, paramset[0], paramset[1])
        else:
            _logger.error("Order of fit not supported")
            return None

        delta = ydata - fit
        s = np.std(delta)
        good = delta < 2 * s
        xdata = xdata[good]
        ydata = ydata[good]

    if plot:
        base = np.arange(-3.6, 3.6, 0.1)
        y = func(base, paramset[0], paramset[1], paramset[2])
        plt.plot(base, y, "--")

    return paramset, s


def parseCommandLine():
    parser = argparse.ArgumentParser(
        description='Fit a focus curve to an autofocus sequence result.')

    parser.add_argument("--focuslist", nargs='+', type=float)
    parser.add_argument("--fwhmlist", nargs='+', type=float)
    parser.add_argument('--plotit', action='store_true',
                        help='make a nice plot')
    parser.add_argument("--plotname", default="focusplot.png", help="Name of output plot file")

    args = parser.parse_args()
    if (len(args.focuslist) != len(args.fwhmlist)) or (len(args.focuslist) < 4):
        _logger.error(
            "Invalid input: either the input liskts differ in size or do not have enough entries (minimum is 4:\n{}\n{}".format(
                args.focuslist, args.fwhmlist))
        exit(1)
    args.focuslist = np.asarray(args.focuslist)
    args.fwhmlist = np.asarray(args.fwhmlist)
    return args


def main():
    args = parseCommandLine()

    if args.plotit:
        plt.figure()
        plt.plot(args.focuslist, args.fwhmlist, 'o')
        plt.xlabel("FOCUS Demand [mm foc plane]")
        plt.ylabel("FWHM (Pixels")
        plt.xlim([-3.6, 3.6])
        plt.ylim([0, 14])

    p, rms = dofit(args.focuslist, args.fwhmlist, sqrtfit, plot=args.plotit)

    if args.plotit:
        plt.axvline(x=p[1], label="best focus sqrt")
        plt.legend()
        plt.title("Sqrt best focus found at {:5.2f}".format(p[1]))
        plt.savefig("focus_{}.png".format(jackstart))

    returnpackage = {'fitok': True,
                     'fit_seeing': p[0],
                     'fit_focus': p[1],
                     'fit_slope': p[2],
                     'fit_rms': rms}

    print(json.dumps(returnpackage))

if __name__ == '__main__':
    main()
