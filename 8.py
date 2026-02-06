"""
助记词地址扫描器
输入助记词，扫描所有常见派生路径，显示对应的地址和私钥
"""
from mnemonic import Mnemonic
from eth_account import Account
import hashlib
import hmac
import base58

def derive_eth_address(seed: bytes, path: str) -> tuple:
    """派生 ETH 地址"""
    from eth_account.hdaccount import key_from_seed
    private_key = key_from_seed(seed, path)
    acct = Account.from_key(private_key)
    return acct.address, acct.key.hex()

def derive_sol_address(seed: bytes, path_indices: list) -> tuple:
    """派生 SOL 地址 (SLIP-0010 Ed25519)"""
    from nacl.signing import SigningKey
    
    I = hmac.new(b"ed25519 seed", seed, hashlib.sha512).digest()
    key = I[:32]
    chain_code = I[32:]
    
    for index in path_indices:
        data = b'\x00' + key + index.to_bytes(4, 'big')
        I = hmac.new(chain_code, data, hashlib.sha512).digest()
        key = I[:32]
        chain_code = I[32:]
    
    signing_key = SigningKey(key)
    public_key = signing_key.verify_key._key
    address = base58.b58encode(public_key).decode('utf-8')
    full_private = key + public_key
    private_key = base58.b58encode(full_private).decode('utf-8')
    
    return address, private_key

def derive_tron_address(seed: bytes, path_indices: list) -> tuple:
    """派生 TRON 地址 (BIP-32 secp256k1)"""
    from ecdsa import SigningKey, SECP256k1
    from Crypto.Hash import keccak
    
    I = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    key = I[:32]
    chain_code = I[32:]
    
    for i, index in enumerate(path_indices):
        hardened = index >= 0x80000000
        
        if hardened:
            data = b'\x00' + key + index.to_bytes(4, 'big')
        else:
            sk = SigningKey.from_string(key, curve=SECP256k1)
            vk = sk.get_verifying_key()
            x = int.from_bytes(vk.to_string()[:32], 'big')
            y = int.from_bytes(vk.to_string()[32:], 'big')
            prefix = b'\x02' if y % 2 == 0 else b'\x03'
            compressed_pubkey = prefix + x.to_bytes(32, 'big')
            data = compressed_pubkey + index.to_bytes(4, 'big')
        
        I = hmac.new(chain_code, data, hashlib.sha512).digest()
        key_int = int.from_bytes(key, 'big')
        I_int = int.from_bytes(I[:32], 'big')
        new_key_int = (key_int + I_int) % SECP256k1.order
        key = new_key_int.to_bytes(32, 'big')
        chain_code = I[32:]
    
    private_key_hex = key.hex()
    
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


# 常见派生路径配置
ETH_PATHS = [
    ("m/44'/60'/0'/0/0", "MetaMask / Trust Wallet / imToken 默认"),
    ("m/44'/60'/0'/0/1", "第2个地址"),
    ("m/44'/60'/0'/0/2", "第3个地址"),
    ("m/44'/60'/0'/0/3", "第4个地址"),
    ("m/44'/60'/0'/0/4", "第5个地址"),
    ("m/44'/60'/1'/0/0", "账户2"),
    ("m/44'/60'/2'/0/0", "账户3"),
    ("m/44'/60'/0'", "Ledger Live 旧版"),
    ("m/44'/60'/0'/0", "某些旧钱包"),
]

SOL_PATHS = [
    ([0x8000002C, 0x800001F5, 0x80000000], "m/44'/501'/0'", "Trust Wallet / Solflare 默认"),
    ([0x8000002C, 0x800001F5, 0x80000000, 0x80000000], "m/44'/501'/0'/0'", "Phantom / Sollet 默认"),
    ([0x8000002C, 0x800001F5], "m/44'/501'", "Solana CLI 根密钥"),
    ([0x8000002C, 0x800001F5, 0x80000001], "m/44'/501'/1'", "第2个账户 (Trust)"),
    ([0x8000002C, 0x800001F5, 0x80000002], "m/44'/501'/2'", "第3个账户 (Trust)"),
    ([0x8000002C, 0x800001F5, 0x80000000, 0x80000001], "m/44'/501'/0'/1'", "第2个地址 (Phantom)"),
    ([0x8000002C, 0x800001F5, 0x80000000, 0x80000002], "m/44'/501'/0'/2'", "第3个地址 (Phantom)"),
    ([0x8000002C, 0x800001F5, 0x80000001, 0x80000000], "m/44'/501'/1'/0'", "账户2 (Phantom)"),
]

