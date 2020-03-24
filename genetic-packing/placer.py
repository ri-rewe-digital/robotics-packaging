from bin import ContainerList
from chromosome import Chromosome
from geometry import Cuboid, Space, SpaceFilter
import math

MAX_INT = 2E63 - 1


class PlacementSolution:
    def __init__(self, num_bins: int, least_load: int, placements):
        self.num_bins = num_bins
        self.least_load = least_load
        self.placements = placements  # Vec<ProductPlacements>


class ProductPlacement:
    def __init__(self, space: Space, bin_number: int, box_index: int):
        self.space = space
        self.bin_number = bin_number
        self.box_index = box_index


class Placer:
    def __init__(self, boxes: [], container_spec: Cuboid):
        self.boxes = boxes  # [ProductBox]
        self.bins = ContainerList(container_spec)
        self.bps = []  # Vec<(usize, f32)>
        self.orientations = []  # Vec<Cuboid>

    def place_boxes(self, chromosome: Chromosome) -> PlacementSolution:
        placements = []
        min_dimension, min_volume = MAX_INT, MAX_INT

        self.calculate_bps(chromosome)
        for (bps_idx, (box_idx, _)) in enumerate(self.bps):
            box_to_pack = self.boxes[box_idx]

            fit_bin, fit_space = self.find_bin_to_fit(box_to_pack)

            placement_space = self.place_box(box_idx, chromosome, fit_space)

            if box_to_pack.smallest_dimension <= min_dimension or box_to_pack.volume <= min_volume:
                min_dimension, min_volume = self.determine_remaining_min_dim_and_volume(self.bps[(bps_idx + 1):])

            self.bins[fit_bin].allocate_space(placement_space, SpaceFilter(min_dimension, min_volume))
            placements.append(ProductPlacement(placement_space, fit_bin, box_idx))

        new_bins = self.bins.opened_containers()
        num_bins = len(new_bins)
        least_load = min(new_bins, key=lambda b: b.used_volume).used_volume
        return PlacementSolution(num_bins, least_load, placements)

    def find_bin_to_fit(self, box_to_pack):
        (fit_bin, fit_space) = (None, None)
        for (i, current_bin) in enumerate(self.bins.opened_containers()):
            if current_bin:
                placement_space = current_bin.try_place_cuboid(box_to_pack.cuboid)
                if placement_space is not None:
                    fit_space = placement_space
                    fit_bin = i
                    break
        if fit_bin is None:
            fit_bin = self.bins.open_new_container()
            fit_space = self.bins[fit_bin].empty_space_list[0]
        return fit_bin, fit_space

    def place_box(self, box_idx: int, chromosome: Chromosome, container_space: Space) -> Space:
        cuboid = self.boxes[box_idx].cuboid

        orientations = cuboid.get_rotation_permutations()
        orientations = [o for o in orientations if o.can_fit_in(container_space)]
        orientation = chromosome.decode_orientation(box_idx, orientations)

        return Space.from_placement(container_space.origin(), orientation)

    def reset(self):
        self.bins.reset()
        self.bps.clear()
        self.orientations.clear()

    def determine_remaining_min_dim_and_volume(self, remain_bps) -> (int, int):
        (min_d, min_v) = (MAX_INT, MAX_INT)
        for (box_idx, _) in remain_bps:
            b = self.boxes[box_idx]
            min_d = min(min_d, b.smallest_dimension)
            min_v = min(min_v, b.volume)
        return min_d, min_v

    def calculate_bps(self, chromosome: Chromosome):
        self.bps.clear()
        # TODO RB: again the .., is it an explode in rust?
        bps = chromosome.get_bps()
        # bps = [(index, score) for (index, score) in enumerate(chromosome[:math.floor(len(chromosome) / 2)])]
        # bps = chromosome[..chromosome.len() / 2].iter().enumerate().map(|(i, score)| (i, score))
        self.bps.extend(bps)
        # sort by score
        self.bps.sort(key=lambda box: box[1], reverse=True)
        # (|a, b| a.1.partial_cmp(b.1).unwrap())
