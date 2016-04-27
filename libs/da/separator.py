from collections import Counter, deque
from . import bits
from . import stats


class Separator:
    distribution = Counter()
    frame = None
    size = 0

    def indexes(self) -> iter:
        indexes = list()
        gaps = self.gaps()
        edge = stats.max_dx_edge(gaps)

        for i, x in enumerate(gaps):
            if x > edge:
                indexes.append(i)

        return indexes

    def apply(self, frame: bytearray):
        size = len(frame)

        if self.frame is not None and self.size == size:
            self.count_bits(bits.xor(frame, self.frame, size), size)

        self.frame = frame
        self.size = size

    def count_bits(self, frame: bytearray, size: int):
        for i in range(8 * size):
            if bits.test(frame, i):
                self.distribution[i] += 1

    def gaps(self) -> iter:
        gaps = deque()
        prev = None

        for x in range(self.size * 8 - 1, -1, -1):
            curr = self.distribution[x]

            if prev is not None:
                if prev < curr:
                    gaps.appendleft(curr - prev)
                else:
                    gaps.appendleft(0)

            prev = curr

        return gaps