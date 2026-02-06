"""
多链靓号生成器 - 交互版 (安全审计修复版 v2)
支持 ETH/SOL/TRON
符合 BIP-39/BIP-44 标准，助记词可在标准钱包恢复
"""
from eth_account import Account
import time
import multiprocessing
import secrets
import hashlib
import base58

# BIP-44 派生路径
# ETH:  m/44'/60'/0'/0/0
# SOL:  m/44'/501'/0'/0'
# TRON: m/44'/195'/0'/0/0

def generate_mnemonic_and_seed() -> tuple:
    """
    安全生成 BIP-39 助记词和种子
    使用 secrets 模块提供密码学安全的熵
    """
    from mnemonic import Mnemonic
    mnemo = Mnemonic("english")
    # 显式使用 secrets 生成熵
    entropy = secrets.token_bytes(16)  # 128 bits = 12 words
    mnemonic = mnemo.to_mnemonic(entropy)
    seed = mnemo.to_seed(mnemonic, passphrase="")
    return mnemonic, seed

def derive_eth_from_seed(seed: bytes) -> tuple:
    """
    从种子派生 ETH 密钥 (BIP-44: m/44'/60'/0'/0/0)
    使用 eth_account 的标准实现
    """
    from eth_keys import keys
    from eth_account.hdaccount import generate_mnemonic, seed_from_mnemonic, key_from_seed
    
    # 使用 eth_account 内置的派生
    private_key = key_from_seed(seed, "m/44'/60'/0'/0/0")
    acct = Account.from_key(private_key)
    return acct.address, acct.key.hex()

def derive_sol_from_seed(seed: bytes, wallet_type: str = "trust") -> tuple:
    """
    从种子派生 SOL 密钥
    Trust Wallet: m/44'/501'/0'
    Phantom: m/44'/501'/0'/0'
    """
    from nacl.signing import SigningKey
    import hmac
    
    # SLIP-0010 Ed25519 派生
    I = hmac.new(b"ed25519 seed", seed, hashlib.sha512).digest()
    key = I[:32]
    chain_code = I[32:]
    
    # 根据钱包类型选择派生路径
    if wallet_type == "phantom":
        # Phantom: m/44'/501'/0'/0'
        path = [0x8000002C, 0x800001F5, 0x80000000, 0x80000000]
    else:
        # Trust Wallet: m/44'/501'/0'
        path = [0x8000002C, 0x800001F5, 0x80000000]
    
    for index in path:
        data = b'\x00' + key + index.to_bytes(4, 'big')
        I = hmac.new(chain_code, data, hashlib.sha512).digest()
        key = I[:32]
        chain_code = I[32:]
    
    signing_key = SigningKey(key)
    public_key = signing_key.verify_key._key
    address = base58.b58encode(public_key).decode('utf-8')
    full_private = key + public_key
    private_key_b58 = base58.b58encode(full_private).decode('utf-8')
    
    return address, private_key_b58

def derive_tron_from_seed(seed: bytes) -> tuple:
    """
    手动实现 TRON BIP-44 派生 (备用方案)
    """
    from ecdsa import SigningKey, SECP256k1
    import hmac
    from Crypto.Hash import keccak
    
    # BIP-32 Master key
    I = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    key = I[:32]
    chain_code = I[32:]
    
    # 派生路径: m/44'/195'/0'/0/0
    # 44' = 0x8000002C, 195' = 0x800000C3, 0' = 0x80000000, 0, 0
    path_indices = [0x8000002C, 0x800000C3, 0x80000000, 0, 0]
    
    for i, index in enumerate(path_indices):
        hardened = index >= 0x80000000
        
        if hardened:
            data = b'\x00' + key + index.to_bytes(4, 'big')
        else:
            # 非硬化派生需要公钥
            sk = SigningKey.from_string(key, curve=SECP256k1)
            vk = sk.get_verifying_key()
            public_key_bytes = b'\x04' + vk.to_string()  # 未压缩公钥
            # 压缩公钥
            x = int.from_bytes(vk.to_string()[:32], 'big')
            y = int.from_bytes(vk.to_string()[32:], 'big')
            prefix = b'\x02' if y % 2 == 0 else b'\x03'
            compressed_pubkey = prefix + x.to_bytes(32, 'big')
            data = compressed_pubkey + index.to_bytes(4, 'big')
        
        I = hmac.new(chain_code, data, hashlib.sha512).digest()
        
        # 新私钥 = (旧私钥 + I[:32]) mod n
        key_int = int.from_bytes(key, 'big')
        I_int = int.from_bytes(I[:32], 'big')
        new_key_int = (key_int + I_int) % SECP256k1.order
        key = new_key_int.to_bytes(32, 'big')
        chain_code = I[32:]
    
    private_key_hex = key.hex()
    
    # 生成地址
    sk = SigningKey.from_string(key, curve=SECP256k1)
    vk = sk.get_verifying_key()
    public_key = vk.to_string()
    
    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(public_key)
    address_bytes = keccak_hash.digest()[-20:]
    
    address_with_prefix = b'\x41' + address_bytes
    sha256_1 = hashlib.sha256(address_with_prefix).digest()
    sha256_2 = hashlib.sha256(sha256_1).digest()
    checksum = sha256_2[:4]
    
    address = base58.b58encode(address_with_prefix + checksum).decode('utf-8')
    return address, private_key_hex


