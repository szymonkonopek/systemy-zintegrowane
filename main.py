import pandas as pd
import ghp
import mrp
# code goes here

ghp.ghp()
mrp.mrp('chairs', 'frame')
mrp.mrp('frame', 'nails')
mrp.mrp('chairs', 'padding')

# mrp.mrp('frame', 'wooden_construction_elements')
# print table using pandas