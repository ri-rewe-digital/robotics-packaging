from chromosome import Chromosome
from geometry import Cuboid
from placer import PlacementSolution, Placer


class ProductBox:
    def __init__(self, cuboid: Cuboid):
        self.cuboid = cuboid
        self.smallest_dimension: int = min(cuboid.dimensions)
        self.volume: int = cuboid.volume()

    def __repr__(self):
        return self.cuboid.__repr__()


class Decoder:

    def decode_chromosome(self, individual) -> PlacementSolution:
        pass

    def fitness_of(self, solution: PlacementSolution) -> float:
        pass

    def reset(self):
        pass


class GADecoder(Decoder):
    def __init__(self, product_boxes, bin_specification: Cuboid):
        self.product_boxes = [ProductBox(pb) for pb in product_boxes]
        self.placer = Placer(self.product_boxes, bin_specification)
        self.bin_volume = bin_specification.volume()
        self.bin_specification = bin_specification

    def decode_chromosome(self, individual: Chromosome) -> PlacementSolution:
        return self.placer.place_boxes(individual)

    def fitness_of(self, solution: PlacementSolution) -> float:
        return float(solution.num_bins) + (float(solution.least_load) / float(self.bin_volume))

    def reset(self):
        self.placer.reset()


