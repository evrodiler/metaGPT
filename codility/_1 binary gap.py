# binary gap

def solution(n: int):
    # Implement your solution here
    binary_form = bin(n)[2:]

    gap = 0
    gap_cnt = 0

    for digit in binary_form:
        if digit == '0':
            gap_cnt += 1
        else:
            gap = max(gap, gap_cnt)
            gap_cnt = 0

    return gap


if __name__ == "__main__":
    solution(3)
