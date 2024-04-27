import pandas as pd
import ghp
import mrp
# code goes here

ghp.ghp()
mrp.mrp('chairs', 'frame')
mrp.mrp('frame', 'wooden_construction_elements')
mrp.mrp('frame', 'nails')
mrp.mrp('chairs', 'padding')
# print table using pandas