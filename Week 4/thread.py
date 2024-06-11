import threading
import time
import random

# Requirements:
  # Prints a message when the Philosopher is hungry -> Done
  # begins eating, swaps forks, and finishes eating -> Done
  # Eating takes a random time -> Done
  # Should also have get_forks, put_forks methods -> Done

class Philosopher(threading.Thread):
  def __init__ (self, phil_number, forks, food_lock):
    threading.Thread.__init__(self) # https://stackoverflow.com/questions/7445742/runtimeerror-thread-init-not-called-when-subclassing-threading-thread
    self.phil_number = phil_number
    self.forks = forks
    self.food_eaten_by_philosopher = food_eaten_by_philosopher
    self.food_lock = food_lock
    self.interruptions = interruptions

  def get_forks(self):
    left_fork = self.phil_number
    right_fork = (self.phil_number + 1) % len(self.forks)
    flag = False

    if self.forks[left_fork].acquire(False):
        print(f"Philosopher {self.phil_number} has grabbed the left fork")
        flag = True
    else:
        print(f"Philosopher {self.phil_number} was not able to grab the left fork. They will try again later.")
        time.sleep(random.random())

    if flag:
      if self.forks[right_fork].acquire(False):
        print(f"Philosopher {self.phil_number} has grabbed the right fork")
        return True
      else:
        print(f"Philosopher {self.phil_number} was not able to grab the right fork. They will try again later.")
        self.put_forks()
        self.interruptions[self.phil_number] += 1
        time.sleep(random.random())
        return False
    self.interruptions[self.phil_number] += 1
    return False

  def put_forks(self):
    left_fork = self.phil_number
    right_fork = (self.phil_number + 1) % len(self.forks)

    if self.forks[left_fork].locked():
      self.forks[left_fork].release()
    if self.forks[right_fork].locked():
      self.forks[right_fork].release()

    time.sleep(random.random())

  def run(self):
    global food
    while food > 0:
      print(f"Philosopher {self.phil_number} is hungry")
      if self.get_forks(): # If these return True, do below
        with self.food_lock:
          global food_eaten_by_philosopher
          if food > 0:
            print(f"Philosopher {self.phil_number} is eating")
            food -= 1
            food_eaten_by_philosopher[self.phil_number] += 1
            time.sleep(random.random()) # Sleep a random amount of time after eating
            print(f"Philosopher {self.phil_number} has finished eating")
            self.put_forks()
      else:
        print(f"Philosopher {self.phil_number} is not able to grab both forks. They will wait and try again.")
        self.interruptions[self.phil_number] += 1
        time.sleep(random.random())
      time.sleep(random.random())

forks = []
philosophers = []

food_eaten_by_philosopher = { # I wanted to map all food eaten to make sure distro was even
  0: 0,
  1: 0,
  2: 0,
  3: 0,
  4: 0
}

interruptions = { # Using this to track the viability of the solution
  0: 0,
  1: 0,
  2: 0,
  3: 0,
  4: 0
}

number_of_phil = 5
food = 50
food_lock = threading.Lock()

for i in range(number_of_phil):
  forks.append(threading.Lock())

for i in range(number_of_phil):
  philosophers.append(Philosopher(i, forks, food_lock))

for phil in philosophers:
  phil.start()

for phil in philosophers:
  phil.join()


nl = "\n"
print(f"All food eaten.{nl}{food_eaten_by_philosopher}{nl}{interruptions}")



"""
Bibliography:

This video helped a lot, it gave me the idea to run even and odd philosophers at different times
-> https://www.youtube.com/watch?v=FYUi-u7UWgw&t=131s

I also used the threading documentation directly from Python
-> https://docs.python.org/3/library/threading.html

Dijkstra's solution
-> https://www.geeksforgeeks.org/dining-philosopher-problem-using-semaphores/

"""
