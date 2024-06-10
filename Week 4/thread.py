import threading
import time

class Philosopher(threading.Thread):
  def __init__ (self, phil_number, forks, food_lock):
    threading.Thread.__init__(self) # https://stackoverflow.com/questions/7445742/runtimeerror-thread-init-not-called-when-subclassing-threading-thread
    self.phil_number = phil_number
    self.forks = forks
    self.food_eaten_by_philosopher = food_eaten_by_philosopher
    self.food_lock = food_lock

  def run(self):
    global food
    while food > 0:
      if self.phil_number % 2 == 0:
        self.run_even()
      else:
        self.run_odd()
      time.sleep(1)

    nl = "\n"
    print(f"All food eaten.{nl}{food_eaten_by_philosopher}")

  def run_even(self):
    left_fork = self.phil_number
    right_fork = (self.phil_number + 1) % len(self.forks)


    self.forks[left_fork].acquire()
    print(f"{self.phil_number} has grabbed the left fork")
    self.forks[right_fork].acquire()
    print(f"{self.phil_number} has grabbed the right fork")

    with self.food_lock:
      global food
      global food_eaten_by_philosopher
      if food > 0:
        print(f"{self.phil_number} is eating")
        food -= 1
        food_eaten_by_philosopher[self.phil_number] += 1

    self.forks[left_fork].release()
    self.forks[right_fork].release() # Need to let the forks go

    print(f"{self.phil_number} has released their forks")

  def run_odd(self):
    left_fork = self.phil_number
    right_fork = (self.phil_number + 1) % len(self.forks)

    if self.forks[left_fork].acquire(False):
      print(f"{self.phil_number} has grabbed the left fork")
      if self.forks[right_fork].acquire(False):
        print(f"{self.phil_number} has picked up the right stick")

        with self.food_lock:
          global food
          global food_eaten_by_philosopher
          if food > 0:
            print(f"{self.phil_number} is eating")
            food -= 1
            food_eaten_by_philosopher[self.phil_number] += 1

        self.forks[left_fork].release()
        self.forks[right_fork].release()

        print(f"{self.phil_number} has released their forks")
      else:
        print(f"{self.phil_number} was not able to grab the right fork, they will wait and try again")
        self.forks[left_fork].release()
        time.sleep(1)
        self.run()
    else:
      print(f"{self.phil_number} was not able to grab the left fork, they will wait and try again")
      time.sleep(1)
      self.run()


forks = []
philosophers = []

food_eaten_by_philosopher = { # I wanted to map all food eaten to make sure there was as even a distro as possible
  0: 0,
  1: 0,
  2: 0,
  3: 0,
  4: 0
}

number_of_phil = 5
food = 500
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

"""
