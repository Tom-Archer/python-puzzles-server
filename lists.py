import numpy as np

# Returns a randomised list of numbers from 1 to maxElement
def get_list(max_element):
    return list(np.random.rand(max_element).argsort())

if __name__ == '__main__':
    my_list = get_list(10)
    print(my_list)
    print(sorted(my_list))
