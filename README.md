# Sand Table Image Path Optimization using Douglas Peucker Algorithm

This README describes how to implement the Douglas Peucker algorithm to optimize path lengths for drawing images on a sand table. Optimizing path lengths reduces drawing time and improves the overall efficiency of the sand table's operation.  Using the sandtable, it seemed that certain patterns produced a lot of noise while drawing ... this seemed to be due to the ball just moving back and forth, so I wondered if we could trim pattern to only include "meaningful" segments, i.e., those that produce a noticable pattern.   My first thought was that we could look at how far the ball moved and if it wasn't a significant value (e.g. .1% of the size of the table), we could drop that segment.  My son Nick Odell suggested the Douglas-Peucker algorithm.

# Introduction

Sand tables are devices that use a ball bearing or similar object to draw images in a bed of sand. The images are created by moving the ball bearing along a predefined path. The Douglas Peucker algorithm is a technique used to simplify polygonal curves by reducing the number of points in the curve. This algorithm can be applied to the paths used to draw images on a sand table, resulting in shorter, more efficient paths.

The sand table is from the [Dune Weaver project](https://makerworld.com/en/models/841332-dune-weaver-a-3d-printed-kinetic-sand-table#profileId-787553)  It's made from two walnut trays making a nice resonant cavity at certain frequencies.   

![image](https://github.com/user-attachments/assets/d4f38014-387b-47be-83f7-38daa333f1c8)

# Algorithm Overview

The Douglas Peucker algorithm works by iteratively removing points from a curve that are within a certain tolerance of a line segment connecting two other points on the curve. The algorithm starts with the line segment connecting the first and last points of the curve. If all the intermediate points are within the tolerance, they are removed. If any point is outside the tolerance, the curve is split at that point, and the algorithm is recursively applied to the two resulting sub-curves.

# Implementation

Here is a basic implementation outline of the algorithm:

1. **Input:** A list of points representing the path to be optimized and a tolerance value.  
2. **Base Case:** If the list of points contains only two points, return the list.  
3. **Find Farthest Point:** Find the point in the list that is farthest from the line segment connecting the first and last points.  
4. **Check Tolerance:** If the distance from the farthest point to the line segment is less than the tolerance, remove all intermediate points and return the list containing only the first and last points.  
5. **Recursive Call:** If the distance is greater than the tolerance, split the list at the farthest point and recursively apply the algorithm to the two sub-lists.  
6. **Output:** A simplified list of points representing the optimized path.

# Usage Example

Assume you have a list of points defining a path for an image:path\_points \= \[(0, 0), (1, 2), (2, 1), (3, 3), (4, 1), (5, 2), (6, 0)\]

tolerance \= 1.0  \# Adjust as needed

You would apply the Douglas Peucker algorithm to `path_points` with the specified `tolerance` to obtain the optimized path.

```
PS C:\Projects\trimTHR> python trimTHR.py                                                                                    
usage: trimTHR.py [-h] [--input_path INPUT_PATH] [--output_dir OUTPUT_DIR] [--threshold_percent THRESHOLD_PERCENT] [--diameter DIAMETER]
                  [--n_buckets N_BUCKETS] [--epsilon EPSILON] [--max_deviation MAX_DEVIATION] [--use_douglas_peucker] [--show_histogram]
                  [--top_n_deviations TOP_N_DEVIATIONS] [--display_time DISPLAY_TIME]

Process and trim path segments.

options:
  -h, --help            show this help message and exit
  --input_path INPUT_PATH
                        Input file or directory containing files to process
  --output_dir OUTPUT_DIR
                        Output directory to save processed files
  --threshold_percent THRESHOLD_PERCENT
                        Threshold percent for filtering segments (default: 0.5)
  --diameter DIAMETER   Diameter of the circle (default: 40)
  --n_buckets N_BUCKETS
                        Number of buckets for the histogram (default: 10)
  --epsilon EPSILON     Epsilon value for Douglas-Peucker algorithm. A reasonable range is 0.1 to 10.0. It determines the maximum distance a point can deviate  
                        from the line before it is considered significant.
  --max_deviation MAX_DEVIATION
                        Maximum deviation allowed for a point to be removed (default: infinity)
  --use_douglas_peucker
                        Use Douglas-Peucker algorithm for trimming segments (default: True)
  --show_histogram      Show histogram of path lengths
  --top_n_deviations TOP_N_DEVIATIONS
                        Number of top deviations to display on the processed graph (default: 0)
  --display_time DISPLAY_TIME
                        Time to display each plot in seconds (default: 5.0)

```
# Benefits

* **Reduced Drawing Time:** Shorter paths require less time to draw (possibly? But the path length doesn't differ that much.
* **Improved Efficiency:** Less movement of the sand table mechanism leads to reduced wear and tear (maybe?) 
* **Less noise:** Hopefully?  This is what started my investigation

# Current Status

So far the results seem promising.  This is the file that I originally noticed the noise in:

![image](https://github.com/user-attachments/assets/208749ad-c2c7-4da3-b520-f9b421086435)

This is using the threshold algorithm (at .5%) The number of segments has been reduced considerable, without any  change in the pattern.   The third graph shows the areas of highest deviance from the original image.

Using Douglas-Peucker with an epsilon of .01 has an even greater reduction:

![image](https://github.com/user-attachments/assets/05e60701-75e4-4300-a07e-3e5733c3a90b)

producing a reduction in segments from 33465 to 3878.

(Some of the patterns seem to get completely distorted with the Douglas-Peucker, and I've had errors where the maximum depth of the recursion has been exceeded.   I'm also curious as to why the errors are concentrated in certain areas.)

# Considerations

* **Tolerance Value:** The tolerance value determines the level of simplification. A smaller tolerance will result in a path that is closer to the original, while a larger tolerance will result in a more simplified path.  
* **Complexity:** The Douglas Peucker algorithm has a time complexity of O(n log n) in the average case, where n is the number of points in the path.
