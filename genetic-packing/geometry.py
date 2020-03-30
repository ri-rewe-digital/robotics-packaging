import copy

import numpy as np


class Point:
    def __init__(self, coordinates: np.array):
        self.coords = coordinates

    @staticmethod
    def new_origin():
        return Point.from_scalars()

    @staticmethod
    def from_scalars(x=0, y=0, z=0):
        return Point(np.array([x, y, z]))

    def squared_distance_from(self, other):
        distance = self.coords - other.coords
        return sum(distance * distance)

    def scalar_less_than(self, other):
        return max(self.coords - other.coords) <= 0

    def maximum(self, other):
        return Point(np.maximum(self.coords, other.coords))

    def minimum(self, other):
        return Point(np.minimum(self.coords, other.coords))

    def prod(self):
        return np.prod(self.coords)

    def swap(self, first_item, sec_item):
        new_coords = np.copy(self.coords)
        new_coords[first_item], new_coords[sec_item] = new_coords[sec_item], new_coords[first_item]
        return Point(new_coords)

    def __add__(self, other):
        return Point(self.coords + other.coords)

    def __sub__(self, other):
        return Point(self.coords - other.coords)

    def __getitem__(self, item):
        return self.coords[item]

    def __str__(self):
        return str(self.coords)

    def __repr__(self):
        return str(self.coords)


class Cuboid:
    def __init__(self, dimensions: Point):
        self.dimensions = dimensions

    def volume(self):
        return self.dimensions.prod()

    def can_fit_in(self, space) -> bool:
        return min(space.dimensions() - self.dimensions) >= 0
        # space.width() >= self.width && space.height() >= self.height && space.depth() >= self.depth

    def __str__(self):
        return str(self.dimensions)

    def __repr__(self):
        return str(self.dimensions)

    def get_rotation_permutations(self):
        orientations = [Cuboid(Point(self.dimensions.coords))]
        if self.dimensions[0] != self.dimensions[1]:
            orientations.append(Cuboid(self.dimensions.swap(0, 1)))
        if self.dimensions[0] != self.dimensions[2]:
            orientations.append(Cuboid(self.dimensions.swap(0, 2)))
        if self.dimensions[1] != self.dimensions[2]:
            orientations.append(Cuboid(self.dimensions.swap(1, 2)))
        if self.dimensions[0] != self.dimensions[1] and self.dimensions[1] != self.dimensions[2]:
            orientations.append(Cuboid(Point(np.array([self.dimensions[2], self.dimensions[0], self.dimensions[1]]))))
            orientations.append(Cuboid(Point(np.array([self.dimensions[1], self.dimensions[2], self.dimensions[0]]))))
        return orientations


class Space:
    bottom_left: Point
    upper_right: Point

    def __init__(self, bottom_left: Point, upper_right: Point):
        self.bottom_left = bottom_left
        self.upper_right = upper_right
        if min((self.upper_right - self.bottom_left).coords) < 0:
            raise ValueError(
                "bottom left " + str(bottom_left) + " must be smaller then upperright: " + str(upper_right))

    @staticmethod
    def from_placement(origin: Point, rect: Cuboid):
        return Space(Point(origin.coords), origin + rect.dimensions)

    def dimensions(self):
        return self.upper_right - self.bottom_left

    def origin(self) -> Point:
        return self.bottom_left

    def center(self) -> Point:
        return Point((self.bottom_left + self.upper_right).coords / 2.0)

    def contains(self, other) -> bool:
        return self.bottom_left.scalar_less_than(other.bottom_left) and \
               other.upper_right.scalar_less_than(self.upper_right)

    def intersects(self, other) -> bool:
        return self.bottom_left.scalar_less_than(other.upper_right) and \
               other.bottom_left.scalar_less_than(self.upper_right)

    def intersection(self, other):
        return Space(self.bottom_left.maximum(other.bottom_left), self.upper_right.minimum(other.upper_right))

    def union(self, other):
        return Space(self.bottom_left.minimum(other.bottom_left), self.upper_right.maximum(other.upper_right))

    def volume(self):
        return self.dimensions().prod()

    def __str__(self):
        return str(self.bottom_left) + ", " + str(self.upper_right)

    # aka the "difference process"
    def create_new_spaces(self, other_space, new_space_filter):
        sb, su, ob, ou = self.bottom_left, self.upper_right, other_space.bottom_left, other_space.upper_right

        spaces = [
            Space(copy.copy(sb), Point.from_scalars(ob[0], su[1], su[2])),
            Space(Point.from_scalars(ou[0], sb[1], sb[2]), copy.copy(su)),
            Space(copy.copy(sb), Point.from_scalars(su[0], ob[1], su[2])),
            Space(Point.from_scalars(sb[0], ou[1], sb[2]), copy.copy(su)),
            Space(copy.copy(sb), Point.from_scalars(su[0], su[1], ob[2])),
            Space(Point.from_scalars(sb[0], sb[1], ou[2]), copy.copy(su))
        ]
        return [space for space in spaces if min(space.dimensions()) > 0 and new_space_filter.is_valid(space)]


class SpaceFilter:
    def __init__(self, min_dimension, min_volume):
        self.min_dimension = min_dimension
        self.min_volume = min_volume

    def is_valid(self, new_space: Space) -> bool:
        return min(new_space.dimensions()) >= self.min_dimension and new_space.volume() >= self.min_volume
