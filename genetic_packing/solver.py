from copy import copy
from random import random, randint

from genetic_packing.chromosome import Chromosome
from genetic_packing.configuration import Parameters, GAParameters
from genetic_packing.encode import GADecoder, RandEncoder, Encoder, Decoder
from genetic_packing.geometry import Space
from genetic_packing.placer import PlacementSolution
from genetic_packing.threadz import MultithreadedGADecoder
from genetic_packing.plott import plot_solution


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
        self.population.extend(
            self.decoder.decode_population(self.encoder.encode_individuals(self.parameters.population_size)))
        Solver.sort_population(self.population)

    def evolve_new_generation(self):
        num_elites = self.parameters.num_elites
        num_mutants = self.parameters.num_mutants
        num_offsprings = self.parameters.population_size - num_elites - num_mutants

        # copy elites to next generation.
        for elite in self.population[0:num_elites]:
            self.population1.append(copy(elite))

        # generate mutants from generator.
        self.population1.extend(self.decoder.decode_population(self.encoder.encode_individuals(num_mutants)))

        # crossover offsprings.
        offspring = []
        for _ in range(0, num_offsprings):
            (elite, non_elite) = self.pickup_parents_for_crossover()
            offspring.append(self.crossover(elite, non_elite))

        self.population1.extend(self.decoder.decode_population(offspring))

        # sort the new generation and swap backend vec.
        Solver.sort_population(self.population1)
        # TODO: we can reuse the memory of individual's vector inside population vector.
        self.population.clear()
        self.population, self.population1 = self.population1, self.population


class SolutionPlacement:
    def __init__(self, space: Space, box_id):
        self.space = space
        self.box_id = box_id

    def __repr__(self):
        return "id: {}, location: {}".format(self.box_id, self.space)


def __solve_multi(product_boxes, ga_params, generator):
    multi_solver = Solver(generator, MultithreadedGADecoder(product_boxes, ga_params.delivery_bin_spec,
                                                            ga_params.number_of_threads), ga_params)
    return multi_solver.solve()


def __solve_single(product_boxes, ga_params, generator):
    multi_solver = Solver(generator, GADecoder(product_boxes, ga_params.delivery_bin_spec), ga_params)
    return multi_solver.solve()


def solve_packing_problem(parameters: Parameters, product_boxes: [], plot: bool = False) -> dict:
    generator = RandEncoder(len(product_boxes) * 2)
    ga_params = parameters.get_ga_params(len(product_boxes))
    solution = __solve_multi(product_boxes, ga_params, generator)

    delivery_bins = dict()
    if solution:
        for inner_placement in solution.placements:
            idx = inner_placement.bin_number
            space = inner_placement.space
            item_idx = inner_placement.box_index
            if not delivery_bins or delivery_bins[idx] is None:
                delivery_bins[idx] = []
            delivery_bins[idx].append(SolutionPlacement(space, item_idx))
        if plot:
            plot_solution(ga_params.delivery_bin_spec, delivery_bins, False)
    return delivery_bins
