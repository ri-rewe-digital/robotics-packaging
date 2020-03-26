import queue
import threading
import time

from chromosome import Chromosome
from encode import IndividualSolution, GADecoder
from genetic_algorithms import Solver
from geometry import Cuboid
from placer import Placer


class PlacerThread(threading.Thread):
    def __init__(self, placer: Placer, individual_queue, queue_lock):
        threading.Thread.__init__(self)
        self.placer = placer
        self.individual_queue = individual_queue
        self.solutions = []
        self.exit_flag = 0
        self.queue_lock = queue_lock

    def run(self):
        while not self.exit_flag:
            self.queue_lock.acquire()
            individual = None
            if not self.individual_queue.empty():
                individual = self.individual_queue.get()
                self.queue_lock.release()
            else:
                self.queue_lock.release()
            if individual is not None:
                solution = self.placer.place_boxes(individual)
                fitness = solution.fitness_for(self.placer.container_spec.volume())
                self.solutions.append(IndividualSolution(individual, solution, fitness))
            time.sleep(1)


class MultithreadedGADecoder(GADecoder):
    def __init__(self, product_boxes, bin_specification: Cuboid, number_of_threads: int):
        GADecoder.__init__(product_boxes, bin_specification)
        self.number_of_threads = number_of_threads

    def initialize_first_generation(self, population_size, encoder):
        population = []
        individual_queue = queue.Queue(population_size)
        thread_lock = threading.Lock()
        worker_threads = []

        for i in range(0, self.number_of_threads):
            placer_thread = PlacerThread(self.placer, individual_queue, thread_lock)
            placer_thread.start()
            worker_threads.append(placer_thread)

        thread_lock.acquire()
        for i in range(0, population_size):
            individual_queue.put(encoder.encode_individual())
        thread_lock.release()

        while not individual_queue.empty():
            pass

        for worker in worker_threads:
            worker.exit_flag = 1
        for worker in worker_threads:
            worker.join()
        for worker in worker_threads:
            population.extend(worker.solutions)
        # population.append(self.decode_individual(encoder.encode_individual()))
