import sys
import cv2
import numpy as np
from filter_img import *
from slope import *


def find_and_narrow_down_lines(img, dis_factor):
	# cvt to gray if not already
	img_gray = img
	#img_gray = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
	#img_gray = cv2.cvtColor(img_gray, cv2.COLOR_BGR2GRAY)
	cv2.imshow("gray", img_gray)
	
	# blur img
	img_blur = cv2.bilateralFilter(img_gray, 9, 75, 75)

	# run canny from blur
	img_cannyblur = cv2.Canny(img_blur, 50,150, apertureSize=3)
	cv2.imshow("blur", img_cannyblur)

	# run canny from gray (no blur)
	img_canny = cv2.Canny(img_gray, 50,150, apertureSize=3)
	cv2.imshow("canny", img_canny)

	# find lines in  x1/y1/x2/y2
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

	# put coordnates into list
	print("start x1_list: " + str(x1_list))
	# check for and delete lines that are similar (start and end are very close)
	counter = 0
	for frist_coor in x1_list:
		# print("counter: " + str(counter))
		# print("current frist_coor: " + str(frist_coor))
		#print("current x1_list: " + str(x1_list))
		for second_coor in x1_list:
			if counter <= len(x1_list):
				# print("current second_coor: " + str(second_coor))
				# print("counter: " + str(counter) + "; len(x1_list): " + str(len(x1_list)))
				#print("comparing " + str(frist_coor) + " with " + str(second_coor))
				if abs(frist_coor - second_coor) <= dis_factor and abs(frist_coor - second_coor) != 0: 
					del x1_list[counter]
					del y1_list[counter]
					del x2_list[counter]
					del y2_list[counter]
					#print("Deleted " + str(frist_coor) + " because " + str(frist_coor) + " - " + str(second_coor) + " is equal to " + str(frist_coor - second_coor))
				#else: 
					#print("Did not delete " + str(frist_coor) + " because " + str(frist_coor) + " - " + str(second_coor) + " is equal to " + str(frist_coor - second_coor))
					
			counter = counter + 1
		counter = 0
	
	# print final list of coordantes without repeats
	print("final x1_list without repeats: " + str(x1_list))
	cv2.imshow("orig_img", orig_img)

	
	return(len(x1_list), orig_len, img, x1_list, y1_list, x2_list, y2_list)

def find_poles(x1_list, y1_list, x2_list, y2_list):
	# store pole locs in x1/y1/x2/y2 order each in own list
	first_pole = [] 
	second_pole = [] 
	counter = 0
	found = False

	for line in range(len(x1_list)):
		if abs(x1_list[counter] - x2_list[counter]) < 15: # essentially if the line is verticle (or close to it)
			if found == False: # counter just counts to see if one pole has already been found
				first_pole.append(x1_list[counter])
				first_pole.append(y1_list[counter])
				first_pole.append(x2_list[counter])
				first_pole.append(y2_list[counter])

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

	print("first_pole: " + str(first_pole))
	print("second_pole: " + str(second_pole))
	return(first_pole, second_pole, x1_list, y1_list, x2_list, y2_list)

def check_reflection(first_pole, second_pole):
	# check for reflection
	reflection = []
	if first_pole != [] and second_pole != []: # if both poles have been found
		if abs(first_pole[0] - second_pole[0]) < 50: # check to see if x1 coord of each line are close, if they are, it is likely detecting a reflection
			# figure out which side of the pole is up
			if first_pole[1] < first_pole[3]: # not greater than because pixel (0,0) is at the top left
				first_y = first_pole[1]
			else:
				first_y = first_pole[3]

			if second_pole[1] < second_pole[3]:
				second_y = second_pole[1]
			else:
				second_y = second_pole[3]

			# redefine poles/reflection
			if first_y < second_y:
				reflection = first_pole
				first_pole = second_pole
				second_pole = []
			else:
				reflection = second_pole
				second_pole = []
	else: 
		print("No reflection without both poles found")

	return(first_pole, second_pole, reflection)

def find_horizontal(x1_list, y1_list, x2_list, y2_list, refined_slopes, first_pole, second_pole):
	horizontal = []
	
	if first_pole == [] or second_pole == []: # only works if both poles are found
		return(horizontal)

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

	if horizontal == []:
		return(horizontal)

	for line in range(len(x1_list)):
		if x1_list[line] == horizontal[0] and y1_list[line] == horizontal[1] and x2_list[line] == horizontal[2] and y2_list[line] == horizontal[3]: # check to make sure it is the same line
			del x1_list[line]
			del y1_list[line]
			del x2_list[line]
			del y2_list[line]
			return(horizontal)

