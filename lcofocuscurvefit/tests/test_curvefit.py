import subprocess as subp
import json

testset = [{'focuslist': "-2.0 -1.5 -1.0 -0.5 0.0 0.5 1.0 1.5 2.0",
            'fwhmlist': "3.6 3.57 3.74 4.21 5.34 5.89 7.1 8.26 9.46",
            'expect_fitok': True,
            'expect_bestfocus': -1.53},
]

def curvaturefit(testset):
    command = './venv/bin/python lcofocuscurvefit/curvefit.py --focuslist {} --fwhmlist {}'.format(testset['focuslist'], testset['fwhmlist'])
    try:
        results = subp.check_output([x for x in command.split()])
    except:
        pass

    results = json.loads(results)
    assert results['fitok'] == testset['expect_fitok']
    if results['fitok']:
        assert abs(results['fit_focus'] - testset['expect_bestfocus']) < 0.1


def test_curvaturefit():
    for test in testset:
        curvaturefit(test)
