import bisect


def find_lt(a, x):
    """ Find rightmost value less than x """
    i = bisect.bisect_left(a, x)
    if i:
        return a[i-1]
    return None


def find_gt(a, x):
    """ Find leftmost value greater than x """
    i = bisect.bisect_right(a, x)
    if i != len(a):
        return a[i]
    return None


def get_nearest(_from, *args):
    nearest = None
    delta = None

    for arg in filter(lambda x: x is not None, args):
        if delta is None or abs(_from - arg) < delta:
            delta = abs(_from - arg)
            nearest = arg

    return nearest


class SortedList(list):
    def add(self, element):
        bisect.insort(self, element)

    def get_next_key(self, from_, direction):
        if direction == 1:
            return find_gt(self, from_)

        else:
            return find_lt(self, from_)

    def get_nearest(self, _from):
        next_upwards = self.get_next_key(_from, 1)
        next_downwards = self.get_next_key(_from, -1)

        return get_nearest(_from, next_upwards, next_downwards)

    def discard(self, element):
        try:
            self.remove(element)
        except ValueError:
            pass
