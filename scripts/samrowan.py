class SamRowan():
    def __init__(self, width, height):
        print("Instantiating")
        self.locations, number_of_brick = self.generate_simple_wall(width, height)
        print("Generated Wall")
        self.pointer = 0
        self.h = height
        self.n = width

    def get_next_goal_loc(self): #TODO DEAL WITH OVERFLOW CASE
        loc = self.locations[self.pointer]
        self.pointer += 1
        return loc

    def generate_simple_wall(self, width=5, height=4): #COPY PASTE SAMS FUNCTINO IN HERE AND RETURN THE DESIRED VALUE

        xpickup=0.5
        ypickup=0.5
        xpicktheta=0
        ypicktheta=0
        zpicktheta=0

        if ypickup >= 0:
            xstart = -0.5
            ystart = -0.5
        else:
            xstart = -0.5
            ystart = 0.5

        zstart=0.2 #add a small offset
        xtheta= 3.14 #THIS MEANS THE GRIPPER WILL BE FACING downward
        ytheta=0
        ztheta= 3.14/4 #AT THIS VALUE THE GRIPPER IS straight with respect to base

        blength = 0.2+0.005                                                       #geometries of the brick
        bwidth = 0.09+0.005
        bheight = 0.062

        bstart=[xstart,ystart,zstart,xtheta,ytheta,ztheta]     #first brick position mirrors position of where we place the bricks
        pos_final = []

        n = 1

        xnos = 0
        znos = 0

        # input_nos = input()
        input_width = width #Pass in from class variable
        wall_width = int(input_width)

        # input_height = input()
        input_height = height #preset for now
        wall_height = int(input_height)

        brick_number = wall_width*wall_height

        for i in range(0, brick_number):

            pos_final.append([round(bstart[0]+xnos*blength, 3),bstart[1],round(bstart[2]+znos*bheight, 3),bstart[3],bstart[4],bstart[5]]) #edit this so the alignment is always correct

            if xnos < wall_width-1:  #No idea why -1 is needed here but it does not work without
                xnos+=1
            else:
                xnos=0
                znos+=1

        print(pos_final)

        return pos_final, brick_number
