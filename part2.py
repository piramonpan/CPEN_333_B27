# Group #: B27
# Student names: Piramon Tisapramotkul and Joshan Gill 

import threading
import queue
import time, random

def consumerWorker (queue : queue.Queue):

    """
    target worker for a consumer thread
    Consume a fixed number of item and remove them from the buffer
    """

    def waitForItemToBeConsumed() -> None: #inner function; use as is
        time.sleep(round(random.uniform(DELAY_RANGE_MIN, DELAY_RANGE_MAX), 2)) #a random delay (100 to 300ms)
    
    while True:
        waitForItemToBeConsumed() # Delay simulating item being consumed
        item = buffer.get()  
        print(f"{threading.current_thread().name}: {item} consumed")
        buffer.task_done()

def producerWorker(queue : queue.Queue):
    """
    target worker for a producer thread
    Produces a fixed number of items and add them to the buffer
    """

    def waitForItemToBeProduced() -> int: #inner function; use as is
        time.sleep(round(random.uniform(DELAY_RANGE_MIN, DELAY_RANGE_MAX), 2)) #a random delay (100 to 300ms)
        return random.randint(1, 50) #an item is produced
    
    for _ in range(ITEMS_PER_THREAD):
        item = waitForItemToBeProduced()
        print(f"{threading.current_thread().name}: {item} produced")
        queue.put(item)

if __name__ == "__main__":
    NUM_PRODUCERS = 4
    NUM_CONSUMERS = 5
    ITEMS_PER_THREAD = 10
    DELAY_RANGE_MIN = 0.1 # Seconds
    DELAY_RANGE_MAX = 0.3  # Seconds

    # Initialize buffer using queue module - No maximum buffer size 
    buffer = queue.Queue()

    # Creating lists to store producer and consumer threads 
    producer_threads : list[threading.Thread] = []
    consumer_threads : list[threading.Thread] = []

    # Create producere threads
    for i in range(NUM_PRODUCERS):
        producer_threads.append(threading.Thread(target=producerWorker, args=(buffer,), name=f"Producer-{i+1}"))
    
    # Create consumer threads as daemons
    for j in range(NUM_CONSUMERS):
        consumer_threads.append(threading.Thread(target=consumerWorker, args=(buffer,), daemon=False, name=f"Consumer-{j+1}"))

    # Start producer threads
    for i in producer_threads:
        i.start()

    # Start consumer threads
    for j in consumer_threads:
        j.start()
    
    # Wait for all producer threads to finish
    for i in producer_threads:
        i.join()

    # Wait until all produced items have been processed
        buffer.join()

    print("All items produced and consumed succesfully!")