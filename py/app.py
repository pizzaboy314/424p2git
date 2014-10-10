import sys
sys.stdout = sys.stderr

import atexit
import threading
import cherrypy
import MySQLdb
import pickle

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
                   

cherrypy.config.update({'environment': 'embedded', 'show_tracebacks': True, 'log.error_file': 'site.log'})

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
#    kids = 0
#    teens = 0
    undertwenty = 0
    twenties = 0
    thirties = 0
    forties = 0
    fifties = 0
    sixtyplus = 0
#    seventies = 0
#    eightyplus = 0
    c.execute(q)
    for row in c.fetchall():
      if row[0] < 20 and row[0] > 0:
        undertwenty += row[1]
#      elif 20 > row[0] and row[0] > 12:
#        teens += row[1]
      elif 30 > row[0] and row[0] > 19:
        twenties += row[1]
      elif 40 > row[0] and row[0] > 29:
        thirties += row[1]
      elif 50 > row[0] and row[0] > 39:
        forties += row[1]
      elif 60 > row[0] and row[0] > 49:
        fifties += row[1]
#      elif 70 > row[0] and row[0] > 59:
#        sixties += row[1]
#      elif 80 > row[0] and row[0] > 69:
#        seventies += row[1]
      elif row[0] > 59:
        sixtyplus += row[1]

    ret = [
      "Age,Count",
#      "0-12,%s" % kids,
#      "12-19,%s" % teens,
      "Under 20,%s" % undertwenty,
      "20-29,%s" % twenties,
      "30-39,%s" % thirties,
      "40-49,%s" % forties,
      "50-59,%s" % fifties,
#      "60-69,%s" % sixties,
#      "70-79,%s" % seventies,
      "60+,%s" % sixtyplus,
    ]
    return "\n".join(ret)
  age.exposed = True

  def station_popularity(self, station_name):
    with open("popularity.pickle", "rb") as f:
      pop = pickle.load(f)
 
    for group in pop:
      if station_name in pop[group]:
        return group
  station_popularity.exposed = True

application = cherrypy.Application(Root(), script_name=None, config=None)
