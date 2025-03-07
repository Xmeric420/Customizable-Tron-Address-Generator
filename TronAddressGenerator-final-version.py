import os
import tronpy
import time
import sys
from tronpy.keys import PrivateKey
import multiprocessing

def check_address(address, address_type, pattern, position):
    """检查生成的地址是否符合条件"""
    if address_type == 1:  # 连续字符
        if position == 1:  # 前缀
            return address[1:].startswith(pattern) or address[1:].startswith(pattern + pattern[0])
        elif position == 2:  # 后缀
            return address.endswith(pattern) or address.endswith(pattern + pattern[0])
        elif position == 3:  # 任意位置
            return pattern in address[1:] or (pattern + pattern[0]) in address[1:]
    elif address_type == 2:  # 固定字符
        if position == 1:  # 前缀
            return address.startswith(pattern)
        elif position == 2:  # 后缀
            return address.endswith(pattern)
        elif position == 3:  # 任意位置
            return pattern in address
    return False

def address_worker(address_type, char, count, position, result_queue):
    """地址生成工作线程"""
    pattern = char * count if address_type == 1 else char
    while True:
        private_key = PrivateKey.random()
        address = private_key.public_key.to_base58check_address()
        if check_address(address, address_type, pattern, position):
            result_queue.put((private_key.hex(), address))

def generate_address(address_type, char, count, position, num_processes=4):
    """使用多进程生成符合条件的Tron地址"""
    pattern = char * count if address_type == 1 else char
    result_queue = multiprocessing.Queue()
    processes = []
    start_time = time.time()
    last_update_time = start_time
    addresses_in_last_second = 0
    matched_count = 0

    # 启动多个进程
    for _ in range(num_processes):
        p = multiprocessing.Process(target=address_worker, args=(address_type, char, count, position, result_queue))
        p.start()
        processes.append(p)

    try:
        while True:
            while not result_queue.empty():
                private_key, address = result_queue.get()
                with open("已生成.txt", "a") as f:
                    f.write(f"Private Key: {private_key}\nAddress: {address}\n\n")
                print(f"匹配地址: {address}")
                matched_count += 1

            addresses_in_last_second += num_processes
            
            current_time = time.time()
            if current_time - last_update_time >= 1:  # 每1秒更新一次
                speed = addresses_in_last_second  # 过去1秒生成的地址总数
                print(f"\r当前速度: {speed:.2f} 地址/秒  运行时间: {int(current_time - start_time)} 秒  已找到符合要求的地址: {matched_count}", end='', flush=True)
                last_update_time = current_time
                addresses_in_last_second = 0
    
    except KeyboardInterrupt:
        print("\n手动中止程序。")
        for p in processes:
            p.terminate()

if __name__ == "__main__":
    if os.name == "nt":
        multiprocessing.set_start_method("spawn", force=True)
    else:
        multiprocessing.set_start_method("fork", force=True)
    
    print("欢迎使用Tron地址生成器")
    print("请选择地址生成类型:")
    print("1. 连续的字符")
    print("2. 固定字符")
    try:
        address_type = int(input("请输入类型编号 (1 或 2): "))
        if address_type not in [1, 2]:
            raise ValueError
    except ValueError:
        print("输入无效，程序退出。")
        exit()

    char = input("请输入指定的字符: ")
    count = None
    if address_type == 1:
        try:
            count = int(input("请输入连续个数: "))
        except ValueError:
            print("输入无效，程序退出。")
            exit()

    print("请选择字符的位置:")
    print("1. 前缀")
    print("2. 后缀")
    print("3. 任意位置")
    try:
        position = int(input("请输入位置编号 (1, 2 或 3): "))
        if position not in [1, 2, 3]:
            raise ValueError
    except ValueError:
        print("输入无效，程序退出。")
        exit()

    print("开始生成地址，匹配到的地址会保存到运行目录下的'已生成.txt'")
    generate_address(address_type=address_type, char=char, count=count, position=position, num_processes=os.cpu_count())
