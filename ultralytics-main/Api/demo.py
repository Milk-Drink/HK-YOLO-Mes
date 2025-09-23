import asyncio
import time
from datetime import datetime

# def run():
#     time.sleep(1)
#     print("The Run response")

# def run2():
#     time.sleep(2)
#     print("The Run2 Response")
def runtimeget(function):
    def wapper(*args,**kwargs):
        starttime=datetime.now()

        # print("This is The 装饰器 Response")
        result=function(*args,**kwargs)
        endtime=datetime.now()
        print(f"The Fun {function.__name__} Run INTO {endtime-starttime}")
        return result
    return wapper

@runtimeget
async def run():
    await asyncio.sleep(3)
    # print("The Run response")
    return "The Run response"

async def run2():
    await asyncio.sleep(2)
    # print("The Run2 Response")
    return "The Run2 Response"

async def main():
    # task=asyncio.create_task(run())
    # task2=asyncio.create_task(run2())
    # taskresult=await task
    # task2result=await task2
    result=  asyncio.as_completed([run(),run2()])
    for x in result:
        print(await x)
if __name__=="__main__":
    starttime=datetime.now()
    # run()
    # run2()
    asyncio.run(main())
    endtime=datetime.now()
    print(f"Run l {endtime-starttime}")