def generate_eth_keypair(fast_mode=True):
    """生成 ETH 密钥对"""
    if fast_mode:
        private_key = secrets.token_bytes(32)
        private_key_hex = "0x" + private_key.hex()
        acct = Account.from_key(private_key_hex)
        return acct.address, private_key_hex, "无 (极速模式)"
    else:
        Account.enable_unaudited_hdwallet_features()
        acct, mnemonic = Account.create_with_mnemonic(
            account_path="m/44'/60'/0'/0/0"
        )
        return acct.address, acct.key.hex(), mnemonic

def generate_sol_keypair(fast_mode=True, wallet_type="trust"):
    """生成 Solana 密钥对"""
    try:
        from nacl.signing import SigningKey
        
        if fast_mode:
            private_key = secrets.token_bytes(32)
            signing_key = SigningKey(private_key)
            public_key = signing_key.verify_key._key
            address = base58.b58encode(public_key).decode('utf-8')
            full_private = private_key + public_key
            private_key_b58 = base58.b58encode(full_private).decode('utf-8')
            return address, private_key_b58, "无 (极速模式)"
        else:
            mnemonic, seed = generate_mnemonic_and_seed()
            address, private_key_b58 = derive_sol_from_seed(seed, wallet_type)
            return address, private_key_b58, mnemonic
            
    except ImportError as e:
        if "mnemonic" in str(e).lower():
            raise ImportError("请安装 mnemonic: pip install mnemonic")
        raise ImportError("请安装 pynacl: pip install pynacl")

def generate_tron_keypair(fast_mode=True):
    """生成 TRON 密钥对"""
    try:
        from ecdsa import SigningKey, SECP256k1
        from Crypto.Hash import keccak
        
        if fast_mode:
            private_key = secrets.token_bytes(32)
            private_key_hex = private_key.hex()
            
            sk = SigningKey.from_string(private_key, curve=SECP256k1)
            vk = sk.get_verifying_key()
            public_key = vk.to_string()
            
            keccak_hash = keccak.new(digest_bits=256)
            keccak_hash.update(public_key)
            address_bytes = keccak_hash.digest()[-20:]
            
            address_with_prefix = b'\x41' + address_bytes
            sha256_1 = hashlib.sha256(address_with_prefix).digest()
            sha256_2 = hashlib.sha256(sha256_1).digest()
            checksum = sha256_2[:4]
            
            address = base58.b58encode(address_with_prefix + checksum).decode('utf-8')
            return address, private_key_hex, "无 (极速模式)"
        else:
            mnemonic, seed = generate_mnemonic_and_seed()
            address, private_key_hex = derive_tron_from_seed(seed)
            return address, private_key_hex, mnemonic
            
    except ImportError as e:
        if "mnemonic" in str(e).lower():
            raise ImportError("请安装 mnemonic: pip install mnemonic")
        raise ImportError("请安装 ecdsa 和 pycryptodome: pip install ecdsa pycryptodome")

def worker_search(process_id, stop_event, counter, chain, prefix, suffix, fast_mode, wallet_type="trust"):
    """通用搜索工作进程"""
    local_count = 0
    time.sleep(process_id * 0.001)
    
    while not stop_event.is_set():
        if chain == "ETH":
            address, priv_key, mnemonic = generate_eth_keypair(fast_mode)
        elif chain == "SOL":
            address, priv_key, mnemonic = generate_sol_keypair(fast_mode, wallet_type)
        else:  # TRON
            address, priv_key, mnemonic = generate_tron_keypair(fast_mode)
        
        match_prefix = (not prefix) or address.startswith(prefix)
        match_suffix = (not suffix) or address.endswith(suffix)
        
        if match_prefix and match_suffix:
            return (chain, address, mnemonic, priv_key, counter.value + local_count)
        
        local_count += 1
        if local_count % 100 == 0:
            counter.value += 100
            local_count = 0
            if stop_event.is_set():
                return None
    return None

