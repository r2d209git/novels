"""『풍랑 속』 표지 생성 (1600x2400). 사용법: python3 make_cover.py <출력 경로>"""
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
        y = rng.randint(1640, 2100)  # 저택 아래 바다 쪽에만 깔린다
        x = rng.randint(-300, W)
        d.ellipse([x, y, x + rng.randint(500, 1100), y + rng.randint(40, 110)], fill=rng.randint(30, 70))
    layer = layer.filter(ImageFilter.GaussianBlur(40))
    return Image.composite(Image.new("RGB", (W, H), (120, 140, 165)), img, layer)


GROUND = 1560          # 저택이 앉은 절벽 위 평탄면
CONCRETE = (22, 26, 34)
CONCRETE_EDGE = (34, 40, 52)
INTERIOR = (96, 74, 46)
FRAME = (12, 14, 20)


def cliff(img):
    d = ImageDraw.Draw(img)
    # 꼭대기는 평평하게 다듬고, 바다 쪽으로만 가파르게 떨어진다
    d.polygon([(470, H), (540, 1760), (600, 1640), (660, 1585), (720, GROUND), (1470, GROUND),
               (1500, 1600), (1530, 1700), (1560, 1820), (1600, 1860), (1600, H)], fill=(5, 7, 12))
    d.line([(720, GROUND), (1470, GROUND)], fill=(30, 34, 44), width=3)  # 축대 윗면
    # 선착장에서 올라오는 지그재그 돌계단
    pts = [(560, 1740), (640, 1712), (590, 1684), (670, 1652), (625, 1622), (700, 1592), (735, GROUND)]
    d.line(pts, fill=(40, 46, 58), width=3)
    for x, y in pts[1:-1]:
        img = glow(img, [x - 10, y - 10, x + 10, y + 10], (60, 48, 30), 6)  # 계단참 등
    return img


