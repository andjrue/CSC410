#! /usr/bin/env python

import sys
from optparse import OptionParser
import random

parser = OptionParser()
parser.add_option("-s", "--seed", default=0, help="the random seed",
                  action="store", type="int", dest="seed")
parser.add_option("-j", "--jobs", default=3, help="number of jobs in the system",
                  action="store", type="int", dest="jobs")
parser.add_option("-l", "--jlist", default="",
                  help="instead of random jobs, provide a comma-separated list of run times",
                  action="store", type="string", dest="jlist")
parser.add_option("-m", "--maxlen", default=10, help="max length of job",
                  action="store", type="int", dest="maxlen")
parser.add_option("-p", "--policy", default="FIFO", help="sched policy to use: SJF, FIFO, RR, STCF",
                  action="store", type="string", dest="policy")
parser.add_option("-q", "--quantum", help="length of time slice for RR policy", default=1,
                  action="store", type="int", dest="quantum")
parser.add_option("-c", help="compute answers for me", action="store_true", default=False, dest="solve")

(options, args) = parser.parse_args()

random.seed(options.seed)

print('ARG policy', options.policy)
if options.jlist == '':
  print('ARG jobs', options.jobs)
  print('ARG maxlen', options.maxlen)
  print('ARG seed', options.seed)
else:
  print('ARG jlist', options.jlist)

print('')

print('Here is the job list, with the run time of each job: ')

import operator

joblist = []
if options.jlist == '':
  for jobnum in range(0, options.jobs):
    # Added Run Time and Start Time for debugging, makes the sort easier later on
    runtime = int(options.maxlen * random.random()) + 1
    starttime = int(options.maxlen * random.random())
    joblist.append([jobnum, runtime, starttime])
    print('  Job', jobnum, '( length = ' + str(runtime) + ')', '(Start Time = ' + str(starttime) + ')')
else:
  jobnum = 0
  for runtime in options.jlist.split(','):
    joblist.append([jobnum, float(runtime)])
    jobnum += 1
  for job in joblist:
    print('  Job', job[0], '( length = ' + str(job[1]) + ' )')
print('\n')

