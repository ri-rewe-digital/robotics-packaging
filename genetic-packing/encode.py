from chromosome import Chromosome
from geometry import Cuboid
from placer import PlacementSolution, Placer


class Decoder:

    def decode_chromosome(self, individual) -> PlacementSolution:
        pass

    def fitness_of(self, solution: PlacementSolution) -> float:
        pass

    def reset(self):
        pass


class GADecoder(Decoder):
    def __init__(self, product_boxes, bin_specification: Cuboid):
        self.product_boxes = product_boxes
        self.bin_volume = bin_specification.volume()
        self.placer = Placer(product_boxes, bin_specification)
        self.bin_specification = bin_specification

    def decode_chromosome(self, individual: Chromosome) -> PlacementSolution:
        return self.placer.place_boxes(individual)

    def fitness_of(self, solution: PlacementSolution) -> float:
        return float(solution.num_bins) + (float(solution.least_load) / float(self.bin_volume))

    def reset(self):
        self.placer.reset()
