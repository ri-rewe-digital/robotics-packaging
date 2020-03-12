from bin import ContainerList
from genetic_algorithms import Chromosome
from geometry import Cuboid, Space

MAX_INT=2^63 - 1

class InnerSolution:
    def __init__(self, num_bins: int, least_load: int, placements):
        self.num_bins=num_bins
        self.least_load=least_load
        self.placements=placements #Vec<InnerPlacement>


class ProductBox:
    def __init__(self, cuboid: Cuboid):
        self.cuboid= cuboid
        self.smallest_dimension: int = min(cuboid.dimensions)
        self.volume: int = cuboid.volume()

class Placer:
    def __init__(self, boxes, container_spec: Cuboid, bps, orientations):
        self.boxes = boxes #[InnerBox]
        self.bins = ContainerList(container_spec)
        self.bps=[]# Vec<(usize, f32)>
        self.orientations=[] # Vec<Cuboid>


    def place_boxes(self, chromosome: Chromosome) -> InnerSolution:
        placements = []
        min_dimension, min_volume = MAX_INT, MAX_INT

        self.calculate_bps(chromosome)
        for (bps_idx, (box_idx, _)) in enumerate(self.bps):
            box_to_pack = self.boxes[box_idx]
            (fit_bin, fit_space) = (None, None)

            for (i, bin) in enumerate(self.bins.opened_containers()):
                placement = bin.try_place_cuboid(box_to_pack.cuboid)
                if placement is not None:
                    fit_space = placement
                    fit_bin = i
                    break

            if fit_bin is None:
                idx = self.bins.open_new_container()
                fit_bin = idx
                fit_space = self.bins[idx].empty_space_list[0]

            placement = self.place_box(box_idx, chromosome, fit_space)

            if box_to_pack.smallest_dimension <= min_dimension or box_to_pack.volume <= min_volume:
                #RB: TODO what does the 1.. exactly do?
                (md, mv) = self.min_dimension_and_volume(self.bps[bps_idx +1..])
                min_dimension = md
                min_volume = mv


            self.bins.nth_mut(fit_bin).allocate_space(&placement, |ns| {
                let (w, d, h) = (ns.width(), ns.depth(), ns.height());
                let v = w * d * h;
                w.min(d).min(h) >= min_dimension && v >= min_volume
            });

            placements.push(InnerPlacement::new(placement, fit_bin, box_idx));
        }

        let bins = self.bins.opened();
        let num_bins = bins.len();
        let least_load = bins.iter().map(|bin| bin.used_volume).min().unwrap();
        InnerSolution::new(num_bins, least_load, placements)


    def place_box(self, box_idx: int, chromosome: Chromosome, container: Space) -> Space:
        let cuboid = &self.boxes[box_idx].cuboid;
        let gene = chromosome[chromosome.len() / 2 + box_idx];

        let mut orientations = self.orientations.borrow_mut();
        orientations.clear();
        rotate_cuboid(self.rotation_type, cuboid, orientations.as_mut());
        orientations.retain(|c| c.can_fit_in(container));

        let decoded_gene = (gene * orientations.len() as f32).ceil() as usize;
        let orientation = &orientations[(decoded_gene).max(1) - 1];
        Space::from_placement(container.origin(), orientation)


    def reset(self):
        self.bins.reset()
        self.bps.clear()
        self.orientations.borrow_mut().clear()


    def min_dimension_and_volume(self, remain_bps) -> (int, int):
        (min_d, min_v) = (MAX_INT, MAX_INT)
        for box_idx, _ in enumerate(remain_bps):
            b = self.boxes[box_idx]
            min_d = min_d.min(b.smallest_dimension)
            min_v = min_v.min(b.volume)

        return (min_d, min_v)


    #[inline]
    def calculate_bps(self, chromosome: Chromosome):
        self.bps.clear()
        bps = chromosome[..chromosome.len() / 2].iter().enumerate().map(|(i, score)| (i, score))
        self.bps.extend(bps)
        self.bps.sort_unstable_by(|a, b| a.1.partial_cmp(b.1).unwrap())



