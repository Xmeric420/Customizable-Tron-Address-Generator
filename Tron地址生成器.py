import os
import tronpy
import time
from tronpy.keys import PrivateKey

def clear_screen():
    """根据操作系统清屏"""
    if os.name == 'nt':  # Windows系统
        os.system('cls')
    else:  # Linux 或 macOS 系统
        os.system('clear')

def calculate_probability(address_type, char, count=None, base58_size=58):
    """计算生成指定字符的概率"""
    if address_type == "连续字符":
        # 连续字符的概率：每个字符的位置是固定的
        probability = (1 / base58_size) ** count
    elif address_type == "固定字符":
        # 固定字符的概率：每个字符位置是固定的，计算该字符出现在地址中的任意位置
        probability = (1 / base58_size) * len(char)  # 假设字符出现在地址的任意位置
    return probability

def generate_address(address_type, char, count, position):
    """生成符合条件的Tron地址"""
    pattern = char * count if address_type == "连续字符" else char  # 只有在"连续字符"时使用count
    base58_size = 58  # Base58字符集的大小

    total_addresses_generated = 0  # 记录生成的地址数量
    start_time = time.time()  # 记录程序开始的时间
    last_update_time = start_time  # 用于控制每秒更新一次显示信息

    while True:
        private_key = PrivateKey.random()
        public_key = private_key.public_key
        address = public_key.to_base58check_address()

        match = False
        if address_type == "连续字符":
            if position == "前缀":
                match = address[1:].startswith(pattern)  # 从 T 后开始匹配
            elif position == "后缀":
                match = address.endswith(pattern)
            elif position == "任意位置":
                match = pattern in address[1:]  # 忽略 T
        elif address_type == "固定字符":
            if position == "前缀":
                match = address.startswith(pattern)
            elif position == "后缀":
                match = address.endswith(pattern)
            elif position == "任意位置":
                match = pattern in address

        if match:
            with open("已生成.txt", "a") as f:
                f.write(f"Private Key: {private_key.hex()}\nAddress: {address}\n\n")
            print(f"匹配地址: {address}")
            break

        # 更新生成的地址数量
        total_addresses_generated += 1

        # 每秒更新信息
        current_time = time.time()
        elapsed_time = current_time - start_time  # 计算已运行时间

        if current_time - last_update_time >= 1:  # 每过1秒更新一次
            clear_screen()  # 清屏
            speed = total_addresses_generated / elapsed_time  # 每秒生成的地址数量

            # 计算生成目标地址的概率
            probability = calculate_probability(address_type, char, count, base58_size)
            probability_percent = probability * 100  # 转换为百分比

            # 估算剩余时间：剩余地址数 / 当前生成速度
            remaining_addresses = (1 / probability)  # 剩余的地址数
            estimated_time = remaining_addresses / speed if speed > 0 else float('inf')

            # 显示信息
            print(f"当前速度: {speed:.2f} 地址/秒")
            print(f"运行时间: {int(elapsed_time)} 秒")  # 显示整数时间
            print(f"生成目标地址的概率: {probability_percent:.10f} %")
            print(f"估算剩余时间: {estimated_time:.2f} 秒")

            # 更新最后更新时间
            last_update_time = current_time

if __name__ == "__main__":
    print("欢迎使用Tron地址生成器")

    print("请选择地址生成类型:")
    print("1. 连续的字符")
    print("2. 固定字符")
    try:
        choice = int(input("请输入类型编号 (1 或 2): "))
    except ValueError:
        print("输入无效，程序退出。")
        exit()

    if choice == 1:
        address_type = "连续字符"
        char = input("请输入指定的字符: ")
        try:
            count = int(input("请输入连续个数: "))
        except ValueError:
            print("输入无效，程序退出。")
            exit()
        print("请选择连续字符的位置:")
        print("1. 前缀")
        print("2. 后缀")
        print("3. 任意位置")
        try:
            pos_choice = int(input("请输入位置编号 (1, 2 或 3): "))
        except ValueError:
            print("输入无效，程序退出。")
            exit()
        position = "前缀" if pos_choice == 1 else "后缀" if pos_choice == 2 else "任意位置"
    elif choice == 2:
        address_type = "固定字符"
        char = input("请输入指定的字符: ")
        print("请选择固定字符的位置:")
        print("1. 前缀")
        print("2. 后缀")
        print("3. 任意位置")
        try:
            pos_choice = int(input("请输入位置编号 (1, 2 或 3): "))
        except ValueError:
            print("输入无效，程序退出。")
            exit()
        position = "前缀" if pos_choice == 1 else "后缀" if pos_choice == 2 else "任意位置"
        count = None  # 固定字符不需要输入count
    else:
        print("无效的选择，程序退出。")
        exit()

    print("开始生成地址，匹配到的地址会保存到运行目录下的'已生成.txt'")
    generate_address(address_type=address_type, char=char, count=count, position=position)
