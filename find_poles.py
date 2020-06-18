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

def find_poles(x1_list, y1_list, x2_list, y2_list):
	# store pole locs in x1/y1/x2/y2 order each in own list
	frist_pole = [] 
	second_pole = [] 
	counter = 0
	found = False

	for line in range(len(x1_list)):
		if abs(x1_list[counter] - x2_list[counter]) < 15: # essentially if the line is verticle (or close to it)
			if found == False: # counter just counts to see if one pole has already been found
				frist_pole.append(x1_list[counter])
				frist_pole.append(y1_list[counter])
				frist_pole.append(x2_list[counter])
				frist_pole.append(y2_list[counter])

				# delete from origional list
				del x1_list[counter]
				del y1_list[counter]
				del x2_list[counter]
				del y2_list[counter]

				found = True
				counter = counter - 1 # because list length has been shortened

			elif found == True:
				second_pole.append(x1_list[counter])
				second_pole.append(y1_list[counter])
				second_pole.append(x2_list[counter])
				second_pole.append(y2_list[counter])

				# delete from origional list
				del x1_list[counter]
				del y1_list[counter]
				del x2_list[counter]
				del y2_list[counter]

				counter = counter - 1 # because list length has been shortened
		counter = counter + 1

	print("one pole at: " + str(frist_pole))
	print("another pole at: " + str(second_pole))
	return(frist_pole, second_pole, x1_list, y1_list, x2_list, y2_list)


def find_horizontal(x1_list, y1_list, x2_list, y2_list, refined_slopes, first_pole, second_pole):
	if first_pole == [] or second_pole == []: # only works if both poles are found
		return(first_pole)

	print("x1_list: " + str(x1_list))
	print("x2_list: " + str(x2_list))
	
	for line in range(len(x1_list)): # since you don't know where the x1/x2 is in the image, this tests all options
		if abs(x1_list[line] - first_pole[0]) < 15 and abs(x1_list[line] - first_pole[0]) != 0:
			horizontal = [x1_list[line], y1_list[line], x2_list[line], y2_list[line]]
		elif abs(x1_list[line] - first_pole[2]) < 15 and abs(x1_list[line] - first_pole[2]) != 0:
			horizontal = [x1_list[line], y1_list[line], x2_list[line], y2_list[line]]
		elif abs(x2_list[line] - first_pole[0]) < 15 and abs(x2_list[line] - first_pole[0]) != 0:
			horizontal = [x1_list[line], y1_list[line], x2_list[line], y2_list[line]]
		elif abs(x2_list[line] - first_pole[2]) < 15 and abs(x2_list[line] - first_pole[2]) != 0:
			horizontal = [x1_list[line], y1_list[line], x2_list[line], y2_list[line]]
		else:
			if abs(x1_list[line] - second_pole[0]) < 15 and abs(x1_list[line] - second_pole[0]) != 0:
				horizontal = [x1_list[line], y1_list[line], x2_list[line], y2_list[line]]
			elif abs(x1_list[line] - second_pole[2]) < 15 and abs(x1_list[line] - second_pole[2]) != 0:
				horizontal = [x1_list[line], y1_list[line], x2_list[line], y2_list[line]]
			elif abs(x2_list[line] - second_pole[0]) < 15 and abs(x2_list[line] - second_pole[0]) != 0:
				horizontal = [x1_list[line], y1_list[line], x2_list[line], y2_list[line]]
			elif abs(x2_list[line] - second_pole[2]) < 15 and abs(x2_list[line] - second_pole[2]) != 0:
				horizontal = [x1_list[line], y1_list[line], x2_list[line], y2_list[line]]

	for line in range(len(x1_list)):
		if x1_list[line] == horizontal[0] and y1_list[line] == horizontal[1] and x2_list[line] == horizontal[2] and y2_list[line] == horizontal[3]: # check to make sure it is the same line
			del x1_list[line]
			del y1_list[line]
			del x2_list[line]
			del y2_list[line]
			return(horizontal)

def confidence(x1_list, refined_slopes, first_pole, second_pole):

	if len(refined_slopes) == 3:
		confidence = 0.8
	elif len(refined_slopes) == 1 or len(refined_slopes) == 2:
		confidence = 0.5
	elif refined_slopes is None:
		confidence = 0
	elif len(refined_slopes) not in range(1, 3):
		confidence = (1/(len(refined_slopes) - 2))

	if horizontal == True:
		confidence = confidence + 0.15
	elif horizontal == False:
		confidence = confidence - 0.15

	if confidence > 1:
		confidence = 1
	elif confidence < 0:
		confidence = 0

	confidence_percent = confidence * 100 # make percent

	confidence_percent = round(confidence_percent, 2) # round to the houndreths

	final_confidence = str(confidence_percent) + "%"

	return(final_confidence)


# make sure terminal line that calls this script has the right number of contents
if len(sys.argv) != 3:
		print("This test requires arguements: python test2.py [path_to_image (string)] max_distance_for_similar_lines(int)") # orig:  also had [debug (bool)]"
		print("Exiting...")
		sys.exit()

# sys.argv is a list ['this_file.py', 'img.jpg', max_distance_for_similar_lines(int)] should be the the items

img, orig_img = filter_img(sys.argv[1])
dis_factor = int(sys.argv[2])

num_poles, orig_len, img_w_lines, x1_list, y1_list, x2_list, y2_list = find_and_narrow_down_lines(img, dis_factor)
print("there were origionally " + str(orig_len) + " line(s) found.")
print("number of lines found (may overlap): " + str(num_poles))

# find all slopes
all_slopes = find_slopes(x1_list, y1_list, x2_list, y2_list)
print("original slopes: " + str(all_slopes))

# get rid of slopes that don't have a ~ paralell partner(s)
refined_slopes, x1_list, y1_list, x2_list, y2_list = elim_from_slope(all_slopes, x1_list, y1_list, x2_list, y2_list)
print("refined slopes: " + str(refined_slopes))

# find pole locations
first_pole, second_pole, x1_list, y1_list, x2_list, y2_list = find_poles(x1_list, y1_list, x2_list, y2_list) 
# list where the first two itemas are the pole coordnates and the third is a horizontal bar

# find horizontal bar
horizontal = find_horizontal(x1_list, y1_list, x2_list, y2_list, refined_slopes, first_pole, second_pole)
print(horizontal)

# determaine confidence
confidence = confidence(x1_list, refined_slopes, first_pole, second_pole)

# add lines to image
if first_pole != []:
	cv2.line(orig_img, (first_pole[0],first_pole[1]),(first_pole[2],first_pole[3]),(0,0,255),2)

if second_pole != []:
	cv2.line(orig_img, (second_pole[0],second_pole[1]),(second_pole[2],second_pole[3]),(0,0,255),2)

if horizontal != []:
	cv2.line(orig_img, (horizontal[0],horizontal[1]),(horizontal[2],horizontal[3]),(255,0,0),2)


cv2.imshow("detection - " + str(confidence), orig_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
