import numpy as np

class Easings:
    """
    class responseble for generating paths for animations
    """
    @staticmethod
    def linear(start, end, size, r=False):
        """
        creates a sequence with linear spacing starting at start* and ending at
        end*, with size* elements, r* allows optional rounding to nearest whole
        number
        int, int, int, [bool] -> ndarray
        :param start: the starting point of the sequence
        :param end: the ending point of the sequence
        :param size: the size of the sequence generated
        :param [r]: flag for rounding elements in the sequence to the nearest
        :return: an ndarray list that represents the generated sequence
        """
        dx = end - start
        x = lambda i: start + (i*dx)/(size-1)

        arr = [x(i) for i in range(size)]
        res = np.array(arr)

        if r:
            res = np.round(res)

        return res

    @staticmethod
    def linear2(start, end, size, r=False):
        """
        creates a 2d sequence with linear spacing starting at start* and ending
        at end*
        :param start: the starting point of the sequence
        :param end: the ending point of the sequence
        :param size: the size of the sequence generated
        :param [r]: flag for rounding the elements of the sequence
        :return: a size*x2 ndarray that represents the generated sequence
        """
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        x = lambda i: start[0] + (i * dx)/(size - 1)
        y = lambda i: start[1] + (i * dx)/(size - 1)
        return None
