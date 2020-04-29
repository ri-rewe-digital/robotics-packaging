from genetic_packing.container import ContainerList, ProductBox
from genetic_packing.chromosome import Chromosome
from genetic_packing.geometry import Cuboid, Space, SpaceFilter
from genetic_packing.placement import PlacementStrategy

MAX_INT = 2E63 - 1


class ProductPlacement:
    def __init__(self, space: Space, bin_number: int, box_index: int):
        self.space = space
        self.bin_number = bin_number
        self.box_index = box_index

    def __repr__(self):
        return "space: {}, bin: {}, box: {}".format(
            self.space,
            self.bin_number,
            self.box_index
        )


class PlacementSolution:
    def __init__(self, num_bins: int, least_load: int, placements):
        self.num_bins = num_bins
        self.least_load = least_load
        self.placements = placements

    def fitness_for(self, bin_volume):
        return float(self.num_bins) + (float(self.least_load) / float(bin_volume))

    def __len__(self):
        return len(self.placements)

    def __repr__(self):
        return "number of bins: {}, least_load: {}, placements ({}): {}".format(
            self.num_bins,
            self.least_load,
            len(self.placements),
            self.placements
        )


class Placer:
    def __init__(self, product_boxes: [], container_spec: Cuboid, placement_strategy: PlacementStrategy):
        self.boxes = [ProductBox(pb) for pb in product_boxes]
        self.container_spec = container_spec
        self.placement_strategy = placement_strategy

    def place_boxes(self, chromosome: Chromosome) -> PlacementSolution:
        min_dimension, min_volume = MAX_INT, MAX_INT
        placements = []
        containers = ContainerList(self.container_spec)
        bps = chromosome.calculate_box_packing_sequence()
        for (bps_idx, box_genome) in enumerate(bps):
            box_to_pack = self.boxes[box_genome.id]

            container_id, placement_ems = Placer.__find_container_to_place(self.placement_strategy, containers,
                                                                           box_to_pack)

            placement_space = self.placement_strategy.place_product(box_genome.id, box_to_pack.cuboid, chromosome,
                                                                    placement_ems)

            if box_to_pack.smallest_dimension <= min_dimension or box_to_pack.volume <= min_volume:
                min_dimension, min_volume = self.__determine_remaining_min_dim_and_volume(bps[(bps_idx + 1):])

            containers[container_id].allocate_new_empty_spaces(placement_space, SpaceFilter(min_dimension, min_volume))
            placements.append(ProductPlacement(placement_space, container_id, box_genome.id))
            # plot_placements(self.bins[fit_bin], placements, True)

        new_containers = containers.opened_containers()
        num_containers = len(new_containers)
        least_load = min(new_containers, key=lambda b: b.used_volume).used_volume
        return PlacementSolution(num_containers, least_load, placements)

    @staticmethod
    def __find_container_to_place(placement_strategy, containers, box_to_pack):
        (fit_bin, fit_space) = (None, None)
        for (i, current_bin) in enumerate(containers):
            if current_bin:
                placement_space = placement_strategy.find_best_placement_space(current_bin, box_to_pack.cuboid)
                if placement_space is not None:
                    fit_space = placement_space
                    fit_bin = i
                    break
        if fit_bin is None:
            fit_bin = containers.open_new_container()
            fit_space = containers[fit_bin].empty_space_list[0]
        return fit_bin, fit_space

    def __determine_remaining_min_dim_and_volume(self, remain_bps) -> (int, int):
        (min_d, min_v) = (MAX_INT, MAX_INT)
        for box_genome in remain_bps:
            b = self.boxes[box_genome.id]
            min_d = min(min_d, b.smallest_dimension)
            min_v = min(min_v, b.volume)
        return min_d, min_v

    def get_target_bin_volume(self):
        return self.container_spec.volume()
