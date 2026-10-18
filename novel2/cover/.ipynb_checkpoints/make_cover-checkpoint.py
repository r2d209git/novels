"""『열 번째 손님』 표지 생성 (1600x2400). 사용법: python3 make_cover.py <출력 경로>"""
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1600, 2400
FONT_DIR = "/usr/share/fonts/google-noto-cjk/"
KR = 1  # Noto CJK ttc 안의 KR 글꼴 인덱스
SKY_TOP, SKY_BOTTOM = (6, 10, 22), (24, 36, 58)
WARM, COLD = (255, 196, 110), (190, 235, 255)


def font(weight, size):
    return ImageFont.truetype(f"{FONT_DIR}NotoSerifCJK-{weight}.ttc", size, index=KR)


def gradient():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(SKY_TOP, SKY_BOTTOM)))
    return img


def glow(img, box, color, radius):
    layer = Image.new("RGB", (W, H))
    ImageDraw.Draw(layer).ellipse(box, fill=color)
    return ImageChops.add(img, layer.filter(ImageFilter.GaussianBlur(radius)))


def fog(img, rng):
    layer = Image.new("L", (W, H))
    d = ImageDraw.Draw(layer)
    for _ in range(14):
        y = rng.randint(1350, 2050)
        x = rng.randint(-300, W)
        d.ellipse([x, y, x + rng.randint(500, 1100), y + rng.randint(40, 110)], fill=rng.randint(30, 70))
    layer = layer.filter(ImageFilter.GaussianBlur(40))
    return Image.composite(Image.new("RGB", (W, H), (120, 140, 165)), img, layer)


def house(img):
    d = ImageDraw.Draw(img)
    cliff = [(560, 2400), (640, 1700), (760, 1560), (1000, 1520), (1250, 1540), (1420, 1640), (1600, 1700), (1600, 2400)]
    d.polygon(cliff, fill=(4, 6, 12))
    d.rectangle([700, 1330, 1460, 1540], fill=(8, 11, 18))   # 1~2층 매스
    d.rectangle([820, 1250, 1280, 1335], fill=(8, 11, 18))   # 3층 전망실
    d.rectangle([1380, 1470, 1600, 1500], fill=(8, 11, 18))  # 절벽 밖으로 뻗은 슬래브
    windows = [(735 + i * 72, 1365) for i in range(10)]
    for i, (x, y) in enumerate(windows):
        color = COLD if i == 9 else WARM
        img = glow(img, [x - 30, y - 20, x + 70, y + 110], tuple(c // 4 for c in color), 30)
        ImageDraw.Draw(img).rectangle([x, y, x + 40, y + 90], fill=color)
    d = ImageDraw.Draw(img)
    for x in range(840, 1270, 20):  # 3층 유리 줄눈
        d.line([(x, 1260), (x, 1325)], fill=(30, 40, 55), width=2)
    return img


def lighthouse(img):
    beam = Image.new("L", (W, H))
    ImageDraw.Draw(beam).polygon([(250, 1620), (W, 980), (W, 1260)], fill=40)
    img = Image.composite(Image.new("RGB", (W, H), (200, 215, 230)), img, beam.filter(ImageFilter.GaussianBlur(25)))
    img = glow(img, [225, 1595, 275, 1645], (255, 240, 200), 12)
    ImageDraw.Draw(img).rectangle([243, 1620, 257, 1720], fill=(10, 12, 18))
    return img


def sea(img):
    d = ImageDraw.Draw(img)
    for y in range(1720, H, 6):
        shade = 10 + (y - 1720) // 40
        d.line([(0, y), (W, y)], fill=(shade // 2, shade, shade + 14))
    for y in range(1730, H, 18):  # 열 번째 창의 차가운 반사
        d.line([(1390, y), (1420 + (y % 36), y)], fill=(70, 100, 120), width=2)
    return img


def text(img):
    d = ImageDraw.Draw(img)

    def center(s, y, f, fill, spacing=0):
        if spacing:
            widths = [d.textlength(ch, font=f) for ch in s]
            x = (W - sum(widths) - spacing * (len(s) - 1)) / 2
            for ch, w in zip(s, widths):
                d.text((x, y), ch, font=f, fill=fill)
                x += w + spacing
        else:
            d.text(((W - d.textlength(s, font=f)) / 2, y), s, font=f, fill=fill)

    center("열 명이 초대되었다. 한 명은 사람이 아니다.", 250, font("Regular", 46), (170, 185, 205))
    center("열 번째 손님", 360, font("Black", 210), (236, 238, 242), spacing=12)
    d.line([(740, 700), (860, 700)], fill=COLD, width=3)
    center("장편소설", 735, font("Medium", 50), (190, 200, 215), spacing=18)
    center("사흘 뒤 자정, 한 사람의 이름이 적힌다.", 2200, font("Regular", 40), (150, 165, 185))
    return img


def grain(img, rng):
    noise = Image.effect_noise((W, H), 18).convert("RGB")
    return Image.blend(img, ImageChops.multiply(img, noise.point(lambda v: 200 + v // 5)), 0.35)


def main(out):
    rng = random.Random(1103)
    img = gradient()
    img = lighthouse(img)
    img = sea(img)
    img = house(img)
    img = fog(img, rng)
    img = grain(img, rng)
    img = text(img)
    img.save(out, optimize=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "cover.png")
