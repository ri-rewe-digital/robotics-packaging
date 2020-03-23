from random import random, randint

from placer import InnerSolution
import numpy as np

Chromosome = []  # floats


class InnerChromosome:
    def __init__(self, chromosome: Chromosome, solution: InnerSolution, fitness: float):
        self.fitness = fitness
        self.solution = solution
        self.chromosome = chromosome


class Parameters:
    population_size: int
    num_elites: int
    num_mutants: int
    inherit_elite_probability: float
    max_generations: int
    max_generations_no_improvement: int


class Decoder:

    def decode_chromosome(self, individual: Chromosome) -> InnerSolution:
        pass

    def fitness_of(self, solution: InnerSolution) -> float:
        pass

    def reset(self):
        pass


class Generator:
    def generate_individual(self) -> Chromosome:
        pass


class RandGenerator(Generator):
    def __init__(self, length: int):
        self.length = length

    def generate_individual(self) -> []:
        return np.random.random(self.length).tolist()


class Solver:
    def __init__(self, generator: Generator, decoder_factory, parameters: Parameters):
        self.generator = generator
        self.decoder_factory = decoder_factory
        self.parameters = parameters
        self.population = []  # Vec<InnerChromosome<D::Solution>>
        self.population1 = []  # Vec<InnerChromosome<D::Solution>>

    def solve(self) -> InnerSolution:
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
        offspring = []
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
        elite = self.population[randint(0, elite_size)]
        non_elite = self.population[elite_size + randint(0, non_elite_size)]

        return (elite.chromosome, non_elite.chromosome)

    def sort_population(self, population):  # Vec<InnerChromosome<D::Solution>>
        pass
        # TODO: RB: check with vec
        # population.sort_unstable_by(|a, b| a.fitness.partial_cmp(b.fitness).unwrap())

    @staticmethod
    def decode_chromosome(decoder: Decoder, chromosome: Chromosome) -> InnerChromosome:
        solution = decoder.decode_chromosome(chromosome)
        fitness = decoder.fitness_of(solution)
        decoder.reset()

        return InnerChromosome(chromosome, solution, fitness)

    def init_first_generation(self):
        decoder = self.decoder_factory.decoder()
        generator = self.generator
        for i in range(0, self.parameters.population_size):
            self.population.append(self.decode_chromosome(decoder, generator.generate_individual()))
        self.sort_population(self.population)

    def evolve_new_generation(self):
        decoder = self.decoder_factory.decoder()
        num_elites = self.parameters.num_elites
        num_mutants = self.parameters.num_mutants
        num_offsprings = self.parameters.population_size - num_elites - num_mutants

        # copy elites to next generation.
        for elite in self.population[0:num_elites]:
            self.population1.append(elite.clone())

        # generate mutants from generator.
        for _ in range(0, num_mutants):
            mutant = self.generator.generate_individual()
            mutant = self.decode_chromosome(decoder, mutant)
            self.population1.append(mutant)

        # crossover offsprings.
        for _ in range(0, num_offsprings):
            (elite, non_elite) = self.pickup_parents_for_crossover()
            offspring = self.crossover(elite, non_elite)
            self.population1.append(self.decode_chromosome(decoder, offspring))

        # sort the new generation and swap backend vec.
        self.sort_population(self.population1)
        # TODO: we can reuse the memory of individual's vector inside population vector.
        self.population.clear()
        # TODO RB: lookop mem::swap
        self.population, self.population1 = self.population1, self.population
    # mem::swap(&mut self.population, &mut self.population1);
