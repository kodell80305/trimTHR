# Sand Table Image Path Optimization using Douglas-Peucker Algorithm

Using the sandtable, it seemed that certain patterns produced a lot of noise while drawing ... this seemed to be due to the ball just moving back and forth, so I wondered if we could trim pattern to only include "meaningful" segments, i.e., those that produce a noticable pattern.   My first thought was that we could look at how far the ball moved and if it wasn't a significant value (e.g. .1% of the size of the table), we could drop that segment.  My son Nick Odell suggested the Douglas-Peucker algorithm.

This was/is an experiment in using AI/Python for data analysis and visualisation.  I spend about 8 hours and had Copilot write all of the code here.  I fixed a bug where the path optimization was being done in polar coordianates ... the code used for the Douglas Peucker algorithm was expecting cartesian so the AI is a combination of being brilliant in some domains and missing what seems obvious in other (intitially I hit an issue that I couldn't understand the results I was getting - it turned out that the Copilot codes was assuming the theta rho file was in degrees - it seemed so obvious to me that a theta rho file would be in radians, and the AI that I didn't think that was something I would need to specify)

Using the sandtable, it seemed that certain patterns produced a lot of noise while drawing ... this seemed to be due to the ball just moving back and forth, so I wondered if we could trim pattern to only include "meaningful" segments, i.e., those that produce a noticable pattern.   My first thought was that we could look at how far the ball moved and if it wasn't a significant value (e.g. .1% of the size of the table), we could drop that segment.  My son Nick Odell suggested the Douglas-Peucker algorithm.

Anyway, at this point I would say that it does reduce the number of points significantly, but most of these points don't change the path at all - i.e. they're interpolated points that lie directly on the path.  They don't add any information, but we're not really worried about data storage ... the entire database of patterns is only 2MB.  

Next round I'll tweek it do ignore points that removing won't change the path.

I've put this aside for now, but there is so much more to explore and the combination of Python and AI generated is incredible.  The Douglas Peuker algorithm actually works pretty well at cutting down the number of segments, but I'm not sure how much value that has ... I would like to see if it has any effect on reducing artifacts (noise, sections where short, unproductive line segments exist) on algorithically generated or image capture paths.

https://www.youtube.com/watch?v=spUNpyF58BY

The Fourier transform is an interesting idea ... I think you would need to transform the THR files into a meaning time series first (i.e., each line in the THR file doesn't represent a fixed time interval).   On the actual device, a Raspberry PI reads the next THR coordinates, converts to a scaled "motor space" - i.e. number of steps for each stepper motor to get to the next point and sends that to the dlc32.  The dlc32 will divide these into segments,  essentially trying to send those out with some rules about the maxium rate/maximum change (velocity/acceleration) for each stepper (there's a little bit more complexity here than I'm describing)
