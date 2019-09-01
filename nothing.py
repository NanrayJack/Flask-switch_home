log = print


def flip(negative):
    return not negative


def dec(i, negative):
    if negative is True:
        return -i
    else:
        return i


def main():
    n = 8
    m = 2
    negative = False
    a = []
    for i in range(1, n + 1):
        if (i + 1) % m == 0:
            negative = flip(negative)
        a.append(dec(i, negative))
    log(a)
    return sum(a)


def max(a):
    m = a[0]
    for i in a:
        if i > m:
            m = i
    return m


def function():
    nq = []
    yh = []
    cards = [3, 1]
    for i in range(len(cards)):
        if (i + 1) % 2 == 1:
            nq.append(max(cards))
            cards.remove(max(cards))
        else:
            yh.append(max(cards))
            cards.remove(max(cards))
    log('nq', nq)
    log('yh', yh)
    return sum(nq) - sum(yh)


def first_day():
    pass


def ways(all_len, a_len, a_num, b_len, b_num):
    if all_len == 0:
        return 1
    elif all_len < 0:
        return 0
    else:
        a_ways = b_ways = 0

        if a_num > 0:
            shorter_len = all_len - a_len
            a_ways = a_num * ways(shorter_len, a_len, a_num - 1, b_len, b_num)
        if b_num > 0:
            shorter_len = all_len - b_len
            b_ways = b_num * ways(shorter_len, a_len, a_num, b_len, b_num - 1)
        log('a_ways, b_ways', a_ways, b_ways)
        return a_ways + b_ways


def sad():
    import sys
    for line in sys.stdin:
        a = line.split()
        print(int(a[0]) + int(a[1]))


if __name__ == '__main__':
    all_len, a_len, a_num, b_len, b_num = 5, 2, 3, 3, 3
    a = ways(all_len, a_len, a_num, b_len, b_num)
    log(a)
