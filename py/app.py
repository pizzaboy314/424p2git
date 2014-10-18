import sys
sys.stdout = sys.stderr

import atexit
import threading
import cherrypy
import MySQLdb
import pickle
import subprocess
from collections import OrderedDict
from datetime import datetime
from dateutil import parser

db = MySQLdb.connect(
  host="127.0.0.1",
  user="divvy",
  passwd="keepC4LM",
  db="divvy"
)

c = db.cursor()
 
def store_popularity_groups():
  with open("stations.pickle", "rb") as f:
    stations = pickle.load(f)
  with open("id_popularity.pickle", "rb") as f:
    id_pop = pickle.load(f)

  pop_rankings = id_pop.values()
  pop_rankings.sort()
  d = {
    0: [], 1: [], 2: [], 3: [], 4:[], 5:[], 6:[]
  }
  for sid, count in id_pop.items():
    if count in pop_rankings[0:10]:
      d[0].append(stations[sid])
    elif count in pop_rankings[10:50]:
      d[1].append(stations[sid])
    elif count in pop_rankings[50:100]:
      d[2].append(stations[sid])
    elif count in pop_rankings[100:150]:
      d[3].append(stations[sid])
    elif count in pop_rankings[150:200]:
      d[4].append(stations[sid])
    elif count in pop_rankings[200:250]:
      d[5].append(stations[sid])
    elif count in pop_rankings[250:300]:
      d[6].append(stations[sid])

  with open("popularity.pickle", "wb") as f:
    pickle.dump(d,f)
                   

cherrypy.config.update({'environment': 'embedded', 'show_tracebacks': True, 'log.error_file': '/tmp/p2site.log'})

if cherrypy.__version__.startswith('3.0') and cherrypy.engine.state == 0:
    cherrypy.engine.start(blocking=False)
    atexit.register(cherrypy.engine.stop)

class Root(object):
  def index(self):
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    return 'Hello World!'
  index.exposed = True

  def rides_by_day_of_year(self):
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    q = """
      SELECT
        startdate, 
        count(*)
      FROM
        divvy_trips_distances
      GROUP BY
        startdate
    """
    c.execute(q)
    ret = []
    ret.append("Date,Count")
    for row in c.fetchall():
      ret.append("%s,%s" % (row[0], row[1]))
    return "\n".join(ret)
  rides_by_day_of_year.exposed = True
    

  def age(self):
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    q = """
      SELECT 
        age_in_2014,
        count(*)
      FROM
        divvy_trips_distances
      GROUP BY
        age_in_2014 
    """
    undertwenty = 0
    twenties = 0
    thirties = 0
    forties = 0
    fifties = 0
    sixtyplus = 0
    c.execute(q)
    for row in c.fetchall():
      if row[0] < 20 and row[0] > 0:
        undertwenty += row[1]
      elif 30 > row[0] and row[0] > 19:
        twenties += row[1]
      elif 40 > row[0] and row[0] > 29:
        thirties += row[1]
      elif 50 > row[0] and row[0] > 39:
        forties += row[1]
      elif 60 > row[0] and row[0] > 49:
        fifties += row[1]
      elif row[0] > 59:
        sixtyplus += row[1]

    ret = [
      "Age,Count",
      "Under 20,%s" % undertwenty,
      "20-29,%s" % twenties,
      "30-39,%s" % thirties,
      "40-49,%s" % forties,
      "50-59,%s" % fifties,
      "60+,%s" % sixtyplus,
    ]
    return "\n".join(ret)
  age.exposed = True

  def station_popularity(self, station_name):
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    try:
      with open("/var/www/cs424/p2/py/popularity.pickle", "rb") as f:
        pop = pickle.load(f)
    except:
      return "can't open file in cwd: %s" % subprocess.check_output(["pwd"])
    for group in pop:
      if station_name in pop[group]:
        return str(group)
  station_popularity.exposed = True
  
  def get_day(self, date):
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    with open("/var/www/cs424/p2/py/station_lat_long.pickle", "rb") as f:
      stat_lat_long = pickle.load(f)
    q = """
        SELECT 
           starttime, 
           stoptime, 
           trip_id, 
           from_station_id, 
           to_station_id 
         FROM 
           divvy_trips_distances 
         WHERE  
           startdate like '%s' 
         ORDER BY 
           stoptime ASC""" % date
    ret = []
    ret.append("timestamp,trip_id,start/end,from,flat,flong,to,tlat,tlong")
    c.execute(q)
    data = OrderedDict()
    keylist = {}
    i = 0
    for row in c.fetchall():
      keylist[i] = parser.parse(row[0])
      data[i] = ( # start timestamp
        row[2], # trip id
        "start",
        stat_lat_long[row[3]][0], # from station name
        stat_lat_long[row[3]][1], # from lat
        stat_lat_long[row[3]][2], # from long
        stat_lat_long[row[4]][0], # to station name
        stat_lat_long[row[4]][1], # from lat
        stat_lat_long[row[4]][2]  # from long
      )
      i = i+1
      # now we do the same thing again but for the end of the trip
      keylist[i] = parser.parse(row[1])
      data[i] = ( # start timestamp
        row[2], # trip id
        "end",
        stat_lat_long[row[3]][0], # from station name
        stat_lat_long[row[3]][1], # from lat
        stat_lat_long[row[3]][2], # from long
        stat_lat_long[row[4]][0], # to station name
        stat_lat_long[row[4]][1], # from lat
        stat_lat_long[row[4]][2]  # from long
      )
      i = i+1
    keys = keylist.values()
    keys.sort()
    for key in keys: 
      l = [key.strftime('%m/%d/%Y %H:%M%p')]
      for j, keylookup, in keylist.items():
        if key == keylookup:
          l.extend(data[j])
      l = tuple(l)
      ret.append("%s,%s,%s,%s,%s,%s,%s,%s,%s" % l)
    return "\n".join(ret)
  get_day.exposed = True

application = cherrypy.Application(Root(), script_name=None, config=None)
