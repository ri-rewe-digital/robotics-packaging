from typing import List

from geometry import Point, Cuboid, Space, SpaceFilter


class Container:
    def __init__(self, specification: Cuboid):
        self.specification = specification
        self.used_volume: int = 0
        self.empty_space_list = [Space.from_placement(Point.new_origin(), specification)]
        self.spaces_intersects = []  #:int
        self.new_empty_spaces = []  # Space
        self.orientations = []  # Cuboid

    #DFTRC-2 Distance to the Front Top Right Corner
    def try_place_cuboid(self, cuboid: Cuboid) -> Space:
        max_dist = -1
        best_ems = None
        orientations = cuboid.get_rotation_permutations()
        container_upper_right = Point(self.specification.dimensions.coords)

        for ems in self.empty_space_list:
            if ems.volume() >= cuboid.volume():
                fitting_orientations = (o for o in orientations if o.can_fit_in(ems))
                for orientation in fitting_orientations:
                    box_upper_right = Space.from_placement(ems.origin(), orientation).upper_right
                    dist = container_upper_right.squared_distance_from(box_upper_right);
                    if dist > max_dist:
                        max_dist = dist
                        best_ems = ems
        return best_ems

    @staticmethod
    def first_true(iterable, default=False, pred=None):
        return next(filter(pred, iterable), default)

    def allocate_space(self, space: Space, new_space_filter: SpaceFilter):
        self.used_volume += space.volume()
        self.spaces_intersects.clear()
        spaces_intersects = (item for item, ems in enumerate(self.empty_space_list) if ems.intersects(space))
        self.spaces_intersects.extend(spaces_intersects)
        self.new_empty_spaces.clear()
        for i in self.spaces_intersects:
            ems = self.empty_space_list[i]
            # TODO RB: Is this supposed to be intersection?
            union = ems.union(space)
            ems.difference_process(union, self.new_empty_spaces, new_space_filter)

        for i in reversed(self.spaces_intersects):
            self.empty_space_list.pop(i)

        # keep all spaces that match the filter
        self.empty_space_list = [filtered_space for filtered_space in self.empty_space_list if
                                 new_space_filter.is_valid(filtered_space)]
        # self.empty_space_list.retain(|s| new_space_filter(s))

        for (i, empty_space) in enumerate(self.new_empty_spaces):
            overlapped = Container.first_true(enumerate(self.new_empty_spaces),
                                              pred=lambda j_and_other_space: i != j_and_other_space[0] and j_and_other_space[1].contains(empty_space))
            if overlapped:
                self.empty_space_list.append(empty_space)

    def reset(self):
        self.used_volume = 0
        self.orientations.clear()
        self.new_empty_spaces.clear()
        self.spaces_intersects.clear()
        self.empty_space_list.clear()
        self.empty_space_list.append(Space.from_placement(Point.new_origin(), self.specification))


class ContainerList:
    def __init__(self, specification: Cuboid):
        self.specification = specification
        self.containers = List[Container]

    def __getitem__(self, item) -> Container:
        return self.containers[item]

    def opened_containers(self):
        return self.containers

    def __sizeof__(self):
        return len(self.containers)

    def open_new_container(self) -> int:
        self.containers.append(Container(self.specification))
        return len(self.containers)

    def reset(self):
        self.containers = []
        # self.size = 0
