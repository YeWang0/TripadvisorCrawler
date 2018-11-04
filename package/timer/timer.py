def signal_handler(signum, frame):
    raise Exception("Timed out, the execution force stopped!")
