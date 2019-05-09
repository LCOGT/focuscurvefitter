import subprocess as subp
import math
import json

testset1 = {'focuslist': "-2.0 -1.5 -1.0 -0.5 0.0 0.5 1.0 1.5 2.0",
            'fwhmlist': "3.6 3.57 3.74 4.21 5.34 5.89 7.1 8.26 9.46",
            'expect_fitok': True,
            'expect_bestfocus': -1.53}


def curvaturefit(testset):
    results = None
    try:
        results = subp.check_output(['python',
                                     '/home/dharbeck/Software/lcofocuscurvefit/curvefit.py',
                                     '--focuslist', '{}'.format(testset['focuslist']),
                                     '--fwhmlist', '{}'.format(testset['fwhmlist'])], shell=True)
    except:
        print ("Error!")

    print(results)
    results = json.loads(results)
    print(results)

curvaturefit (testset1)