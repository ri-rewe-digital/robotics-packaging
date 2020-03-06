import numpy as np


def fill_knapsack(current_volume, item, volumes, values, dynamic_results):
    # check for valid item count
    if item < len(volumes):
        # did we calculate the value already (dynamic programming)
        if dynamic_results[item][current_volume] != -1:
            return dynamic_results[item][current_volume]
        # Calculate result without current item
        a: int = fill_knapsack(current_volume, item + 1, volumes, values, dynamic_results)
        # Calculate result with current item
        b: int = 0
        if current_volume - volumes[item] >= 0:
            b = values[item] + fill_knapsack(current_volume - volumes[item], item + 1, volumes, values, dynamic_results)
        # The maximum of the two is saved and returned
        dynamic_results[item][current_volume] = max(a, b);
        return dynamic_results[item][current_volume]
    return 0


def backtracking(knapsack_value, dynamic_results, volumes, values):
    number_of_items = len(volumes) -1
    # Find maximum volume for optimal value (always first row)
    current_volume = np.argmax(dynamic_results[0])

    # iterate the items
    item: int = 0
    while item < number_of_items:
        # does the item fit the knapsack and if so, does the current value - item-value fit the volume-value?
        # If so; he item was selected to be optimal and we can reduce the volume and value and check the next item.
        if (current_volume - volumes[item] >= 0
                and knapsack_value - values[item] == dynamic_results[item + 1][current_volume - volumes[item]]):
            print_item(item, volumes, values)
            knapsack_value -= values[item]
            current_volume -= volumes[item]
        else:
            # Item is not in the Knapsack
            print_item(item, volumes, values, False)
        item += 1
    # If the last item was inside the kp, we didn't find it in the loop.
    print_item(number_of_items, volumes, values, knapsack_value > 0)


def print_item(item: int, volumes, values, selected: bool = True):
    out = ""
    if not selected:
        out = "NOT "
    out += "selecting item:{} (vol: {}, val: {})"
    print(out.format(item, volumes[item], values[item]))


def main(max_n=300, max_v=1000):
    rucksack_volume = 30
    volumes = np.fromstring('5, 5, 6, 8, 10, 11, 12, 15, 15, 30', dtype=np.int, sep=',')
    values = np.fromstring('8, 8, 6, 5, 10, 5, 10, 17, 20, 20', dtype=np.int, sep=',')

    dynamic_results = np.zeros((len(volumes), rucksack_volume + 1))
    dynamic_results[:] = -1

    kp_value = fill_knapsack(rucksack_volume, 0, volumes, values, dynamic_results)
    print("Value of knapsack:{}".format(kp_value))
    backtracking(kp_value, dynamic_results, volumes, values)


if __name__ == '__main__':
    main()
