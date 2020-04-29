from genetic_packing.chromosome import Chromosome
from genetic_packing.container import Container
from genetic_packing.geometry import Cuboid, Space, Point


class PlacementStrategy:

    def find_best_placement_space(self, container: Container, product_box: Cuboid):
        pass

    def place_product(self, box_idx: int, box_cuboid: Cuboid, chromosome: Chromosome, container_space: Space) -> Space:
        orientations = box_cuboid.get_rotation_permutations()
        orientations = [o for o in orientations if o.can_fit_in(container_space)]

        orientation = chromosome.decode_orientation(box_idx, orientations)

        return Space.from_placement(container_space.origin(), orientation)


class DFTRCStrategy(PlacementStrategy):
    def __init__(self, container_spec: Cuboid):
        self.container_spec = container_spec
        self.container_upper_right = Point(self.container_spec.dimensions.coords)

    # DFTRC-2 Distance to the Front Top Right Corner
    def find_best_placement_space(self, container: Container, product_box: Cuboid) -> Space:
        max_dist = -1.0
        best_ems = None
        orientations = product_box.get_rotation_permutations()

        for ems in container.empty_space_list:
            if ems.volume() >= product_box.volume():
                max_dist, best_ems = self._find_best_ems_for_orientations(max_dist, best_ems, ems, orientations)
        return best_ems

    def _find_best_ems_for_orientations(self, max_dist, best_ems, ems: Space, orientations: []) -> (float, Space):
        fitting_orientations = (o for o in orientations if o.can_fit_in(ems))
        for orientation in fitting_orientations:
            box_upper_right = Space.from_placement(ems.origin(), orientation).upper_right
            dist = self.container_upper_right.squared_distance_from(box_upper_right)
            if dist > max_dist:
                max_dist = dist
                best_ems = ems
        return max_dist, best_ems


class BottomDFTRCStrategy(DFTRCStrategy):

    def __init__(self, container_spec: Cuboid, sort_axis: int = 2):
        DFTRCStrategy.__init__(self, container_spec)
        self.sort_axis = sort_axis

    # Bottom placement first, than calculate DFTRC-2 Distance to the Front Top Right Corner
    def find_best_placement_space(self, container: Container, product_box: Cuboid):
        max_dist = -1
        best_ems = None
        if len(container.empty_space_list) == 0:
            return best_ems
        orientations = product_box.get_rotation_permutations()
        bottom_sorted = container.empty_space_list[:]
        bottom_sorted.sort(key=lambda s: self.__axis_value(s))
        z_level = self.__axis_value(bottom_sorted[0])
        for ems in bottom_sorted:
            current_z_level = self.__axis_value(ems)
            # TODO rb: this is pretty hard-edge, works for equal ground level,
            #  but for values > 0 maybe a more interval based approach?
            if z_level < current_z_level and best_ems is not None:
                break
            if ems.volume() >= product_box.volume():
                max_dist, best_ems = self._find_best_ems_for_orientations(max_dist, best_ems, ems, orientations)
            z_level = current_z_level
        return best_ems

    def __axis_value(self, space: Space) -> float:
        return space.bottom_left[self.sort_axis]


class PlacementFactory:

    @staticmethod
    def placement_strategy_for_key(key: str, parameters: dict) -> PlacementStrategy:
        return {
            'DFTRC': PlacementFactory.__create_dftrc(parameters),
            'BOTTOM': PlacementFactory.__create_bottom(parameters)
        }.get(key.upper(), PlacementFactory.__create_dftrc(parameters))

    @staticmethod
    def __create_dftrc(parameters):
        return DFTRCStrategy(parameters['delivery_bin_spec'])

    @staticmethod
    def __create_bottom(parameters):
        return BottomDFTRCStrategy(parameters['delivery_bin_spec'], parameters['bottom']['sort_axis'])
