import yaml

from configuration import Parameters


def solve_packing_problem():
    pass


def read_config(file="config.yaml"):
    with open(file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def main():
    parameters = Parameters.from_yaml(read_config())

    print(parameters)


if __name__ == '__main__':
    main()
