class Parameters:
    def __init__(self, population_factor=30, elites_percentage=0.1, mutants_percentage=0.15,
                 inherit_elite_probability=0.7, max_generations=200, max_generations_no_improvement=5):
        self.population_factor = population_factor
        self.elites_percentage = elites_percentage
        self.mutants_percentage = mutants_percentage
        self.inherit_elite_probability = inherit_elite_probability
        self.max_generations = max_generations
        self.max_generations_no_improvement = max_generations_no_improvement

    @staticmethod
    def from_yaml(config):
        return Parameters(
            config['population_factor'],
            config['elites_percentage'],
            config['mutants_percentage'],
            config['inherit_elite_probability'],
            config['max_generations'],
            config['max_generations_no_improvement'],
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
            max_generations_no_improvement=self.max_generations_no_improvement
        )

    def __repr__(self):
        return "(population_factor=%r, elites_percentage=%r, mutants_percentage=%r, inherit_elite_probability=%r, max_generations=%r, max_generations_no_improvement=%r)" % (
            self.population_factor,
            self.elites_percentage,
            self.mutants_percentage,
            self.inherit_elite_probability,
            self.max_generations,
            self.max_generations_no_improvement,
        )


class GAParameters():
    def __init__(self, population_size, num_elites, num_mutants, inherit_elite_probability, max_generations,
                 max_generations_no_improvement):
        self.max_generations = max_generations
        self.inherit_elite_probability = inherit_elite_probability
        self.max_generations_no_improvement = max_generations_no_improvement
        self.num_mutants = num_mutants
        self.num_elites = num_elites
        self.population_size = population_size
