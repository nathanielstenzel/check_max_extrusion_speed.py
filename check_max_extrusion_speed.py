#!/usr/bin/python
#Written by Nathaniel J Stenzel on January 14, 2020
"""
This program will help you find out just how fast your filament gets pushed in a particular gcode file.
If you set print_speed in the parameter list, this program will instead tell you just how fast you could push it given x_speed, y_speed, print_speed and extrusion_speed.
"""
file_name = ""
import math,sys
line = ""
last_extrusion = last_x = last_y = extrusion = x = y = 0
max_movement_speed = max_extrusion_speed = 0 #start tracking the fastest later
print_speed = None
min_x = min_y = max_x = max_y = 0
x_speed = y_speed = extrusion_speed = move_speed = 999999
jerk = 0
params = {}
debug = False
for param in ["x_speed","y_speed","extrusion_speed","print_speed","debug","jerk"]:
    params[param] = locals()[param]
if len(sys.argv) < 2 or "help" in sys.argv or "-h" in sys.argv or sys.argv[1].count("="):
    print "Usage:"
    print "\tcheck_max_extrusion_speed.py filename [x_speed=#] [y_speed=#] [print_speed=#] [extrusion_speed=#] [debug=True/False]"
    print "Setting the print speed parameter will override the movement speed defined in the gcode."
    print "These speeds are in mm/s."
    exit()
file_name = sys.argv[1]
for arg in sys.argv[2:]:
    exec(arg,{},params)
gcode = open(file_name,"r")
locals().update(params)
if print_speed !=None:
    move_speed = print_speed
retract_count = 0
#add something to consider more printing areas like infill and support and inner and outer wall or whatever the slicer gives us a clue to
line_number = 0
while str(line).upper() .split(";")[0]<> "M107":
    line = gcode.readline().strip().upper()
    line_number += 1
while line:
    line = line.split(";")[0]
    line = line.split()
    if line and line[0] in ("G0","G1"):
        last_x = x
        last_y = y
        last_extrusion = extrusion
        for part in line:
            if part[0] == "X":
                x = float(part[1:])
            elif part[0] == "Y":
                y = float(part[1:])
            elif part[0] == "E":
                extrusion = float(part[1:])
            elif part[0] == "F" and print_speed == None: #feed rate in mm/min
                move_speed = float(part[1:])/60
        extrusion_delta = extrusion-last_extrusion
        #basic changes in x,y
        x_delta = abs(x-last_x)
        y_delta = abs(y-last_y)
        if extrusion_delta < 0:
            retract_count += 1
            #print line, "from",last_extrusion

        if line[0] == "G1":
            min_x = min(min_x,x)
            min_y =  min(min_y,y)
            max_x = max(max_x,x)
            max_y = max(max_y,y)

            if extrusion_delta > 0 and (x_delta > 0 or y_delta > 0): #we do not care about retractions
                move = math.hypot(x_delta,y_delta)
                #find out the speed based on x_speed and y_speed
                scaled_x = x_delta / x_speed
                scaled_y = y_delta / y_speed
                scaled_move = move / move_speed
                scaled_extrusion = extrusion_delta / extrusion_speed
                max_scale = 0
                speed_limit = ""
                #I am doing something totally wrong here and need to think this through.
                if debug:
                    if scaled_x > max_scale:
                        speed_limit = "X"
                    if scaled_y > max_scale:
                        speed_limit = "Y"
                    if scaled_move > max_scale:
                        speed_limit = "move"
                    if scaled_extrusion > max_scale:
                        speed_limit = "E"
                max_scale = max(scaled_x,scaled_y,scaled_move,scaled_extrusion)
                this_extrusion_speed = extrusion_delta/max_scale
                max_extrusion_speed = max(this_extrusion_speed,max_extrusion_speed)
                max_movement_speed = max(move/max_scale, max_movement_speed)
                #print scaled_x,scaled_y,scaled_move,scaled_extrusion,"\t",scaled_x,scaled_y,scaled_move,scaled_extrusion
                if debug:
                    print max_scale, speed_limit, this_extrusion_speed, x_delta/max_scale, y_delta/max_scale, move/max_scale
    line = gcode.readline().strip().upper()
    line_number += 1
print "Maximum extrusion speed requested:",max_extrusion_speed
print "Maximum movement speed requested:",max_movement_speed
print "Retraction count:",retract_count
print "Line count:",line_number
print "Build dimensions:", max_x-min_x,"x",max_y-min_y
if jerk == 0:
    exit()
"""
echo:Maximum feedrates (mm/s):
echo: M203 X150.00 Y150.00 Z150.00 E50.00
echo:Maximum Acceleration (mm/s2):
echo: M201 X800 Y800 Z800 E10000
echo:Accelerations: P=printing, R=retract and T=travel
echo: M204 P3000.00 R3000.00 T3000.00
echo:Advanced variables: S=Min feedrate (mm/s), T=Min travel feedrate (mm/s), B=minimum segment time (ms), X=maximum XY jerk (mm/s), Z=maximum Z jerk (mm/s), E=maximum E jerk (mm/s)
echo: M205 S0.00 T0.00 B20000 X20.00 Z20.00 E5.00
"""
maximum_length = max(max_x-min_x, max_y-min_y) #build plate size
for t in range(1,1000):
    time = t/100.0
    d=jerk*math.pow(time,3)/6
    a=jerk*time
    v=jerk*pow(time,2)/2
    if d > maximum_length:
        break
    #print time, d,v,a#,jerk,acceleration
print "In this distance, the print could have reached a maximum speed of about %.00fmm/s and an acceleration of %.00f given the provided maximum jerk setting of %d that you mentioned. This is assuming one of the distances to speed up over was actually %d. Since it takes time to build up speed, your extrusion speeds and movement speeds might not always be what you requested them to be." % ( d,a,jerk,maximum_length)
