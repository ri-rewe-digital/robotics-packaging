from geometry import Point, Cuboid, Space
from typing import List
from placer import SpaceFilter
import numpy as np

class Container:
    def __init__(self, specification: Cuboid):
        self.specification = specification
        self.used_volume: int = 0
        self.empty_space_list= [Space.from_placement(Point.new_origin(),specification)]
        self.spaces_intersects= []#:int
        self.new_empty_spaces = []#Space
        self.orientations = []#Cuboid

    def try_place_cuboid(self, cuboid: Cuboid) -> Space :
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


    def allocate_space(self, space: Space,  new_space_filter: SpaceFilter):
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

        #TODO RB: what is swap_remove?
        for i in reversed(self.spaces_intersects):
            self.empty_space_list.swap_remove(i)

        #TODO RB: what does retain do?
        #self.empty_space_list.retain(|s| new_space_filter(s))


        for (i, empty_space) in enumerate(self.new_empty_spaces):
            for j, other_empty_space in enumerate(self.new_empty_spaces):
                if i != j and other_empty_space.contains(empty_space)
            overlapped = for j, other_empty_space in enumerate(self.new_empty_spaces) if i != j and other_empty_space.contains(empty_space)
            .iter()
            .enumerate()
            #TODO RB: does rust.any return a list or the first match?
            .any(|(j, other_empty_space)| i != j and other_empty_space.contains(empty_space));
            if not overlapped :
                self.empty_space_list.append(empty_space);



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

    def __getitem__(self, item)->Container:
        return self.containers[item]

    def opened_containers(self):
        return self.containers

    def __sizeof__(self):
        return len(self.containers)

    def open_new_container(self)->int:
        self.containers.append(Container(self.specification))
        return len(self.containers)

    def reset(self):
        self.containers = []
        # self.size = 0