def calculate_difficulty(chain, prefix, suffix):
    """计算难度"""
    if chain == "ETH":
        prefix_len = len(prefix) - 2 if prefix.startswith("0x") else len(prefix)
        suffix_len = len(suffix)
        if prefix_len + suffix_len == 0:
            return 1
        return 16 ** (prefix_len + suffix_len)
    elif chain == "SOL":
        total_len = len(prefix) + len(suffix)
        if total_len == 0:
            return 1
        return 58 ** total_len
    else:  # TRON
        prefix_len = len(prefix) - 1 if prefix.startswith("T") else len(prefix)
        suffix_len = len(suffix)
        if prefix_len + suffix_len == 0:
            return 1
        return 58 ** (prefix_len + suffix_len)

def validate_prefix_suffix(chain, prefix, suffix):
    """验证前后缀格式"""
    errors = []
    
    if chain == "ETH":
        valid_chars = set("0123456789abcdefABCDEF")
        if prefix:
            if not prefix.startswith("0x"):
                errors.append("ETH 前缀必须以 0x 开头")
            else:
                for c in prefix[2:]:
                    if c not in valid_chars:
                        errors.append(f"ETH 前缀包含无效字符: {c}")
                        break
        if suffix:
            for c in suffix:
                if c not in valid_chars:
                    errors.append(f"ETH 后缀包含无效字符: {c}")
                    break
                    
    elif chain == "SOL":
        valid_chars = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
        for c in prefix + suffix:
            if c not in valid_chars:
                errors.append(f"SOL 地址不能包含字符: {c} (Base58 排除 0,O,I,l)")
                break
                
    else:  # TRON
        valid_chars = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
        if prefix and not prefix.startswith("T"):
            errors.append("TRON 前缀必须以 T 开头")
        for c in (prefix + suffix):
            if c not in valid_chars:
                errors.append(f"TRON 地址不能包含字符: {c}")
                break
    
    return errors


def interactive_menu():
    """交互式菜单"""
    print("\n" + "="*60)
    print("🔥 多链靓号生成器 - 交互版 v2")
    print("   ✅ 符合 BIP-39/BIP-44 标准")
    print("   ✅ 助记词可在标准钱包恢复")
    print("="*60)
    
    print("\n请选择链类型:")
    print("  1. ETH (以太坊)  - 派生路径: m/44'/60'/0'/0/0")
    print("  2. SOL (Solana)  - 派生路径: m/44'/501'/0'/0'")
    print("  3. TRON (波场)   - 派生路径: m/44'/195'/0'/0/0")
    
    while True:
        choice = input("\n请输入选项 (1/2/3): ").strip()
        if choice == "1":
            chain = "ETH"
            break
        elif choice == "2":
            chain = "SOL"
            break
        elif choice == "3":
            chain = "TRON"
            break
        else:
            print("❌ 无效选项，请重新输入")
    
    print(f"\n📝 {chain} 地址格式说明:")
    if chain == "ETH":
        print("   - 以 0x 开头，共42位")
        print("   - 16进制字符: 0-9, a-f, A-F")
        print("   - 示例: 0xB14F...A66A")
    elif chain == "SOL":
        print("   - Base58编码，32-44位")
        print("   - 字符: 1-9, A-Z, a-z (无0,O,I,l)")
        print("   - 示例: So1...ana")
    else:
        print("   - 以 T 开头，共34位")
        print("   - Base58编码 (无0,O,I,l)")
        print("   - 示例: T...sun")
    
    while True:
        print(f"\n请输入目标前缀 (留空则不限制):")
        if chain == "ETH":
            print("   提示: 需要包含 0x，如 0xB14F")
        elif chain == "TRON":
            print("   提示: 需要以 T 开头，如 Tsun")
        prefix = input("前缀: ").strip()
        suffix = input("请输入目标后缀 (留空则不限制): ").strip()
        
        errors = validate_prefix_suffix(chain, prefix, suffix)
        if errors:
            print("\n❌ 格式错误:")
            for err in errors:
                print(f"   - {err}")
            print("请重新输入...")
        else:
            break
    
    print("\n请选择生成模式:")
    print("  1. 极速模式 (只生成私钥，推荐)")
    print("  2. 助记词模式 (生成助记词，可在钱包恢复)")
    mode_choice = input("请输入选项 (1/2，默认1): ").strip()
    fast_mode = mode_choice != "2"
    
    # SOL 助记词模式需要选择钱包类型
    wallet_type = "trust"
    if chain == "SOL" and not fast_mode:
        print("\n请选择目标钱包 (不同钱包派生路径不同):")
        print("  1. Trust Wallet / Solflare  - m/44'/501'/0'")
        print("  2. Phantom                  - m/44'/501'/0'/0'")
        wallet_choice = input("请输入选项 (1/2，默认1): ").strip()
        wallet_type = "phantom" if wallet_choice == "2" else "trust"
    
    return chain, prefix, suffix, fast_mode, wallet_type

