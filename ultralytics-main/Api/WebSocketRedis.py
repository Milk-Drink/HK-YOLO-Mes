import asyncio
import websockets
import redis
import json
 
# 连接到 Redis 服务器
redis_client = redis.StrictRedis(host='192.168.2.229', port=8092, db=0, decode_responses=True)
 
# Redis Pub/Sub 订阅者
class RedisSubscriber:
    def __init__(self, channel):
        self.pubsub = redis_client.pubsub()
        self.pubsub.subscribe(channel)
        self.message_queue = asyncio.Queue()
 
    async def listen(self):
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                await self.message_queue.put(message['data'])
 
async def handler(websocket):
    subscriber = RedisSubscriber(channel='video_stream')
    listening_task = asyncio.create_task(subscriber.listen())  # 启动 Redis 订阅者监听任务
 
    try:
        async for _ in websocket:  # 这将是一个无限循环，直到 WebSocket 连接关闭
            message = await subscriber.message_queue.get()
            await websocket.send(message)
    finally:
        listening_task.cancel()  # 确保在 WebSocket 关闭时取消监听任务
 
async def main():
    async with websockets.serve(handler, "172.21.2.84", 8765):
        await asyncio.Future()  # 这将阻塞直到被取消（在这个例子中，实际上永远不会被取消）
        # 注意：这里使用 asyncio.Future() 只是为了保持服务器运行。
        # 在实际应用中，你可能会有一个更优雅的关闭机制。
 
# 使用 asyncio.run() 来运行主函数
asyncio.run(main())