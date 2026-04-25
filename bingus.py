from PIL import Image, ImageDraw, ImageFont
import random

def read_lines_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]
    return [ln for ln in lines if ln.strip()]

def load_font(sz):
    # try common TTF locations; adjust/add paths as necessary
    for p in (
        "/Library/Fonts/Arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            pass
    return ImageFont.load_default()

def make_square(lines, size=200, font_size=36, padding=24, border_width=4, min_font_size=14):
    img = Image.new("RGB", (size, size), color="white")
    draw = ImageDraw.Draw(img)
    font = load_font(font_size)

    text = random.choice(lines) if lines else "Sample"

    max_width = size - 2 * (padding + border_width)
    max_height = size - 2 * (padding + border_width)

    # wrap and reduce font only if needed
    while True:
        words = text.split()
        wrapped_lines = []
        if not words:
            wrapped_lines = [""]
        else:
            line = words[0]
            for word in words[1:]:
                test_line = f"{line} {word}"
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] <= max_width:
                    line = test_line
                else:
                    wrapped_lines.append(line)
                    line = word
            wrapped_lines.append(line)

        line_heights = []
        max_line_w = 0
        for ln in wrapped_lines:
            bbox = draw.textbbox((0, 0), ln, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            line_heights.append(h)
            max_line_w = max(max_line_w, w)

        line_spacing = int(0.2 * (font.size if hasattr(font, "size") else 0)) or 2
        total_height = sum(line_heights) + line_spacing * (len(line_heights) - 1)

        if total_height <= max_height or (hasattr(font, "size") and font.size <= min_font_size):
            break

        if hasattr(font, "size"):
            new_size = max(min_font_size, font.size - 2)
            if new_size == font.size:
                break
            font = load_font(new_size)
        else:
            break

    y = border_width + padding + (max_height - total_height) / 2
    for i, ln in enumerate(wrapped_lines):
        bbox = draw.textbbox((0, 0), ln, font=font)
        line_w = bbox[2] - bbox[0]
        x = border_width + padding + (max_width - line_w) / 2
        draw.text((x, y), ln, fill="black", font=font)
        y += line_heights[i] + line_spacing

    draw.rectangle(
        [(border_width - 1, border_width - 1), (size - border_width, size - border_width)],
        outline="black", width=border_width
    )
    return img

def make_free_square(size=200, font_size=36, padding=24, border_width=4, min_font_size=14, text="FREE", free_image_path=None):
    img = Image.new("RGB", (size, size), color="white")
    draw = ImageDraw.Draw(img)
    font = load_font(font_size)

    max_inner = size - 2 * (padding + border_width)

    if free_image_path:
        try:
            with Image.open(free_image_path) as im:
                # convert and ensure square by center-cropping
                im = im.convert("RGBA")
                w, h = im.size
                side = min(w, h)
                left = (w - side) // 2
                top = (h - side) // 2
                im = im.crop((left, top, left + side, top + side))
                # resize to fit inner box
                im = im.resize((max_inner, max_inner), Image.LANCZOS)
                # paste centered
                paste_x = border_width + padding + (max_inner - im.width) // 2
                paste_y = border_width + padding + (max_inner - im.height) // 2
                img.paste(im, (int(paste_x), int(paste_y)), im)
        except Exception:
            # on failure, fall back to text rendering below
            free_image_path = None

    if not free_image_path:
        # same wrapping/resizing logic as make_square for the text
        text_to_draw = text
        while True:
            words = text_to_draw.split()
            wrapped_lines = []
            if not words:
                wrapped_lines = [""]
            else:
                line = words[0]
                for word in words[1:]:
                    test_line = f"{line} {word}"
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    if bbox[2] - bbox[0] <= max_inner:
                        line = test_line
                    else:
                        wrapped_lines.append(line)
                        line = word
                wrapped_lines.append(line)

            line_heights = []
            max_line_w = 0
            for ln in wrapped_lines:
                bbox = draw.textbbox((0, 0), ln, font=font)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                line_heights.append(h)
                max_line_w = max(max_line_w, w)

            line_spacing = int(0.2 * (font.size if hasattr(font, "size") else 0)) or 2
            total_height = sum(line_heights) + line_spacing * (len(line_heights) - 1)

            if total_height <= max_inner or (hasattr(font, "size") and font.size <= min_font_size):
                break

            if hasattr(font, "size"):
                new_size = max(min_font_size, font.size - 2)
                if new_size == font.size:
                    break
                font = load_font(new_size)
            else:
                break

        y = border_width + padding + (max_inner - total_height) / 2
        for i, ln in enumerate(wrapped_lines):
            bbox = draw.textbbox((0, 0), ln, font=font)
            line_w = bbox[2] - bbox[0]
            x = border_width + padding + (max_inner - line_w) / 2
            draw.text((x, y), ln, fill="black", font=font)
            y += line_heights[i] + line_spacing

    draw.rectangle(
        [(border_width - 1, border_width - 1), (size - border_width, size - border_width)],
        outline="black", width=border_width
    )
    return img

def add_banner_above_card(card_img, banner_path, banner_max_height=None, bg_color="white"):
    # open banner
    banner = Image.open(banner_path).convert("RGBA")
    card_w, card_h = card_img.size

    # scale banner to card width, preserving aspect ratio
    bw, bh = banner.size
    new_bw = card_w
    new_bh = int(bh * (new_bw / bw))
    banner = banner.resize((new_bw, new_bh), Image.LANCZOS)

    # optional: if banner_max_height set, further scale down
    if banner_max_height and new_bh > banner_max_height:
        scale = banner_max_height / new_bh
        new_bh = banner_max_height
        new_bw = int(new_bw * scale)
        banner = banner.resize((new_bw, new_bh), Image.LANCZOS)
        # center horizontally if narrower than card
        offset_x = (card_w - new_bw) // 2
    else:
        offset_x = 0

    # create combined image
    combined_h = new_bh + card_h
    combined = Image.new("RGB", (card_w, combined_h), color=bg_color)

    # paste banner (handle transparency)
    if banner.mode == "RGBA":
        combined.paste(banner, (offset_x, 0), banner)
    else:
        combined.paste(banner, (offset_x, 0))

    # paste card below banner
    combined.paste(card_img, (0, new_bh))

    return combined

def main():
    lines = read_lines_from_file("lines.txt")

    # Bingo card layout: 5x5 tiles, but center is free. We need 24 random squares.
    tile_size = 600
    font_size = 80
    cols, rows = 5, 5
    board_w = cols * tile_size
    board_h = rows * tile_size
    board = Image.new("RGB", (board_w, board_h), color="white")

    # Generate 24 random squares (without replacement if you prefer unique lines)
    # Use sampling without replacement when there are enough lines; otherwise allow repeats.
    if len(lines) >= 24:
        choices = random.sample(lines, 24)
    else:
        choices = [random.choice(lines) if lines else "Sample" for _ in range(24)]

    # Place tiles row-major. Reserve center (row=2,col=2) as free (index 12, 0-based).
    idx = 0
    for r in range(rows):
        for c in range(cols):
            if r == 2 and c == 2:
                tile = make_free_square(size=tile_size, font_size=font_size, padding=0, border_width=4, free_image_path='img/kk_logo_pink.png')
            else:
                tile = make_square([choices[idx]], size=tile_size, font_size=font_size, padding=32, border_width=4)  # pass single-item list so make_square picks that item
                idx += 1
            board.paste(tile, (c * tile_size, r * tile_size))

    card = board
    combined = add_banner_above_card(card, "img/Word-Logo-Bingo.png", banner_max_height=800)
    combined.save("output/bingo_with_banner.png")

if __name__ == "__main__":
    main()

