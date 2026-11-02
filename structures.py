class MyHashMap:
    MAX_LOAD_FACTOR = 0.75

    def __init__(self, capacity=8):
        self.capacity = capacity
        self.size = 0
        self.buckets = [[] for _ in range(capacity)]

    def _index(self, key):
        return hash(key) % self.capacity

    def load_factor(self):
        return self.size / self.capacity

    def _resize(self):
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        for bucket in old_buckets:
            for key, value in bucket:
                idx = self._index(key)
                self.buckets[idx].append((key, value))

    def put(self, key, value):
        idx = self._index(key)
        bucket = self.buckets[idx]

        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return

        if (self.size + 1) / self.capacity > self.MAX_LOAD_FACTOR:
            self._resize()
            idx = self._index(key)
            bucket = self.buckets[idx]

        bucket.append((key, value))
        self.size += 1

    def get(self, key):
        idx = self._index(key)
        for k, v in self.buckets[idx]:
            if k == key:
                return v
        return None

    def contains(self, key):
        return self.get(key) is not None

    def remove(self, key):
        idx = self._index(key)
        bucket = self.buckets[idx]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self.size -= 1
                return True
        return False

    def stats(self):
        empty_buckets = sum(1 for b in self.buckets if len(b) == 0)
        max_bucket = max((len(b) for b in self.buckets), default=0)
        return {
            'size': self.size,
            'capacity': self.capacity,
            'load_factor': round(self.load_factor(), 4),
            'empty_buckets': empty_buckets,
            'max_bucket': max_bucket
        }

    def __len__(self):
        return self.size


class SegmentTree:
    def __init__(self, a):
        self.a = list(a)
        self.n = len(self.a)
        self.tree = [0] * (4 * self.n)
        if self.n > 0:
            self._build(1, 0, self.n - 1)

    def _build(self, v, tl, tr):
        if tl == tr:
            self.tree[v] = self.a[tl]
        else:
            tm = (tl + tr) // 2
            self._build(2 * v, tl, tm)
            self._build(2 * v + 1, tm + 1, tr)
            self.tree[v] = self.tree[2 * v] + self.tree[2 * v + 1]

    def query(self, l, r):
        if self.n == 0 or l > r or l < 0 or r >= self.n:
            return 0
        return self._query(1, 0, self.n - 1, l, r)

    def _query(self, v, tl, tr, l, r):
        if r < tl or tr < l:
            return 0
        if l <= tl and tr <= r:
            return self.tree[v]
        tm = (tl + tr) // 2
        return self._query(2 * v, tl, tm, l, r) + self._query(2 * v + 1, tm + 1, tr, l, r)

    def update(self, pos, value):
        if 0 <= pos < self.n:
            self.a[pos] = value
            self._update(1, 0, self.n - 1, pos, value)

    def _update(self, v, tl, tr, pos, value):
        if tl == tr:
            self.tree[v] = value
        else:
            tm = (tl + tr) // 2
            if pos <= tm:
                self._update(2 * v, tl, tm, pos, value)
            else:
                self._update(2 * v + 1, tm + 1, tr, pos, value)
            self.tree[v] = self.tree[2 * v] + self.tree[2 * v + 1]


class SegmentTreeIndex:
    def __init__(self, values):
        self.st = SegmentTree(values)

    def update(self, pos, value):
        self.st.update(pos, value)

    def query(self, l, r):
        return self.st.query(l, r)