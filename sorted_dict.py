import bisect
import collections
import threading


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


class SortedDict(collections.MutableMapping):

    def __init__(self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)
        self._list = sorted(self._dict.keys())

        self.lock = threading.RLock()

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        with self.lock:
            if key not in self._dict:
                bisect.insort(self._list, key)

            self._dict[key] = value

    def __delitem__(self, key):
        with self.lock:
            if key in self._dict:
                del self._dict[key]
                self._list.remove(key)

    def __iter__(self):
        return iter(self._list)

    def __len__(self):
        return len(self._list)

    def get_next(self, key, direction):
        if direction == 1:
            return find_gt(self._list, key)
        elif direction == -1:
            return find_lt(self._list, key)

    def get_nearest(self, key):
        next_upwards = self.get_next(key, 1)
        next_downwards = self.get_next(key, -1)

        if next_upwards and next_downwards:
            if next_upwards - key > key - next_downwards:
                return next_downwards
            else:
                return next_upwards

        else:
            return next_upwards or next_downwards
