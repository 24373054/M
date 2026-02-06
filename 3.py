from eth_account import Account
import time
import sys

# =================配置区=================
# 这里必须严格写出你想要的大小写格式
TARGET_SUFFIX = "A66A"  
# ========================================

def run_strict_search():
    # 0. 开启 HD 钱包功能
    Account.enable_unaudited_hdwallet_features()

    print(f"🛠️  正在执行启动自检...")
    # --- 安全阀 1: 逻辑自检 ---
    # 我们故意制造一个不匹配的测试，确保代码不会因为大小写搞混
    test_addr_lower = "0x1234a66a"
    test_addr_upper = "0x1234A66A"
    
    # 如果代码把小写误判为符合目标，立刻报错
    if test_addr_lower.endswith(TARGET_SUFFIX): 
        print("❌ 致命错误：代码逻辑无法区分大小写，已紧急终止！")
        return
    
    # 确保目标后缀本身是合法的十六进制字符
    import string
    if not all(c in string.hexdigits for c in TARGET_SUFFIX):
        print("❌ 错误：目标后缀包含非十六进制字符！")
        return

    print(f"✅ 自检通过：代码能够精准识别 '{TARGET_SUFFIX}' (严格区分大小写)")
    print(f"🔥 任务开始：寻找后四位严格为 '{TARGET_SUFFIX}' 且带有助记词的钱包")
    print(f"⏳ 预估难度：非常高。可能需要运行 1 ~ 3 小时，请耐心等待...")
    print("-" * 50)

    count = 0
    start_time = time.time()
    
    while True:
        # 1. 生成带助记词的新账户 (这是最耗时的步骤，因为涉及 PBKDF2)
        acct, mnemonic = Account.create_with_mnemonic()
        
        # 2. 严格匹配 (去掉 .upper()，必须一模一样)
        # eth_account 生成的 acct.address 默认就是带 EIP-55 校验(大小写)的
        if acct.address.endswith(TARGET_SUFFIX):
            end_time = time.time()
            
            # --- 安全阀 2: 最终验证 ---
            # 找到后，我们不要急着高兴，先用助记词反推一遍，确保 100% 对得上
            print("\n🔍 正在进行最终一致性校验...")
            re_derived_acct = Account.from_mnemonic(mnemonic)
            
            if re_derived_acct.address != acct.address:
                print("❌ 灾难性错误：助记词反推地址不匹配！结果无效！")
                break
                
            print("\n" + "🎉" * 20)
            print("  恭喜！成功捕获指定大小写靓号！")
            print("🎉" * 20)
            print(f"\n[地址] (EIP-55校验格式):")
            print(f"{acct.address}")
            print(f"\n[助记词] (请务必离线手抄):")
            print(f"{mnemonic}")
            print(f"\n[私钥]:")
            print(f"{acct.key.hex()}")
            print("-" * 50)
            print(f"总尝试: {count} 次")
            print(f"总耗时: {(end_time - start_time)/60:.1f} 分钟")
            print("=" * 50)
            break

        count += 1
        
        # 进度条：每 50 次打印一次，显示当前速度
        if count % 50 == 0:
            elapsed = time.time() - start_time
            speed = count / elapsed
            print(f"已扫描 {count} 个钱包... 当前速度: {speed:.1f} 个/秒 | 预计还需等待...", end="\r")

if __name__ == "__main__":
    try:
        run_strict_search()
    except KeyboardInterrupt:
        print("\n\n🛑 用户手动停止。")