def house(img):
    d = ImageDraw.Draw(img)
    # 1층: 유리 벽
    d.rectangle([760, 1452, 1400, GROUND], fill=INTERIOR)
    for x in range(760, 1401, 32):
        d.line([(x, 1452), (x, GROUND)], fill=FRAME, width=3)
    d.rectangle([700, 1452, 760, GROUND], fill=CONCRETE)  # 현관 벽체
    # 2층: 노출 콘크리트 매스, 절벽 밖으로 캔틸레버
    d.rectangle([700, 1322, 1580, 1452], fill=CONCRETE)
    d.line([(700, 1322), (1580, 1322)], fill=CONCRETE_EDGE, width=4)
    d.line([(700, 1452), (1580, 1452)], fill=CONCRETE_EDGE, width=3)
    for x in range(700, 1581, 88):  # 거푸집 줄눈과 폼타이 구멍
        d.line([(x, 1324), (x, 1450)], fill=(28, 32, 42), width=1)
        for y in (1340, 1436):
            d.point([(x + 22, y), (x + 66, y)], fill=(40, 46, 58))
    # 손님방 창 열 개: 아홉은 불이 켜져 있고 하나는 아직 비어 있다
    for i in range(10):
        x, y = 735 + i * 82, 1352
        if i < 9:
            warm = tuple(min(255, c + (i % 3 - 1) * 12) for c in WARM)
            img = glow(img, [x - 26, y - 18, x + 70, y + 92], tuple(c // 5 for c in warm), 26)
            d = ImageDraw.Draw(img)
            d.rectangle([x, y, x + 44, y + 74], fill=warm)
            d.line([(x + 22, y), (x + 22, y + 74)], fill=FRAME, width=2)
            d.rectangle([x + 4, y + 50, x + 18, y + 74], fill=tuple(c * 3 // 5 for c in warm))  # 커튼 그림자
        else:
            d.rectangle([x, y, x + 44, y + 74], fill=(10, 13, 20))
            d.line([(x + 22, y), (x + 22, y + 74)], fill=(24, 28, 38), width=2)
        d.rectangle([x - 3, y - 3, x + 47, y + 77], outline=FRAME, width=3)
    # 캔틸레버 아래 그림자와 받침 철골
    d.rectangle([1470, 1452, 1580, 1462], fill=(8, 10, 15))
    d.line([(1470, GROUND), (1560, 1456)], fill=(26, 30, 40), width=5)
    # 3층: 유리 전망실, 얇은 지붕 슬래브, 옥상 난간과 안테나
    d.rectangle([880, 1236, 1240, 1322], fill=(40, 52, 70))
    for x in range(880, 1241, 24):
        d.line([(x, 1236), (x, 1322)], fill=FRAME, width=2)
    d.line([(880, 1290), (1240, 1290)], fill=FRAME, width=2)
    d.rectangle([856, 1226, 1264, 1236], fill=CONCRETE_EDGE)
    for x in range(704, 1580, 14):
        if not 876 < x < 1244:
            d.line([(x, 1300), (x, 1322)], fill=(30, 36, 48), width=1)
    d.line([(700, 1300), (876, 1300)], fill=(36, 42, 54), width=2)
    d.line([(1244, 1300), (1580, 1300)], fill=(36, 42, 54), width=2)
    d.line([(1200, 1226), (1200, 1150)], fill=(30, 36, 48), width=3)
    img = glow(img, [1194, 1144, 1206, 1156], (120, 20, 20), 4)  # 안테나 표시등
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

    center("열 장의 초대장, 아무도 모르는 열 개의 죄", 250, font("Regular", 46), (170, 185, 205))
    center("풍랑 속", 360, font("Black", 230), (236, 238, 242), spacing=40)
    d.line([(740, 700), (860, 700)], fill=COLD, width=3)
    center("장편소설", 735, font("Medium", 50), (190, 200, 215), spacing=18)
    center("사흘 뒤 자정, 한 사람의 이름이 적힌다.", 2200, font("Regular", 40), (150, 165, 185))
    return img


def grain(img, rng):
    noise = Image.effect_noise((W, H), 18).convert("RGB")
    return Image.blend(img, ImageChops.multiply(img, noise.point(lambda v: 200 + v // 5)), 0.35)


def waves(img, rng):
    """풍랑: 흰 물마루. 절벽보다 먼저 그려 절벽 뒤로 가려지게 한다."""
    foam = Image.new("L", (W, H))
    d = ImageDraw.Draw(foam)
    for _ in range(300):
        y = rng.randint(1730, H)
        x = rng.randint(-100, W)
        length = rng.randint(30, 140) * (y - 1600) // 600
        d.arc([x, y, x + length, y + length // 4], 200, 340, fill=rng.randint(70, 160), width=2)
    for _ in range(25):  # 절벽 밑에서 부서지는 파도
        x, y = rng.randint(330, 560), rng.randint(1725, 1820)
        d.arc([x, y, x + rng.randint(60, 140), y + rng.randint(14, 30)], 180, 360, fill=rng.randint(110, 190), width=3)
    return Image.composite(Image.new("RGB", (W, H), (150, 170, 190)), img, foam.filter(ImageFilter.GaussianBlur(1.5)))


def rain(img, rng):
    layer = Image.new("L", (W, H))
    d = ImageDraw.Draw(layer)
    for _ in range(1400):
        x, y = rng.randint(-400, W), rng.randint(0, H)
        n = rng.randint(30, 80)
        d.line([(x, y), (x + n // 3, y + n)], fill=rng.randint(25, 60), width=1)
    return Image.composite(Image.new("RGB", (W, H), (170, 185, 205)), img, layer)


def main(out):
    rng = random.Random(1103)
    img = gradient()
    img = lighthouse(img)
    img = sea(img)
    img = waves(img, rng)
    img = cliff(img)
    img = house(img)
    img = fog(img, rng)
    img = rain(img, rng)
    img = grain(img, rng)
    img = text(img)
    img.save(out, optimize=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "cover.png")
