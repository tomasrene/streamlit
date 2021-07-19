import time

class Timer():

    def start(self):
        """Start a new timer"""
        self._start_time = time.perf_counter()

    def stop(self) -> float:
        """Stop the timer, and report the elapsed time"""
        # Calculate elapsed time
        elapsed_time = time.perf_counter() - self._start_time
        
        # Report elapsed time
        print("Elapsed time: {:0.4f} seconds".format(elapsed_time))
        
        return elapsed_time

    def __enter__(self):
        """Start a new timer as a context manager"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Stop the context manager timer"""
        self.stop()