from datetime import datetime
import time
import asyncio




def runtime(function):
    async def wapper(*args,**kwargs):
        starttime=datetime.now()
        result= await function(*args,**kwargs)
        endtime=datetime.now()
        print(f"The Function [{function.__name__}] Run Time INTO {endtime-starttime}")
        return result
    return wapper

@runtime
async def run():
    for a in ['a','b','c','d','e','f','g']:
        print( a)
        await asyncio.sleep(1)
@runtime
async def run2():
    for i in range(10):
        print( i)
        await asyncio.sleep(1)

@runtime
async def main():
    # result=await asyncio.gather(run(),run2(),)
    result=asyncio.as_completed([run(),run2()])
    for x in result:

        print(await x )


if __name__=="__main__":
    asyncio.run(main())