import multiprocessing
import secrets
from eth_account import Account
import time
import os

# ================= 目标配置 =================
# 目标：USDT (Tether) 风格地址
# 注意：脚本默认匹配小写数值 (dac...31ec7)，这是CPU算力的极限
TARGET_PREFIX = "0xdac"  # 必须小写
TARGET_SUFFIX = "31ec7"  # 必须小写
# ===========================================

def worker(stop_event, cpu_id):
    """
    极速工作进程：只做生成私钥 -> 算地址 -> 比对字符串
    """
    # 预加载函数到局部变量，减少全局查找开销
    from_key = Account.from_key
    token_hex = secrets.token_hex
    p_start = TARGET_PREFIX
    p_end = TARGET_SUFFIX
    
    # 错开时间种子
    time.sleep(cpu_id * 0.1)
    
    count = 0
    while not stop_event.is_set():
        # 1. 生成私钥 (这是Python能做到的最快方式)
        private_key = "0x" + token_hex(32)
        
        # 2. 推导地址
        acct = from_key(private_key)
        addr_lower = acct.address.lower() # 转小写比对
        
        # 3. 极速比对 (先比后缀5位，再比前缀3位，效率最高)
        if addr_lower.endswith(p_end):
            if addr_lower.startswith(p_start):
                return (acct.address, private_key)
        
        count += 1
        # 每 5000 次检查一次退出信号
        if count % 5000 == 0:
            if stop_event.is_set():
                return None

def main():
    # 获取核心数
    cpu_count = multiprocessing.cpu_count()
    # 留一个核给系统，其他的全跑
    workers = max(1, cpu_count - 1)
    
    print(f"🚀 极速引擎启动 | 目标: {TARGET_PREFIX}...{TARGET_SUFFIX}")
    print(f"🔥 调用核心: {workers} 个 | 预计难度: 42亿次尝试")
    print("⏳ 正在计算中，请耐心挂机 (建议使用 screen/nohup)...")
    
    pool = multiprocessing.Pool(processes=workers)
    manager = multiprocessing.Manager()
    stop_event = manager.Event()
    
    results = []
    start_time = time.time()
    
    for i in range(workers):
        results.append(pool.apply_async(worker, args=(stop_event, i)))
        
    try:
        while True:
            # 轮询检查是否有结果
            for res in results:
                if res.ready():
                    data = res.get()
                    if data:
                        addr, key = data
                        stop_event.set()
                        pool.terminate()
                        
                        end_time = time.time()
                        hours = (end_time - start_time) / 3600
                        
                        print("\n" + "="*50)
                        print("🎉 找到啦！USDT 风格地址生成成功！")
                        print("="*50)
                        print(f"地址: {addr}")
                        print(f"私钥: {key}")
                        print("-" * 50)
                        print(f"总耗时: {hours:.2f} 小时")
                        print("="*50)
                        return
            
            # 简单的进度展示
            time.sleep(5)
            elapsed = time.time() - start_time
            # 估算速度：假设单核 2万次/秒 (纯私钥模式很快)
            speed = 20000 * workers
            total = speed * elapsed
            # 进度百分比 (基于43亿次期望)
            progress = (total / 4294967296) * 100
            
            print(f"已运行 {elapsed/60:.1f} 分钟 | 估算速度: {speed/1000:.0f}k/s | 期望进度: {progress:.4f}%", end="\r")
            
    except KeyboardInterrupt:
        print("\n🛑 停止")
        stop_event.set()
        pool.terminate()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()