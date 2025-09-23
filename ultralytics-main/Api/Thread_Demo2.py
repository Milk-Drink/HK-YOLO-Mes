import time
import asyncio
from datetime import datetime
import threading


def runtime(function):
    def wapper(*args,**kwargs):
        starttime=datetime.now()
        result=function(*args,**kwargs)
        endtime=datetime.now()
        print(f"The Function [{function.__name__}] Run Time INTO {endtime-starttime}")
        return result
    return wapper

@runtime
def run():
    for a in ['a','b','c']:
        print(a)
        # time.sleep(1)
@runtime
def run2():
    for i in range(10):
        print(i)
        # time.sleep(1)


if __name__=="__main__":
    task=threading.Thread(target=run)
    task2=threading.Thread(target=run2)

    task.start()
    task2.start()
    task.join()
    task2.join()
    # run()
    # run2()
