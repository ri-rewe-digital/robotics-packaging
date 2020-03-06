import numpy as np

def lambda_weight_vector(m, number_of_weight_vectors, g, weight_change_frequency):
    for i in pow(number_of_weight_vectors, (1/m-1)):

    lambda_1 = np.log(
        ((4*g*np.e)/weight_change_frequency)+
        np.cos((2*np.pi*g)/weight_change_frequency)
    )
    return [lambda_1, 1-lambda_1]

def main():




if __name__ == '__main__':
    main()