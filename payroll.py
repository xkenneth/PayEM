#!/usr/bin/env python

### Imports ###
import mx.DateTime
import sys
from pybase import Basecamp
from config import *
from helper import *
import pdb
from optparse import OptionParser

from mail import mail

import os

parser = OptionParser()

parser.add_option('-d',"--defaults",dest="defaults",action="store_true",
                  help="use defaults",default=False)

options, args = parser.parse_args()

print options

if not options.defaults:

    while(1):
        answer = raw_input("Use today's date? (y/n)")
        answer = answer.lower()
        if answer == 'y':
            process_date = mx.DateTime.now()
            break
        elif answer == 'n':
            process_date = get_date()
            break
        else:
            pass

else:
    process_date = mx.DateTime.now()

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

if start_date > end_date:
    print "Error, start date is after end date."
    sys.exit(0)

#program starting
print "ProcessDate:", process_date
print "Invoice Period:"
print "Start:",start_date
print "End:",end_date


#connect to basecamp
print "Connecting to Basecamp"
print ""

conn = Basecamp(bc_url,bc_user,bc_pwd)

people = conn.people_id_map(our_company)

print "ID:Name"
for id in people:
    print "%d:%s" % (id,people[id])
print ""

projects = conn.project_id_map()

print "ID:Project"
for id in projects:
    print "%d:%s" % (id,projects[id])

#get all of the time entries
#a hash {project id:[time entires]}
time_entries = dict([(id,[]) for id in projects])

#for each project id
for project in projects:
    print "Retrieving data for %s" % projects[project]
    #get ALL the entires for the project
    entries = conn.get_project_time(project)
    for entry in entries:
        print "%s, %s, %3.2f Hours, on %s." % (projects[entry.project_id].upper(),people[entry.person_id],entry.hours,entry.date.date)
    #for entry in entries.data:
        
    #filter them according to the start and end date
    for entry in entries:
        if entry.date >= start_date and entry.date <= end_date:
            #print "%s, %s, %3.2f Hours, on %s." % (projects[entry.project_id].upper(),people[entry.person_id],entry.hours,entry.date.date)
            time_entries[project].append(entry)
        else:
            pass
            #print "REJECTED: %s, %s, %3.2f Hours on %s." % (projects[entry.project_id].upper(),people[entry.person_id],entry.hours, entry.date.date)

#a hash {employee_id:[time entries]}
hours_by_employee = dict([(id,[]) for id in people])

#for all the entries
for project in time_entries:
    #for each project
    for entry in time_entries[project]:
        #assign hours to the individual employees
        hours_by_employee[entry.person_id].append(entry)

# print a simple summary for each employee and calculate their total hours
total_hours_by_employee = dict([(id,0.0) for id in people])

for id in hours_by_employee:
    print "Employee: %s" % people[id]
    for entry in hours_by_employee[id]:
        print "%3.2f Hours. %s on %s" % (entry.hours, projects[entry.project_id], entry.date.date)
        #sum
        total_hours_by_employee[id] += entry.hours
    print "Total: %d" % total_hours_by_employee[id]


# send the emails! and write the log files
for person in people:

    #write the log file

    log_text = ""
    
    log_text += "%s's hours between %s and %s\n" % (people[person],start_date.date,end_date.date)

    body = ""
    
    print people[person]
    body += "%s,\n" % people[person]
    
    body += """

How are you today? I'm quite well, thank you.

Well now then .. we're processing payroll! You're about to get paid for the hours you worked between %s and %s.

""" % (start_date.date, end_date.date)
    
    for entry in hours_by_employee[person]:
        body += "%3.2f Hours. %s on %s\n" % (entry.hours, projects[entry.project_id], entry.date.date)
        log_text += "%3.2f Hours. %s on %s\n" % (entry.hours, projects[entry.project_id], entry.date.date)
            
    
    #add the total
    
    body += 'Total Hours: %3.2f\n\n' % total_hours_by_employee[person]
    log_text += 'Total Hours: %3.2f\n\n' % total_hours_by_employee[person]


    body += """If this is correct, please reply letting us know! If it's not, please let us know what's wrong!

Thanks!
EM

"""
    
    person_data = conn.get_person(person)
    email_address = person_data.email_address
    
    if debug:
        print email_address
        print body
        print log_text
        # for person in people_summary:
#             for project in people_summary[person]:
#                 if people_summary[person][project] > 0.0:
#                     print "%s: %3.2f Hours.\n" % (our_projects[project],people_summary[person][project])
        
    
    else:
        print "Sending email to %s" % people[person]
        f = open(os.path.join(repo_dir,people[person].strip().replace(' ',''))+'.txt','w')
        f.write(log_text)
        f.close()
        
        mail(email_address, "Erdos Miller - Payroll - Please Verify", body)
