# 多链钱包工具集

纯 Python 实现的多链加密货币工具，支持 ETH / SOL / TRON。

## 功能

### 7.py - 靓号生成器
- 生成指定前缀/后缀的钱包地址
- 支持 ETH、SOL、TRON 三条链
- 支持极速模式（纯私钥）和助记词模式（BIP-44 标准）
- 多进程并行计算

### 8.py - 助记词地址扫描器
- 输入助记词，扫描所有常见派生路径
- 显示对应的地址和私钥
- 支持 ETH、SOL、TRON

### 9.py - 钱包工具（余额查询 & 转账）
- 余额查询：主币 + 主流代币（USDT、USDC 等）
- 转账：支持主币和代币转账
- 支持 Tor 代理隐私保护
- 纯代码操作，不依赖任何钱包 App

## 安装依赖

```bash
pip install eth-account mnemonic ecdsa pycryptodome pynacl base58 solders requests pysocks
```

## 使用方法

```bash
# 靓号生成
python 7.py

# 助记词扫描
python 8.py

# 钱包工具
python 9.py
```

## 安全提示

- 使用 `secrets` 模块生成密码学安全随机数
- 助记词模式符合 BIP-39/BIP-44 标准
- 建议在离线环境运行
- 私钥和助记词请妥善保管

## 派生路径

| 链 | 派生路径 | 兼容钱包 |
|---|---|---|
| ETH | m/44'/60'/0'/0/0 | MetaMask, Trust Wallet |
| SOL | m/44'/501'/0' | Trust Wallet, Solflare |
| SOL | m/44'/501'/0'/0' | Phantom |
| TRON | m/44'/195'/0'/0/0 | TronLink, Trust Wallet |
