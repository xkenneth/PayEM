import mx.DateTime
import sys
from pybase import Basecamp
from config import *
from helper import *



def get_date(name=''):

    date_str = raw_input('Enter %s Date (YYYY-MM-DD) ' % name)
    year, month, day = date_str.split('-')
    return datetime.date(int(year),int(month),int(day))


conn = Basecamp(bc_url,bc_user,bc_pwd)

our_people = conn.people_id_map()
our_projects = conn.project_id_map()

#for project in conn.get_projects():
#    print project.id

all_entries = []

today = mx.DateTime.now()

#the previous sunday
end_date = previous_sunday(today)

#the second preceeding monday
start_date = two_weeks_ago(end_date)

#reset to the end of the day
end_date = end_day(end_date)

#reset to the beginning of that day
start_date = start_day(start_date)


if start_date > end_date:
    print "Error, start date is after end date."
    sys.exit(0)

for project in our_projects.keys():
    print "Retrievin data for %s" % our_projects[project]
    all_entries.extend(conn.get_project_time(project))

summary = {}

for project in our_projects.keys():
    summary[project] = {}
    for person in our_people.keys():
        summary[project][person] = 0.0
    
for entry in all_entries:
    if entry.date >= start_date and entry.date <= end_date:
        summary[entry.project_id][entry.person_id] += entry.hours
        #print entry.hours, entry.date, our_people[entry.person_id], our_projects[entry.project_id]

for project in summary.keys():
    print "Project %s" % our_projects[project]

    for person in summary[project].keys():
        if summary[project][person] > 0.0:
            print "%s %f" % (our_people[person], summary[project][person])
