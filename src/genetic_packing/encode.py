import math

import numpy as np

from genetic_packing.chromosome import Chromosome
from genetic_packing.placer import PlacementSolution, Placer


class IndividualSolution:
    def __init__(self, chromosome: Chromosome, solution: PlacementSolution, fitness: float):
        self.fitness = fitness
        self.solution = solution
        self.chromosome = chromosome


class Decoder:

    def decode_individual(self, individual) -> IndividualSolution:
        pass

    def decode_population(self, individuals: []):
        pass


class GADecoder(Decoder):
    def __init__(self, placer: Placer):
        self.placer = placer

    def decode_individual(self, individual: Chromosome) -> IndividualSolution:
        solution = self.placer.place_boxes(individual)
        print("all boxes placed: {}".format(solution))
        fitness = solution.fitness_for(self.placer.get_target_bin_volume())
        return IndividualSolution(individual, solution, fitness)

    def decode_population(self, individuals: []):
        solutions = []
        for individual in individuals:
            solutions.append(self.decode_individual(individual))
        return solutions


class Encoder:
    def encode_individual(self) -> Chromosome:
        pass

    def encode_individuals(self, number_of_individuals):
        pass


class RandEncoder(Encoder):
    def __init__(self, length: int):
        self.length = length

    def encode_individual(self) -> Chromosome:
        result = Chromosome(math.floor(self.length * 0.5))
        result.set_genes(np.random.random(self.length).tolist())
        return result

    def encode_individuals(self, number_of_individuals):
        individuals = []
        for i in range(0, number_of_individuals):
            individuals.append(self.encode_individual())
        return individuals