def touch_up(first_pole, second_pole, horizontal, orig_img, confidence):
	ext_percent = 0
	# if one pole is found (under first_pole) make pole_missing = to 1, if both missing = 0 or if both found = 2
	if second_pole == []:
		pole_missing = 1
		if first_pole == []:
			pole_missing = pole_missing - 1
			return(orig_img, ext_percent, first_pole, second_pole)
	else:
		pole_missing = 2
		
		
	# figure out which x1/x2 // y1/y2 is on top
	if pole_missing > 0:
		if len(first_pole) != 0:
			if first_pole[0] < first_pole[2]:
				first1_top = True
			else:
				first1_top = False


		if pole_missing > 1: # 
			if len(second_pole) != 0:
				if second_pole[0] < second_pole[2]:
					second1_top = True
				else:
					second1_top = False

		# figure out which x1/x2 / y1/y2  of horizontal bar is on left	
		if len(horizontal) != 0:
			if horizontal[0] < horizontal[2]:
				horz1_left = True
			else:
				horz1_left = False
	else:
		sys.exit("Error: no poles")


	
	synth_horizontal = []
	if horizontal == []: # if no horizontal was found, predict one 
		if pole_missing > 0:
			if first1_top == True:
				synth_horizontal.append(first_pole[0])
				synth_horizontal.append(first_pole[1])
			else:
				synth_horizontal.append(first_pole[2])
				synth_horizontal.append(first_pole[3])

			if pole_missing > 1:
				if second1_top == True:
					synth_horizontal.append(second_pole[0])
					synth_horizontal.append(second_pole[1])
				else:
					synth_horizontal.append(second_pole[2])
					synth_horizontal.append(second_pole[3])

				print("synth_horizontal: " + str(synth_horizontal))
				cv2.line(orig_img, (synth_horizontal[0],synth_horizontal[1]),(synth_horizontal[2],synth_horizontal[3]),(177,237,157),2) # some lime green color

				ext_len = line_length(synth_horizontal)
				ext_percent = ext_len/ext_len
			else:
				ext_percent = 0
		else:
			ext_percent = 0

	elif len(horizontal) == 4:
		
		first_pole_horz_intersect = line_intersection(first_pole, horizontal)
		second_pole_horz_intersect = line_intersection(second_pole, horizontal)
		
		ext1 = []
		ext2 = []

		if horz1_left == True:
			ext1.append(first_pole_horz_intersect[0])
			ext1.append(first_pole_horz_intersect[1])
			ext1.append(horizontal[0])
			ext1.append(horizontal[1])

			ext2.append(second_pole_horz_intersect[0])
			ext2.append(second_pole_horz_intersect[1])
			ext2.append(horizontal[2])
			ext2.append(horizontal[3])
		else:
			ext1.append(first_pole_horz_intersect[0])
			ext1.append(first_pole_horz_intersect[1])
			ext1.append(horizontal[2])
			ext1.append(horizontal[3])

			ext2.append(second_pole_horz_intersect[0])
			ext2.append(second_pole_horz_intersect[1])
			ext2.append(horizontal[0])
			ext2.append(horizontal[1])

		if first1_top == True:
			first_pole[0] = ext1[0]
			first_pole[1] = ext1[1]
		else:
			first_pole[2] = ext1[0]
			first_pole[3] = ext1[1]
		
		if second1_top == True:
			second_pole[0] = ext2[0]
			second_pole[1] = ext2[1]
		else:
			second_pole[2] = ext2[0]
			second_pole[3] = ext2[1]

		cv2.line(orig_img, (ext1[0],ext1[1]),(ext1[2],ext1[3]),(177,237,157),2) # some lime green color
		cv2.line(orig_img, (ext2[0],ext2[1]),(ext2[2],ext2[3]),(177,237,157),2) # some lime green color

		ext1_len = line_length(ext1)
		ext2_len = line_length(ext2)

		total_ext_len = round(ext1_len + ext2_len)
		horz_len = round(line_length(horizontal))
		ext_percent = round(horz_len/total_ext_len)

	# add legend
	cv2.putText(orig_img, 'poles', (5,25), cv2.FONT_HERSHEY_SIMPLEX,  0.75, (0,0,255), 1, cv2.LINE_AA)
	if len(horizontal) == 4:
		cv2.putText(orig_img, 'horizontal har (detected)', (5,50), cv2.FONT_HERSHEY_SIMPLEX,  0.75, (255,0,0), 1, cv2.LINE_AA)
		cv2.putText(orig_img, 'horizontal bar fill', (5,75), cv2.FONT_HERSHEY_SIMPLEX,  0.75, (177,237,157), 1, cv2.LINE_AA)
	elif synth_horizontal != []:
		cv2.putText(orig_img, 'predicted horizontal bar', (5,50), cv2.FONT_HERSHEY_SIMPLEX,  0.75, (177,237,157), 1, cv2.LINE_AA)

	# add circles at corners
	if horizontal != []:
		cv2.circle(orig_img, (ext1[0], ext1[1]), 5, (255,255,255), 4)
		cv2.circle(orig_img, (ext2[0], ext2[1]), 5, (255,255,255), 4)
	elif synth_horizontal != []:
		cv2.circle(orig_img, (synth_horizontal[0], synth_horizontal[1]), 5, (255,255,255), 4)
		cv2.circle(orig_img, (synth_horizontal[2], synth_horizontal[3]), 5, (255,255,255), 4)

	return(orig_img, ext_percent, first_pole, second_pole)


