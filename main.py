import pandas as pd
import ghp
import mrp
import my_dash_app
from dictionary import *
# code goes here

ghp.ghp()
mrp.mrp('chairs', 'padding')
mrp.mrp('chairs', 'frame')
mrp.mrp('frame', 'nails')
mrp.mrp('frame', 'wooden_construction_elements')
# print table using pandas

my_dash_app.runDashApp()