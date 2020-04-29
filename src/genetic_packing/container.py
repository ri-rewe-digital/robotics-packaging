from genetic_packing.geometry import Point, Cuboid, Space, SpaceFilter


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

    @staticmethod
    def __first_true(iterable, default=False, pred=None):
        return next(filter(pred, iterable), default)

    def allocate_new_empty_spaces(self, space: Space, new_space_filter: SpaceFilter):
        self.used_volume += space.volume()

        # keep all remaining spaces that match the filter
        self.empty_space_list = [filtered_space for filtered_space in self.empty_space_list if
                                 new_space_filter.is_valid(filtered_space)]

        spaces_intersects = [item for item, ems in enumerate(self.empty_space_list) if ems.intersects(space)]
        new_empty_spaces = self._create_new_ems_from_intersection(space, spaces_intersects, new_space_filter)
        self._add_allocated_spaces(new_empty_spaces)

    def _create_new_ems_from_intersection(self, new_box_to_place, intersecting_space_idxs, new_space_filter):
        new_empty_spaces = []
        for sp_idx in intersecting_space_idxs:
            ems = self.empty_space_list[sp_idx]
            intersection = ems.intersection(new_box_to_place)
            new_empty_spaces.extend(ems.create_new_spaces(intersection, new_space_filter))

        for sp_idx in reversed(intersecting_space_idxs):
            self.empty_space_list.pop(sp_idx)
        return new_empty_spaces

    def _add_allocated_spaces(self, new_empty_spaces):
        for (i, empty_space) in enumerate(new_empty_spaces):
            overlapped = Container.__first_true(
                enumerate(new_empty_spaces),
                pred=lambda j_and_other_space: i != j_and_other_space[0] and j_and_other_space[1].contains(empty_space)
            )
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
