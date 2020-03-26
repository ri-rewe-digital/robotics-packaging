from geometry import Point, Cuboid, Space, SpaceFilter


class ProductBox:
    def __init__(self, cuboid: Cuboid):
        self.cuboid = cuboid
        self.smallest_dimension: int = min(cuboid.dimensions)
        self.volume: int = cuboid.volume()

    def __repr__(self):
        return self.cuboid.__repr__()


class Container:
    def __init__(self, specification: Cuboid):
        self.specification = specification
        self.used_volume: int = 0
        self.empty_space_list = [Space.from_placement(Point.new_origin(), specification)]
        # self.spaces_intersects = []  #:int

    # DFTRC-2 Distance to the Front Top Right Corner
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
                    dist = container_upper_right.squared_distance_from(box_upper_right)
                    if dist > max_dist:
                        max_dist = dist
                        best_ems = ems
        return best_ems

    @staticmethod
    def __first_true(iterable, default=False, pred=None):
        return next(filter(pred, iterable), default)

    def allocate_new_empty_spaces(self, space: Space, new_space_filter: SpaceFilter):
        self.used_volume += space.volume()
        spaces_intersects = [item for item, ems in enumerate(self.empty_space_list) if ems.intersects(space)]
        new_empty_spaces = self._create_new_ems_from_intersection(space, spaces_intersects, new_space_filter)

        # keep all remaining spaces that match the filter
        self.empty_space_list = [filtered_space for filtered_space in self.empty_space_list if
                                 new_space_filter.is_valid(filtered_space)]

        self._add_allocated_spaces(new_empty_spaces)

    def reset(self):
        self.used_volume = 0
        self.empty_space_list.clear()
        self.empty_space_list.append(Space.from_placement(Point.new_origin(), self.specification))

    def _create_new_ems_from_intersection(self, new_box_to_place, spaces_intersects, new_space_filter):
        new_empty_spaces = []
        for i in spaces_intersects:
            ems = self.empty_space_list[i]
            intersection = ems.intersection(new_box_to_place)
            new_empty_spaces.extend(ems.create_new_spaces(intersection, new_space_filter))

        for i in reversed(spaces_intersects):
            self.empty_space_list.pop(i)
        return new_empty_spaces

    def _add_allocated_spaces(self, new_empty_spaces):
        for (i, empty_space) in enumerate(new_empty_spaces):
            overlapped = Container.__first_true(enumerate(new_empty_spaces),
                                                pred=lambda j_and_other_space: i != j_and_other_space[0] and
                                                                             j_and_other_space[1].contains(empty_space))
            if not overlapped:
                self.empty_space_list.append(empty_space)


class ContainerList:
    def __init__(self, specification: Cuboid):
        self.specification = specification
        self.containers = []  # List[Container]

    def __getitem__(self, item) -> Container:
        return self.containers[item]

    def opened_containers(self):
        return self.containers

    def __sizeof__(self):
        return len(self.containers)

    def open_new_container(self) -> int:
        self.containers.append(Container(self.specification))
        return len(self.containers) - 1

    def reset(self):
        self.containers = []
        # self.size = 0

    def find_container_to_place(self, box_to_pack):
        (fit_bin, fit_space) = (None, None)
        for (i, current_bin) in enumerate(self.containers):
            if current_bin:
                placement_space = current_bin.try_place_cuboid(box_to_pack.cuboid)
                if placement_space is not None:
                    fit_space = placement_space
                    fit_bin = i
                    break
        if fit_bin is None:
            fit_bin = self.open_new_container()
            fit_space = self.containers[fit_bin].empty_space_list[0]
        return fit_bin, fit_space
