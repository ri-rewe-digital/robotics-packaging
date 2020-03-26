from copy import copy
from random import random, randint

from chromosome import Chromosome
from configuration import GAParameters
from encode import Decoder, Encoder
from placer import PlacementSolution


# Chromosome = []  # floats


class Solver:
    def __init__(self, generator: Encoder, decoder: Decoder, parameters: GAParameters):
        self.encoder = generator
        self.decoder = decoder
        self.parameters = parameters
        self.population = []  # Vec<IndividualSolution<D::Solution>>
        self.population1 = []  # Vec<IndividualSolution<D::Solution>>

    def solve(self) -> PlacementSolution:
        generation = 0
        generations_no_improvement = 0
        self.init_first_generation()

        while generation < self.parameters.max_generations and \
                generations_no_improvement < self.parameters.max_generations_no_improvement:
            prev_fitness = self.population[0].fitness
            self.evolve_new_generation()
            curr_fitness = self.population[0].fitness
            if curr_fitness < prev_fitness:
                generations_no_improvement = 0
            else:
                generations_no_improvement += 1
            generation += 1

        return self.population[0].solution

    def crossover(self, elite: Chromosome, non_elite: Chromosome) -> Chromosome:
        offspring = Chromosome(elite.number_of_boxes)
        for i in range(0, len(elite)):
            prob = random()
            if prob <= self.parameters.inherit_elite_probability:
                offspring.append(elite[i])
            else:
                offspring.append(non_elite[i])
        return offspring

    def pickup_parents_for_crossover(self) -> (Chromosome, Chromosome):
        elite_size = self.parameters.num_elites
        non_elite_size = self.parameters.population_size - elite_size
        elite = self.population[randint(0, elite_size - 1)]
        non_elite_id = elite_size + randint(0, non_elite_size - 1)
        if non_elite_id >= len(self.population):
            print("WHAT?")
        non_elite = self.population[non_elite_id]

        return elite.chromosome, non_elite.chromosome

    @staticmethod
    def sort_population(population):
        population.sort(key=lambda c: c.fitness)

    def init_first_generation(self):
        self.population.extend(self.decoder.initialize_first_generation(self.parameters.population_size, self.encoder))
        Solver.sort_population(self.population)

    def evolve_new_generation(self):
        num_elites = self.parameters.num_elites
        num_mutants = self.parameters.num_mutants
        num_offsprings = self.parameters.population_size - num_elites - num_mutants

        # copy elites to next generation.
        for elite in self.population[0:num_elites]:
            self.population1.append(copy(elite))

        # generate mutants from generator.
        for _ in range(0, num_mutants):
            mutant = self.encoder.encode_individual()
            mutant = self.decoder.decode_individual(mutant)
            self.population1.append(mutant)

        # crossover offsprings.
        for _ in range(0, num_offsprings):
            (elite, non_elite) = self.pickup_parents_for_crossover()
            offspring = self.crossover(elite, non_elite)
            self.population1.append(self.decoder.decode_individual(offspring))

        # sort the new generation and swap backend vec.
        Solver.sort_population(self.population1)
        # TODO: we can reuse the memory of individual's vector inside population vector.
        self.population.clear()
        self.population, self.population1 = self.population1, self.population
