import threading
import time
import random

class Philosopher(threading.Thread):
  def __init__ (self, phil_number, forks, food_lock):
    threading.Thread.__init__(self) # https://stackoverflow.com/questions/7445742/runtimeerror-thread-init-not-called-when-subclassing-threading-thread
    self.phil_number = phil_number
    self.forks = forks
    self.food_eaten_by_philosopher = food_eaten_by_philosopher
    self.food_lock = food_lock

  def run(self):
    left_fork = self.phil_number
    right_fork = (self.phil_number + 1) % len(self.forks)
    global food
    while food > 0:

      """
      We add these if statements to check if both forks are obtainable. If they are not,
      we put the philsopher to sleep and make then try again at a random interval.
      I found this approach the easiest. It's almost like this Dijkstra guy knew what we was talking about.

      Initially I thought an odd and even strategy would be best with the philsophers. Evens being greedy and always
      holding one fork, odds being generous and releasing the fork they were holding if they could not obtain the other.
      This was nice, but it was a lot more code to write. It also doesn't seem to be as fair.

      Here is a link to my GitHub history with the original implementation if you'd like to take a look:
        -> https://github.com/andjrue/CSC410/commit/62aaf0e0b88ef2edaadba5c3baf72d19ad041361

      The distribution for the method below is much more balanced, and appears to get better as the "amount of food"
      increases.

      I also intially put all of the sleeps to 1 second, but it took forever to run. random.random() makes it
      much quicker and more testable.
      """

      if self.forks[left_fork].acquire(False):
        print(f"Philosopher {self.phil_number} has grabbed the left fork")
        if self.forks[right_fork].acquire(False):
          print(f"Philosopher {self.phil_number} is now holding both forks")

          with self.food_lock:
            global food_eaten_by_philosopher
            if food > 0:
              print(f"Philsopher {self.phil_number} is eating")
              food -= 1
              food_eaten_by_philosopher[self.phil_number] += 1

          self.forks[left_fork].release()
          self.forks[right_fork].release()

          print(f"Philosopher {self.phil_number} has released their forks")
        else:
          print(f"{self.phil_number} was not able to grab the right fork, they will wait and try again")
          self.forks[left_fork].release()
          time.sleep(random.random())
          self.run()
      else:
        print(f"{self.phil_number} was not able to grab the left fork, they will wait and try again")
        time.sleep(random.random())
        self.run()
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
print(f"All food eaten.{nl}{food_eaten_by_philosopher}")



"""
Bibliography:

This video helped a lot, it gave me the idea to run even and odd philosophers at different times
-> https://www.youtube.com/watch?v=FYUi-u7UWgw&t=131s

I also used the threading documentation directly from Python
-> https://docs.python.org/3/library/threading.html

Dijkstra's solution
-> https://www.geeksforgeeks.org/dining-philosopher-problem-using-semaphores/

"""
