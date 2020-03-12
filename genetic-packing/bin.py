from geometry import Point, Cuboid, Space
from bin import Container
from typing import List


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

class Container:
    def __init__(self, specification: Cuboid):
        self.specification = specification
        self.used_volume: int = 0
        self.empty_space_list= [Space.from_placement(Point(0,0,0),specification)]
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

    def
    new_space_filter(space: Space):
        dimensions = space.dimensions()
        v = space.volume()
        return min(dimensions) >= min_dimension and v >= min_volume





        self.used_volume += space.volume()
        self.spaces_intersects.clear()
        spaces_intersects = (item for item, ems in enumerate(self.empty_space_list) if ems.intersects(space))
        self.spaces_intersects.extend(spaces_intersects)
        self.new_empty_spaces.clear()
        for i in self.spaces_intersects:
            ems = self.empty_space_list[i]
            # Is this supposed to be intersection?
            union = ems.union(space)
            difference_process(ems, union, self.new_empty_spaces, |s| {new_space_filter(s)})

        for &i in self.spaces_intersects.iter().rev() {
        self.empty_space_list.swap_remove(i);
        }
        self.empty_space_list.retain(|s| new_space_filter(s));

        for (i, this) in self.new_empty_spaces.iter().enumerate() {
        let overlapped = self.new_empty_spaces
        .iter()
        .enumerate()
        .any(|(j, other)| i != j && other.contains(this));
        if !overlapped {
        self.empty_space_list.push(*this);
        }
        }


    def allocate_space(self, space: Space, new_space_filter):{
        where
            F: FnMut(&Space) -> bool, {



        }

        #[inline]
        fn reset(&mut self) {
            self.used_volume = 0;
            self.orientations.borrow_mut().clear();
            self.new_empty_spaces.clear();
            self.spaces_intersects.clear();
            self.empty_space_list.clear();
            self.empty_space_list.push(Space::from_placement(&Point::new(0, 0, 0), &self.spec))
        }
    }

    #[inline]
    def difference_process(self, this: Space, other: Space, new_spaces: List[Space], new_space_filter)
        where F: FnMut(&Space) -> bool, {
            let (sb, su, ob, ou) = (
                &this.bottom_left,
                &this.upper_right,
                &other.bottom_left,
                &other.upper_right,
            );
        let spaces = [Space::new(*sb, Point::new(ob.x, su.y, su.z)),
                        Space::new(Point::new(ou.x, sb.y, sb.z), *su),
                        Space::new(*sb, Point::new(su.x, ob.y, su.z)),
                        Space::new(Point::new(sb.x, ou.y, sb.z), *su),
                        Space::new(*sb, Point::new(su.x, su.y, ob.z)),
                        Space::new(Point::new(sb.x, sb.y, ou.z), *su)];

        let spaces = spaces
                 .iter()
                 .filter(|ns| ns.width().min(ns.depth()).min(ns.height()) != 0 && new_space_filter(ns));
        for space in spaces {
            new_spaces.push(*space);
        }
    }