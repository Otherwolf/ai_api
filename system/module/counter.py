def get_counter(start=1, step=1):
    while True:
        yield start
        start += step
