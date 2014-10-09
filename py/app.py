import sys
sys.stdout = sys.stderr

import atexit
import threading
import cherrypy
import MySQLdb

db = MySQLdb.connect(
  host="127.0.0.1",
  user="divvy",
  passwd="keepC4LM",
  db="divvy"
)

c = db.cursor()
                   

cherrypy.config.update({'environment': 'embedded'})

if cherrypy.__version__.startswith('3.0') and cherrypy.engine.state == 0:
    cherrypy.engine.start(blocking=False)
    atexit.register(cherrypy.engine.stop)

class Root(object):
  def index(self):
    return 'Hello World!'
  index.exposed = True

  def age(self):
    q = """
      SELECT 
        age_in_2014,
        count(*)
      FROM
        divvy_trips_distances
      GROUP BY
        age_in_2014 
    """
    kids = 0
    teens = 0
    twenties = 0
    thirties = 0
    forties = 0
    fifties = 0
    sixtyplus = 0
    seventies = 0
    eightyplus = 0
    c.execute(q)
    for row in c.fetchall():
      if row[0] < 12:
        kids += row[1]
      elif 20 > row[0] and row[0] > 12:
        teens += row[1]
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
      "0-12,%s" % kids,
      "12-19,%s" % teens,
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

application = cherrypy.Application(Root(), script_name=None, config=None)