TRON_PATHS = [
    ([0x8000002C, 0x800000C3, 0x80000000, 0, 0], "m/44'/195'/0'/0/0", "TronLink / Trust Wallet 默认"),
    ([0x8000002C, 0x800000C3, 0x80000000, 0, 1], "m/44'/195'/0'/0/1", "第2个地址"),
    ([0x8000002C, 0x800000C3, 0x80000000, 0, 2], "m/44'/195'/0'/0/2", "第3个地址"),
    ([0x8000002C, 0x800000C3, 0x80000001, 0, 0], "m/44'/195'/1'/0/0", "账户2"),
    ([0x8000002C, 0x800000C3, 0x80000002, 0, 0], "m/44'/195'/2'/0/0", "账户3"),
]

def scan_eth(seed: bytes):
    """扫描 ETH 地址"""
    Account.enable_unaudited_hdwallet_features()
    print("\n" + "="*80)
    print("🔷 ETH (以太坊) 地址扫描结果")
    print("="*80)
    
    for path, desc in ETH_PATHS:
        try:
            address, private_key = derive_eth_address(seed, path)
            print(f"\n📍 {desc}")
            print(f"   路径: {path}")
            print(f"   地址: {address}")
            print(f"   私钥: {private_key}")
        except Exception as e:
            print(f"\n❌ {path}: {e}")

def scan_sol(seed: bytes):
    """扫描 SOL 地址"""
    print("\n" + "="*80)
    print("🟣 SOL (Solana) 地址扫描结果")
    print("="*80)
    
    for path_indices, path_str, desc in SOL_PATHS:
        try:
            address, private_key = derive_sol_address(seed, path_indices)
            print(f"\n📍 {desc}")
            print(f"   路径: {path_str}")
            print(f"   地址: {address}")
            print(f"   私钥: {private_key}")
        except Exception as e:
            print(f"\n❌ {path_str}: {e}")

def scan_tron(seed: bytes):
    """扫描 TRON 地址"""
    print("\n" + "="*80)
    print("🔴 TRON (波场) 地址扫描结果")
    print("="*80)
    
    for path_indices, path_str, desc in TRON_PATHS:
        try:
            address, private_key = derive_tron_address(seed, path_indices)
            print(f"\n📍 {desc}")
            print(f"   路径: {path_str}")
            print(f"   地址: {address}")
            print(f"   私钥: {private_key}")
        except Exception as e:
            print(f"\n❌ {path_str}: {e}")

def main():
    print("\n" + "="*60)
    print("🔍 助记词地址扫描器")
    print("   扫描所有常见派生路径，找到对应的地址和私钥")
    print("="*60)
    
    # 选择网络
    print("\n请选择网络:")
    print("  1. ETH (以太坊)")
    print("  2. SOL (Solana)")
    print("  3. TRON (波场)")
    print("  4. 全部扫描")
    
    while True:
        choice = input("\n请输入选项 (1/2/3/4): ").strip()
        if choice in ["1", "2", "3", "4"]:
            break
        print("❌ 无效选项")
    
    # 输入助记词
    print("\n请输入助记词 (12或24个单词，空格分隔):")
    mnemonic = input().strip()
    
    # 验证助记词
    mnemo = Mnemonic("english")
    if not mnemo.check(mnemonic):
        print("\n❌ 助记词无效！请检查拼写和单词数量")
        return
    
    # 生成种子
    seed = mnemo.to_seed(mnemonic, passphrase="")
    
    print("\n✅ 助记词有效，开始扫描...")
    
    # 扫描
    if choice == "1":
        scan_eth(seed)
    elif choice == "2":
        scan_sol(seed)
    elif choice == "3":
        scan_tron(seed)
    else:
        scan_eth(seed)
        scan_sol(seed)
        scan_tron(seed)
    
    print("\n" + "="*60)
    print("✅ 扫描完成！")
    print("⚠️  请妥善保管私钥，不要泄露给任何人")
    print("="*60)

if __name__ == "__main__":
    main()
