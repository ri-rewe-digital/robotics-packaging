from configuration import Parameters
from encode import GADecoder, RandEncoder
from genetic_algorithms import Solver
from geometry import Space
from threadz import MultithreadedGADecoder
from plott import plot_solution


class SolutionPlacement:
    def __init__(self, space: Space, box_id):
        self.space = space
        self.box_id = box_id

    def __repr__(self):
        return "id: {}, location: {}".format(self.box_id, self.space)


def solve_multi(product_boxes, ga_params, generator):
    multi_solver = Solver(generator, MultithreadedGADecoder(product_boxes, ga_params.delivery_bin_spec,
                                                            ga_params.number_of_threads), ga_params)
    return multi_solver.solve()


def solve_single(product_boxes, ga_params, generator):
    multi_solver = Solver(generator, GADecoder(product_boxes, ga_params.delivery_bin_spec), ga_params)
    return multi_solver.solve()


def solve_packing_problem(parameters: Parameters, product_boxes: []) -> dict:
    generator = RandEncoder(len(product_boxes) * 2)
    ga_params = parameters.get_ga_params(len(product_boxes))
    solution = solve_multi(product_boxes, ga_params, generator)

    # elapsed_time = timeit.timeit(solve_multi(product_boxes, ga_params, generator),number=1)
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
        plot_solution(ga_params.delivery_bin_spec, delivery_bins, False)
    return delivery_bins
