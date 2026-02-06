"""
多链钱包工具 - 余额查询 & 转账
支持 ETH/SOL/TRON
纯代码操作，不依赖任何钱包App
支持 Tor 代理隐私保护
"""
import requests
import time
import subprocess
import os
import socket

# ================= RPC 节点配置 =================
ETH_RPC = "https://eth.llamarpc.com"
SOL_RPC = "https://api.mainnet-beta.solana.com"
TRON_API = "https://api.trongrid.io"

# ================= Tor 配置 =================
# 独立 Tor 服务端口是 9050，Tor Browser 是 9150
TOR_SOCKS_PORT = 9050
TOR_PROXY = f"socks5h://127.0.0.1:{TOR_SOCKS_PORT}"
USE_TOR = False  # 全局开关

# Tor 服务路径
TOR_EXE_PATH = "C:/Users/23157/CODE/TOR/tor-expert-bundle-windows-x86_64-14.5.7/tor/tor.exe"
TOR_CONFIG_PATH = "C:/Users/23157/AppData/Roaming/tor/torrc"

def get_proxies():
    """获取代理配置"""
    if USE_TOR:
        return {
            "http": TOR_PROXY,
            "https": TOR_PROXY
        }
    return None

def check_tor_running() -> bool:
    """检查 Tor 是否在运行"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', TOR_SOCKS_PORT))
        sock.close()
        return result == 0
    except:
        return False

def start_tor():
    """启动 Tor 服务"""
    global USE_TOR
    
    if check_tor_running():
        print("✅ Tor 已在运行")
        USE_TOR = True
        return True
    
    # 检查 tor.exe 是否存在
    if not os.path.exists(TOR_EXE_PATH):
        print(f"❌ 找不到 Tor: {TOR_EXE_PATH}")
        return False
    
    if not os.path.exists(TOR_CONFIG_PATH):
        print(f"❌ 找不到配置文件: {TOR_CONFIG_PATH}")
        return False
    
    print(f"⏳ 正在启动 Tor 服务...")
    try:
        # 后台启动 Tor
        subprocess.Popen(
            [TOR_EXE_PATH, "-f", TOR_CONFIG_PATH],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        # 等待 Tor 连接
        print("⏳ 等待 Tor 网络连接...")
        for i in range(30):
            time.sleep(1)
            if check_tor_running():
                print("✅ Tor 连接成功!")
                USE_TOR = True
                return True
            print(f"   等待中... {i+1}s")
        
        print("❌ Tor 连接超时")
        return False
    except Exception as e:
        print(f"❌ 启动 Tor 失败: {e}")
        return False

def stop_tor_service():
    """停止 Tor 服务"""
    global USE_TOR
    USE_TOR = False
    try:
        if os.name == 'nt':
            subprocess.run(["taskkill", "/F", "/IM", "tor.exe"], 
                         capture_output=True, check=False)
        else:
            subprocess.run(["pkill", "tor"], capture_output=True, check=False)
        print("✅ Tor 服务已停止")
    except Exception as e:
        print(f"❌ 停止失败: {e}")

def get_my_ip():
    """获取当前出口 IP"""
    try:
        resp = requests.get("https://api.ipify.org?format=json", 
                          proxies=get_proxies(), 
                          timeout=10)
        return resp.json()["ip"]
    except Exception as e:
        return f"获取失败: {e}"

def toggle_tor():
    """切换 Tor 开关"""
    global USE_TOR
    
    print("\n" + "="*60)
    print("🧅 Tor 代理设置")
    print("="*60)
    print(f"\n当前状态: {'🟢 已启用 Tor' if USE_TOR else '🔴 直连模式'}")
    
    if check_tor_running():
        print(f"Tor 服务: 🟢 运行中 (端口 {TOR_SOCKS_PORT})")
    else:
        print(f"Tor 服务: 🔴 未运行")
    
    print(f"\n当前出口 IP: {get_my_ip()}")
    
    print("\n请选择操作:")
    print("  1. 启用 Tor 代理")
    print("  2. 关闭 Tor 代理（直连）")
    print("  3. 启动 Tor 服务")
    print("  4. 停止 Tor 服务")
    print("  5. 返回")
    
    choice = input("\n请输入选项: ").strip()
    
    if choice == "1":
        if check_tor_running():
            USE_TOR = True
            print(f"\n✅ 已启用 Tor 代理")
            print(f"   新的出口 IP: {get_my_ip()}")
        else:
            print("\n❌ Tor 未运行，请先启动 Tor 服务")
    elif choice == "2":
        USE_TOR = False
        print("✅ 已切换到直连模式")
        print(f"   当前出口 IP: {get_my_ip()}")
    elif choice == "3":
        start_tor()
        if USE_TOR:
            print(f"   当前出口 IP: {get_my_ip()}")
    elif choice == "4":
        stop_tor_service()
    elif choice == "5":
        return
    else:
        print("❌ 无效选项")

def get_eth_balance(address: str) -> dict:
    """查询 ETH 及主流代币余额"""
    balances = {}
    proxies = get_proxies()
    
    # ETH 余额
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1
    }
    resp = requests.post(ETH_RPC, json=payload, proxies=proxies, timeout=30)
    result = resp.json()
    if "result" in result:
        wei = int(result["result"], 16)
        balances["ETH"] = wei / 1e18
    
    # ERC20 代币 (USDT, USDC, DAI 等)
    tokens = {
        "USDT": ("0xdAC17F958D2ee523a2206206994597C13D831ec7", 6),
        "USDC": ("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 6),
        "DAI": ("0x6B175474E89094C44Da98b954EescdeCB5BE3830", 18),
        "WETH": ("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 18),
    }
    
    # balanceOf(address) 函数签名
    method_id = "0x70a08231"
    
    for token_name, (contract, decimals) in tokens.items():
        try:
            # 构造调用数据: balanceOf(address)
            padded_address = address[2:].lower().zfill(64)
            data = method_id + padded_address
            
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_call",
                "params": [{"to": contract, "data": data}, "latest"],
                "id": 1
            }
            resp = requests.post(ETH_RPC, json=payload, proxies=proxies, timeout=30)
            result = resp.json()
            if "result" in result and result["result"] != "0x":
                balance = int(result["result"], 16) / (10 ** decimals)
                if balance > 0:
                    balances[token_name] = balance
        except:
            pass
    
    return balances

def get_sol_balance(address: str) -> dict:
    """查询 SOL 及 SPL 代币余额"""
    balances = {}
    proxies = get_proxies()
    
    # SOL 余额
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [address]
    }
    resp = requests.post(SOL_RPC, json=payload, proxies=proxies, timeout=30)
    result = resp.json()
    if "result" in result:
        lamports = result["result"]["value"]
        balances["SOL"] = lamports / 1e9
    
    # SPL 代币余额 (USDT, USDC 等)
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            address,
            {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
            {"encoding": "jsonParsed"}
        ]
    }
    resp = requests.post(SOL_RPC, json=payload, proxies=proxies, timeout=30)
    result = resp.json()
    
    # 主流代币 Mint 地址
    known_tokens = {
        "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": "USDT",
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC",
        "So11111111111111111111111111111111111111112": "wSOL",
    }
    
    if "result" in result and result["result"]["value"]:
        for account in result["result"]["value"]:
            try:
                info = account["account"]["data"]["parsed"]["info"]
                mint = info["mint"]
                amount = float(info["tokenAmount"]["uiAmount"] or 0)
                if amount > 0:
                    token_name = known_tokens.get(mint, mint[:8] + "...")
                    balances[token_name] = amount
            except:
                pass
    
    return balances

def get_tron_balance(address: str) -> dict:
    """查询 TRON 及 TRC20 代币余额"""
    balances = {}
    proxies = get_proxies()
    
    url = f"{TRON_API}/v1/accounts/{address}"
    resp = requests.get(url, proxies=proxies, timeout=30)
    result = resp.json()
    
    if "data" in result and len(result["data"]) > 0:
        account = result["data"][0]
        # TRX 余额
        balances["TRX"] = account.get("balance", 0) / 1e6
        
        # TRC20 代币
        trc20 = account.get("trc20", [])
        known_tokens = {
            "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t": "USDT",
            "TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8": "USDC",
        }
        
        for token_data in trc20:
            for contract, amount in token_data.items():
                token_name = known_tokens.get(contract, contract[:8] + "...")
                # TRC20 USDT 是 6 位小数
                decimals = 6 if "USDT" in token_name or "USDC" in token_name else 18
                balance = int(amount) / (10 ** decimals)
                if balance > 0:
                    balances[token_name] = balance
    
    return balances


def transfer_eth(private_key: str, to_address: str, amount: float) -> str:
    """ETH 转账"""
    from eth_account import Account
    
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key
    acct = Account.from_key(private_key)
    from_address = acct.address
    
    proxies = get_proxies()
    
    # 获取 nonce
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionCount",
        "params": [from_address, "latest"],
        "id": 1
    }
    resp = requests.post(ETH_RPC, json=payload, proxies=proxies, timeout=30)
    nonce = int(resp.json()["result"], 16)
    
    # 获取 gas price
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_gasPrice",
        "params": [],
        "id": 1
    }
    resp = requests.post(ETH_RPC, json=payload, proxies=proxies, timeout=30)
    gas_price = int(resp.json()["result"], 16)
    
    # 获取 chain id
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_chainId",
        "params": [],
        "id": 1
    }
    resp = requests.post(ETH_RPC, json=payload, proxies=proxies, timeout=30)
    chain_id = int(resp.json()["result"], 16)
    
    # 构建交易
    tx = {
        "nonce": nonce,
        "gasPrice": gas_price,
        "gas": 21000,
        "to": to_address,
        "value": int(amount * 1e18),
        "chainId": chain_id,
    }
    
    # 签名
    signed_tx = acct.sign_transaction(tx)
    
    # 获取原始交易数据 (兼容不同版本)
    if hasattr(signed_tx, 'rawTransaction'):
        raw_tx = signed_tx.rawTransaction.hex()
    elif hasattr(signed_tx, 'raw_transaction'):
        raw_tx = signed_tx.raw_transaction.hex()
    else:
        raw_tx = bytes(signed_tx.raw_transaction).hex()
    
    if not raw_tx.startswith("0x"):
        raw_tx = "0x" + raw_tx
    
    # 广播
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_sendRawTransaction",
        "params": [raw_tx],
        "id": 1
    }
    resp = requests.post(ETH_RPC, json=payload, proxies=proxies, timeout=30)
    result = resp.json()
    
    if "result" in result:
        return result["result"]
    raise Exception(result.get("error", {}).get("message", "转账失败"))

def transfer_erc20(private_key: str, to_address: str, amount: float, token: str) -> str:
    """ERC20 代币转账"""
    from eth_account import Account
    
    # 代币合约地址和精度
    tokens = {
        "USDT": ("0xdAC17F958D2ee523a2206206994597C13D831ec7", 6),
        "USDC": ("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 6),
        "DAI": ("0x6B175474E89094C44Da98b954EescdeCB5BE3830", 18),
    }
    
    if token not in tokens:
        raise Exception(f"不支持的代币: {token}")
    
    contract_address, decimals = tokens[token]
    
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key
    acct = Account.from_key(private_key)
    from_address = acct.address
    
    proxies = get_proxies()
    
    # 获取 nonce
    payload = {"jsonrpc": "2.0", "method": "eth_getTransactionCount", "params": [from_address, "latest"], "id": 1}
    resp = requests.post(ETH_RPC, json=payload, proxies=proxies, timeout=30)
    nonce = int(resp.json()["result"], 16)
    
    # 获取 gas price
    payload = {"jsonrpc": "2.0", "method": "eth_gasPrice", "params": [], "id": 1}
    resp = requests.post(ETH_RPC, json=payload, proxies=proxies, timeout=30)
    gas_price = int(resp.json()["result"], 16)
    
    # 获取 chain id
    payload = {"jsonrpc": "2.0", "method": "eth_chainId", "params": [], "id": 1}
    resp = requests.post(ETH_RPC, json=payload, proxies=proxies, timeout=30)
    chain_id = int(resp.json()["result"], 16)
    
    # 构造 transfer(address,uint256) 调用数据
    # 函数签名: 0xa9059cbb
    token_amount = int(amount * (10 ** decimals))
    data = "0xa9059cbb" + to_address[2:].lower().zfill(64) + hex(token_amount)[2:].zfill(64)
    
    tx = {
        "nonce": nonce,
        "gasPrice": gas_price,
        "gas": 100000,  # ERC20 转账需要更多 gas
        "to": contract_address,
        "value": 0,
        "data": data,
        "chainId": chain_id,
    }
    
    signed_tx = acct.sign_transaction(tx)
    if hasattr(signed_tx, 'rawTransaction'):
        raw_tx = signed_tx.rawTransaction.hex()
    elif hasattr(signed_tx, 'raw_transaction'):
        raw_tx = signed_tx.raw_transaction.hex()
    else:
        raw_tx = bytes(signed_tx.raw_transaction).hex()
    
    if not raw_tx.startswith("0x"):
        raw_tx = "0x" + raw_tx
    
    payload = {"jsonrpc": "2.0", "method": "eth_sendRawTransaction", "params": [raw_tx], "id": 1}
    resp = requests.post(ETH_RPC, json=payload, proxies=proxies, timeout=30)
    result = resp.json()
    
    if "result" in result:
        return result["result"]
    raise Exception(result.get("error", {}).get("message", "转账失败"))

def transfer_sol(private_key: str, to_address: str, amount: float) -> str:
    """SOL 转账"""
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solders.system_program import transfer, TransferParams
    from solders.transaction import Transaction
    from solders.message import Message
    from solders.hash import Hash
    import base58
    
    proxies = get_proxies()
    
    private_bytes = base58.b58decode(private_key)
    keypair = Keypair.from_bytes(private_bytes)
    from_pubkey = keypair.pubkey()
    to_pubkey = Pubkey.from_string(to_address)
    
    payload = {"jsonrpc": "2.0", "id": 1, "method": "getLatestBlockhash", "params": []}
    resp = requests.post(SOL_RPC, json=payload, proxies=proxies, timeout=30)
    blockhash_str = resp.json()["result"]["value"]["blockhash"]
    blockhash = Hash.from_string(blockhash_str)
    
    lamports = int(amount * 1e9)
    ix = transfer(TransferParams(from_pubkey=from_pubkey, to_pubkey=to_pubkey, lamports=lamports))
    
    msg = Message.new_with_blockhash([ix], from_pubkey, blockhash)
    tx = Transaction.new_unsigned(msg)
    tx.sign([keypair], blockhash)
    
    tx_bytes = bytes(tx)
    tx_base64 = __import__('base64').b64encode(tx_bytes).decode('utf-8')
    
    payload = {"jsonrpc": "2.0", "id": 1, "method": "sendTransaction", "params": [tx_base64, {"encoding": "base64"}]}
    resp = requests.post(SOL_RPC, json=payload, proxies=proxies, timeout=30)
    result = resp.json()
    
    if "result" in result:
        return result["result"]
    raise Exception(result.get("error", {}).get("message", "转账失败"))

def transfer_spl_token(private_key: str, to_address: str, amount: float, token: str) -> str:
    """SPL 代币转账（自动创建接收方 ATA）"""
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solders.transaction import Transaction
    from solders.message import Message
    from solders.hash import Hash
    from solders.instruction import Instruction, AccountMeta
    from solders.system_program import ID as SYS_PROGRAM_ID
    import base58
    import struct
    
    # 代币 Mint 地址和精度
    tokens = {
        "USDT": ("Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB", 6),
        "USDC": ("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", 6),
    }
    
    if token not in tokens:
        raise Exception(f"不支持的代币: {token}")
    
    mint_address, decimals = tokens[token]
    
    proxies = get_proxies()
    
    private_bytes = base58.b58decode(private_key)
    keypair = Keypair.from_bytes(private_bytes)
    from_pubkey = keypair.pubkey()
    to_pubkey = Pubkey.from_string(to_address)
    mint_pubkey = Pubkey.from_string(mint_address)
    
    # Program IDs
    token_program = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
    ata_program = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
    
    # 获取发送方的 Token Account
    payload = {
        "jsonrpc": "2.0", "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [str(from_pubkey), {"mint": mint_address}, {"encoding": "jsonParsed"}]
    }
    resp = requests.post(SOL_RPC, json=payload, proxies=proxies, timeout=30)
    result = resp.json()
    
    if not result.get("result", {}).get("value"):
        raise Exception("发送方没有该代币账户")
    
    from_token_account = Pubkey.from_string(result["result"]["value"][0]["pubkey"])
    
    # 计算接收方的 ATA 地址
    # ATA = PDA([owner, token_program, mint], ata_program)
    seeds = [bytes(to_pubkey), bytes(token_program), bytes(mint_pubkey)]
    to_ata, _ = Pubkey.find_program_address(seeds, ata_program)
    
    # 检查接收方 ATA 是否存在
    payload = {"jsonrpc": "2.0", "id": 1, "method": "getAccountInfo", "params": [str(to_ata), {"encoding": "base64"}]}
    resp = requests.post(SOL_RPC, json=payload, proxies=proxies, timeout=30)
    result = resp.json()
    
    ata_exists = result.get("result", {}).get("value") is not None
    
    # 获取 blockhash
    payload = {"jsonrpc": "2.0", "id": 1, "method": "getLatestBlockhash", "params": []}
    resp = requests.post(SOL_RPC, json=payload, proxies=proxies, timeout=30)
    blockhash_str = resp.json()["result"]["value"]["blockhash"]
    blockhash = Hash.from_string(blockhash_str)
    
    instructions = []
    
    # 如果 ATA 不存在，先创建
    if not ata_exists:
        print("   📝 接收方没有代币账户，正在创建...")
        # CreateAssociatedTokenAccount 指令
        create_ata_ix = Instruction(
            program_id=ata_program,
            accounts=[
                AccountMeta(pubkey=from_pubkey, is_signer=True, is_writable=True),  # payer
                AccountMeta(pubkey=to_ata, is_signer=False, is_writable=True),  # ata
                AccountMeta(pubkey=to_pubkey, is_signer=False, is_writable=False),  # owner
                AccountMeta(pubkey=mint_pubkey, is_signer=False, is_writable=False),  # mint
                AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),  # system program
                AccountMeta(pubkey=token_program, is_signer=False, is_writable=False),  # token program
            ],
            data=bytes()  # CreateAssociatedTokenAccount 不需要数据
        )
        instructions.append(create_ata_ix)
    
    # 构造 transfer 指令
    token_amount = int(amount * (10 ** decimals))
    # SPL Token transfer 指令: instruction type (1 byte) + amount (8 bytes LE)
    transfer_data = bytes([3]) + struct.pack('<Q', token_amount)
    
    transfer_ix = Instruction(
        program_id=token_program,
        accounts=[
            AccountMeta(pubkey=from_token_account, is_signer=False, is_writable=True),
            AccountMeta(pubkey=to_ata, is_signer=False, is_writable=True),
            AccountMeta(pubkey=from_pubkey, is_signer=True, is_writable=False),
        ],
        data=transfer_data
    )
    instructions.append(transfer_ix)
    
    # 构建交易
    msg = Message.new_with_blockhash(instructions, from_pubkey, blockhash)
    tx = Transaction.new_unsigned(msg)
    tx.sign([keypair], blockhash)
    
    tx_bytes = bytes(tx)
    tx_base64 = __import__('base64').b64encode(tx_bytes).decode('utf-8')
    
    payload = {"jsonrpc": "2.0", "id": 1, "method": "sendTransaction", "params": [tx_base64, {"encoding": "base64"}]}
    resp = requests.post(SOL_RPC, json=payload, proxies=proxies, timeout=30)
    result = resp.json()
    
    if "result" in result:
        return result["result"]
    raise Exception(result.get("error", {}).get("message", "转账失败"))


def transfer_tron(private_key: str, to_address: str, amount: float) -> str:
    """TRON TRX 转账"""
    from ecdsa import SigningKey, SECP256k1
    import hashlib
    import base58
    
    proxies = get_proxies()
    
    private_bytes = bytes.fromhex(private_key)
    sk = SigningKey.from_string(private_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()
    public_key = vk.to_string()
    
    from Crypto.Hash import keccak
    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(public_key)
    address_bytes = keccak_hash.digest()[-20:]
    from_address_bytes = b'\x41' + address_bytes
    
    sha256_1 = hashlib.sha256(from_address_bytes).digest()
    sha256_2 = hashlib.sha256(sha256_1).digest()
    checksum = sha256_2[:4]
    from_address = base58.b58encode(from_address_bytes + checksum).decode('utf-8')
    
    to_address_decoded = base58.b58decode(to_address)
    to_address_hex = to_address_decoded[:-4].hex()
    
    sun_amount = int(amount * 1e6)
    url = f"{TRON_API}/wallet/createtransaction"
    payload = {
        "owner_address": from_address_bytes.hex(),
        "to_address": to_address_hex,
        "amount": sun_amount
    }
    resp = requests.post(url, json=payload, proxies=proxies, timeout=30)
    tx = resp.json()
    
    if "Error" in tx:
        raise Exception(tx["Error"])
    
    tx_id = bytes.fromhex(tx["txID"])
    signature = sk.sign_digest(tx_id, sigencode=lambda r, s, order: r.to_bytes(32, 'big') + s.to_bytes(32, 'big'))
    tx["signature"] = [signature.hex()]
    
    url = f"{TRON_API}/wallet/broadcasttransaction"
    resp = requests.post(url, json=tx, proxies=proxies, timeout=30)
    result = resp.json()
    
    if result.get("result"):
        return tx["txID"]
    raise Exception(result.get("message", "转账失败"))

def transfer_trc20(private_key: str, to_address: str, amount: float, token: str) -> str:
    """TRC20 代币转账"""
    from ecdsa import SigningKey, SECP256k1
    import hashlib
    import base58
    
    # 代币合约地址和精度
    tokens = {
        "USDT": ("TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t", 6),
        "USDC": ("TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8", 6),
    }
    
    if token not in tokens:
        raise Exception(f"不支持的代币: {token}")
    
    contract_address, decimals = tokens[token]
    
    proxies = get_proxies()
    
    private_bytes = bytes.fromhex(private_key)
    sk = SigningKey.from_string(private_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()
    public_key = vk.to_string()
    
    from Crypto.Hash import keccak
    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(public_key)
    address_bytes = keccak_hash.digest()[-20:]
    from_address_bytes = b'\x41' + address_bytes
    
    sha256_1 = hashlib.sha256(from_address_bytes).digest()
    sha256_2 = hashlib.sha256(sha256_1).digest()
    checksum = sha256_2[:4]
    from_address = base58.b58encode(from_address_bytes + checksum).decode('utf-8')
    
    # 解码目标地址
    to_address_decoded = base58.b58decode(to_address)
    to_address_hex = to_address_decoded[:-4].hex()
    
    # 解码合约地址
    contract_decoded = base58.b58decode(contract_address)
    contract_hex = contract_decoded[:-4].hex()
    
    # 构造 transfer(address,uint256) 参数
    token_amount = int(amount * (10 ** decimals))
    # 参数: to_address (32 bytes) + amount (32 bytes)
    parameter = to_address_hex[2:].zfill(64) + hex(token_amount)[2:].zfill(64)
    
    url = f"{TRON_API}/wallet/triggersmartcontract"
    payload = {
        "owner_address": from_address_bytes.hex(),
        "contract_address": contract_hex,
        "function_selector": "transfer(address,uint256)",
        "parameter": parameter,
        "fee_limit": 100000000,  # 100 TRX
        "call_value": 0
    }
    resp = requests.post(url, json=payload, proxies=proxies, timeout=30)
    result = resp.json()
    
    if "Error" in str(result):
        raise Exception(result.get("Error", str(result)))
    
    tx = result.get("transaction")
    if not tx:
        raise Exception("创建交易失败")
    
    # 签名
    tx_id = bytes.fromhex(tx["txID"])
    signature = sk.sign_digest(tx_id, sigencode=lambda r, s, order: r.to_bytes(32, 'big') + s.to_bytes(32, 'big'))
    tx["signature"] = [signature.hex()]
    
    # 广播
    url = f"{TRON_API}/wallet/broadcasttransaction"
    resp = requests.post(url, json=tx, proxies=proxies, timeout=30)
    result = resp.json()
    
    if result.get("result"):
        return tx["txID"]
    raise Exception(result.get("message", "转账失败"))


def query_balance():
    """余额查询"""
    print("\n" + "="*60)
    print("💰 余额查询")
    print("="*60)
    
    print("\n请选择网络:")
    print("  1. ETH (以太坊)")
    print("  2. SOL (Solana)")
    print("  3. TRON (波场)")
    
    while True:
        choice = input("\n请输入选项 (1/2/3): ").strip()
        if choice in ["1", "2", "3"]:
            break
        print("❌ 无效选项")
    
    address = input("\n请输入地址: ").strip()
    
    try:
        print("\n⏳ 正在查询...")
        if choice == "1":
            balances = get_eth_balance(address)
            print(f"\n✅ ETH 链余额:")
        elif choice == "2":
            balances = get_sol_balance(address)
            print(f"\n✅ SOL 链余额:")
        else:
            balances = get_tron_balance(address)
            print(f"\n✅ TRON 链余额:")
        
        if balances:
            for token, amount in balances.items():
                print(f"   {token}: {amount:.6f}")
        else:
            print("   (无余额)")
            
    except Exception as e:
        print(f"\n❌ 查询失败: {e}")


def get_address_from_private_key(chain: str, private_key: str) -> str:
    """从私钥获取地址"""
    if chain == "ETH":
        from eth_account import Account
        if not private_key.startswith("0x"):
            private_key = "0x" + private_key
        return Account.from_key(private_key).address
    elif chain == "SOL":
        from solders.keypair import Keypair
        import base58
        private_bytes = base58.b58decode(private_key)
        keypair = Keypair.from_bytes(private_bytes)
        return str(keypair.pubkey())
    else:  # TRON
        from ecdsa import SigningKey, SECP256k1
        from Crypto.Hash import keccak
        import hashlib
        import base58
        private_bytes = bytes.fromhex(private_key)
        sk = SigningKey.from_string(private_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()
        keccak_hash = keccak.new(digest_bits=256)
        keccak_hash.update(vk.to_string())
        address_bytes = b'\x41' + keccak_hash.digest()[-20:]
        sha256_1 = hashlib.sha256(address_bytes).digest()
        sha256_2 = hashlib.sha256(sha256_1).digest()
        return base58.b58encode(address_bytes + sha256_2[:4]).decode('utf-8')

def do_transfer():
    """执行转账"""
    print("\n" + "="*60)
    print("💸 转账")
    print("="*60)
    
    print("\n请选择网络:")
    print("  1. ETH (以太坊)")
    print("  2. SOL (Solana)")
    print("  3. TRON (波场)")
    
    while True:
        choice = input("\n请输入选项 (1/2/3): ").strip()
        if choice in ["1", "2", "3"]:
            break
        print("❌ 无效选项")
    
    chain = {"1": "ETH", "2": "SOL", "3": "TRON"}[choice]
    
    private_key = input("\n请输入私钥: ").strip()
    
    # 获取地址并查询余额
    try:
        from_address = get_address_from_private_key(chain, private_key)
        print(f"\n📍 发送地址: {from_address}")
        print("⏳ 正在查询余额...")
        
        if chain == "ETH":
            balances = get_eth_balance(from_address)
        elif chain == "SOL":
            balances = get_sol_balance(from_address)
        else:
            balances = get_tron_balance(from_address)
        
        if not balances:
            print("❌ 该地址没有任何余额")
            return
        
        print("\n💰 可用余额:")
        token_list = list(balances.keys())
        for i, (token, amount) in enumerate(balances.items(), 1):
            print(f"   {i}. {token}: {amount:.6f}")
        
    except Exception as e:
        print(f"❌ 获取余额失败: {e}")
        return
    
    # 选择要转账的币种
    print("\n请选择要转账的币种:")
    while True:
        token_choice = input(f"请输入选项 (1-{len(token_list)}): ").strip()
        try:
            token_idx = int(token_choice) - 1
            if 0 <= token_idx < len(token_list):
                selected_token = token_list[token_idx]
                break
        except:
            pass
        print("❌ 无效选项")
    
    available = balances[selected_token]
    print(f"\n已选择: {selected_token}, 可用: {available:.6f}")
    
    to_address = input("请输入目标地址: ").strip()
    amount = float(input(f"请输入转账金额 (最大 {available:.6f}): ").strip())
    
    if amount > available:
        print("❌ 余额不足")
        return
    
    # 确认
    print(f"\n⚠️  确认转账:")
    print(f"   网络: {chain}")
    print(f"   币种: {selected_token}")
    print(f"   从: {from_address}")
    print(f"   到: {to_address}")
    print(f"   金额: {amount} {selected_token}")
    
    confirm = input("\n确认转账? (输入 YES 确认): ").strip()
    if confirm != "YES":
        print("❌ 已取消")
        return
    
    try:
        print("\n⏳ 正在发送交易...")
        
        if chain == "ETH":
            if selected_token == "ETH":
                tx_hash = transfer_eth(private_key, to_address, amount)
            else:
                tx_hash = transfer_erc20(private_key, to_address, amount, selected_token)
            print(f"\n✅ 转账成功!")
            print(f"   交易哈希: {tx_hash}")
            print(f"   查看: https://etherscan.io/tx/{tx_hash}")
            
        elif chain == "SOL":
            if selected_token == "SOL":
                tx_hash = transfer_sol(private_key, to_address, amount)
            else:
                tx_hash = transfer_spl_token(private_key, to_address, amount, selected_token)
            print(f"\n✅ 转账成功!")
            print(f"   交易哈希: {tx_hash}")
            print(f"   查看: https://solscan.io/tx/{tx_hash}")
            
        else:  # TRON
            if selected_token == "TRX":
                tx_hash = transfer_tron(private_key, to_address, amount)
            else:
                tx_hash = transfer_trc20(private_key, to_address, amount, selected_token)
            print(f"\n✅ 转账成功!")
            print(f"   交易哈希: {tx_hash}")
            print(f"   查看: https://tronscan.org/#/transaction/{tx_hash}")
            
    except Exception as e:
        print(f"\n❌ 转账失败: {e}")


def main():
    print("\n" + "="*60)
    print("🔐 多链钱包工具")
    print("   支持 ETH / SOL / TRON")
    print("   纯代码操作，不依赖任何钱包App")
    print("   支持 Tor 代理隐私保护")
    print("="*60)
    
    # 显示当前网络状态
    tor_status = "🟢 已启用" if USE_TOR else "🔴 未启用"
    print(f"\n🧅 Tor 代理: {tor_status}")
    
    while True:
        print("\n请选择功能:")
        print("  1. 余额查询")
        print("  2. 转账")
        print("  3. Tor 代理设置")
        print("  4. 退出")
        
        choice = input("\n请输入选项 (1/2/3/4): ").strip()
        
        if choice == "1":
            query_balance()
        elif choice == "2":
            do_transfer()
        elif choice == "3":
            toggle_tor()
        elif choice == "4":
            print("\n👋 再见!")
            break
        else:
            print("❌ 无效选项")


if __name__ == "__main__":
    main()
