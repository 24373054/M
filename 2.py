from eth_account import Account

# 1. 把你刚才试图导入 MetaMask 的那个私钥粘贴在下面引号里
suspicious_key = "0xe0318a57f230ac38935100a080ff5ef393e61a1b904922f0c54182226d6ee859"

# 2. 看看这个私钥到底是谁
real_address = Account.from_key(suspicious_key).address

print(f"真相时刻：")
print(f"这个私钥对应的真实地址是: {real_address}")

if real_address.upper().endswith("A66A"):
    print("结论：MetaMask 显示错了（极小概率事件，可能是缓存）")
else:
    print("结论：你复制错私钥了！这不是那个 A66A 的私钥。")