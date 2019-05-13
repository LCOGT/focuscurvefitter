import argparse
import math
import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize
import json


_LIMIT_EXPONENT_U=1

# This describes our model for a focus curve: Seeing and defocus add in quadrature.
sqrtfit = lambda x, seeing, bestfocus, slope, tweak: (seeing ** 2 + (slope * (x - bestfocus)) ** 2) ** tweak
polyfit = lambda x, p0, p1, p2: p2 * (x - p1) ** 2 + p0

def focus_curve_fit(xdata, ydata, func=sqrtfit, plot=False):
    # TODO: Verification that we have enough points.

    initial_guess = [2,0,1,0.6] if func == sqrtfit else None
    bounds = [[0,-3,0,0.5], [5, 3,5,_LIMIT_EXPONENT_U]]  if func == sqrtfit else [-math.inf, math.inf]

    for iter in range(2):
        (paramset, istat) = optimize.curve_fit(func, xdata, ydata, p0=initial_guess, bounds=bounds)
        # sigma rejection and rms estimate:
        fit = func(xdata, *paramset)
        delta = ydata - fit
        s = np.std(delta)
        good = (delta < 3 * s)
        xdata = xdata[good]
        ydata = ydata[good]

    paramerrors = np.sqrt(np.diag(istat))

    if plot:
        base = np.arange(-3.6, 3.6, 0.1)
        y = func(base, *paramset)
        plt.plot(base, y, "--", label="sqrt {:5.2f}".format (paramset[3]) if func == sqrtfit else "parabola")

    return paramset, paramerrors


def parseCommandLine():
    parser = argparse.ArgumentParser(
        description='Fit a focus curve to an autofocus sequence result.')
    parser.add_argument("--focuslist", nargs='+', type=float)
    parser.add_argument("--fwhmlist", nargs='+', type=float)
    parser.add_argument('--makepng', action='store_true',
                        help='make a nice plot')
    parser.add_argument("--pngname", default="focusplot.png", help="Name of output plot file")

    args = parser.parse_args()

    if (len(args.focuslist) != len(args.fwhmlist)) or (len(args.focuslist) < 4):
        # TODO: For service integration, trickle up error condition.
        print(json.dumps({'fitok': False,
                          'errormsg': "Invalid input: either the input lists differ in size or do not have enough entries (minimum is 4:\n{}\n{}".format(
                              args.focuslist, args.fwhmlist)}))
        exit(0)

    args.focuslist = np.asarray(args.focuslist)
    args.fwhmlist = np.asarray(args.fwhmlist)
    return args


def makeprettyplot():
    # TODO: Move all the plotting stuff in here
    pass


def main():
    args = parseCommandLine()

    if args.makepng:
        plt.figure()
        plt.plot(args.focuslist, args.fwhmlist, 'o')
        plt.xlabel("FOCUS Demand [mm foc plane]")
        plt.ylabel("FWHM (Pixels")
        plt.xlim([-3.6, 3.6])
        plt.ylim([0, 30])

    focus_curve_fit(args.focuslist, args.fwhmlist, polyfit, plot=args.makepng)
    p, rms = focus_curve_fit(args.focuslist, args.fwhmlist, sqrtfit, plot=args.makepng)

    deltafocus = rms[1]
    if args.makepng:
        if math.isfinite(deltafocus):
            plt.axvline(x=p[1], label="best focus sqrt")
        plt.legend()
        plt.title("Sqrt best focus found at {:5.2f} +/- {:5.2f}".format(p[1], deltafocus) if math.isfinite(
            deltafocus) else "Fit failed")
        plt.savefig("{}".format(args.pngname))

    errorstring = None
    if not math.isfinite(deltafocus):
        errorstring = "fit did not converge"

    if deltafocus > 0.25:
        errorstring = "focus fit is too noisy"


    if (p[3] >0.99):
        errorstring = "Curvature of focus curve is suspicious"

    returnpackage = {'fitok': True if errorstring is None else False,
                     'fit_seeing': round (p[0],2),
                     'fit_focus': round (p[1],2),
                     'fit_slope': round (p[2],2),
                     'fit_exponent': round(p[3],2),
                     'fit_rms': round (deltafocus,2),
                     'errormsg': errorstring}

    # TODO: Eventually return json from a web query. So far, we dump to stdout.
    print(json.dumps(returnpackage))
    return returnpackage


if __name__ == '__main__':
    main()
