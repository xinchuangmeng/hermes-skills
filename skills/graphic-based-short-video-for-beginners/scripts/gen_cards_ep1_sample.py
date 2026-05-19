#!/usr/bin/env python3
"""
新手开店第1期 知识卡片生成脚本（竖屏9:16，1080x1920）
可复用模板：复制为gen_cards_v2.py，改card1~card6函数里的文案和配色即可

V2纯图文模式（无口播，纯文字+BGM）
"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1080, 1920
BG = "#0a0a0a"

# 字体路径 — 不同系统需调整
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REGULAR = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_LIGHT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Light.ttc"
FONT_SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

OUTPUT_DIR = "./cards"  # 改成输出路径


def create_card(filename, draw_func):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_func(draw, img)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    img.save(path, "PNG")
    print(f"✅ {path}")


# ============ 卡片模板（复制改文案即可）============

def card_cover(draw, img):
    """封面卡：悬念标题"""
    draw.text((540, 740), "做跨境前", fill="#FFFFFF",
              font=ImageFont.truetype(FONT_BOLD, 110), anchor="mm")
    draw.text((540, 880), "先搞清楚这3个问题", fill="#FFFFFF",
              font=ImageFont.truetype(FONT_BOLD, 110), anchor="mm")
    draw.text((540, 1100), "???  ???  ???", fill="#555555",
              font=ImageFont.truetype(FONT_BOLD, 70), anchor="mm")
    draw.text((540, 1680), "下划进入正片 →", fill="#666666",
              font=ImageFont.truetype(FONT_LIGHT, 36), anchor="mm")


def card_pain(draw, img):
    """痛点卡：场景共鸣+反问"""
    draw.text((540, 600), "90%新手都这样：", fill="#FFFFFF",
              font=ImageFont.truetype(FONT_BOLD, 90), anchor="mm")
    # 箭头流程（逐个位置绘制）
    parts = [("看别人赚钱", "#FFFFFF", 160, 900),
             ("→", "#FF4444", 420, 900),
             ("注册开店", "#FFFFFF", 540, 900),
             ("→", "#FF4444", 760, 900),
             ("亏钱收场", "#FF4444", 900, 900)]
    for text, color, x, y in parts:
        draw.text((x, y), text, fill=color,
                  font=ImageFont.truetype(FONT_BOLD if text in ["→"] else FONT_REGULAR, 55),
                  anchor="mm")
    draw.text((540, 1300), "你呢？", fill="#FFFFFF",
              font=ImageFont.truetype(FONT_BOLD, 90), anchor="mm")
    draw.text((540, 1450), "准备走老路还是新路？", fill="#AAAAAA",
              font=ImageFont.truetype(FONT_REGULAR, 55), anchor="mm")


def card_1(draw, img):
    """① 预算：深蓝底+金色数字"""
    draw.text((120, 350), "①", fill="#FFD700",
              font=ImageFont.truetype(FONT_BOLD, 120), anchor="mm")
    draw.text((540, 480), "你准备花多少钱？", fill="#FFFFFF",
              font=ImageFont.truetype(FONT_BOLD, 80), anchor="mm")
    items = [("营业执照", "¥0", "#4CAF50"),
             ("首批货款", "¥1000-3000", "#FFFFFF"),
             ("物流运费", "¥500", "#FFFFFF"),
             ("广告费用", "¥0-500", "#FFFFFF")]
    y = 700
    for name, price, color in items:
        draw.text((300, y), name, fill="#CCCCCC",
                  font=ImageFont.truetype(FONT_REGULAR, 55), anchor="lm")
        draw.text((780, y), price, fill=color,
                  font=ImageFont.truetype(FONT_BOLD, 55), anchor="rm")
        draw.line([(300, y+40), (780, y+40)], fill="#333333", width=1)
        y += 120
    draw.text((540, 1400), "前两个月至少 ¥3000 打底", fill="#FFD700",
              font=ImageFont.truetype(FONT_BOLD, 60), anchor="mm")


def card_2(draw, img):
    """② 平台：深绿底+✅❌对比"""
    draw.text((120, 300), "②", fill="#4CAF50",
              font=ImageFont.truetype(FONT_BOLD, 120), anchor="mm")
    draw.text((540, 420), "你选哪个平台？", fill="#FFFFFF",
              font=ImageFont.truetype(FONT_BOLD, 80), anchor="mm")
    draw.text((540, 600), "新手推荐 →", fill="#CCCCCC",
              font=ImageFont.truetype(FONT_REGULAR, 50), anchor="mm")
    draw.text((540, 700), "Shopee 马来站", fill="#4CAF50",
              font=ImageFont.truetype(FONT_BOLD, 60), anchor="mm")
    checks = [("✅", "新执照也能开"), ("✅", "英文运营不用学小语种"), ("✅", "新店有流量扶持")]
    y = 900
    for icon, text in checks:
        draw.text((250, y), f"{icon}  {text}", fill="#FFFFFF",
                  font=ImageFont.truetype(FONT_REGULAR, 52), anchor="lm")
        y += 110
    draw.line([(300, 1380), (780, 1380)], fill="#333333", width=1)
    draw.text((540, 1480), "❌  先别碰亚马逊", fill="#FF6666",
              font=ImageFont.truetype(FONT_BOLD, 60), anchor="mm")


def card_3(draw, img):
    """③ 时间：暗红底+⚠️警示"""
    draw.text((120, 300), "③", fill="#FF6B6B",
              font=ImageFont.truetype(FONT_BOLD, 120), anchor="mm")
    draw.text((540, 420), "每天能挤出1小时吗？", fill="#FFFFFF",
              font=ImageFont.truetype(FONT_BOLD, 80), anchor="mm")
    draw.text((540, 650), "前30天是黄金期", fill="#FFD700",
              font=ImageFont.truetype(FONT_BOLD, 65), anchor="mm")
    draw.text((540, 780), "每天1-2小时做：", fill="#CCCCCC",
              font=ImageFont.truetype(FONT_REGULAR, 55), anchor="mm")
    y = 920
    for t in ["· 选品", "· 上架", "· 看数据"]:
        draw.text((540, y), t, fill="#FFFFFF",
                  font=ImageFont.truetype(FONT_REGULAR, 55), anchor="mm")
        y += 100
    draw.line([(300, 1400), (780, 1400)], fill="#FF4444", width=2)
    draw.text((540, 1520), "挤不出时间？先别开店", fill="#FF4444",
              font=ImageFont.truetype(FONT_BOLD, 60), anchor="mm")


def card_end(draw, img):
    """结尾卡：总结+预告+品牌"""
    draw.text((540, 650), "这3个问题想清楚", fill="#FFFFFF",
              font=ImageFont.truetype(FONT_BOLD, 70), anchor="mm")
    draw.text((540, 780), "再往下走", fill="#FFFFFF",
              font=ImageFont.truetype(FONT_BOLD, 70), anchor="mm")
    draw.line([(300, 950), (780, 950)], fill="#333333", width=2)
    draw.text((540, 1080), "👇 下期预告", fill="#888888",
              font=ImageFont.truetype(FONT_REGULAR, 50), anchor="mm")
    draw.text((540, 1200), "开店注册，一步都不能错", fill="#FFD700",
              font=ImageFont.truetype(FONT_BOLD, 70), anchor="mm")
    draw.text((540, 1550), "关注我，下期见", fill="#AAAAAA",
              font=ImageFont.truetype(FONT_REGULAR, 50), anchor="mm")
    draw.text((540, 1700), "我和AI做跨境电商", fill="#666666",
              font=ImageFont.truetype(FONT_BOLD, 45), anchor="mm")


if __name__ == "__main__":
    cards = [
        ("card_cover.png", card_cover),
        ("card_pain.png", card_pain),
        ("card_1_budget.png", card_1),
        ("card_2_platform.png", card_2),
        ("card_3_time.png", card_3),
        ("card_end.png", card_end),
    ]
    for filename, func in cards:
        create_card(filename, func)
    print(f"\n🎉 共 {len(cards)} 张 | 目录: {OUTPUT_DIR}")
