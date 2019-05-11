import subprocess as subp
import json
from delayed_assert import expect, assert_expectations

testset = [{'focuslist': "-2.0 -1.5 -1.0 -0.5 0.0 0.5 1.0 1.5 2.0",
            'fwhmlist': "3.6 3.57 3.74 4.21 5.34 5.89 7.1 8.26 9.46",
            'expect_fitok': True,
            'expect_bestfocus': -1.6},

           {'focuslist': " 2.0 1.5 1.0 0.5 0.0 -0.5 -1.0 -1.5 -2.0",
            'fwhmlist': "8.1301 5.88946 3.55935 2.20952 1.33816 1.74272 3.36874 5.66773 7.77222",
            'expect_fitok': True,
            'expect_bestfocus': 0.0},
            #using mean values of largfe defocus
           {'focuslist': " 2.0 1.5 1.0 0.5 0.0 -0.5 -1.0 -1.5 -2.0",
            'fwhmlist': "17.7 16.2 14.8 10.4 7.7 5.5 3.3 2.0 1.6",
            'expect_fitok': True,
            'expect_bestfocus': -1.8},

             #using median values fo large defocus
           {'focuslist': " 2.0 1.5 1.0 0.5 0.0 -0.5 -1.0 -1.5 -2.0",
            'fwhmlist': "19.67562 17.3883 14.77033 10.54968 7.65941 5.25539 3.15868 1.77384 1.39651",
            'expect_fitok': True,
            'expect_bestfocus': -1.8},

            # example with fwhm derived from Daniels tools.
           {'focuslist': "-3.5 -2.5 -1.5 -0.5 0.5 1.5 2.5 3.5",
            'fwhmlist': "4.19 3.3 3.5 4.98 7.18 9.46 12.32 14.81",
            'expect_fitok': True,
            'expect_bestfocus': -2.17},

           {'focuslist': "3.5 2.5 1.5 0.5 -0.5 -1.5 -2.5 -3.5",
            'fwhmlist': "16.38468 9.28154 4.45016 2.07726 1.75828 6.0684 10.92312 12.24961",
            'expect_fitok': True,
            'expect_bestfocus': 0},

           {'focuslist': "3.5 2.5 1.5 0.5 -0.5 -1.5 -2.5 -3.5",
            'fwhmlist': "28.05468 23.21941 15.63002 8.9081 4.55519 1.97612 1.74272 5.5627",
            'expect_fitok': True,
            'expect_bestfocus': -2},


           ]

def curvaturefit(testset, iter= None):

    command = './venv/bin/python lcofocuscurvefit/curvefit.py --focuslist {} --fwhmlist {}'.format(testset['focuslist'], testset['fwhmlist'])
    if iter is not None:
        command = command + " --makepng --pngname focus_{}.png".format (iter)
    try:
        results = subp.check_output([x for x in command.split()])
    except:
        pass

    results = json.loads(results)
    expect ( results['fitok'] == testset['expect_fitok'])


    if results['fitok']:
        expect (abs(results['fit_focus'] - testset['expect_bestfocus']) < 0.15, "example Nr {}".format (iter))


def test_curvaturefit():
    iter = 1
    for test in testset:
        curvaturefit(test, iter)
        iter = iter + 1
    assert_expectations()



