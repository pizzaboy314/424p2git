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
      ret.append("%s,%s" % (row[0], row[1]))
    return "\n".join(ret)
  rides_by_day_of_year.exposed = True
    
  def gender(self,
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
    for row in c.fetchall():
      ret.append("%s,%d" % (row[0],row[1]))
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
    for row in c.fetchall():
      ret.append("%s,%d" % (row[0],row[1]))
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

  def avg_days_of_week(start='2013-06-26', 
                       end='2013-12-31',
                       time_of_day=None, 
                       gender=None,
                       subscriber=None,
                       age=None,
                       stations=None):
    pass

  def avg_dist_traveled(start='2013-06-26', 
                       end='2013-12-31', 
                       time_of_day=None,
                       gender=None,
                       subscriber=None,
                       age=None,
                       stations=None):
    pass

  def avg_trip_length(start='2013-06-26', 
                       end='2013-12-31', 
                       time_of_day=None,
                       gender=None,
                       subscriber=None,
                       age=None,
                       stations=None):
    pass

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
      ret.append("%s,%s" % (row[0], row[1]))
    return "\n".join(ret)

  bikes_out_by_day.exposed = True

  def hour_of_day(self, date=None,
                  gender=None,
                  subscriber=None,
                  age=None,
                  stations=None):
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
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
    # lets do some ghetto caching
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
 
    days =  {"Sunday":0, 
            "Monday":0, 
            "Tuesday":0, 
            "Wednesday":0, 
            "Thursday":0, 
            "Friday":0, 
            "Saturday":0 }
    for row in sql:
      days[row[1].strftime("%A")] += 1
    for day, count in days.items():
      ret.append('{"range":"%s", "frequency":"%d"},' % (day, count))
    ret[len(ret)-1] = ret[len(ret)-1].rstrip(",")
    ret.append("]")    
    with open ("%s/%s_trip_id_starttime_days.json" % \
      (os.path.join(PATH,"cache"), cache_string), "wb") as f:
      f.write("\n".join(ret)) 
 
    return "\n".join(ret)
  day_of_week.exposed = True

  def weather(self, date, hour):
    dt = parser.parse(date)
    ret = ["icon,temp"]
    with open('%s/weather/%s.pickle' % \
      (PATH, "%s%02d%s" %(dt.year, dt.month, dt.day)), 'rb') as f:
 
      winfo = pickle.load(f)

    ret.append("%s,%s" % winfo[hour])
    return "\n".join(ret)
  weather.exposed = True


application = cherrypy.Application(Root(), script_name=None, config=None)
