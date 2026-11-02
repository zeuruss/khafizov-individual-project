class Trip:
    def __init__(
        self,
        row_id,
        id,
        vendor_id,
        pickup_datetime,
        dropoff_datetime,
        passenger_count,
        pickup_longitude,
        pickup_latitude,
        dropoff_longitude,
        dropoff_latitude,
        store_and_fwd_flag,
        trip_duration
    ):
        self.row_id = row_id
        self.id = id
        self.vendor_id = vendor_id
        self.pickup_datetime = pickup_datetime
        self.dropoff_datetime = dropoff_datetime
        self.passenger_count = passenger_count
        self.pickup_longitude = pickup_longitude
        self.pickup_latitude = pickup_latitude
        self.dropoff_longitude = dropoff_longitude
        self.dropoff_latitude = dropoff_latitude
        self.store_and_fwd_flag = store_and_fwd_flag
        self.trip_duration = trip_duration