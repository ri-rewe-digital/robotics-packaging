#!/usr/bin/env python3
import csv
import timeit

import yaml

from configuration import Parameters
from encode import GADecoder, RandEncoder
from genetic_algorithms import Solver
from geometry import Cuboid, Point, Space
from plott import plot_solution
from threadz import MultithreadedGADecoder


class SolutionPlacement:
    def __init__(self, space: Space, box_id):
        self.space = space
        self.box_id = box_id

    def __repr__(self):
        return "id: {}, location: {}".format(self.box_id, self.space)


def solve_multi(product_boxes, delivery_bin_specification, ga_params, generator):
    multi_solver = Solver(generator, MultithreadedGADecoder(product_boxes, delivery_bin_specification,
                                                            ga_params.number_of_threads), ga_params)
    return multi_solver.solve()


def solve_single(product_boxes, delivery_bin_specification, ga_params, generator):
    multi_solver = Solver(generator, GADecoder(product_boxes, delivery_bin_specification), ga_params)
    return multi_solver.solve()


def solve_packing_problem(parameters, product_boxes, delivery_bin_specification):
    generator = RandEncoder(len(product_boxes) * 2)
    ga_params = parameters.get_ga_params(len(product_boxes))
    solution = solve_multi(product_boxes, delivery_bin_specification, ga_params, generator)

    # elapsed_time = timeit.timeit(solve_multi(product_boxes, delivery_bin_specification, ga_params, generator),number=1)
    # print("execution time with threading: {}".format(elapsed_time))

    delivery_bins = dict()

    if solution:
        for inner_placement in solution.placements:
            idx = inner_placement.bin_number
            space = inner_placement.space
            item_idx = inner_placement.box_index
            if not delivery_bins or delivery_bins[idx] is None:
                delivery_bins[idx] = []
            delivery_bins[idx].append(SolutionPlacement(space, item_idx))
        plot_solution(delivery_bin_specification, delivery_bins, False)
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
                product_boxes.append(
                    Cuboid(Point.from_scalars(int(row['width']), int(row['depth']), int(row['height']))))
                index += 1
    return product_boxes


def main():
    parameters = Parameters.from_yaml(read_config())
    print(parameters)
    product_boxes = read_csv_data()
    print(product_boxes)
    delivery_bin_spec = Cuboid(Point.from_scalars(30, 30, 30))
    delivery_bins = solve_packing_problem(parameters, product_boxes, delivery_bin_spec)
    for db in delivery_bins:
        print("deliverybox: {}, with products: {}".format(db, delivery_bins[db]))


if __name__ == '__main__':
    main()
