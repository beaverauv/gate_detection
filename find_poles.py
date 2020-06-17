import sys
import cv2
import numpy as np
from filter_img import *
from slope import *


def find_and_narrow_down_lines(img, dis_factor):
	# cvt to gray
	img_gray = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
	img_gray = cv2.cvtColor(img_gray, cv2.COLOR_BGR2GRAY)
	cv2.imshow("gray", img_gray)
	
	# blur img
	img_blur = cv2.bilateralFilter(img_gray, 9, 75, 75)

	# run canny from blur
	img_cannyblur = cv2.Canny(img_blur, 50,150, apertureSize=3)
	cv2.imshow("blur", img_cannyblur)

	# run canny from gray (no blur)
	img_canny = cv2.Canny(img_gray, 50,150, apertureSize=3)
	cv2.imshow("canny", img_canny)

	# find lines
	lines = cv2.HoughLinesP(img_canny, rho = 1, theta = 1*np.pi/180, threshold = 20, lines = 1, minLineLength = 100, maxLineGap = 15)

	# if no lines found
	if lines is None:
		cv2.imshow("detection", img)
		return("No lines detected")

	# make coordantes lists

	x1_list = []
	y1_list = []
	x2_list = []
	y2_list = []

	orig_len = len(lines)
	for x in range(0,len(lines)):
		for x1,y1,x2,y2 in lines[x]:
			x1_list.append(x1)
			y1_list.append(y1)
			x2_list.append(x2)
			y2_list.append(y2)
			
	

	
	# check for if there are more x1/y1/x2/y2 data points than others, not sure how this would happen but I'm sure it would cause problems if it did
	if len(x1_list) != len(y1_list) != len(x2_list) != len(y2_list):
		print("An error has occured regarding x y coordnates of the detected lines.")
		print("Exiting...")
		sys.exit()

	print("start x1_list: " + str(x1_list))
	# check for and delete lines that are similar (start and end are very close)
	counter = 0
	for frist_coor in x1_list:
		# print("counter: " + str(counter))
		# print("current frist_coor: " + str(frist_coor))
		print("current x1_list: " + str(x1_list))
		for second_coor in x1_list:
			if counter <= len(x1_list):
				# print("current second_coor: " + str(second_coor))
				# print("counter: " + str(counter) + "; len(x1_list): " + str(len(x1_list)))
				print("comparing " + str(frist_coor) + " with " + str(second_coor))
				if abs(frist_coor - second_coor) <= dis_factor and abs(frist_coor - second_coor) != 0: 
					del x1_list[counter]
					del y1_list[counter]
					del x2_list[counter]
					del y2_list[counter]
					print("Deleted " + str(frist_coor) + " because " + str(frist_coor) + " - " + str(second_coor) + " is equal to " + str(frist_coor - second_coor))
				else: 
					print("Did not delete " + str(frist_coor) + " because " + str(frist_coor) + " - " + str(second_coor) + " is equal to " + str(frist_coor - second_coor))
					
			counter = counter + 1
		counter = 0
	
	# print final list of coordantes without repeats
	print("final x1_list without repeats: " + str(x1_list))

	
	return(len(x1_list), orig_len, img, x1_list, y1_list, x2_list, y2_list)

def confidence(x1_list, refined_slopes):
	confidence = 1

	if len(refined_slopes) != 2:
		confidence = confidence - (1/(len(refined_slopes) - 2))
	elif refined_slopes is None:
		confidence = 0


	return(confidence)


# make sure terminal line that calls this script has the right number of contents
if len(sys.argv) != 3:
		print("This test requires arguements: python test2.py [path_to_image (string)] max_distance_for_similar_lines(int)") # orig:  also had [debug (bool)]"
		print("Exiting...")
		sys.exit()

# sys.argv is a list ['this_file.py', 'img.jpg'] should be the the items

img = filter_img(sys.argv[1])
dis_factor = int(sys.argv[2])

num_poles, orig_len, img_w_lines, x1_list, y1_list, x2_list, y2_list = find_and_narrow_down_lines(img, dis_factor)
print("there were origionally " + str(orig_len) + " line(s) found.")
print("number of lines found (may overlap): " + str(num_poles))

# find all slopes
all_slopes = find_slopes(x1_list, y1_list, x2_list, y2_list)
print("original slopes: " + str(all_slopes))

# get rid of slopes that don't have a paralell partner(s)
refined_slopes, x1_list, y1_list, x2_list, y2_list = elim_from_slope(all_slopes, x1_list, y1_list, x2_list, y2_list)
print("refined slopes: " + str(refined_slopes))

print(x1_list)

confidence = confidence(x1_list, refined_slopes)

# add lines to image
count = 0
for points in x1_list:
	cv2.line(img,(x1_list[count],y1_list[count]),(x2_list[count],y2_list[count]),(255,255,0),1)
	count = count + 1



cv2.imshow("detection - " + str(confidence), img)
cv2.waitKey(0)
cv2.destroyAllWindows()