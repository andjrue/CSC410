#! /usr/bin/env python

import sys
from optparse import OptionParser
import random
import heapq

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
            print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' % (
            thetime, job[0], job[1], thetime + job[1]))
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
                print('  [ time %3d ] Run job %3d for %.2f secs ( DONE at %.2f )' % (
                thetime, jobnum, ranfor, thetime + ranfor))
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
            print(
                '  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (i, response[i], turnaround[i], wait[i]))
        count = len(joblist)

        print('\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (
            responseSum / count, turnaroundSum / count, waitSum / count))

    # STCF starts here

    if options.policy == 'STCF':
        turnaround = {}
        response = {}
        wait = {}
        remaining_time = {}
        job_arrival_time = {}
        completion_time = {}
        heap = []  # You could also call this a priority queue
        # Heap idea from -> https://stackoverflow.com/questions/69340417/python-cpu-scheduler-simulator
        the_time = 0.0
        job_count = len(joblist)
        jobs_in_heap = set()  # Need to keep track of potential duplicates, process was stuck in a loop before this was added

        for i in joblist:
            job_num = i[0]
            turnaround[job_num] = 0.0
            response[job_num] = -1  # Flags jobs that have not run, stolen from RR
            wait[job_num] = 0.0
            remaining_time[job_num] = i[1]
            job_arrival_time[job_num] = i[2]
            # print(f"Hello, this if your object: {i}") Debug

        runlist = []
        for e in joblist:
            runlist.append(e)

        while job_count > 0:
            for job in joblist:
                job_number = job[0]
                if job_arrival_time[job_number] <= the_time and remaining_time[job_number] > 0 and job_number not in jobs_in_heap:
                    heapq.heappush(heap, (remaining_time[job_number], job_number))
                    jobs_in_heap.add(job_number)
                    # print(f"Objects added to Heap: {heap}")

            if heap:
                runtime, job_number = heapq.heappop(heap)
                # print(f"Objects removed from Heap: {heap}")
                jobs_in_heap.remove(job_number)
                # print(f"Jobs currently in Heap: {jobs_in_heap}")

                if response[job_number] == -1:  # If the job hasn't run yet...
                    response[job_number] = the_time  # ...set the response to the current time

                print('  [ time %3d ] Run job %3d for %.2f secs' % (the_time, job_number, 1))  # Run the job once
                remaining_time[job_number] -= 1
                the_time += 1

                if remaining_time[job_number] == 0:
                    completion_time[job_number] = the_time
                    turnaround[job_number] = completion_time[job_number] - job_arrival_time[job_number]
                    print(f"Job {job_number} is complete!") # I like this addition, jobs completing jumps out at you
                    job_count -= 1  # Need to subtract the job here, otherwise we never break the while loop

                else:
                    heapq.heappush(heap, (remaining_time[job_number], job_number))
                    jobs_in_heap.add(job_number)

            else:
                print(' [ time %3d ] No jobs to run -> Time taken: %.2f secs' % (the_time, 1))
                the_time += 1

        for job in joblist:
            job_number = job[0]
            wait[job_number] = turnaround[job_number] - job[1]

        print('\nFinal statistics:')  # Stolen from RR
        turnaroundSum = 0.0
        waitSum = 0.0
        responseSum = 0.0
        for i in range(0, len(joblist)):
            turnaroundSum += turnaround[i]
            responseSum += response[i]
            waitSum += wait[i]
            print(
                '  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (i, response[i], turnaround[i], wait[i]))
        count = len(joblist)

        print('\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (
            responseSum / count, turnaroundSum / count, waitSum / count))

    # I believe the math is mathing correctly here. I've been through a bunch of test cases and haven't noticed anything unusual.
    # There might have been a few debugging statements that I didn't comment out, apologies if it prints incorrectly.
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