def confidence(x1_list, y1_list, x2_list, y2_list, refined_slopes, first_pole, second_pole, ext_percent):

	if len(refined_slopes) == 3:
		confidence = 0.8
	elif len(refined_slopes) == 1 or len(refined_slopes) == 2:
		confidence = 0.5
	elif refined_slopes is None:
		confidence = 0
	elif len(refined_slopes) not in range(1, 3):
		confidence = (1/(len(refined_slopes) - 2))

	if second_pole == [] and first_pole != []: # if one pole is found
		confidence = confidence - 0.4
	elif first_pole == []: # if neither pole is found
		confidence = confidence - 0.8
	else: # if both poles are found
		confidence = confidence + 0.5

	if horizontal == []:
		confidence = confidence - 0.35
	elif len(horizontal) == 4:
		confidence = confidence + 0.35


	counter = 0
	for coord in horizontal:
		if counter == 0:
			if horizontal[counter] in x1_list:
				confidence = confidence + 0.2
		elif counter == 1:
			if horizontal[counter] in y1_list:
				confidence = confidence + 0.2
		elif counter == 2:
			if horizontal[counter] in x2_list:
				confidence = confidence + 0.2
		elif counter == 3:
			if horizontal[counter] in y2_list:
				confidence = confidence + 0.2
		counter = counter + 1

			
	if confidence > 1:
		confidence = 1
	elif confidence < 0:
		confidence = 0
	
	if ext_percent != None:
		confidence = confidence - (0.04 * ext_percent)

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
all_slopes = find_slopes_multiline(x1_list, y1_list, x2_list, y2_list)
print("original slopes: " + str(all_slopes))

# get rid of slopes that don't have a ~ paralell partner(s)
refined_slopes, x1_list, y1_list, x2_list, y2_list = elim_from_slope(all_slopes, x1_list, y1_list, x2_list, y2_list)
print("refined slopes: " + str(refined_slopes))

# find pole locations
first_pole, second_pole, x1_list, y1_list, x2_list, y2_list = find_poles(x1_list, y1_list, x2_list, y2_list) 
# list where the first two itemas are the pole coordnates and the third is a horizontal bar

# check for refelction
first_pole, second_pole, reflection = check_reflection(first_pole, second_pole)

if reflection == []:
	print("No reflection found")
else: 
	print("reflection: " + str(reflection))

# find horizontal bar
horizontal = find_horizontal(x1_list, y1_list, x2_list, y2_list, refined_slopes, first_pole, second_pole)
print("horizontal: " + str(horizontal))
cv2.imshow("orig_img", orig_img)

""" SHOWS ROUGH DETECTION
# add lines to image
if first_pole != []:
	cv2.line(orig_img, (first_pole[0],first_pole[1]),(first_pole[2],first_pole[3]),(0,0,255),2) # red

if second_pole != []:
	cv2.line(orig_img, (second_pole[0],second_pole[1]),(second_pole[2],second_pole[3]),(0,0,255),2) # red

if horizontal != []:
	cv2.line(orig_img, (horizontal[0],horizontal[1]),(horizontal[2],horizontal[3]),(255,0,0),2) # blue

cv2.imshow("rough detection", orig_img)
"""
final, ext_percent, first_pole, second_pole = touch_up(first_pole, second_pole, horizontal, orig_img, confidence)

# add lines to image # FIS THIS NEW IMG VARIABLE
if first_pole != []:
	cv2.line(final, (first_pole[0],first_pole[1]),(first_pole[2],first_pole[3]),(0,0,255),2) # red

if second_pole != []:
	cv2.line(final, (second_pole[0],second_pole[1]),(second_pole[2],second_pole[3]),(0,0,255),2) # red

if horizontal != []:
	cv2.line(final, (horizontal[0],horizontal[1]),(horizontal[2],horizontal[3]),(255,0,0),2) # blue


# determaine confidence
confidence = confidence(x1_list, y1_list, x2_list, y2_list, refined_slopes, first_pole, second_pole, ext_percent)

cv2.imshow("final detection - " + str(confidence), final)

cv2.waitKey(0)
cv2.destroyAllWindows()
