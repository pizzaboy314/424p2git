import sys
sys.stdout = sys.stderr

import os
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

if subprocess.check_output("hostname") == "praxis\n":
  PATH = ""
else:
  PATH = "/var/www/cs424/p2/py"

c = db.cursor()

def parse_age(age):
  """Parse age groups... when you get an age, return the range as its displayed
  in the pie chart.  This is currently unused.

  Args:
    age - int

  Returns:
    tuple - two ints, uninclusive
  """
  if age == "Under 20":
    return (0, 20)
  elif age == "20-29":
    return (19,30)
  elif age == "30-39":
    return (29, 40)
  elif age == "40-49":
    return (39, 50)
  elif age == "50-59":
    return (49, 60)
  elif age == "60+":
    return (59, 180)

def parse_time_of_day(time_of_day):
  """given a time of day string, return the time range (inclusive).

  Args:
    time_of_day - string, one of morning, lunch, "after work", or evening

  Returns:
    a two tuple of inclusive time range (low, high)
  """
  if time_of_day == "morning":
    return(6, 9)
  elif time_of_day == "lunch":
    return(11,13)
  elif time_of_day == "after work":
    return(4, 7)
  elif time_of_day == "evening":
    return(7,9)
 
def store_popularity_groups():
  """Stores popularity in a pickle.  To be run offline."""
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
  """ Root class for the cherrypy instance running the backend """

  def index(self):
    """Hello world, for index"""
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    return 'Hello World!'
  index.exposed = True

  def rides_by_day_of_year(self):
    """Display the number of rides on each day of the year.

    Returns a csv like Date,Count
    """
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
      print "match1 %s" % type(row[0])
      dt = row[0]
      if dt == parser.parse('2013-06-27').date:
        date = 'June 27, 2013'
      elif dt.day == 1:
        print "match2"
        date = "%s %s" % (dt.strftime("%b"), dt.year)
      else:
        date = " "
      ret.append("%s,%s" % (date, row[1]))
    return "\n".join(ret)
  rides_by_day_of_year.exposed = True
    
  def gender(self,
          date=None,
          gender=None,
          subscriber=None,
          age=None,
          stations=None):
    """Display the gender breakdown of riders based on filters
  
    Args (all optional):
      gender - string - Male or Female
      subscriber - string - Subscriber or Customer
      age - a string like "low,high"
      station - a string like "station_id1,station_id2,station_id3"

    Returns:
      a csv like Gender,Count
    """
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    where = "WHERE "
    if date or gender or subscriber or age or stations:
      where_stmts = []
      if date:
        where_stmts.append("startdate like '%s'" % date)
      if gender:
        where_stmts.append("gender like '%s' " % gender)
      if subscriber:
        where_stmts.append("usertype like '%s%%' " % subscriber)
      if age:
        bottom, top = age.split(",")
        where_stmts.append("age_in_2014 < %s " % top)
        where_stmts.append("age_in_2014 > %s " % bottom)
      if stations:
        # since its bikes out, we'll only look at the depating station
        stations = stations.split(",")
        where_stmts.append("from_station_id in ('%s')" % \
          "', '".join(stations))
      if where_stmts:
        where = where + where_stmts[0]
        for stmt in where_stmts[1:]:
          where += "AND " + stmt + " "
    else:
      where = ""
    q = """
      SELECT
        gender,
        count(*)
      FROM
        divvy_trips_distances
      %s
      GROUP BY
        gender
    """ % where
    c.execute(q)
    ret = []
    ret.append("Gender,Count")
    for row in c.fetchall():
      if not row[0]:
        ret.append("Unknown,%d" % row[1])
      else:
        ret.append("%s,%d" % (row[0], row[1]))
    return "\n".join(ret)
  gender.exposed = True

  def usertype(self,
          date=None,
          gender=None,
          subscriber=None,
          age=None,
          stations=None):
    """Displays statistics on usertype.

    Args (all optional):
      gender - string - Male or Female
      subscriber - string - Subscriber or Customer
      age - a string like "low,high"
      station - a string like "station_id1,station_id2,station_id3"

    Returns a csv like Usertype,Count
    """
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    where = "WHERE "
    if date or gender or subscriber or age or stations:
      where_stmts = []
      if date:
        where_stmts.append("startdate like '%s'" % date)
      if gender:
        where_stmts.append("gender like '%s' " % gender)
      if subscriber:
        where_stmts.append("usertype like '%s%%' " % subscriber)
      if age:
        bottom, top = age.split(",")
        where_stmts.append("age_in_2014 < %s " % top)
        where_stmts.append("age_in_2014 > %s " % bottom)
      if stations:
        # since its bikes out, we'll only look at the depating station
        stations = stations.split(",")
        where_stmts.append("from_station_id in ('%s')" % \
          "', '".join(stations))
      if where_stmts:
        where = where + where_stmts[0]
        for stmt in where_stmts[1:]:
          where += "AND " + stmt + " "
    else:
      where = ""
    q = """
      SELECT 
        usertype,
        count(*)
      FROM
        divvy_trips_distances
      %s
      GROUP BY
        usertype 
    """ % where
    c.execute(q)
    ret = []
    ret.append("Type,Count")
    for row in c.fetchall():
      ret.append("%s,%d" % (row[0], row[1]))
    return "\n".join(ret)
  usertype.exposed = True

  def age(self,
          date=None,
          gender=None,
          subscriber=None,
          age=None,
          stations=None):
    """Displays statistics on age, based on filters.

    Args (all optional):
      gender - string - Male or Female
      subscriber - string - Subscriber or Customer
      age - a string like "low,high"
      station - a string like "station_id1,station_id2,station_id3"

    Returns a csv like Age,Count
    """
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"

    where = "WHERE "
    if date or gender or subscriber or age or stations:
      where_stmts = []
      if date:
        where_stmts.append("startdate like '%s'" % date)
      if gender:
        where_stmts.append("gender like '%s' " % gender)
      if subscriber:
        where_stmts.append("usertype like '%s%%' " % subscriber)
      if age:
        bottom, top = age.split(",")
        where_stmts.append("age_in_2014 < %s " % top)
        where_stmts.append("age_in_2014 > %s " % bottom)
      if stations:
        # since its bikes out, we'll only look at the depating station
        stations = stations.split(",")
        where_stmts.append("from_station_id in ('%s')" % \
          "', '".join(stations))
      if where_stmts:
        where = where + where_stmts[0]
        for stmt in where_stmts[1:]:
          where += "AND " + stmt + " "
    else:
      where = ""
    q = """
      SELECT 
        age_in_2014,
        count(*)
      FROM
        divvy_trips_distances
      %s
      GROUP BY
        age_in_2014 
    """ % where
    undertwenty = 0
    twenties = 0
    thirties = 0
    forties = 0
    fifties = 0
    sixtyplus = 0
    print "q looks like %s" % q
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

  def outflow(self, station_id,
          gender=None,
          subscriber=None,
          age=None):
    """Displays outflow data based on filters.

    Args:
      station_id - int - required
      gender (optional) - string - Male or Female
      subscriber (optional) - string - Subscriber or Customer
      age (optional) - a string like "low,high"

    Returns a csv like to_station_id,count
    """
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"

    where = ""
    if gender or subscriber or age:
      where_stmts = []
      if gender:
        where_stmts.append("gender like '%s' " % gender)
      if subscriber:
        where_stmts.append("usertype like '%s%%' " % subscriber)
      if age:
        bottom, top = age.split(",")
        where_stmts.append("age_in_2014 < %s " % top)
        where_stmts.append("age_in_2014 > %s " % bottom)
      if where_stmts:
        for stmt in where_stmts:
          where += "AND " + stmt + " "
    else:
      where = ""
    q = """
      SELECT 
        to_station_id,
        count(*)
      FROM
        divvy_trips_distances
      WHERE from_station_id = '%s'
        %s 
      GROUP BY
        to_station_id
    """ % (station_id, where)
    ret = []
    ret.append("to_station,count")
    c.execute(q) 
    count = 0
    for row in c.fetchall():
      ret.append("%s,%d" % (row[0],row[1]))
      count += row[1]
    #with open('/tmp/outflow', 'a') as f:
    #  f.write("window.outflow.set(%s, %d)\n " % (station_id, count))
    return "\n".join(ret)
  outflow.exposed = True

  def inflow(self, station_id,
          gender=None,
          subscriber=None,
          age=None):
    """Displays inflow data based on filters.

    Args:
      station_id - int - required
      gender (optional) - string - Male or Female
      subscriber (optional) - string - Subscriber or Customer
      age (optional) - a string like "low,high"

    Returns a csv like from_station_id,count
    """
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"

    where = ""
    if gender or subscriber or age:
      where_stmts = []
      if gender:
        where_stmts.append("gender like '%s' " % gender)
      if subscriber:
        where_stmts.append("usertype like '%s%%' " % subscriber)
      if age:
        bottom, top = age.split(",")
        where_stmts.append("age_in_2014 < %s " % top)
        where_stmts.append("age_in_2014 > %s " % bottom)
      if where_stmts:
        for stmt in where_stmts:
          where += "AND " + stmt + " "
    else:
      where = ""
    q = """
      SELECT 
        from_station_id,
        count(*)
      FROM
        divvy_trips_distances
      WHERE to_station_id = '%s'
        %s 
      GROUP BY
        from_station_id
    """ % (station_id, where)
    ret = []
    ret.append("from_station,count")
    c.execute(q)
    count = 0
    for row in c.fetchall():
      ret.append("%s,%d" % (row[0],row[1]))
      count += row[1]
    #with open('/tmp/inflow', 'a') as f:
    #  f.write("window.inflow.set(%s, %d)\n " % (station_id, count))
    return "\n".join(ret)
  inflow.exposed = True

  def station_popularity(self, station_name):
    """Display station popularity data for a specific station.

    Args:
      station_name - string - the station name.
   
    Returns:
      An int - one of 7 popularity groups.
    """
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
  
  def get_day(self, date, gender=None,
                       subscriber=None,
                       age=None,
                       stations=None):
    """Get data on an individual day for playback, based on filters.

    Args (all optional):
      gender - string - Male or Female
      subscriber - string - Subscriber or Customer
      age - a string like "low,high"
      station - a string like "station_id1,station_id2,station_id3"
  
    Returns:
      a csv like timestamp,trip_id,start/end,from,flat,flong,to,tlat,tlong
    """
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    with open(os.path.join(PATH, "station_lat_long.pickle"), "rb") as f:
      stat_lat_long = pickle.load(f)

    where = ""
    if gender or subscriber or age or stations:
      where_stmts = []
      if gender:
        where_stmts.append("gender like '%s' " % gender)
      if subscriber:
        where_stmts.append("usertype like '%s%%' " % subscriber)
      if age:
        bottom, top = age.split(",")
        where_stmts.append("age_in_2014 < %s " % top)
        where_stmts.append("age_in_2014 > %s " % bottom)
      if stations:
        # since its bikes out, we'll only look at the depating station
        stations = stations.split(",")
        where_stmts.append("from_station_id in ('%s')" % \
          "', '".join([str(i) for i in stations]))
      where = where + where_stmts[0]
      for stmt in where_stmts[1:]:
        where += "AND " + stmt + " "
    if not where:
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
    else:
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
             startdate like '%s' AND %s
           ORDER BY 
             stoptime ASC""" % (date, where)
    print "assembled q = %s" % q
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
          keylist.pop(j)
          break
      l = tuple(l)
      ret.append("%s,%s,%s,%s,%s,%s,%s,%s,%s" % l)
    return "\n".join(ret)
  get_day.exposed = True

  def bikes_out_by_day(time_of_day=None,
                       gender=None,
                       subscriber=None,
                       age=None,
                       stations=None):
    """Display the number of rides on each day of the year. Based on filters.

    Args (all optional):
      gender - string - Male or Female
      subscriber - string - Subscriber or Customer
      age - a string like "low,high"
      station - a string like "station_id1,station_id2,station_id3"

    Returns:
      a csv like Date,Count
    """
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    base_q = """
      SELECT
        startdate, 
        count(*)
      FROM
        divvy_trips_distances
    """
    if time_of_day or gender or subscriber or age or stations:
      where = "WHERE "
      where_stmts = []
    if time_of_day: 
      #TODO: do we need this?
      pass
    if gender:
      where_stmts.append("gender like '%s'" % gender)
    if subscriber:
      where_stmts.append("usertype like '%s'" % subscriber)
    if age:
      bottom, top = parse_age(age)
      where_stmts.append("age_in_2014 < %d" % top)
      where_stmts.append("age_in_2014 > %d" % bottom)
    if stations:
      stations = stations.split(",")
      # since its bikes out, we'll only look at the depating station
      where_stmts.append("from_station_id in ('%s')" % \
        "', '".join(stations))
    if where_stmts:
      where = where + where_stmts[0]
      for stmt in where_stmts[1:]:
        where += "AMD " + stmt + " "
    group_by = """
      GROUP BY
        startdate
    """
    if where_stmts:
      assembled_q = " ".join((base_q, where, group_by))
    else:
      assembled_q = " ".join((base_q, group_by))

    print assembled_q
    c.execute(assembled_q)
    ret = []
    ret.append("Date,Count")
    for row in c.fetchall():
      dt = row[0]
      if dt == parser.parse('2013-06-27').date:
        date = 'June 27, 2013'
      elif dt.day == 1:
        date = "%s %s" % (dt.strftime("%b"), dt.year)
      else:
        date = " "
      ret.append("%s,%s" % (date, row[1]))
    return "\n".join(ret)

  bikes_out_by_day.exposed = True

  def hour_of_day(self, date=None,
                  gender=None,
                  subscriber=None,
                  age=None,
                  stations=None):
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    sql = []
    cache_string = ""
    where = ""
    if date or gender or subscriber or age or stations:
    # lets do some ghetto caching
      cache_string = ""
      if date:
        cache_string += date.replace(" ", "").replace("/", "")
      if gender:
        cache_string += gender
      if subscriber:
        cache_string += subscriber
      if age:
        cache_string += age
      if stations: cache_string += stations
      try:
        with open ("%s/%s_trip_id_starttime_hours.json" % \
          (os.path.join(PATH,"cache"), cache_string), "rb") as f:
            return f.read()
      except:
        pass
    try:
      with open ("%s/%s_trip_id_starttime.pickle" % \
        (os.path.join(PATH,"cache"), cache_string), "rb") as f:
        sql = pickle.load(f)
      print "running from cached version"
    except:
      print "running from SQL"
      where = "WHERE "
      where_stmts = []
      if date:
        where_stmts.append("startdate like '%s'" % date)
      if gender:
        where_stmts.append("gender like '%s'" % gender)
      if subscriber:
        where_stmts.append("usertype like '%s'" % subscriber)
      if age:
        bottom, top = parse_age(age)
        where_stmts.append("age_in_2014 < %d" % top)
        where_stmts.append("age_in_2014 > %d" % bottom)
      if stations:
        stations = stations.split(",")
        # since its bikes out, we'll only look at the depating station
        where_stmts.append("from_station_id in (%s)" % \
          ", ".join(stations))
      if where_stmts:
        where = where + where_stmts[0]
        for stmt in where_stmts[1:]:
          where += "AND " + stmt + " "
      else:
        where = ""
    q = """
      SELECT
        trip_id,
        starttime
      FROM
        divvy_trips_distances
      %s
      GROUP BY
        trip_id
    """ % where
    c.execute(q)
    sql = []
    for row in c.fetchall():
      sql.append((row[0],parser.parse(row[1])))
    with open ("%s/%s_trip_id_starttime.pickle" % \
      (os.path.join(PATH,"cache"), cache_string), "wb") as f:

      pickle.dump(sql, f)
      
    ret = []
    ret.append("[")
    d = {}
    for i in range(0, 24):      
      count = 0
      d[i] = count
    for row in sql:
      for i in range(0,24):
        if i == row[1].hour:
          d[i] += 1
    for i in range(0, 24):
      ret.append('{"range":"%d", "frequency":"%d"},' % (i, d[i]))
    ret[len(ret)-1] = ret[len(ret)-1].rstrip(",")
    ret.append("]")
    with open ("%s/%s_trip_id_starttime_hours.json" % \
      (os.path.join(PATH,"cache"), cache_string), "wb") as f:
      f.write("\n".join(ret))

    return "\n".join(ret)
  hour_of_day.exposed = True

  def day_of_week(self, date=None,
                  gender=None,
                  subscriber=None,
                  age=None,
                  stations=None):  
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    sql = []
    cache_string = ""
    # lets do some ghetto caching
    where = ""
    if date or gender or subscriber or age or stations:
    # lets do some ghetto caching
      if date:
        cache_string += date.replace(" ", "").replace("/", "")
      if gender:
        cache_string += gender
      if subscriber:
        cache_string += subscriber
      if age:
        cache_string += age
      if stations: cache_string += stations
      try:
        with open ("%s/%s_trip_id_starttime_days.json" % \
          (os.path.join(PATH,"cache"), cache_string), "rb") as f:
            return f.read()
      except:
        pass
    try:
      with open ("%s/%s_trip_id_starttime.pickle" % \
        (os.path.join(PATH,"cache"), cache_string), "rb") as f:
        sql = pickle.load(f)
      print "running from cached version"
    except:
      print "running from SQL"

      where = "WHERE "
      where_stmts = []
      if date:
        where_stmts.append("startdate like '%s'" % date)
      if gender:
        where_stmts.append("gender like '%s'" % gender)
      if subscriber:
        where_stmts.append("usertype like '%s'" % subscriber)
      if age:
        bottom, top = parse_age(age)
        where_stmts.append("age_in_2014 < %d" % top)
        where_stmts.append("age_in_2014 > %d" % bottom)
      if stations:
        stationsstr = stations
        stations = stations.split(",")
        # since its bikes out, we'll only look at the depating station
        where_stmts.append("from_station_id in (%s)" % \
          ", ".join(stations))
      if where_stmts:
        where = where + where_stmts[0]
        for stmt in where_stmts[1:]:
          where += "AND " + stmt + " "
      else:
        where = ""
    q = """
      SELECT
        trip_id,
        starttime
      FROM
        divvy_trips_distances
      %s
      GROUP BY
        trip_id
    """ % where
    c.execute(q)
    sql = []
    for row in c.fetchall():
      sql.append((row[0],parser.parse(row[1])))
    with open ("%s/%s_trip_id_starttime.pickle" % \
      (os.path.join(PATH,"cache"), cache_string), "wb") as f:

      pickle.dump(sql, f)


    ret = []
    ret.append("[")
    days = OrderedDict()
    days["Sun"] = 0  
    days["Mon"] = 0 
    days["Tue"] = 0 
    days["Wed"] = 0 
    days["Thu"] = 0 
    days["Fri"] = 0 
    days["Sat"] = 0 
    for row in sql:
      days[row[1].strftime("%a")] += 1
    for day, count in days.items():
      ret.append('{"range":"%s", "frequency":"%d"},' % (day, count))
    ret[len(ret)-1] = ret[len(ret)-1].rstrip(",")
    ret.append("]")    
    with open ("%s/%s_trip_id_starttime_days.json" % \
      (os.path.join(PATH,"cache"), cache_string), "wb") as f:
      f.write("\n".join(ret)) 
 
    return "\n".join(ret)
  day_of_week.exposed = True
 
  def distance_dist(self, date=None,
                  gender=None,
                  subscriber=None,
                  age=None,
                  stations=None):
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    base_q = """
      SELECT
        meters
      FROM
        divvy_trips_distances
    """
    where = ""
    where_stmts = []
    if gender or subscriber or age or stations:
      where = "WHERE "
    if gender:
      where_stmts.append("gender like '%s'" % gender)
    if subscriber:
      where_stmts.append("usertype like '%s'" % subscriber)
    if age:
      bottom, top = parse_age(age)
      where_stmts.append("age_in_2014 < %d" % top)
      where_stmts.append("age_in_2014 > %d" % bottom)
    if stations:
      stations = stations.split(",")
      # since its bikes out, we'll only look at the depating station
      where_stmts.append("from_station_id in ('%s')" % \
        "', '".join(stations))
    if where_stmts:
      where = where + where_stmts[0]
      for stmt in where_stmts[1:]:
        where += "AMD " + stmt + " "
    group_by = """
      GROUP BY
        meters
    """
    if where_stmts:
      assembled_q = " ".join((base_q, where, group_by))
    else:
      assembled_q = " ".join((base_q, group_by))
    c.execute(assembled_q)
    ranges = [(0,0.5), (0.5,1), (1,1.5), (1.5,2), (2,2.5), (2.5,3), (3,3.5), (3.5,4), (4,4.5), (4.5,5), (5,5.5), (5.5,6), (6,6.5), (6.5,7), (7,7.5), (7.5,8), (8,8.5), (8.5,9), (9,9.5), (9.5,10), (10,10.5), (10.5,11), (11,11.5), (11.5,12), (12,12.5), (12.5,13), (13,13.5), (13.5,14), (14,14.5), (14.5,15), (15,15.5), (15.5,16), (16,16.5), (16.5,17), (17,17.5), (17.5,18), (18, 100),]
    d = OrderedDict()
    for item in ranges:
      d[item] = 0
    for row in c.fetchall():
      for r in ranges:
        km = float(float(row[0]) / 1000)
        if km > r[0] and km <= r[1]:
          d[r] += 1

    ret = ["["]
    for r, count in d.items():  
      ret.append('{ "range": "%s", "frequency": "%d" },' % ("%.1f-%.1f" % r, count))
    ret[len(ret)-1] = ret[len(ret)-1].rstrip(",")
    ret.append("]")
    return "\n".join(ret)
  distance_dist.exposed = True

  def time_dist(self, date=None,
                  gender=None,
                  subscriber=None,
                  age=None,
                  stations=None):
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    base_q = """
      SELECT
        seconds
      FROM
        divvy_trips_distances
    """
    where = ""
    where_stmts = []
    if gender or subscriber or age or stations:
      where = "WHERE "
    if gender:
      where_stmts.append("gender like '%s'" % gender)
    if subscriber:
      where_stmts.append("usertype like '%s'" % subscriber)
    if age:
      bottom, top = parse_age(age)
      where_stmts.append("age_in_2014 < %d" % top)
      where_stmts.append("age_in_2014 > %d" % bottom)
    if stations:
      stations = stations.split(",")
      # since its bikes out, we'll only look at the depating station
      where_stmts.append("from_station_id in ('%s')" % \
        "', '".join(stations))
    if where_stmts:
      where = where + where_stmts[0]
      for stmt in where_stmts[1:]:
        where += "AMD " + stmt + " "
    group_by = """
      GROUP BY
        seconds
    """
    if where_stmts:
      assembled_q = " ".join((base_q, where, group_by))
    else:
      assembled_q = " ".join((base_q, group_by))
    c.execute(assembled_q)
    ranges = [(0,5), (5,10), (10,15), (15,20), (20,25), (25,30), (30,35), (35,40), (40,45), (45,50), (50,55), (55,60), (60,65), (65,70), (70,75), (75,80), (80,85), (85,90), (90,95), (95,100), (100,105), (105,110), (110,115), (115,120), (120,125), (125,130), (130,135), (135,140), (140,145), (145,150), (150,300),]
    d = OrderedDict()
    for item in ranges:
      d[item] = 0
    for row in c.fetchall():
      for r in ranges:
        m = float(float(row[0]) / 60)
        if m > r[0] and m <= r[1]:
          d[r] += 1

    ret = ["["]
    for r, count in d.items():
      ret.append('{ "range": "%s", "frequency": "%s" },' % ("%d-%d" % r, int(count)))
    ret[len(ret)-1] = ret[len(ret)-1].rstrip(",")
    ret.append("]")
    return "\n".join(ret)
  time_dist.exposed = True


  def weather(self, date, hour):
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    dt = parser.parse(date)
    ret = ["icon,temp"]
    with open('%s/weather/%s.pickle' % \
      (PATH, "%s%02d%02d" %(dt.year, dt.month, dt.day)), 'rb') as f:
 
      winfo = pickle.load(f)

    ret.append("%s,%s" % winfo[hour])
    return "\n".join(ret)
  weather.exposed = True
 
  def get_morning_trips(self, date):
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    q = """
         select 
           from_station_id,
           to_station_id,
           starttime 
         from 
           divvy_trips_distances 
         where 
            startdate = '%s' AND (
           (starttime like '%%8:%%'  and starttime not like '%%18:%%')
           OR (starttime like '%%6:%%' and starttime not like '%%16:%%')
           OR (starttime like '%%7:%%' and starttime not like '%%17:%%')
           )
         order by 
           starttime 
        """ % date
    c.execute(q)
    ret = ["from_station_id,to_station_id,starttime"]
    i = 0
    for row in c.fetchall():
      ret.append("%s,%s,%s" % (row[0], row[1], row[2]))
      i += 1
    print i
    return "\n".join(ret)
  get_morning_trips.exposed = True

  def get_lunch_trips(self, date):
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    q = """
         select 
           from_station_id,
           to_station_id,
           starttime 
         from 
           divvy_trips_distances 
         where 
            startdate = '%s' AND (
           (starttime like '%%11:%%')
           OR (starttime like '%%12:%%')
           )
         order by 
           starttime 
        """ % date
    c.execute(q)
    ret = ["from_station_id,to_station_id,starttime"]
    i = 0
    for row in c.fetchall():
      ret.append("%s,%s,%s" % (row[0], row[1], row[2]))
      i += 1
    print i
    return "\n".join(ret)
  get_lunch_trips.exposed = True

  def get_after_work_trips(self, date):
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    q = """
         select 
           from_station_id,
           to_station_id,
           starttime 
         from 
           divvy_trips_distances 
         where 
            startdate = '%s' AND (
           (starttime like '%%16:%%')
           OR (starttime like '%%17:%%')
           OR (starttime like '%%18:%%')
           )
         order by 
           starttime 
        """ % date
    c.execute(q)
    ret = ["from_station_id,to_station_id,starttime"]
    i = 0
    for row in c.fetchall():
      ret.append("%s,%s,%s" % (row[0], row[1], row[2]))
      i += 1
    print i
    return "\n".join(ret)
  get_after_work_trips.exposed = True

  def get_evening_trips(self, date):
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    q = """
         select 
           from_station_id,
           to_station_id,
           starttime 
         from 
           divvy_trips_distances 
         where 
            startdate = '%s' AND (
           (starttime like '%%19:%%')
           OR (starttime like '%%29:%%')
           )
         order by 
           starttime 
        """ % date
    c.execute(q)
    ret = ["from_station_id,to_station_id,starttime"]
    i = 0
    for row in c.fetchall():
      ret.append("%s,%s,%s" % (row[0], row[1], row[2]))
      i += 1
    print i
    return "\n".join(ret)
  get_evening_trips.exposed = True

application = cherrypy.Application(Root(), script_name=None, config=None)
