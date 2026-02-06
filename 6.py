
import time
import secrets
from eth_account import Account
import multiprocessing

# 强制单核测速，看看基准
def benchmark():
    print("正在测试单核真实算力，请等待 5 秒...")
    start = time.time()
    count = 0
    # 模拟真实的计算负载
    while time.time() - start < 5:
        pk = "0x" + secrets.token_hex(32)
        Account.from_key(pk).address.lower()
        count += 1
    
    speed = count / 5
    print(f"单核真实速度: {speed:.1f} ops/s")
    
    cpu_count = multiprocessing.cpu_count() - 1
    total_speed = speed * cpu_count
    print(f"你的 19 核总理论速度: {total_speed:.1f} ops/s")
    
    # 计算找到目标的真实期望时间
    # 目标难度 42.9亿
    expected_seconds = 4294967296 / total_speed
    print(f"------------------------------------------------")
    print(f"跑完 100% 概率期望需要: {expected_seconds/3600:.2f} 小时")

if __name__ == "__main__":
    benchmark()