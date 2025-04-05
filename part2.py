# Group #:
# Student names:

import threading
import queue
import time, random

def consumerWorker (queue : queue.Queue):
    """target worker for a consumer thread"""
    def waitForItemToBeConsumed() -> None: #inner function; use as is
        time.sleep(round(random.uniform(.1, .3), 2)) #a random delay (100 to 300

    for _ in range(SIZE * 2): #we just consume twice the buffer size for testing
        #write the code below to correctly remove an item from the circular buffer
        waitForItemToBeConsumed() #wait for the item to be consumed
        item = queue.get()
        print(f"DEBUG: {item} consumed")
        
def producerWorker(queue : queue.Queue):
    """target worker for a producer thread"""

    def waitForItemToBeProduced() -> int: #inner function; use as is
        time.sleep(round(random.uniform(.1, .3), 2)) #a random delay (100 to 300ms)
        return random.randint(1, 50) #an item is produced
    
    for _ in range(SIZE * 2):
        item = waitForItemToBeProduced()
        print(f"DEBUG: {item} produced" )
        queue.put(item=item)
        print(list(queue.queue))


if __name__ == "__main__":
    SIZE = 5
    THREADS = 5

    buffer = queue.Queue()

    # Creating producer and consumer threads 
    producer_threads : list[threading.Thread] = []
    consumer_threads : list[threading.Thread] = []

    for _ in range(4):
        producer_threads.append(threading.Thread(target=producerWorker, args=(buffer,)))
    for _ in range(5):
        consumer_threads.append(threading.Thread(target=consumerWorker, args=(buffer,), daemon=True))

    for i in producer_threads:
        i.start()
    for j in consumer_threads:
        j.start()
        
    for i in producer_threads:
        i.join()

    print("All items produced and consumed succesfully")