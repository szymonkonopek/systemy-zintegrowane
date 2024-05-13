import ghp
import mrp
import my_dash_app
from dictionary import *
# code goes here

ghp.ghp()
mrp.mrp('chairs', 'frame')
mrp.mrp('frame', 'wooden_construction_elements')
mrp.mrp('frame', 'nails')
mrp.mrp('chairs', 'padding')
# print table using pandas

my_dash_app.runDashApp()