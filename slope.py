import math
import numpy as np

def find_slopes_multiline(x1, y1, x2, y2): # where each x1/y1/x2/y2 are parallel lists
    counter = 0
    slopes = []
    for line in range(len(x1)):
        rise = y2[counter] - y1[counter]
        run = x2[counter] - x1[counter]

        unrounded = (rise / run)
        rounded = round(unrounded, 3)
        counter = counter + 1
        slopes.append(rounded)
    
    return(slopes)

def find_slope_singleline(line): # where a is a list of four elements (x1/y1/x2/y2) 
    rise = line[1] - line[3]
    run = line[0] - line[2]
    slope = rise/run

    return(slope)

def elim_from_slope(slopes, x1_list, y1_list, x2_list, y2_list, debug):
    counter = 0
    if debug == True:
        print("total slopes: " + str(slopes))
    for slope in range(len(slopes)):
        if abs(slopes[counter]) in range(1, 10):
            if abs(slopes[counter]) == float('inf'):
                counter = counter + 1
                break
            else:
                del slopes[counter]
                del x1_list[counter]
                del y1_list[counter]
                del x2_list[counter]
                del y2_list[counter]
        else: 
            counter = counter + 1

    return(slopes, x1_list, y1_list, x2_list, y2_list)

def line_intersection(one_list, two_list, debug):
    intersect = [] # at the end it should be (x,y)
    # calculate slopes
    one_slope = find_slope_singleline(one_list)
    two_slope = find_slope_singleline(two_list)

    if math.isinf(float(one_slope)):
        one_slope = 100000 # because it can not compute inf but a big number is fine too

    if math.isinf(float(two_slope)):
        two_slope = 100000 # because it can not compute inf but a big number is fine too


    # calculate y-intercepts
    one_b=one_list[1]-one_slope*one_list[0]
    two_b=two_list[1]-two_slope*two_list[0]

    # calculate line intersectipn
    sum_slope = one_slope - two_slope
    x_intersect = (two_b - one_b) / sum_slope
    y_intersect = (two_slope * x_intersect) + two_b

    if debug == True:
        print("one_slope:" + str(one_slope))
        print("two_slope:" + str(two_slope))
        print("one_b:" + str(one_b))
        print("two_b:" + str(two_b))
        print("sum_slope:" + str(sum_slope))
        print("x_intersect:" + str(x_intersect))
        print("y_intersect:" + str(y_intersect))

    x_intersect = int(x_intersect)
    y_intersect = int(y_intersect)
    
    # add to intersect list
    intersect.append(x_intersect)
    intersect.append(y_intersect)

    return(intersect)

def line_length(line): # line must be list of four elements: x1/y1/x2/y2
    
    x_val = line[2] - line[0]
    y_val = line[3] - line[1]

    length = np.sqrt(np.square(x_val) + np.square(y_val))

    return(length)

def slope_to_rad(slope):
    rad = np.arctan(slope)
    return(rad)

def rad_to_slope(rad):
    slope = np.tan(rad)
    return(slope)
