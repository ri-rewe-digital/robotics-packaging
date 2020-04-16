import numpy as np

from genetic_packing.geometry import Cuboid, Point


class Parameters:
    def __init__(self, population_factor=30, elites_percentage=0.1, mutants_percentage=0.15,
                 inherit_elite_probability=0.7, max_generations=200, max_generations_no_improvement=5,
                 number_of_threads=10,
                 delivery_bin_spec=None):
        self.population_factor = population_factor
        self.elites_percentage = elites_percentage
        self.mutants_percentage = mutants_percentage
        self.inherit_elite_probability = inherit_elite_probability
        self.max_generations = max_generations
        self.max_generations_no_improvement = max_generations_no_improvement
        self.number_of_threads = number_of_threads
        if delivery_bin_spec is None:
            delivery_bin_spec = [30, 30, 30]
        self.delivery_bin_spec = Cuboid(Point(np.array(delivery_bin_spec)))

    @staticmethod
    def from_yaml(config):
        return Parameters(
            config['population_factor'],
            config['elites_percentage'],
            config['mutants_percentage'],
            config['inherit_elite_probability'],
            config['max_generations'],
            config['max_generations_no_improvement'],
            config['number_of_threads'],
            config['delivery_bin_spec']
        )

    def get_ga_params(self, num_items: int):
        population_size = self.population_factor * num_items
        num_elites = int(self.elites_percentage * float(population_size))
        num_mutants = int(self.mutants_percentage * float(population_size))
        return GAParameters(
            population_size,
            num_elites,
            num_mutants,
            inherit_elite_probability=self.inherit_elite_probability,
            max_generations=self.max_generations,
            max_generations_no_improvement=self.max_generations_no_improvement,
            number_of_threads=self.number_of_threads,
            delivery_bin_spec=self.delivery_bin_spec
        )

    def __repr__(self):
        return "(population_factor=%r, " \
               "elites_percentage=%r, " \
               "mutants_percentage=%r, " \
               "inherit_elite_probability=%r, " \
               "max_generations=%r, " \
               "max_generations_no_improvement=%r, " \
               "number_of_threads=%r, " \
               "delivery_bin_spec=%r" \
               ")" % (
                   self.population_factor,
                   self.elites_percentage,
                   self.mutants_percentage,
                   self.inherit_elite_probability,
                   self.max_generations,
                   self.max_generations_no_improvement,
                   self.number_of_threads,
                   self.delivery_bin_spec
               )


class GAParameters:
    def __init__(self, population_size, num_elites, num_mutants, inherit_elite_probability, max_generations,
                 max_generations_no_improvement, number_of_threads, delivery_bin_spec):
        self.max_generations = max_generations
        self.inherit_elite_probability = inherit_elite_probability
        self.max_generations_no_improvement = max_generations_no_improvement
        self.num_mutants = num_mutants
        self.num_elites = num_elites
        self.population_size = population_size
        self.number_of_threads = number_of_threads
        self.delivery_bin_spec = delivery_bin_spec
