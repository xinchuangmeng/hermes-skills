#!/usr/bin/env python3
"""生成新手开店第1期6张知识卡片图片（竖屏9:16）"""

from PIL import Image, ImageDraw, ImageFont
import os

# 尺寸：竖屏1080x1920 (9:16)
W, H = 1080, 1920
BG_COLOR = "#0a0a0a"  # 近黑色

# 字体路径
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REGULAR = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_LIGHT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Light.ttc"
FONT_SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

OUTPUT_DIR = "/home/agentuser/sea-ecommerce/series/系列一_新手开店从0到1/cards"


def create_card(filename, draw_func):
    """创建一张卡片"""
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_func(draw, img)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    img.save(path, "PNG")
    print(f"✅ 已生成: {path}")


# ============ 卡片1：封面 ============
def card1(draw, img):
    # 底部小字
    font_small = ImageFont.truetype(FONT_LIGHT, 36)
    draw.text((540, 1680), "下划进入正片 →", fill="#666666", anchor="mm", font=font_small)
    
    # 主标题
    font_title = ImageFont.truetype(FONT_BOLD, 110)
    draw.text((540, 740), "做跨境前", fill="#FFFFFF", anchor="mm", font=font_title)
    draw.text((540, 880), "先搞清楚这3个问题", fill="#FFFFFF", anchor="mm", font=font_title)
    
    # 三个问号
    font_q = ImageFont.truetype(FONT_BOLD, 70)
    draw.text((540, 1100), "???  ???  ???", fill="#555555", anchor="mm", font=font_q)
    
    # 顶部分隔线
    draw.line([(200, 400), (880, 400)], fill="#333333", width=2)
    draw.line([(200, 1350), (880, 1350)], fill="#333333", width=2)


# ============ 卡片2：痛点引入 ============
def card2(draw, img):
    font_big = ImageFont.truetype(FONT_BOLD, 90)
    font_mid = ImageFont.truetype(FONT_REGULAR, 55)
    font_small = ImageFont.truetype(FONT_LIGHT, 40)
    
    # 主标题
    draw.text((540, 600), "90%新手都这样：", fill="#FFFFFF", anchor="mm", font=font_big)
    
    # 箭头流程
    steps = ["看别人赚钱", "→", "注册开店", "→", "亏钱收场"]
    colors = ["#FFFFFF", "#FF4444", "#FFFFFF", "#FF4444", "#FF4444"]
    fonts = [font_mid, font_big, font_mid, font_big, font_mid]
    x_start = 160
    for i, (step, color, f) in enumerate(zip(steps, colors, fonts)):
        draw.text((x_start, 900), step, fill=color, anchor="mm", font=f)
        x_start += 200 if step in ["→"] else 280
    
    # 底部提问
    draw.text((540, 1300), "你呢？", fill="#FFFFFF", anchor="mm", font=font_big)
    draw.text((540, 1450), "准备走老路还是新路？", fill="#AAAAAA", anchor="mm", font=font_mid)


# ============ 卡片3：预算 ============
def card3(draw, img):
    font_num = ImageFont.truetype(FONT_BOLD, 120)
    font_title = ImageFont.truetype(FONT_BOLD, 80)
    font_item = ImageFont.truetype(FONT_REGULAR, 55)
    font_price = ImageFont.truetype(FONT_BOLD, 55)
    
    # 编号
    draw.text((120, 350), "①", fill="#FFD700", anchor="mm", font=font_num)
    draw.text((540, 480), "你准备花多少钱？", fill="#FFFFFF", anchor="mm", font=font_title)
    
    # 列表
    items = [
        ("营业执照", "¥0", "#4CAF50"),
        ("首批货款", "¥1000-3000", "#FFFFFF"),
        ("物流运费", "¥500", "#FFFFFF"),
        ("广告费用", "¥0-500", "#FFFFFF"),
    ]
    y_start = 700
    for name, price, color in items:
        draw.text((300, y_start), name, fill="#CCCCCC", anchor="lm", font=font_item)
        draw.text((780, y_start), price, fill=color, anchor="rm", font=font_price)
        draw.line([(300, y_start+40), (780, y_start+40)], fill="#333333", width=1)
        y_start += 120
    
    # 底部高亮
    draw.text((540, 1400), "前两个月至少 ¥3000 打底", fill="#FFD700", anchor="mm", 
              font=ImageFont.truetype(FONT_BOLD, 60))
    
    # 💰 图标（用文字代替）
    draw.text((540, 340), "💰", fill="#FFD700", anchor="mm", 
              font=ImageFont.truetype(FONT_REGULAR, 80))


