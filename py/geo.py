import json
import pickle
from shapely.geometry import shape, Point
from pprint import pprint

# load GeoJSON file containing sectors
with open ('../static-json/boundaries.json', 'r') as f:
    js = json.load(f)

with open('station_lat_long.pickle', 'rb') as f:
  st = pickle.load(f)

ret = []
ret.append("window.neighborhood_map = new Map")
n_map = {}
for station, li in st.items():
  point = Point(li[1],li[2])

  # check each polygon to see if it contains the point
  for neighborhood in js:
    #print "checking %s" % neighborhood["properties"]["slug"]
    slug = neighborhood["properties"]["slug"]
    if not n_map.has_key(slug):
      n_map[slug] = [] # this will be a list of station ids
    for coord in neighborhood['geometry'].values()[1][0][0]:
      coord.sort(reverse=True)
    #pprint(neighborhood['geometry'])
    polygon = shape(neighborhood['geometry'])
    #pprint(polygon.is_closed)
    #print dir(polygon)
    if polygon.contains(point):
      n_map[slug].append(station)

for n, s in n_map.items():
  ret.append("window.neighborhood_map.set('%s', %s)" % (n, s))

with open('../js/neighborhoods.js', 'wb') as f:
  f.write("\n".join(ret))
