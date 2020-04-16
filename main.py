#!/usr/bin/env python3
import csv

import yaml

from genetic_packing.configuration import Parameters
from genetic_packing.geometry import Cuboid, Point
from genetic_packing.solver import solve_packing_problem


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
    delivery_bins = solve_packing_problem(parameters, product_boxes)
    for db in delivery_bins:
        print("deliverybox: {}, with products: {}".format(db, delivery_bins[db]))


if __name__ == '__main__':
    main()
