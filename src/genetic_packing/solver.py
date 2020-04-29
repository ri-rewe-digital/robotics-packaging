from copy import copy
from random import random, randint

import numpy as np

from genetic_packing.chromosome import Chromosome
from genetic_packing.encode import GADecoder, RandEncoder, Encoder, Decoder
from genetic_packing.geometry import Space, Cuboid, Point
from genetic_packing.placement import PlacementFactory
from genetic_packing.placer import PlacementSolution, Placer
from genetic_packing.plott import plot_solution
from genetic_packing.threadz import MultithreadedGADecoder


class Solver:
    def __init__(self, generator: Encoder, decoder: Decoder, parameters: dict):
        self.encoder = generator
        self.decoder = decoder
        self.parameters = parameters
        self.num_elites = parameters['num_elites']
        self.non_elite_size = parameters['population_size'] - self.num_elites
        self.num_mutants = parameters['num_mutants']
        self.num_offsprings = self.non_elite_size - self.num_mutants
        self.elite_probability = self.parameters['inherit_elite_probability']

    def solve(self) -> PlacementSolution:
        generation = 0
        generations_no_improvement = 0
        population = self.__init_first_generation(self.parameters['population_size'])

        while generation < self.parameters['max_generations'] and \
                generations_no_improvement < self.parameters['max_generations_no_improvement']:
            prev_fitness = population[0].fitness
            population = self.__evolve_new_generation(population)
            curr_fitness = population[0].fitness
            if curr_fitness < prev_fitness:
                generations_no_improvement = 0
            else:
                generations_no_improvement += 1
            generation += 1

        return population[0].solution

    def __crossover(self, elite: Chromosome, non_elite: Chromosome) -> Chromosome:
        offspring = Chromosome(elite.number_of_boxes)
        for i in range(0, len(elite)):
            prob = random()
            if prob <= self.elite_probability:
                offspring.append(elite[i])
            else:
                offspring.append(non_elite[i])
        return offspring

    def __pickup_parents_for_crossover(self, population) -> (Chromosome, Chromosome):
        elite = population[randint(0, self.num_elites - 1)]
        non_elite_id = self.num_elites + randint(0, self.non_elite_size - 1)
        non_elite = population[non_elite_id]
        return elite.chromosome, non_elite.chromosome

    @staticmethod
    def __sort_population(population):
        population.sort(key=lambda c: c.fitness)

    def __init_first_generation(self, population_size) -> []:
        population = self.decoder.decode_population(self.encoder.encode_individuals(population_size))
        Solver.__sort_population(population)
        return population

    def __evolve_new_generation(self, population):
        next_generation = []

        # copy elites to next generation.
        for elite in population[0:self.num_elites]:
            next_generation.append(copy(elite))

        # generate mutants from generator.
        next_generation.extend(self.decoder.decode_population(self.encoder.encode_individuals(self.num_mutants)))

        # crossover offsprings.
        offspring = []
        for _ in range(0, self.num_offsprings):
            (elite, non_elite) = self.__pickup_parents_for_crossover(population)
            offspring.append(self.__crossover(elite, non_elite))

        next_generation.extend(self.decoder.decode_population(offspring))

        Solver.__sort_population(next_generation)
        return next_generation


class SolutionPlacement:
    def __init__(self, space: Space, box_id):
        self.space = space
        self.box_id = box_id

    def __repr__(self):
        return "id: {}, location: {}".format(self.box_id, self.space)


def __calculate_genetic_parameters(parameters: dict, num_items: int):
    parameters['population_size'] = parameters['population_factor'] * num_items
    parameters['num_elites'] = int(parameters['elites_percentage'] * parameters['population_size'])
    parameters['num_mutants'] = int(parameters['mutants_percentage'] * parameters['population_size'])
    if parameters['delivery_bin_spec'] is None:
        parameters['delivery_bin_spec'] = [30, 30, 30]
    parameters['delivery_bin_spec'] = Cuboid(Point(np.array(parameters['delivery_bin_spec'])))
    return parameters


def solve_packing_problem(parameters: dict, product_boxes: [], plot: bool = False) -> dict:
    encoder = RandEncoder(len(product_boxes) * 2)
    ga_params = __calculate_genetic_parameters(parameters, len(product_boxes))
    placer = Placer(product_boxes,
                    ga_params['delivery_bin_spec'],
                    PlacementFactory.placement_strategy_for_key(key=ga_params['placement_strategy'], parameters=ga_params))
    if ga_params['number_of_threads'] > 0:
        decoder = MultithreadedGADecoder(placer, ga_params['number_of_threads'])
    else:
        decoder = GADecoder(placer)
    solver = Solver(encoder, decoder, ga_params)
    solution = solver.solve()

    delivery_bins = dict()
    if solution:
        for inner_placement in solution.placements:
            idx = inner_placement.bin_number
            space = inner_placement.space
            item_idx = inner_placement.box_index
            if idx not in delivery_bins:
                delivery_bins[idx] = []
            delivery_bins[idx].append(SolutionPlacement(space, item_idx))
        if plot:
            plot_solution(ga_params['delivery_bin_spec'], delivery_bins, False)
    return delivery_bins
