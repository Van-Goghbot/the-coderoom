import math
import bezier_conversion

class Coordinate:
	'''
	Allows for a more readable and intuative usage of the output of this script.
	Is a representation of the pose of a brick on the table.
	'''
	def __init__(self, x, y, rot):
		self.x = x
		self.y = y
		self.rot = rot

	def __repr__(self):
		'''Displays all the attributes in one line.'''
		return(str(self.x) + " " + str(self.y) + " " + str(self.rot))

def create_path(start_x, start_y, start_rot, end_x, end_y, end_rot, handle_influence):
	'''
	Takes the start and end poses specified and interpolates a curved path between them
	using a Bezier. 
	
	The handle_influence parameter allows you to control how "curvy" the path is,
	at 100 it's a very pronounced curve and at 0 its basically a straight line.
	
	This is helpful when using this function with an inverse kinematics solver, as
	this function can be recalled with a smaller and smaller value of handle_influence
	until the inverse kinematics can be solved.
	'''
	
	# Variables to to with the starting brick's pose
	angle_1 = start_rot
	x1, y1 = (start_x, start_y)
	
	# Variables to to with the end brick's pose
	angle_2 = end_rot
	x2, y2 = (end_x, end_y)

	# Using trignometry to caclulate the location of the Bezier handles
	length = handle_influence
	handle_1_dx = length * math.cos(angle_1)
	handle_1_dy = length * math.sin(angle_1)

	handle_2_dx = length * math.cos(angle_2)
	handle_2_dy = length * math.sin(angle_2)

	P0_x = x1
	P0_y = y1

	P1_x = x1 + (handle_1_dx/2)
	P1_y = y1 + (handle_1_dy/2)

	P2_x = x2 - (handle_2_dx/2)
	P2_y = y2 - (handle_2_dy/2)

	P3_x = x2
	P3_y = y2
	
	# Converting the coordinate values calculated into the XML string fomat which the Bezier class can interpret
	bezier_string = "M" + str(P0_x) + "," + str(P0_y) + "C" + str(P1_x) + "," + str(P1_y) + "," + str(P2_x) + "," + str(P2_y) + "," + str(P3_x) + "," + str(P3_y)
	brick_path = bezier_conversion.Bezier(bezier_string)
	
	# Approximating the length using a resolution of 150 points
	# This was found experimentally to be a good comprimise
	# Between running time and accuracy
	brick_path.length_approximation(150.0) # The larger this number the higher the accuracy but the slower the running time

	# How far either side of a point to check when calculating tangents
	# t has nothing to do with time but instead refers to the 
	# t value which is passed into the bezier functions
	dt = 0.01

	# 14 was our ideal spacing value, however the path generated
	# is unlikely to be an exact multiple of 14
	# so it is used to calculate how many bricks will fit
	# along the path, and then this brick number is used
	# to calculate the spacing which will result in an even
	# distribution of bricks
	spacing = 14
	bricks = int(math.floor(brick_path.length/spacing))
	spacing = brick_path.length/bricks

	brick_poses = []
	#print(brick_path.t_map)

	for i in range(bricks+1):
		try:
			# the t_map only contains distances to 3 decimal places
			# so the spacing needs to be rounded to 3d.p before
			# being used as a key
			
			# the t_map looks up a distance and returns the closest
			# computed t value to that distance
			t = brick_path.t_map[round(i*spacing,3)]
		except KeyError:
			# the full length of the path never gets added to the dictionary
			# so this handles the exception that occurs when the full length
			# is looked up
			t = 1
		
		x = brick_path.B_x(t)
		y = brick_path.B_y(t)
		
		# scaling and translations are required due to the different origins
		# and units of the Bezier and the Robot
		x = (x - 60) / 100
		y = (- y + 120) / 100 - 0.1
		
		# this bit of code calculates the angle which is tangent to the
		# curve by looking a little bit either side of the point
		# this ensures a domino path where they'll be able to knock
		# each other over in the desired way
		dy = brick_path.B_y(t + dt) - brick_path.B_y(t - dt)
		dx = brick_path.B_x(t + dt) - brick_path.B_x(t - dt)
		angle = math.atan2(dy,dx)
		
		# creates a list of all the brick posed calculated
		new_pose = Coordinate(x, y, angle)
		brick_poses.append(new_pose)
	return brick_poses


