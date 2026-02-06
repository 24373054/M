from eth_account import Account
import secrets
import time

# 开启加速功能（可选，部分环境需要）
Account.enable_unaudited_hdwallet_features()

target_suffix = "A66A"
count = 0
start_time = time.time()

print(f"正在寻找后四位是 {target_suffix} 的地址，开始暴力穷举...")

while True:
    # 1. 生成 32 字节的随机私钥 (比 os.urandom 更适合密码学)
    private_key = "0x" + secrets.token_hex(32)
    
    # 2. 从私钥推导账户
    acct = Account.from_key(private_key)
    
    # 3. 检查地址后缀 (注意大小写，这里统一转大写比较)
    if acct.address.upper().endswith(target_suffix):
        end_time = time.time()
        print("\n" + "="*30)
        print(f"🔥 找到啦！(尝试次数: {count})")
        print(f"耗时: {end_time - start_time:.4f} 秒")
        print("-" * 30)
        print(f"地址: {acct.address}")
        print(f"私钥: {private_key}")
        print("="*30)
        print("⚠️ 请务必离线保存私钥，不要截图，不要通过网络传输！")
        break
    
    count += 1
    
    # 每 5000 次打印一下进度，避免以为死机
    if count % 5000 == 0:
        print(f"已尝试 {count} 次...", end="\r")