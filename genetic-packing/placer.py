from bin import ContainerList
from chromosome import Chromosome
from geometry import Cuboid, Space, SpaceFilter
from typing import List
import math

MAX_INT = 2 ^ 63 - 1


class PlacementSolution:
    def __init__(self, num_bins: int, least_load: int, placements):
        self.num_bins = num_bins
        self.least_load = least_load
        self.placements = placements  # Vec<ProductPlacements>


class ProductBox:
    def __init__(self, cuboid: Cuboid):
        self.cuboid = cuboid
        self.smallest_dimension: int = min(cuboid.dimensions)
        self.volume: int = cuboid.volume()


# [derive(Clone, Copy, Debug)]
class ProductPlacement:
    def __init__(self, space: Space, bin_number: int, box_index: int):
        self.space = space
        self.bin_number = bin_number
        self.box_index = box_index


class Placer:
    def __init__(self, boxes: List[ProductBox], container_spec: Cuboid):
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
            (fit_bin, fit_space) = (None, None)

            for (i, current_bin) in enumerate(self.bins.opened_containers()):
                placement_space = current_bin.try_place_cuboid(box_to_pack.cuboid)
                if placement_space is not None:
                    fit_space = placement_space
                    fit_bin = i
                    break

            if fit_bin is None:
                idx = self.bins.open_new_container()
                fit_bin = idx
                fit_space = self.bins[idx].empty_space_list[0]

            placement_space = self.place_box(box_idx, chromosome, fit_space)

            if box_to_pack.smallest_dimension <= min_dimension or box_to_pack.volume <= min_volume:
                min_dimension, min_volume = self.min_dimension_and_volume(self.bps[(bps_idx + 1):])
                # (md, mv) = self.min_dimension_and_volume(self.bps[bps_idx +1..])

            self.bins[fit_bin].allocate_space(placement_space, SpaceFilter(min_dimension, min_volume))

            placements.append(ProductPlacement(placement_space, fit_bin, box_idx))

        new_bins = self.bins.opened_containers()
        num_bins = len(new_bins)
        least_load = min(new_bins, key=lambda b: b.used_volume)
        return PlacementSolution(num_bins, least_load, placements)

    def place_box(self, box_idx: int, chromosome: Chromosome, container_space: Space) -> Space:
        cuboid = self.boxes[box_idx].cuboid
        # gene = chromosome[len(chromosome) / 2 + box_idx]

        orientations = self.orientations[:]
        orientations.clear()
        orientations = cuboid.get_rotation_permutations()
        orientations = [o for o in orientations if o.can_fit_in(container_space)]
        # orientations.retain(|c| c.can_fit_in(container_space));

        orientation = chromosome.decode_orientation(box_idx, orientations)
        return Space.from_placement(container_space.origin(), orientation)

    def reset(self):
        self.bins.reset()
        self.bps.clear()
        self.orientations.clear()

    def min_dimension_and_volume(self, remain_bps) -> (int, int):
        (min_d, min_v) = (MAX_INT, MAX_INT)
        for box_idx, _ in enumerate(remain_bps):
            b = self.boxes[box_idx]
            min_d = min_d.min(b.smallest_dimension)
            min_v = min_v.min(b.volume)
        return min_d, min_v

    def calculate_bps(self, chromosome: Chromosome):
        self.bps.clear()
        # TODO RB: again the .., is it an explode in rust?
        bps = [(index, score) for (index, score) in enumerate(chromosome[:math.floor(len(chromosome) / 2)])]
        # bps = chromosome[..chromosome.len() / 2].iter().enumerate().map(|(i, score)| (i, score))
        self.bps.extend(bps)
        # sort by score
        self.bps.sort(key=lambda index_score: index_score[1])
        # (|a, b| a.1.partial_cmp(b.1).unwrap())
