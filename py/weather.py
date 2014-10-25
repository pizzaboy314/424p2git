import urllib2 
import json 
from pprint import pprint
import pickle
from dateutil import parser
from datetime import timedelta
from collections import OrderedDict
import sys

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


if not sys.argv[1]:
  print "uh oh"
  startdate = '20130711'
  enddate = '20130712'
else:
  startdate = sys.argv[1]
  enddate = sys.argv[2]

sdt = parser.parse(startdate)
edt = parser.parse(enddate)

for date in daterange(sdt, edt):
  date = "%s%02d%02d" % (date.year, date.month, date.day)
  f = urllib2.urlopen('http://api.wunderground.com/api/9d7e28be82bf1469/history_%s/conditions/q/IL/Chicago.json' % date) 

  json_string = f.read() 
  parsed_json = json.loads(json_string) 
  w = OrderedDict()
  for i in parsed_json['history']['observations']:
    w[i['date']['hour']] = (i['icon'], i['tempi'])

  with open('/home/mt/src/git/p2git/py/weather/%s.pickle' % date, 'wb') as fi:
    pickle.dump(w, fi)
  f.close()