def run_search(chain, prefix, suffix, fast_mode, wallet_type="trust"):
    """运行搜索"""
    cpu_count = multiprocessing.cpu_count()
    workers = max(1, cpu_count - 1)
    difficulty = calculate_difficulty(chain, prefix, suffix)
    
    print("\n" + "="*60)
    print(f"🚀 开始搜索 | 核心数: {cpu_count} | 进程数: {workers}")
    print(f"� 链: {chain}")
    print(f"🎯 前缀: [{prefix if prefix else '无'}] | 后缀: [{suffix if suffix else '无'}]")
    print(f"⚡ 模式: {'极速私钥' if fast_mode else '助记词 (BIP-44标准)'}")
    if chain == "SOL" and not fast_mode:
        print(f"📱 钱包: {'Phantom' if wallet_type == 'phantom' else 'Trust Wallet / Solflare'}")
    print(f"📊 理论平均尝试次数: {difficulty:,}")
    print("="*60)
    print("按 Ctrl+C 停止搜索\n")
    
    pool = multiprocessing.Pool(processes=workers)
    manager = multiprocessing.Manager()
    stop_event = manager.Event()
    counter = manager.Value('i', 0)
    
    start_time = time.time()
    results = []

    for i in range(workers):
        results.append(pool.apply_async(
            worker_search, 
            args=(i, stop_event, counter, chain, prefix, suffix, fast_mode, wallet_type)
        ))
    
    try:
        while True:
            for res in results:
                if res.ready():
                    data = res.get()
                    if data:
                        found_chain, found_address, found_mnemonic, found_key, attempts = data
                        stop_event.set()
                        end_time = time.time()
                        
                        print("\n\n" + "🎉" * 30)
                        print(f"🌟 找到 {found_chain} 靓号地址！ 🌟")
                        print("🎉" * 30)
                        print(f"链:     {found_chain}")
                        print(f"地址:   {found_address}")
                        if found_mnemonic and not found_mnemonic.startswith("无"):
                            print(f"助记词: {found_mnemonic}")
                            print(f"        ⚠️  请妥善保管助记词，可在标准钱包恢复")
                        else:
                            print(f"助记词: {found_mnemonic}")
                        print(f"私钥:   {found_key}")
                        print("-" * 60)
                        print(f"总尝试: {attempts:,} 次")
                        print(f"总耗时: {(end_time - start_time):.2f} 秒")
                        pool.terminate()
                        return True

            time.sleep(0.5)
            elapsed = time.time() - start_time
            total_scanned = counter.value
            
            speed = total_scanned / elapsed if elapsed > 0 else 0
            progress = (total_scanned / difficulty) * 100 if difficulty > 0 else 100
            if progress > 100:
                progress_str = f"期望的 {progress/100:.1f}x"
            else:
                progress_str = f"{progress:.2f}%"
            
            print(f"[{chain}] 已尝试: {total_scanned:,} | 速度: {speed:.0f}/s | 耗时: {elapsed:.1f}s | 进度: {progress_str}    ", end="\r")

    except KeyboardInterrupt:
        print(f"\n\n🛑 搜索已停止，共尝试 {counter.value:,} 次")
        stop_event.set()
        pool.terminate()
        return False

def main():
    """主函数"""
    print("\n" + "="*60)
    print("⚠️  安全提示:")
    print("   - 本工具使用 secrets 模块生成密码学安全随机数")
    print("   - 助记词模式符合 BIP-39/BIP-44 标准")
    print("   - 生成的助记词可在 MetaMask/Phantom/TronLink 恢复")
    print("   - 请在安全的离线环境运行")
    print("="*60)
    
    while True:
        chain, prefix, suffix, fast_mode, wallet_type = interactive_menu()
        
        print("\n" + "-"*40)
        print("📋 确认信息:")
        print(f"   链: {chain}")
        print(f"   前缀: {prefix if prefix else '无'}")
        print(f"   后缀: {suffix if suffix else '无'}")
        print(f"   模式: {'极速私钥' if fast_mode else '助记词 (BIP-44)'}")
        if chain == "SOL" and not fast_mode:
            print(f"   钱包: {'Phantom' if wallet_type == 'phantom' else 'Trust Wallet / Solflare'}")
        
        confirm = input("\n确认开始? (y/n): ").strip().lower()
        if confirm == 'y':
            run_search(chain, prefix, suffix, fast_mode, wallet_type)
        
        again = input("\n是否继续生成? (y/n): ").strip().lower()
        if again != 'y':
            print("\n👋 再见!")
            break

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
