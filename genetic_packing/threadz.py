import queue
import threading

import time

from genetic_packing.encode import GADecoder
from genetic_packing.geometry import Cuboid
from genetic_packing.placer import Placer


class PlacerThread(threading.Thread):
    def __init__(self, id, decoder, placer: Placer, individual_queue, queue_lock):
        threading.Thread.__init__(self)
        self.id = id
        self.decoder = decoder
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
                self.solutions.append(self.decoder.decode_individual(individual))

            time.sleep(0.1)


class MultithreadedGADecoder(GADecoder):
    def __init__(self, product_boxes, bin_specification: Cuboid, number_of_threads: int):
        GADecoder.__init__(self, product_boxes, bin_specification)
        self.number_of_threads = number_of_threads

    def decode_population(self, individuals):
        population = []
        individual_queue = queue.Queue(len(individuals))
        thread_lock = threading.Lock()
        worker_threads = []

        for i in range(0, self.number_of_threads):
            placer_thread = PlacerThread(i, self, self.placer, individual_queue, thread_lock)
            placer_thread.start()
            worker_threads.append(placer_thread)

        thread_lock.acquire()
        for individual in individuals:
            individual_queue.put(individual)
        thread_lock.release()

        while not individual_queue.empty():
            pass

        for worker in worker_threads:
            worker.exit_flag = 1
        for worker in worker_threads:
            worker.join()
        for worker in worker_threads:
            population.extend(worker.solutions)
        return population
        # population.append(self.decode_individual(encoder.encode_individual()))
