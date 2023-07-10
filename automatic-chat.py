# -*- codeing = utf-8 -*-
# @Time       : 2023/7/7 21:56
# @Author     : Baxkiller
# @File       : automatic-chat.py
# @Software   : PyCharm
# @Description: 预定提问顺序向Bing Chat提问
import asyncio
import websockets

from config import *
from class_library import InstGenerator

# 存储所有连接的客户端
clients = set()


async def receive(websocket, path):
    # 添加新的客户端到集合中
    clients.add(websocket)
    print('有新的客户端连接')
    FIRST = True

    try:
        async for message in websocket:
            print(f'接收到客户端发来的消息：{message}')

            # 检查API 调用API之后获得返回
            if FIRST:
                instructions = InstGenerator(prompt_seq, prompt_filepath, paper_filepath, response_filepath)
                FIRST = False

            new_instruction = instructions.get_prompt(message)
            print(new_instruction)
            if new_instruction is not None and new_instruction != "" and new_instruction != " ":
                pass
            else:
                while True:
                    print("请输入您的问题:")
                    _ = input()
                    break
            result = new_instruction.strip()
            # 将消息发送给所有已连接的客户端
            await websocket.send(result)

    except websockets.exceptions.ConnectionClosed:
        print('客户端断开连接')

    finally:
        # 移除已断开连接的客户端
        clients.remove(websocket)


async def send(message):
    # 向所有已连接的客户端发送消息
    for client in clients:
        if client.open:
            await client.send(message)


async def start_server():
    async with websockets.serve(receive, "localhost", 8888):
        print("WebSocket 服务器已启动")
        await asyncio.Future()  # 阻止停止


if __name__ == "__main__":
    asyncio.run(start_server())