# ============ 卡片4：平台 ============
def card4(draw, img):
    font_num = ImageFont.truetype(FONT_BOLD, 120)
    font_title = ImageFont.truetype(FONT_BOLD, 80)
    font_item = ImageFont.truetype(FONT_REGULAR, 52)
    font_highlight = ImageFont.truetype(FONT_BOLD, 60)
    
    draw.text((120, 300), "②", fill="#4CAF50", anchor="mm", font=font_num)
    draw.text((540, 420), "你选哪个平台？", fill="#FFFFFF", anchor="mm", font=font_title)
    
    # 推荐
    draw.text((540, 600), "新手推荐 →", fill="#CCCCCC", anchor="mm", 
              font=ImageFont.truetype(FONT_REGULAR, 50))
    draw.text((540, 700), "Shopee 马来站", fill="#4CAF50", anchor="mm", font=font_highlight)
    
    # 勾选项
    checks = [
        ("✅", "新执照也能开"),
        ("✅", "英文运营，不用学小语种"),
        ("✅", "新店有流量扶持"),
    ]
    y_start = 900
    for icon, text in checks:
        draw.text((250, y_start), f"{icon}  {text}", fill="#FFFFFF", anchor="lm", font=font_item)
        y_start += 110
    
    # 不推荐
    draw.line([(300, 1380), (780, 1380)], fill="#333333", width=1)
    draw.text((540, 1480), "❌  先别碰亚马逊", fill="#FF6666", anchor="mm", font=font_highlight)


# ============ 卡片5：时间 ============
def card5(draw, img):
    font_num = ImageFont.truetype(FONT_BOLD, 120)
    font_title = ImageFont.truetype(FONT_BOLD, 80)
    font_item = ImageFont.truetype(FONT_REGULAR, 55)
    font_warn = ImageFont.truetype(FONT_BOLD, 60)
    
    draw.text((120, 300), "③", fill="#FF6B6B", anchor="mm", font=font_num)
    draw.text((540, 420), "每天能挤出1小时吗？", fill="#FFFFFF", anchor="mm", font=font_title)
    
    draw.text((540, 650), "前30天是黄金期", fill="#FFD700", anchor="mm", 
              font=ImageFont.truetype(FONT_BOLD, 65))
    
    draw.text((540, 780), "每天1-2小时做：", fill="#CCCCCC", anchor="mm", font=font_item)
    
    tasks = ["· 选品", "· 上架", "· 看数据"]
    y_start = 920
    for t in tasks:
        draw.text((540, y_start), t, fill="#FFFFFF", anchor="mm", font=font_item)
        y_start += 100
    
    # ⏰ 图标
    draw.text((540, 350), "⏰", fill="#FFD700", anchor="mm",
              font=ImageFont.truetype(FONT_REGULAR, 80))
    
    # 警告
    draw.line([(300, 1400), (780, 1400)], fill="#FF4444", width=2)
    draw.text((540, 1520), "挤不出时间？先别开店", fill="#FF4444", anchor="mm", font=font_warn)


# ============ 卡片6：结尾 ============
def card6(draw, img):
    font_big = ImageFont.truetype(FONT_BOLD, 70)
    font_mid = ImageFont.truetype(FONT_REGULAR, 50)
    font_brand = ImageFont.truetype(FONT_BOLD, 45)
    font_small = ImageFont.truetype(FONT_LIGHT, 35)
    
    draw.text((540, 650), "这3个问题想清楚", fill="#FFFFFF", anchor="mm", font=font_big)
    draw.text((540, 780), "再往下走", fill="#FFFFFF", anchor="mm", font=font_big)
    
    # 分割线
    draw.line([(300, 950), (780, 950)], fill="#333333", width=2)
    
    # 预告
    draw.text((540, 1080), "👇 下期预告", fill="#888888", anchor="mm", font=font_mid)
    draw.text((540, 1200), "开店注册，一步都不能错", fill="#FFD700", anchor="mm", font=font_big)
    
    # 品牌
    draw.text((540, 1550), "关注我，下期见", fill="#AAAAAA", anchor="mm", font=font_mid)
    draw.text((540, 1700), "我和AI做跨境电商", fill="#666666", anchor="mm", font=font_brand)
    
    # 底部装饰线
    draw.line([(200, 1780), (880, 1780)], fill="#333333", width=1)


# ============ 生成全部 ============
if __name__ == "__main__":
    cards = [
        ("card1_cover.png", card1),
        ("card2_pain.png", card2),
        ("card3_budget.png", card3),
        ("card4_platform.png", card4),
        ("card5_time.png", card5),
        ("card6_end.png", card6),
    ]
    for filename, func in cards:
        create_card(filename, func)
    print(f"\n🎉 全部生成完毕！共 {len(cards)} 张卡片")
    print(f"📂 目录: {OUTPUT_DIR}")
