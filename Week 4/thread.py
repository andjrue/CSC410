import threading
import time
import random

# Requirements:
  # Prints a message when the Philosopher is hungry -> Done
  # begins eating, swaps forks, and finishes eating -> Done
  # Eating takes a random time -> Done
  # Should also have get_forks, put_forks methods -> Done

"""
I tried my best to write an original solution to this problem. After a bunch of research, I thought the "leave one philosopher
out" approach would be best. The semaphore below ensures that only 4 philosophers can attempt to pick up forks at one time,
this removes the potential for deadlock.
"""

class Philosopher(threading.Thread):
  def __init__ (self, phil_number, forks, food_lock, permission):
    threading.Thread.__init__(self) # https://stackoverflow.com/questions/7445742/runtimeerror-thread-init-not-called-when-subclassing-threading-thread
    self.phil_number = phil_number
    self.forks = forks
    self.food_eaten_by_philosopher = food_eaten_by_philosopher
    self.food_lock = food_lock
    self.permission = permission


  def get_forks(self):
    left_fork = self.phil_number
    right_fork = (self.phil_number + 1) % len(self.forks)

    with self.permission: # Ensures the philosopher has permission to eat
      self.forks[left_fork].acquire()
      print(f"Philosopher {self.phil_number} has grabbed the left fork")
      self.forks[right_fork].acquire()
      print(f"Philosopher {self.phil_number} has grabbed the Right fork")

  def put_forks(self):
    left_fork = self.phil_number
    right_fork = (self.phil_number + 1) % len(self.forks)

    self.forks[left_fork].release()
    print(f"Philosopher {self.phil_number} has put down the left fork")
    self.forks[right_fork].release()
    print(f"Philosopher {self.phil_number} has put down the right fork")
    time.sleep(random.random())

  def run(self):
    global FOOD
    while FOOD > 0:
        print(f"Philosopher {self.phil_number} is hungry")
        self.get_forks() # Need to grab the forks here
        with self.food_lock:
          global food_eaten_by_philosopher
          if FOOD > 0:
            print(f"Philosopher {self.phil_number} is eating")
            FOOD -= 1
            food_eaten_by_philosopher[self.phil_number] += 1
            time.sleep(random.random()) # Sleep a random amount of time after eating
            print(f"Philosopher {self.phil_number} has finished eating")
        self.put_forks()
        time.sleep(random.random())

forks = []
philosophers = []
semaphores = [threading.Semaphore(0) for _ in range(5)] # https://www.youtube.com/watch?v=91_RHE_U3t4

food_eaten_by_philosopher = { # I wanted to map all food eaten to make sure distro was even
  0: 0,
  1: 0,
  2: 0,
  3: 0,
  4: 0
}

number_of_phil = 5
FOOD = 5000
food_lock = threading.Lock()
permission = threading.Semaphore(4) # https://www.geeksforgeeks.org/synchronization-by-using-semaphore-in-python/
# This gave me the idea for leaving one philsopher out and using Semaphores

for i in range(number_of_phil):
  forks.append(threading.Lock())

for i in range(number_of_phil):
  philosophers.append(Philosopher(i, forks, food_lock, permission))

for phil in philosophers:
  phil.start()

for phil in philosophers:
  phil.join()


nl = "\n"
print(f"All food eaten.{nl}{food_eaten_by_philosopher}")

"""
Bibliography:

Not listed anywhere specifically are the official Python docs, I referenced these quite a bit
-> https://docs.python.org/3/library/threading.html

Stallings Solution:
->
https://en.wikipedia.org/wiki/Dining_philosophers_problem#:~:text=Concurrent%20algorithm%20design-,Limiting%20the%20number%20of%20diners%20in%20the%20table,requests%20access%20to%20any%20fork.
"""
