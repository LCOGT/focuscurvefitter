import argparse
import math
import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize
import json

_LIMIT_EXPONENT_U = 0.7
_MIN_NUMBER_OF_POINTS = 5

# This describes our model for a focus curve: Seeing and defocus add in quadrature.
sqrtfit = lambda x, seeing, bestfocus, slope, tweak: (seeing ** 2 + (slope * (x - bestfocus)) ** 2) ** tweak
polyfit = lambda x, p0, p1, p2: p2 * (x - p1) ** 2 + p0


def focus_curve_fit(xdata, ydata, func=sqrtfit):
    """
    Generic iterative fit with sigma rejection.

    :param xdata:
    :param ydata:
    :param func:
    :param plot:
    :return:
    """

    # TODO: Verification that we have enough points.

    # TODO: Boundaries and intial guess externally driven by context.
    initial_guess = [2, 0, 1, 0.6] if func == sqrtfit else None
    bounds = [[0, -3, 0, 0.5], [5, 3, 5, _LIMIT_EXPONENT_U]] if func == sqrtfit else [-math.inf, math.inf]

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

    return paramset, paramerrors


def overplot_fit(func, paramset):
    base = np.arange(-3.6, 3.6, 0.1)
    y = func(base, *paramset)
    plt.plot(base, y, "--", label="sqrt {:5.2f}".format(paramset[3]) if func == sqrtfit else "parabola")


def parseCommandLine():
    parser = argparse.ArgumentParser(
        description='Fit a focus curve to an autofocus sequence result.')
    parser.add_argument("--focuslist", nargs='+', type=float)
    parser.add_argument("--fwhmlist", nargs='+', type=float)
    parser.add_argument('--makepng', action='store_true',
                        help='make a nice plot')
    parser.add_argument("--pngname", default="focusplot.png", help="Name of output plot file")
    args = parser.parse_args()

    error_string = None
    if len(args.focuslist) != len(args.fwhmlist):
        error_string = "Argument error: fwhmlist and focuslist must have the same length"
    if len(args.focuslist) < 4:
        error_string = "Argument error: Not enough data pairs provided, minimum is {}".format(_MIN_NUMBER_OF_POINTS)

    args.focuslist = np.asarray(args.focuslist)
    args.fwhmlist = np.asarray(args.fwhmlist)

    if (np.isfinite(args.focuslist).sum() != len(args.focuslist)) or (
            np.isfinite(args.fwhmlist).sum() != len(args.fwhmlist)):
        error_string = "Input list are not finite numbers"
    return args, error_string


def makeprettyplot():
    # TODO: Move all the plotting stuff in here
    pass


def errorexit(error_string):
    '''
    Short cut emergency exist method
    '''

    return_package = {'fitok': False,
                      'errormsg': error_string}
    print(json.dumps(return_package))
    exit(0)


def main():
    args, error_string = parseCommandLine()

    if error_string is not None:
        errorexit(error_string)

    parabola_p, parabola_e = focus_curve_fit(args.focuslist, args.fwhmlist, polyfit)
    exponential_p, exponential_rms = focus_curve_fit(args.focuslist, args.fwhmlist, sqrtfit)

    deltafocus = exponential_rms[1]

    if not math.isfinite(deltafocus):
        error_string = "fit did not converge"
    if deltafocus > 0.25:
        error_string = "focus fit is too noisy"
    if abs(exponential_p[1]) > 2.5:
        error_string = "Focus offset too large to be credible."

    return_package = {'fitok': True if error_string is None else False,
                      'fit_seeing': round(exponential_p[0], 2),
                      'fit_focus': round(exponential_p[1], 2),
                      'fit_slope': round(exponential_p[2], 2),
                      'fit_exponent': round(exponential_p[3], 2),
                      'fit_rms': round(deltafocus, 2),
                      'errormsg': error_string}

    # TODO: Eventually return json from a web query. So far, we dump to stdout.
    print(json.dumps(return_package))

    if args.makepng:
        plt.figure()
        if math.isfinite(deltafocus):
            plt.axvline(x=exponential_p[1], label="best focus sqrt")
            plt.axes().axvspan(exponential_p[1] - deltafocus, exponential_p[1] + deltafocus, alpha=0.1, color='grey')
        plt.plot(args.focuslist, args.fwhmlist, 'o')
        plt.xlabel("FOCUS Demand [mm foc plane]")
        plt.ylabel("FWHM (Pixels")
        plt.xlim([-3.6, 3.6])
        plt.ylim([0, 30])
        overplot_fit(polyfit, parabola_p)
        overplot_fit(sqrtfit, exponential_p)
        plt.legend()
        plt.title("Sqrt best focus found at {:5.2f} +/- {:5.2f}".format(exponential_p[1], deltafocus) if math.isfinite(
            deltafocus) else "Fit failed")
        plt.savefig("{}".format(args.pngname))


    return return_package


if __name__ == '__main__':
    main()