if options.solve == True:
  print('** Solutions **\n')
  if options.policy == 'SJF':
    joblist = sorted(joblist, key=operator.itemgetter(1))
    options.policy = 'FIFO'

  if options.policy == 'FIFO':
    thetime = 0
    print('Execution trace:')
    for job in joblist:
      print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' % (thetime, job[0], job[1], thetime + job[1]))
      thetime += job[1]

    print('\nFinal statistics:')
    t = 0.0
    count = 0
    turnaroundSum = 0.0
    waitSum = 0.0
    responseSum = 0.0
    for tmp in joblist:
      jobnum = tmp[0]
      runtime = tmp[1]

      response = t
      turnaround = t + runtime
      wait = t
      print('  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (jobnum, response, turnaround, wait))
      responseSum += response
      turnaroundSum += turnaround
      waitSum += wait
      t += runtime
      count = count + 1
    print('\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (
      responseSum / count, turnaroundSum / count, waitSum / count))

  if options.policy == 'RR':
    print('Execution trace:')
    turnaround = {}
    response = {}
    lastran = {}
    wait = {}
    quantum = float(options.quantum)
    jobcount = len(joblist)
    for i in range(0, jobcount):
      lastran[i] = 0.0
      wait[i] = 0.0
      turnaround[i] = 0.0
      response[i] = -1

    runlist = []
    for e in joblist:
      runlist.append(e)

    thetime = 0.0
    while jobcount > 0:
      # print '%d jobs remaining' % jobcount
      job = runlist.pop(0)
      jobnum = job[0]
      runtime = float(job[1])
      if response[jobnum] == -1:
        response[jobnum] = thetime
      currwait = thetime - lastran[jobnum]
      wait[jobnum] += currwait
      if runtime > quantum:
        runtime -= quantum
        ranfor = quantum
        print('  [ time %3d ] Run job %3d for %.2f secs' % (thetime, jobnum, ranfor))
        runlist.append([jobnum, runtime])
      else:
        ranfor = runtime;
        print('  [ time %3d ] Run job %3d for %.2f secs ( DONE at %.2f )' % (thetime, jobnum, ranfor, thetime + ranfor))
        turnaround[jobnum] = thetime + ranfor
        jobcount -= 1
      thetime += ranfor
      lastran[jobnum] = thetime

    print('\nFinal statistics:')
    turnaroundSum = 0.0
    waitSum = 0.0
    responseSum = 0.0
    for i in range(0, len(joblist)):
      turnaroundSum += turnaround[i]
      responseSum += response[i]
      waitSum += wait[i]
      print('  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (i, response[i], turnaround[i], wait[i]))
    count = len(joblist)

    print('\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (
      responseSum / count, turnaroundSum / count, waitSum / count))

  # STCF starts here

  if options.policy == 'STCF':
    turnaround = {}
    response = {}
    wait = {}
    remaining_time = {}  # Need a place to hold remaining time
    job_arrival_time = {}
    completion_time = {} # Need a place to hold the completion time of a task
    thetime = 0.0
    '''
    time_increase = 2 <-- I thought this would be really cool to add. Unfortunately, the program explodes if 
    the time isn't set to 1 at all times. I imagine it has something to do with some start times not being available
    if we don't "check every second". 
    
    For example: If something has a start time of 2, but we increment time by 3, then the computer doesn't actually recognize 
    the program should've started at the second "tick" and actually should have run for a second. I'll leave it at 1 for now,
    it would be possible to add a check for that but it's Wednesday and I'm running low on time. 
    '''
    jobcount = len(joblist)

    for job in joblist:
      job_number = job[0]  # Grabs the job number so we can easily keep track
      remaining_time[job_number] = job[1] # Maps to remaining_time
      wait[job_number] = 0.0
      turnaround[job_number] = 0.0
      response[job_number] = -1 # Stole this from RR
      job_arrival_time[job_number] = job[2]
      # print(remaining_time)
      # print(wait)
      # print(turnaround)
      # print(response)
      # All debugs


    runlist = []
    for e in joblist:
      runlist.append(e)
      # print(runlist)

    while jobcount > 0:
      available_jobs = []
      for job in joblist:
        job_number = job[0]
        if job_arrival_time[job_number] <= thetime and remaining_time[job_number] > 0:
          available_jobs.append(job)

      if available_jobs:
        available_jobs.sort(key=lambda x: remaining_time[x[0]]) # Sorts jobs by remaining time
        # https://www.geeksforgeeks.org/python-sort-tuple-list-by-nth-element-of-tuple/
        current_job = available_jobs[0]
        job_number = current_job[0]
        runtime = remaining_time[job_number]
        # print(f"Available jobs debug: {available_jobs}")

        if response[job_number] == -1: # Stole this from RR as well
          response[job_number] = thetime

        print('  [ time %3d ] Run job %3d for %.2f secs' % (thetime, job_number, 1))
        remaining_time[job_number] -= 1 # After it runs, we can remove the time taken from the remaining time
        thetime += 1 # And increment total time by the time_increase variable

        if remaining_time[job_number] == 0: # Once there is no more remaining time for a job...
          completion_time[job_number] = thetime
          turnaround[job_number] = thetime - job_arrival_time[job_number]
          print(f"Job Number: {job_number} (COMPLETE)") # A nice debug to make sure each job is completed as expected

          jobcount -= 1 # ...We can remove it from the total job count

      else:
        # I added this to keep track of time spent w/o an available job.
        # I found it was pretty useful in some of the test cases I ran. The start time of the first task
        # isn't always 0 and this allowed me to visualize that.
        print('  [ time %3d ] No job run -> Time spent:  %.2f secs' % (thetime, 1))
        thetime += 1 # Increment time by one if no available tasks


    for job in joblist:
      job_number = job[0]
      wait[job_number] = turnaround[job_number] - job[1]
      # print(job[1])

    print('\nFinal statistics:') # Stolen from RR
    turnaroundSum = 0.0
    waitSum = 0.0
    responseSum = 0.0
    for i in range(0, len(joblist)):
      turnaroundSum += turnaround[i]
      responseSum += response[i]
      waitSum += wait[i]
      print('  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (i, response[i], turnaround[i], wait[i]))
    count = len(joblist)

    print('\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (
      responseSum / count, turnaroundSum / count, waitSum / count))

  # I believe the math is mathing correctly here. I've been through a bunch of test cases and haven't noticed anything unusual.

  # STCF ends here

if options.policy != 'FIFO' and options.policy != 'SJF' and options.policy != 'RR' and options.policy != 'STCF':
  print('Error: Policy', options.policy, 'is not available.')
  sys.exit(0)
else:
  print('Compute the turnaround time, response time, and wait time for each job.')
  print('When you are done, run this program again, with the same arguments,')
  print('but with -c, which will thus provide you with the answers. You can use')
  print('-s <somenumber> or your own job list (-l 10,15,20 for example)')
  print('to generate different problems for yourself.')
  print('')
