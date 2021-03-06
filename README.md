# focuscurvefitter

This package emerged from the 2019 focus project.

Experimental implementation of an alternative way to fit a focus curve in focus sequences.

Currently, focus seuqences at LCO telescopes are modeled via a parabola. The new algorithm implemented
here is adding seeing and defocus in quadrature, which is a better model as it correctly describes
the linear increase of image size for large defocus. 

This package is tailored towards an experimental deployment at site via installation in the eng home directory ono the
 pubsub machine, and then being called via a system call from a sequencer script. 
 
The package is designed to be easilly plug into a a web service. 
 frame work or similar.
 
 
Usage
====
<pre>
python lcofocuscurvefit/curvefit.py -h
usage: curvefit.py [-h] [--focuslist FOCUSLIST [FOCUSLIST ...]]
                   [--fwhmlist FWHMLIST [FWHMLIST ...]] [--makepng]
                   [--pngname PNGNAME]

Fit a focus curve to an autofocus sequence result.

optional arguments:
  -h, --help            show this help message and exit
  --focuslist FOCUSLIST [FOCUSLIST ...]
  --fwhmlist FWHMLIST [FWHMLIST ...]
  --makepng             make a nice plot
  --pngname PNGNAME     Name of output plot file
</pre>


E.g.:
<pre>
python lcofocuscurvefit/curvefit.py --focuslist -2 -1.5 -1 -0.5 -0 0.5 1 1.5 2  --fwhmlist 3.6 3.57 3.74 4.21 5.34 5.89 7.1 8.26 9.46 --makepng
{"fitok": true, "fit_seeing": 3.4802276117800797, "fit_focus": -1.5252690391150956, "fit_slope": 2.472104038485136, "fit_rms": 0.11436685187985646}
</pre>


Installation & testing:
==
Clone git repository, and enter directoy.
```
git clone ....
cd ...

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

pytest
```

Now you can look at example fits, called focus_?.png
