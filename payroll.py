#!/usr/bin/env python

import mx.DateTime
import sys
from pybase import Basecamp
from config import *
from helper import *

from mail import mail

import os

def get_date(name=''):
    date_str = raw_input('Enter %s Date (YYYY-MM-DD) ' % name)
    year, month, day = date_str.split('-')
    return mx.DateTime.DateTime(int(year),int(month),int(day))

while(1):
    answer = raw_input("Use today's date? (y/n)")
    if answer == 'y':
        process_date = mx.DateTime.now()
        break
    elif answer == 'n':
        process_date = get_date()
        break
    else:
        pass

#report repo
repo_name = "%s_%s_%s" % (process_date.year,process_date.month,process_date.day)
repo_dir = os.path.join(payroll_repository,repo_name)

#create the repo for this run
if not debug:
    os.mkdir(repo_dir)



#for project in conn.get_projects():
#    print project.id

#the previous sunday
end_date = days_ago(previous_sunday(process_date),43)

#the second preceeding monday
start_date = two_weeks_ago(end_date)

#reset to the end of the day
end_date = end_day(end_date)

#reset to the beginning of that day
start_date = start_day(start_date)

#program starting
print "ProcessDate:", process_date
print "Invoice Period:"
print "Start:",start_date
print "End:",end_date


#connect to basecamp
conn = Basecamp(bc_url,bc_user,bc_pwd)

our_people = conn.people_id_map(our_company)
our_projects = conn.project_id_map()


if start_date > end_date:
    print "Error, start date is after end date."
    sys.exit(0)

all_entries = []
summary = {}
people_summary = {}

for project in our_projects:
    #this could run over hours if we de-activate a project
    #project_data = conn.get_project(project)
    #if project_data.status == 'active':
    
    print "Retrieving data for %s" % our_projects[project]
    
    all_entries.extend(conn.get_project_time(project))
    
    summary[project] = {}
    
    
    for person in our_people:
        summary[project][person] = 0.0

for people in our_people:
    people_summary[people] = {}
    for project in our_projects:
        people_summary[people][project] = 0.0
    

for entry in all_entries:
    if entry.date >= start_date and entry.date <= end_date:
        
        summary[entry.project_id][entry.person_id] += entry.hours

        people_summary[entry.person_id][entry.project_id] += entry.hours
        #print entry.hours, entry.date, our_people[entry.person_id], our_projects[entry.project_id]

#write the log files

for project in summary.keys():
    
    project_summary_path = os.path.join(repo_dir,our_projects[project].replace(' - ','_').replace(' ','_'))
    
    if not debug:
        summary_file = open(project_summary_path,'w+')
    
    
    summary_body = "Project %s\n\n" % our_projects[project]
    
    for person in summary[project]:
        if summary[project][person] > 0.0:
            summary_body += "%s\t%s\n" % (our_people[person], summary[project][person])

    if not debug:
        summary_file.write(summary_body)

#send the emails
print people_summary



for person in people_summary:
    body = ""
    
    print our_people[person]
    body += "%s,\n" % our_people[person]
    
    body += """

We're processing payroll! Here's your work summary for the following dates:

Start Date: %s

End Date: %s



""" % (str(start_date), str(end_date))
    
    for project in people_summary[person]:
        if people_summary[person][project] > 0.0:
            body += "%s: %f Hours.\n" % (our_projects[project],people_summary[person][project])

    body += """

If this is correct, please let Ken know! If it's not, fix it, and then let Ken know!

Thanks!
Erdos Miller

"""
    
    person_data = conn.get_person(person)
    email_address = person_data.email_address
    
    print "Sending email to %s" % our_people[person]
    
    if debug:
        print email_address
        print body
    else:
        mail(email_address, "Erdos Miller - Payroll - Please Verify", body)
