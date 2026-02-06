"""
Generate project images: Logo, Cover, Screenshots
Project name: M
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Color scheme
BG_DARK = (15, 23, 42)
BG_GRADIENT = (30, 41, 59)
ACCENT_BLUE = (59, 130, 246)
ACCENT_PURPLE = (139, 92, 246)
ACCENT_GREEN = (34, 197, 94)
WHITE = (255, 255, 255)
GRAY = (148, 163, 184)

def create_logo(size=512):
    """Create Logo"""
    img = Image.new('RGB', (size, size), BG_DARK)
    draw = ImageDraw.Draw(img)
    
    # Gradient background
    center = size // 2
    for r in range(size // 2, 0, -2):
        ratio = r / (size // 2)
        color = tuple(int(BG_DARK[i] + (ACCENT_BLUE[i] - BG_DARK[i]) * (1 - ratio) * 0.3) for i in range(3))
        draw.ellipse([center - r, center - r, center + r, center + r], fill=color)
    
    # Three chain rings
    ring_size = size // 6
    ring_width = size // 20
    
    # ETH ring (blue)
    x1, y1 = center - ring_size, center - ring_size // 2
    draw.ellipse([x1 - ring_size, y1 - ring_size, x1 + ring_size, y1 + ring_size], outline=ACCENT_BLUE, width=ring_width)
    
    # SOL ring (purple)
    x2, y2 = center + ring_size // 2, center - ring_size // 2
    draw.ellipse([x2 - ring_size, y2 - ring_size, x2 + ring_size, y2 + ring_size], outline=ACCENT_PURPLE, width=ring_width)
    
    # TRON ring (green)
    x3, y3 = center, center + ring_size
    draw.ellipse([x3 - ring_size, y3 - ring_size, x3 + ring_size, y3 + ring_size], outline=ACCENT_GREEN, width=ring_width)
    
    # Center lock icon
    lock_size = size // 8
    lock_x, lock_y = center, center
    draw.rounded_rectangle(
        [lock_x - lock_size//2, lock_y - lock_size//4, lock_x + lock_size//2, lock_y + lock_size//2],
        radius=size//40, fill=WHITE
    )
    draw.arc(
        [lock_x - lock_size//3, lock_y - lock_size//2 - lock_size//4, lock_x + lock_size//3, lock_y],
        start=180, end=0, fill=WHITE, width=ring_width//2
    )
    
    # Text "M"
    try:
        font = ImageFont.truetype("arial.ttf", size // 5)
    except:
        font = ImageFont.load_default()
    
    text = "M"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    draw.text((center - text_width // 2, size - size // 4), text, fill=WHITE, font=font)
    
    img.save('logo.png')
    print("Done: logo.png")

def create_cover(width=1280, height=720):
    """Create Cover image"""
    img = Image.new('RGB', (width, height), BG_DARK)
    draw = ImageDraw.Draw(img)
    
    # Gradient background
    for y in range(height):
        ratio = y / height
        color = tuple(int(BG_DARK[i] + (BG_GRADIENT[i] - BG_DARK[i]) * ratio) for i in range(3))
        draw.line([(0, y), (width, y)], fill=color)
    
    # Decorative lines
    for i in range(5):
        y = height // 6 + i * height // 8
        alpha = 0.1 + i * 0.05
        color = tuple(int(ACCENT_BLUE[j] * alpha) for j in range(3))
        draw.line([(0, y), (width, y + 50)], fill=color, width=2)
    
    # Three chain icons
    icons = [
        ("ETH", ACCENT_BLUE, width // 4),
        ("SOL", ACCENT_PURPLE, width // 2),
        ("TRON", ACCENT_GREEN, 3 * width // 4),
    ]
    
    icon_y = height // 3
    icon_size = 60
    
    try:
        font_small = ImageFont.truetype("arial.ttf", 24)
    except:
        font_small = ImageFont.load_default()
    
    for name, color, x in icons:
        draw.ellipse([x - icon_size, icon_y - icon_size, x + icon_size, icon_y + icon_size], 
                    outline=color, width=4)
        bbox = draw.textbbox((0, 0), name, font=font_small)
        tw = bbox[2] - bbox[0]
        draw.text((x - tw // 2, icon_y - 12), name, fill=color, font=font_small)
    
    # Connection lines
    draw.line([(width // 4 + icon_size, icon_y), (width // 2 - icon_size, icon_y)], fill=GRAY, width=2)
    draw.line([(width // 2 + icon_size, icon_y), (3 * width // 4 - icon_size, icon_y)], fill=GRAY, width=2)
    
    # Main title
    try:
        font_large = ImageFont.truetype("arial.ttf", 120)
        font_medium = ImageFont.truetype("arial.ttf", 32)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
    
    title = "M"
    bbox = draw.textbbox((0, 0), title, font=font_large)
    tw = bbox[2] - bbox[0]
    draw.text((width // 2 - tw // 2, height // 2), title, fill=WHITE, font=font_large)
    
    subtitle = "Multi-Chain Wallet Toolkit"
    bbox = draw.textbbox((0, 0), subtitle, font=font_medium)
    tw = bbox[2] - bbox[0]
    draw.text((width // 2 - tw // 2, height // 2 + 130), subtitle, fill=GRAY, font=font_medium)
    
    # Feature tags
    features = ["Vanity Generator", "Mnemonic Scanner", "Token Transfer", "Tor Privacy"]
    tag_y = height - 100
    tag_width = 180
    start_x = (width - len(features) * tag_width) // 2
    
    try:
        font_tag = ImageFont.truetype("arial.ttf", 18)
    except:
        font_tag = ImageFont.load_default()
    
    for i, feat in enumerate(features):
        x = start_x + i * tag_width + tag_width // 2
        draw.rounded_rectangle(
            [x - 80, tag_y - 15, x + 80, tag_y + 15],
            radius=15, outline=ACCENT_BLUE, width=2
        )
        bbox = draw.textbbox((0, 0), feat, font=font_tag)
        tw = bbox[2] - bbox[0]
        draw.text((x - tw // 2, tag_y - 10), feat, fill=WHITE, font=font_tag)
    
    img.save('cover.png')
    print("Done: cover.png")

def create_screenshot_terminal(filename, title, content_lines, width=800, height=500):
    """Create terminal-style screenshot"""
    img = Image.new('RGB', (width, height), (30, 30, 30))
    draw = ImageDraw.Draw(img)
    
    # Terminal title bar
    draw.rectangle([0, 0, width, 35], fill=(50, 50, 50))
    
    # Window buttons
    draw.ellipse([12, 12, 24, 24], fill=(255, 95, 86))
    draw.ellipse([32, 12, 44, 24], fill=(255, 189, 46))
    draw.ellipse([52, 12, 64, 24], fill=(39, 201, 63))
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 14)
        font_mono = ImageFont.truetype("consola.ttf", 14)
    except:
        font_title = ImageFont.load_default()
        font_mono = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text((width // 2 - tw // 2, 10), title, fill=(200, 200, 200), font=font_title)
    
    # Content
    y = 50
    for line in content_lines:
        if line.startswith("[OK]") or line.startswith("[FOUND]"):
            color = ACCENT_GREEN
        elif line.startswith("[ERR]"):
            color = (255, 100, 100)
        elif line.startswith("[>]") or line.startswith("[*]"):
            color = ACCENT_BLUE
        elif line.startswith("   "):
            color = GRAY
        else:
            color = WHITE
        draw.text((20, y), line, fill=color, font=font_mono)
        y += 22
    
    img.save(filename)
    print(f"Done: {filename}")

# Generate all images
if __name__ == "__main__":
    create_logo(512)
    create_cover(1280, 720)
    
    # Screenshot 1: Vanity Generator
    create_screenshot_terminal('screenshot1.png', 'M - Vanity Address Generator', [
        "[*] Multi-Chain Vanity Generator v2",
        "    BIP-39/BIP-44 compliant",
        "    Mnemonic recoverable in standard wallets",
        "",
        "Select chain:",
        "  1. ETH (Ethereum)  - m/44'/60'/0'/0/0",
        "  2. SOL (Solana)    - m/44'/501'/0'/0'",
        "  3. TRON            - m/44'/195'/0'/0/0",
        "",
        "[>] Target: prefix[0xB14F] | suffix[A66A]",
        "[>] Mode: Mnemonic (BIP-44)",
        "",
        "[*] Attempts: 125,000 | Speed: 28,500/s",
        "",
        "[FOUND] ETH vanity address!",
        "   Address: 0xB14F...A66A",
        "[OK] Mnemonic recoverable in MetaMask",
    ])
    
    # Screenshot 2: Wallet Tool
    create_screenshot_terminal('screenshot2.png', 'M - Wallet Tool', [
        "[*] Multi-Chain Wallet Tool",
        "    Supports ETH / SOL / TRON",
        "    Tor Proxy: ENABLED",
        "",
        "[>] Balance Query",
        "",
        "[*] Address: HKip1B8Y...ovq5d7je",
        "",
        "[OK] SOL chain balance:",
        "   SOL: 0.042495",
        "   USDT: 2.028876",
        "",
        "[>] Transfer",
        "   Token: USDT",
        "   Amount: 1.0 USDT",
        "",
        "[OK] Transfer successful!",
        "   View: https://solscan.io/tx/...",
    ])
    
    # Screenshot 3: Mnemonic Scanner
    create_screenshot_terminal('screenshot3.png', 'M - Mnemonic Scanner', [
        "[*] Mnemonic Address Scanner",
        "",
        "[OK] Mnemonic valid, scanning...",
        "",
        "[*] SOL (Solana) scan results:",
        "",
        "[>] Trust Wallet / Solflare default",
        "   Path: m/44'/501'/0'",
        "   Address: Gnnozr...YJoi",
        "",
        "[>] Phantom / Sollet default",
        "   Path: m/44'/501'/0'/0'",
        "   Address: YZsSDv...Lnw",
        "",
        "[OK] Scan complete!",
        "[*] Keep your private keys safe!",
    ])
    
    print("\nAll images generated!")
