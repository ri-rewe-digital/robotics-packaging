import numpy as np

def lambda_weight_vector(m, number_of_weight_vectors, g, weight_change_frequency):
    for i in pow(number_of_weight_vectors, (1/m-1)):

    lambda_1 = np.log(
        ((4*g*np.e)/weight_change_frequency)+
        np.cos((2*np.pi*g)/weight_change_frequency)
    )
    return [lambda_1, 1-lambda_1]


def initialize_pheromone_trails(trails=1, generation=0):
    pass


def generate_weight_functions(size_of_weightfunction):
    return []


def explore_pareto_space(number_of_generations):
    generation: int = 0
    while generation < number_of_generations:
        # 1) Archive initialization: A ← ∅
        # 2) Weight vector selection: Select weight vector λ(g)=(λ1(g),...,λm(g)) ∈ Λ
        # 3) Solutions construction: For h from 1 to Nbants: Ant h constructs a solution Sh
        # with probability pSh (Ij ) defined in Eq.(8)
        # 4) Archive update: If no solution in A  Sh add Sh to A and remove from A all
        # solutions dominated by Sh
        # 5) Pheromone update: Update pheromone trails for each member of A with τ(Ij )
        # defined in Eq.(11)
        # 6) Pareto approximation set update: P ← non-dominated solutions of P ∪ A
        # 7) Generation index incrementation: g ← g + 1

        generation +=1


def main():
    # Input: Nbants (number of ants)
    #gmax (maximum number of generations)
    # m (number of objectives)
    # Output: P (Pareto approximation set)
    # Step 1 - initialization: Initialize the pheromone trails τinit ← 1 and g ← 0
    # Step2 -  weight vector generation: Generate the weight vectors set Λ of size L according to Gw method
    # Step 3 - main loop: While g < gmax do: explore
    # Step 4-Termination: Return the Pareto approximation set P
    number_of_generations: int = 200
    number_of_objectives: int = 2
    number_of_ants: int = 100
    number_of_items: int = 10
    size_of_weightfunction = 10
    initialize_pheromone_trails(1, 0)
    weight_functions = generate_weight_functions(size_of_weightfunction)
    explore_pareto_space()




if __name__ == '__main__':
    main()