import math
import numpy as np

from chromosome import Chromosome
from container import ProductBox
from geometry import Cuboid
from placer import PlacementSolution, Placer


class IndividualSolution:
    def __init__(self, chromosome: Chromosome, solution: PlacementSolution, fitness: float):
        self.fitness = fitness
        self.solution = solution
        self.chromosome = chromosome


class Decoder:

    def decode_individual(self, individual) -> IndividualSolution:
        pass

    def reset(self):
        pass


class GADecoder(Decoder):
    def __init__(self, product_boxes, bin_specification: Cuboid):
        self.product_boxes = [ProductBox(pb) for pb in product_boxes]
        self.placer = Placer(self.product_boxes, bin_specification)
        self.bin_volume = bin_specification.volume()

    def decode_individual(self, individual: Chromosome) -> IndividualSolution:
        solution = self.placer.place_boxes(individual)
        print("all boxes placed: {}".format(solution))
        fitness = solution.fitness_for(self.bin_volume)
        return IndividualSolution(individual, solution, fitness)

    def reset(self):
        pass #self.placer.reset()


class Encoder:
    def encode_individual(self) -> Chromosome:
        pass


class RandEncoder(Encoder):
    def __init__(self, length: int):
        self.length = length

    def encode_individual(self) -> []:
        result = Chromosome(math.floor(self.length * 0.5))
        result.set_genes(np.random.random(self.length).tolist())
        return result
