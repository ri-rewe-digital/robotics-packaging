import yaml
import csv

from configuration import Parameters
from encode import GADecoder
from genetic_algorithms import RandGenerator, Solver
from geometry import Cuboid, Point, Space


class SolutionPlacement:
    def __init__(self, space: Space, box_id):
        self.space = space
        self.box_id = box_id


def solve_packing_problem(parameters, product_boxes, delivery_bin_specification):
    generator = RandGenerator(len(product_boxes) * 2)
    ga_params = parameters.get_ga_params(len(product_boxes))
    solver = Solver(generator, GADecoder(product_boxes, delivery_bin_specification), ga_params)
    solution = solver.solve()

    delivery_bins = []
    for inner_placement in solution.placements:
        idx = inner_placement.bin_no
        space = inner_placement.space
        item_idx = inner_placement.box_idx
        if delivery_bins[idx] is None:
            delivery_bins[idx] = []
        delivery_bins[idx].append(SolutionPlacement(space, item_idx))

    return delivery_bins


def read_config(file="config.yaml"):
    with open(file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def read_csv_data(file="data/product_boxes.csv"):
    product_boxes = []
    with open(file, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            count = int(row['count'])
            index = 0
            while index < count:
                product_boxes.append(Cuboid(Point.from_scalars(int(row['width']), int(row['depth']), int(row['height']))))
                index += 1
    return product_boxes


def main():
    parameters = Parameters.from_yaml(read_config())
    print(parameters)
    product_boxes = read_csv_data()
    print(product_boxes)
    delivery_bin_spec = Cuboid(Point.from_scalars(30, 30, 30))
    delivery_bins = solve_packing_problem(parameters, product_boxes, delivery_bin_spec)
    for i, db in enumerate(delivery_bins):
        print("deliverybox: {}, with products: {}".format(i, db))



if __name__ == '__main__':
    main()
