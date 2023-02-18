"""
An array A consisting of N integers is given. Rotation of the array means that each element is shifted right by one index,
 and the last element of the array is moved to the first place. For example, the rotation of array A = [3, 8, 9, 7, 6]
  is [6, 3, 8, 9, 7] (elements are shifted right by one index and 6 is moved to the first place).
The goal is to rotate array A K times; that is, each element of A will be shifted to the right K times.
"""


def solution(a1, k1):
    # Return the original array if K is 0 or the array is empty
    if k1 == 0 or len(a1) == 0:
        return a1

    # Perform K rotations using slicing
    for i in range(k1):
        a1 = a1[-1:] + a1[:-1]

    return a1


if __name__ == "__main__":
    a = [3, 8, 9, 7, 6]
    k = 3

    print("solution:", solution(a, k))