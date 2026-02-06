from eth_account import Account
import time
import multiprocessing
import os
import secrets

# ================= 核心配置区 =================
# 目标前缀 (注意大小写 B14F)
TARGET_PREFIX = "0xB14F" 
# 目标后缀 (注意大小写 A66A)
TARGET_SUFFIX = "A66A"   

# 【关键开关】
# True  = 极速模式 (只生成私钥，不带助记词) -> 预计耗时: 1~2 天
# False = 助记词模式 (生成助记词)          -> 预计耗时: 1~3 年 (严重不推荐)
FAST_MODE = False
# ============================================

def worker_search(process_id, stop_event, fast_mode):
    """搜索工作进程"""
    # 如果是助记词模式，需要开启 HD 功能
    if not fast_mode:
        Account.enable_unaudited_hdwallet_features()
    
    count = 0
    # 错开随机种子
    time.sleep(process_id * 0.001)
    
    while not stop_event.is_set():
        if fast_mode:
            # === 极速模式：纯随机私钥 ===
            # 手动生成私钥比 Account.create() 快很多
            private_key = "0x" + secrets.token_hex(32)
            acct = Account.from_key(private_key)
            mnemonic = "无 (极速模式)"
        else:
            # === 慢速模式：生成助记词 ===
            acct, mnemonic = Account.create_with_mnemonic()
        
        # 1. 第一轮筛选：后缀 (概率 1/65536)
        if acct.address.endswith(TARGET_SUFFIX):
            # 2. 第二轮筛选：前缀 (概率 1/65536)
            # startswith("0xB14F")
            if acct.address.startswith(TARGET_PREFIX):
                return (acct.address, mnemonic, acct.key.hex(), count)
        
        count += 1
        # 每 1000 次检查一次退出信号
        if count % 1000 == 0 and stop_event.is_set():
            return None
            
    return None

def run_ultimate_search():
    cpu_count = multiprocessing.cpu_count()
    workers = max(1, cpu_count - 1)
    
    print("="*60)
    print(f"🔥 终极算号器启动 | 核心数: {cpu_count} | 进程数: {workers}")
    print(f"🎯 目标: 前缀[{TARGET_PREFIX}] ... 后缀[{TARGET_SUFFIX}]")
    print(f"⚡ 模式: {'【极速私钥模式】(推荐)' if FAST_MODE else '【龟速助记词模式】(警告：可能需要跑几年)'}")
    print("="*60)
    
    # 预估难度提示
    # 8位16进制组合 = 42.9亿分之一
    # 大小写组合(EIP55) = 再除以 16
    print("⏳ 正在进行数学期望计算...")
    print("   理论平均尝试次数: 约 68,719,476,736 次 (687亿次)")
    
    pool = multiprocessing.Pool(processes=workers)
    manager = multiprocessing.Manager()
    stop_event = manager.Event()
    
    start_time = time.time()
    results = []

    for i in range(workers):
        results.append(pool.apply_async(worker_search, args=(i, stop_event, FAST_MODE)))
    
    try:
        total_scanned_display = 0
        last_time = start_time
        
        while True:
            # 检查是否有结果
            for res in results:
                if res.ready():
                    data = res.get()
                    if data:
                        found_address, found_mnemonic, found_key, attempts = data
                        stop_event.set()
                        end_time = time.time()
                        
                        print("\n\n" + "🎉" * 30)
                        print("🌟🌟🌟 奇迹诞生！找到指定前后缀地址！ 🌟🌟🌟")
                        print("🎉" * 30)
                        print(f"地址:   {found_address}")
                        print(f"助记词: {found_mnemonic}")
                        print(f"私钥:   {found_key}")
                        print("-" * 60)
                        print(f"总耗时: {(end_time - start_time)/3600:.2f} 小时")
                        pool.terminate()
                        return

            time.sleep(2)
            current_time = time.time()
            elapsed = current_time - start_time
            
            # 简单的速度估算
            if FAST_MODE:
                # 私钥模式单核约 30k/s (保守估计)
                speed = 30000 * workers
            else:
                # 助记词模式单核约 50/s
                speed = 55 * workers
            
            total_scanned_display = speed * elapsed
            progress = (total_scanned_display / 68719476736) * 100
            
            # 动态显示
            print(f"正在计算... 速度: {speed/1000:.1f}k/s | 已耗时: {elapsed/60:.1f}m | 进度期望: {progress:.6f}%", end="\r")

    except KeyboardInterrupt:
        print("\n🛑 任务终止")
        stop_event.set()
        pool.terminate()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    run_ultimate_search()