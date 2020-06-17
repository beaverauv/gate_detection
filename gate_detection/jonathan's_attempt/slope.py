from math import log10, floor

def find_slopes(x1, y1, x2, y2):
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

def elim_from_slope(slopes, x1_list, y1_list, x2_list, y2_list):
    counter = 0
    print("total slopes: " + str(slopes))
    for slope in range(len(slopes)): # CHANGE THIS TO range(len(slopes)) SO IT GETS EVERY ITEM IN LIST
        print("asessing: " + str(slopes[counter]) + " at index " + str(counter))
        print(slopes)
        if abs(slopes[counter]) <= 10:
            if abs(slopes[counter]) == float('inf'):
                print(str(slopes[counter]) + " is inf")
                counter = counter + 1
                break
            else:
                print("deleting " + str(slopes[counter]) + " at index " + str(counter)+ " because its too big/small")
                del slopes[counter]
                del x1_list[counter]
                del y1_list[counter]
                del x2_list[counter]
                del y2_list[counter]
        else: 
            counter = counter + 1
            print("counter incremented")


    """

    def elim_from_slope(slopes, x1_list, y1_list, x2_list, y2_list):
        counter = 0
        print("total slopes: " + str(slopes))
        for slope in slopes: # CHANGE THIS TO range(len(slopes)) SO IT GETS EVERY ITEM IN LIST
            print("asessing: " + str(slope) + " at index " + str(counter))
            print(slopes)
            if abs(slope) <= 10:
                if abs(slope) == float('inf'):
                    print(str(slope) + " is inf")
                    counter = counter + 1
                    break
                else:
                    print("deleting " + str(slope) + " at index " + str(counter)+ " because its too big/small")
                    del slopes[counter]
                    del x1_list[counter]
                    del y1_list[counter]
                    del x2_list[counter]
                    del y2_list[counter]
            else: 
                counter = counter + 1
                print("counter incremented")

    """
                
        
    """
    for first_slope in slopes:
        counter = 0
        for second_slope in slopes:
            if counter <= len(slopes):
                if abs(first_slope - second_slope) > 1:
                    del slopes[counter]
                    del x1_list[counter]
                    del y1_list[counter]
                    del x2_list[counter]
                    del y2_list[counter]
                counter = counter + 1
    """

    return(slopes, x1_list, y1_list, x2_list, y2_list)
