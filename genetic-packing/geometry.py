import numpy as np
from typing import List


class Point:
    def __init__(self, coordinates: np.array):
        self.coords = coordinates

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

    # pub fn width(&self) -> i32 {
    #    self.upper_right.x - self.bottom_left.x
    # }

    # pub fn depth(&self) -> i32 {
    #    self.upper_right.z - self.bottom_left.z
    # }

    # pub fn height(&self) -> i32 {
    #    self.upper_right.y - self.bottom_left.y
    # }

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


if __name__ == '__main__':
    a = Point(np.array([3, 7, 3]))
    b = Point(np.array([5, 5, 5]))
    print(a)
    print(b)
    print(a.scalar_less_than(b))
    print(a.squared_distance_from(b))
    print(a - b)
    print(a + b)
    print(a.minimum(b))
    print(a.maximum(b))
    print(a.prod())
    print(b.prod())

    print("swap0,1: " + str(a.swap(0, 1)))
    print("swap1,2: " + str(a.swap(1, 2)))
    print("swap0,2: " + str(a.swap(0, 2)))

    c = Cuboid(Point(np.array([3, 5, 7])))
    print(c)
    print(c.volume())
    cuboids = c.get_rotation_permutations()
    for cu in cuboids:
        print(cu)

    d = Point(np.array([3, 2, 3]))
    s = Space(d, b)
    print(s)
    s2 = Space.from_placement(d, c)
    print(s2)

    print(s.dimensions())
    print(s.origin())
    print(s.center())
    print("s: " + str(s))
    print("s2: " + str(s2))
    print(s.contains(s2))
    print(s.intersects(s2))
    print(s.union(s2))
    print(s.intersection(s2))

    p = [a,b,d]
    r = []
    test = (item for item, point in enumerate(p) if point.coords[2]==5 or point.coords[1]==2)
    r.extend(test)
    for t in r:
        print("Found: " + str(p[t]))
