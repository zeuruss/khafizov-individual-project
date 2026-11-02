import csv
import random
from pathlib import Path
from time import perf_counter

from structures import MyHashMap, SegmentTreeIndex
from trip import Trip

LIMIT_ROWS = 50000
DATASET_PATH = Path(__file__).with_name('train.csv')


def load_trips():
    rows = []
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            if LIMIT_ROWS is not None and len(rows) >= LIMIT_ROWS:
                break

    rows.sort(key=lambda r: r['pickup_datetime'])

    result = []
    for i, row in enumerate(rows):
        trip = Trip(
            row_id=i,
            id=row['id'],
            vendor_id=int(row['vendor_id']),
            pickup_datetime=row['pickup_datetime'],
            dropoff_datetime=row['dropoff_datetime'],
            passenger_count=int(row['passenger_count']),
            pickup_longitude=float(row['pickup_longitude']),
            pickup_latitude=float(row['pickup_latitude']),
            dropoff_longitude=float(row['dropoff_longitude']),
            dropoff_latitude=float(row['dropoff_latitude']),
            store_and_fwd_flag=row['store_and_fwd_flag'],
            trip_duration=int(row['trip_duration'])
        )
        result.append(trip)
    return result


trips = load_trips()

# 1. Строим HashMap (начинаем с capacity=8, как в ДЗ №2)
start = perf_counter()
hash_index = MyHashMap()
for trip in trips:
    hash_index.put(trip.id, trip.row_id)
hash_build_ms = round((perf_counter() - start) * 1000, 2)

# 2. Строим SegmentTree (как в ДЗ №3)
durations = [t.trip_duration for t in trips]
start = perf_counter()
st_index = SegmentTreeIndex(durations)
segment_build_ms = round((perf_counter() - start) * 1000, 2)


def get_trips_page(page: int = 1, per_page: int = 50):
    if per_page < 1:
        raise ValueError('per_page must be positive')
    total_pages = max(1, (len(trips) + per_page - 1) // per_page)
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages
    start_idx = (page - 1) * per_page
    return trips[start_idx:start_idx + per_page], page, total_pages


def linear_search_trip(trip_id: str):
    for trip in trips:
        if trip.id == trip_id:
            return trip
    return None


def find_trip_by_id(trip_id: str):
    start = perf_counter()
    row_id = hash_index.get(trip_id)
    hash_ms = round((perf_counter() - start) * 1000, 4)

    start = perf_counter()
    linear_trip = linear_search_trip(trip_id)
    linear_ms = round((perf_counter() - start) * 1000, 4)

    trip = trips[row_id] if row_id is not None else linear_trip
    return trip, hash_ms, linear_ms


def query_duration_range(l: int, r: int):
    if l > r:
        l, r = r, l
    if not trips or l < 0 or r >= len(trips):
        raise ValueError(f'Индексы должны быть в диапазоне 0..{len(trips) - 1}')

    start = perf_counter()
    st_sum = st_index.query(l, r)
    st_ms = round((perf_counter() - start) * 1000, 4)

    start = perf_counter()
    naive_sum = 0
    for i in range(l, r + 1):
        naive_sum += trips[i].trip_duration
    naive_ms = round((perf_counter() - start) * 1000, 4)

    return l, r, st_sum, st_ms, naive_sum, naive_ms


def update_trip_duration(row_id: int, new_value: int):
    if not 0 <= row_id < len(trips):
        raise ValueError('Позиция поездки находится вне диапазона')
    if new_value < 0:
        raise ValueError('Длительность не может быть отрицательной')
    trips[row_id].trip_duration = new_value
    st_index.update(row_id, new_value)


def run_benchmark_test():
    n = len(trips)
    rng = random.Random(42)
    test_vals = [t.trip_duration for t in trips]
    naive_vals = list(test_vals)
    test_st = SegmentTreeIndex(test_vals)

    ops = []
    for i in range(1000):
        if i % 2 == 0:
            pos = rng.randint(0, n - 1)
            val = rng.randint(60, 3600)
            ops.append(('update', pos, val))
        else:
            l = rng.randint(0, n // 2)
            r = rng.randint(n // 2, n - 1)
            ops.append(('query', l, r))

    start = perf_counter()
    for op, x, y in ops:
        if op == 'update':
            naive_vals[x] = y
        else:
            sum(naive_vals[x:y + 1])
    naive_ms = round((perf_counter() - start) * 1000, 2)

    start = perf_counter()
    for op, x, y in ops:
        if op == 'update':
            test_st.update(x, y)
        else:
            test_st.query(x, y)
    st_ms = round((perf_counter() - start) * 1000, 2)

    speedup = round(naive_ms / st_ms, 1) if st_ms > 0 else 0
    return {'naive_ms': naive_ms, 'st_ms': st_ms, 'speedup': speedup}