# check_max_extrusion_speed.py
This program will help you find out just how fast your filament gets pushed in a particular gcode file.
If you set print_speed in the parameter list, this program will instead tell you just how fast you could push it given x_speed, y_speed, print_speed and extrusion_speed.

Keep in mind that the extrusion speed listed in Pronterface and other printer control software for preparing the printer for printing is probably mm/min and not mm/sec.
