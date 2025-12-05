import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from apng import APNG
import io
import os
import zipfile
from datetime import datetime

# ページ設定
st.set_page_config(
    page_title="APNG Generator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# モダンなダークモードCSS（UI刷新・シンプル版）
st.markdown("""
<style>
    /* グローバル設定 - フォント変更なし */
    * {
        font-family: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN", "Hiragino Sans", Meiryo, sans-serif;
    }
    
    /* 背景色 - 真っ黒ではなく深いグレーで目に優しく */
    .stApp {
        background-color: #1a1a1a;
        color: #f0f0f0;
    }
    
    /* メインコンテナ調整 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 98%;
    }
    
    /* タイトル - 装飾を抑えてシンプルに */
    h1 {
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
        border-left: 5px solid #007bff; /* アクセントカラー */
        padding-left: 15px;
        margin-bottom: 2rem;
    }
    
    /* 入力フィールド - コントラスト確保 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        background-color: #2c2c2c;
        color: #ffffff;
        border: 1px solid #444;
        border-radius: 4px;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #007bff;
    }

    /* タブのスタイル調整 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #2c2c2c;
        border-radius: 4px 4px 0 0;
        color: #aaa;
        padding: 8px 16px;
        border: 1px solid #333;
        border-bottom: none;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #007bff;
        color: white;
        border-color: #007bff;
    }

    /* ボタン - シンプルで押しやすく */
    .stButton > button {
        border-radius: 4px;
        font-weight: 600;
        border: 1px solid #444;
        background-color: #333;
        color: #fff;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        border-color: #666;
        background-color: #444;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #007bff;
        border-color: #0056b3;
        color: white;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #0069d9;
    }
    
    /* エキスパンダー - 区切りを明確に */
    .streamlit-expanderHeader {
        background-color: #252525;
        border: 1px solid #333;
        border-radius: 4px;
    }
    .streamlit-expanderContent {
        border: 1px solid #333;
        border-top: none;
        background-color: #202020;
        padding: 15px;
    }

    /* プレビューエリアのSticky化（修正版） */
    /* 親コンテナの高さ制限を解除し、カラム自体をstickyにする */
    div[data-testid="stHorizontalBlock"] {
        align-items: flex-start; /* これが重要：カラムの高さを合わせない */
    }
    
    /* 右カラム（プレビュー） */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-of-type(2) {
        position: -webkit-sticky;
        position: sticky;
        top: 3rem; /* 上部の余白 */
        z-index: 100;
    }
    
    /* プレビューボックス */
    .preview-box {
        background-color: #000;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 15px;
    }
    
    /* セクション見出し（装飾なし） */
    .simple-header {
        font-size: 16px;
        font-weight: bold;
        color: #ddd;
        margin-top: 10px;
        margin-bottom: 10px;
        border-bottom: 1px solid #444;
        padding-bottom: 5px;
    }
    
    /* 注釈リストのアイテム */
    .annotation-item {
        background-color: #252525;
        border: 1px solid #333;
        border-left: 4px solid #007bff;
        padding: 10px;
        margin-bottom: 8px;
        border-radius: 0 4px 4px 0;
    }

</style>
""", unsafe_allow_html=True)

# グローバル設定
WIDTH = 600
HEIGHT = 400

# 日本語フォント読み込み関数（変更なし）
def get_font(font_type="ゴシック", weight="W7", size=40):
    """日本語フォントを取得（Streamlit Cloud対応）"""
    font_paths = []
    
    if font_type == "ゴシック":
        linux_paths = [
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansMonoCJKjp-Bold.otf",
            "/usr/share/fonts/opentype/noto/NotoSansMonoCJKjp-Regular.otf",
        ]
        font_paths.extend(linux_paths)
        
        hiragino_std_paths = {
            "W3": "/Library/Fonts/ヒラギノ角ゴ Std W4.otf",
            "W4": "/Library/Fonts/ヒラギノ角ゴ Std W4.otf",
            "W5": "/Library/Fonts/ヒラギノ角ゴ Std W6.otf",
            "W6": "/Library/Fonts/ヒラギノ角ゴ Std W6.otf",
            "W7": "/Library/Fonts/ヒラギノ角ゴ Std W8.otf",
            "W8": "/Library/Fonts/ヒラギノ角ゴ Std W8.otf",
            "W9": "/Library/Fonts/ヒラギノ角ゴ Std W8.otf",
        }
        
        hiragino_paths = {
            "W3": "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            "W4": "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
            "W5": "/System/Library/Fonts/ヒラギノ角ゴシック W5.ttc",
            "W6": "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
            "W7": "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc",
            "W8": "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc",
            "W9": "/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc",
        }
        
        windows_paths = {
            "W3": ["C:\\Windows\\Fonts\\meiryo.ttc", "C:\\Windows\\Fonts\\YuGothL.ttc"],
            "W4": ["C:\\Windows\\Fonts\\meiryo.ttc", "C:\\Windows\\Fonts\\YuGothR.ttc"],
            "W5": ["C:\\Windows\\Fonts\\meiryo.ttc", "C:\\Windows\\Fonts\\YuGothM.ttc"],
            "W6": ["C:\\Windows\\Fonts\\meiryob.ttc", "C:\\Windows\\Fonts\\YuGothB.ttc"],
            "W7": ["C:\\Windows\\Fonts\\meiryob.ttc", "C:\\Windows\\Fonts\\YuGothB.ttc"],
            "W8": ["C:\\Windows\\Fonts\\meiryob.ttc", "C:\\Windows\\Fonts\\YuGothB.ttc"],
            "W9": ["C:\\Windows\\Fonts\\meiryob.ttc", "C:\\Windows\\Fonts\\YuGothB.ttc"],
        }
        
        if weight in hiragino_std_paths:
            font_paths.append(hiragino_std_paths[weight])
        if weight in hiragino_paths:
            font_paths.append(hiragino_paths[weight])
        if weight in windows_paths:
            font_paths.extend(windows_paths[weight])
        
        font_paths.extend([
            "msgothic.ttc",
            "C:\\Windows\\Fonts\\msgothic.ttc",
        ])
    else:  # 明朝
        linux_paths = [
            "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
            "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSerifCJK-Bold.ttc",
            "/usr/share/fonts/truetype/noto/NotoSerifCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ]
        font_paths.extend(linux_paths)
        
        font_paths.extend([
            "/System/Library/Fonts/ヒラギノ明朝 ProN W6.ttc",
            "/Library/Fonts/ヒラギノ明朝 Std W6.otf",
            "/System/Library/Fonts/ヒラギノ明朝 ProN W3.ttc",
            "/Library/Fonts/ヒラギノ明朝 Std W3.otf",
            "C:\\Windows\\Fonts\\msmincho.ttc",
            "msmincho.ttc"
        ])
    
    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, size)
        except Exception as e:
            continue
    
    st.warning(f"日本語フォントが見つかりませんでした。デフォルトフォントを使用します。")
    return ImageFont.load_default()

# 描画関連関数群（変更なし）
def draw_text_bold(draw, position, text, font, fill, anchor="mm", is_mincho_bold=False):
    x, y = position
    if is_mincho_bold:
        offsets = [(0, 0), (1, 0), (0, 1), (1, 1)]
        for dx, dy in offsets:
            draw.text((x + dx, y + dy), text, fill=fill, font=font, anchor=anchor)
    else:
        draw.text((x, y), text, fill=fill, font=font, anchor=anchor)

def load_icon_image(icon_name, size):
    icon_path = f"icons/{icon_name}"
    if os.path.exists(icon_path):
        icon = Image.open(icon_path).convert("RGBA")
        icon = icon.resize((size, size), Image.Resampling.LANCZOS)
        return icon
    return None

def draw_text_with_spacing(img, draw, text, x, y, font, color, char_spacing=0, line_spacing=0, aspect_ratio=1.0, is_mincho_bold=False):
    lines = text.split('\n')
    current_y = y
    
    for line in lines:
        if not line:
            bbox = draw.textbbox((0, 0), "A", font=font)
            current_y += (bbox[3] - bbox[1]) + line_spacing
            continue
        
        if char_spacing != 0 or aspect_ratio != 1.0:
            total_width = 0
            char_data = []
            
            for char in line:
                bbox = draw.textbbox((0, 0), char, font=font)
                char_width = (bbox[2] - bbox[0])
                char_height = (bbox[3] - bbox[1])
                scaled_width = char_width * aspect_ratio
                char_data.append((char, scaled_width, char_height))
                total_width += scaled_width + char_spacing
            
            total_width -= char_spacing
            start_x = x - total_width / 2
            current_x = start_x
            
            for char, scaled_width, char_height in char_data:
                temp_size = int(font.size * 3)
                temp_img = Image.new('RGBA', (temp_size, temp_size), (255, 255, 255, 0))
                temp_draw = ImageDraw.Draw(temp_img)
                
                if is_mincho_bold:
                    offsets = [(0, 0), (1, 0), (0, 1), (1, 1)]
                    for dx, dy in offsets:
                        temp_draw.text((temp_size // 2 + dx, temp_size // 2 + dy), char, fill=color, font=font, anchor="mm")
                else:
                    temp_draw.text((temp_size // 2, temp_size // 2), char, fill=color, font=font, anchor="mm")
                
                if aspect_ratio != 1.0:
                    new_width = int(temp_img.width * aspect_ratio)
                    temp_img = temp_img.resize((new_width, temp_img.height), Image.Resampling.LANCZOS)
                
                paste_x = int(current_x + scaled_width / 2 - temp_img.width / 2)
                paste_y = int(current_y - temp_img.height / 2)
                img.paste(temp_img, (paste_x, paste_y), temp_img)
                
                current_x += scaled_width + char_spacing
        else:
            draw_text_bold(draw, (x, current_y), line, font, color, "mm", is_mincho_bold)
        
        bbox = draw.textbbox((0, 0), line, font=font)
        current_y += (bbox[3] - bbox[1]) + line_spacing
    
    return current_y

# テンプレート関数群（変更なし）
def create_red_border_blink_frames(width, height, text_elements, annotation_elements, uploaded_image, image_config, border_width=13, border_color="red", num_frames=5):
    frames = []
    color_map = {"red": "#FF0000", "blue": "#0000FF", "green": "#00FF00", "black": "#000000", "orange": "#FF6600"}
    border_rgb = color_map.get(border_color, "#FF0000")
    
    for i in range(num_frames):
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        if uploaded_image is not None and image_config is not None:
            img_scale = image_config.get('scale', 1.0)
            original_width = image_config.get('original_width', 100)
            original_height = image_config.get('original_height', 100)
            
            img_width = int(original_width * img_scale)
            img_height = int(original_height * img_scale)
            img_x = image_config.get('x', width // 2)
            img_y = image_config.get('y', height // 2)
            
            resized_img = uploaded_image.resize((img_width, img_height), Image.Resampling.LANCZOS)
            paste_x = img_x - img_width // 2
            paste_y = img_y - img_height // 2
            
            if uploaded_image.mode == 'RGBA':
                img.paste(resized_img, (paste_x, paste_y), resized_img)
            else:
                img.paste(resized_img, (paste_x, paste_y))
        
        if i % 2 == 0:
            draw.rectangle([0, 0, width-1, height-1], outline=border_rgb, width=border_width)
        
        for elem in text_elements:
            if elem.get('enabled', True):
                font = get_font(elem['font'], elem.get('weight', 'W7'), elem['size'])
                is_mincho_bold = elem['font'] == "明朝" and elem.get('weight', 'W7') in ["W7", "W8", "W9"]
                draw_text_with_spacing(img, draw, elem['text'], elem['x'], elem['y'], font, elem['color'],
                                     char_spacing=elem.get('char_spacing', 0),
                                     line_spacing=elem.get('line_spacing', 0),
                                     aspect_ratio=elem.get('aspect_ratio', 1.0),
                                     is_mincho_bold=is_mincho_bold)
        
        for elem in annotation_elements:
            if elem.get('enabled', True):
                font = get_font(elem['font'], elem.get('weight', 'W7'), elem['size'])
                is_mincho_bold = elem['font'] == "明朝" and elem.get('weight', 'W7') in ["W7", "W8", "W9"]
                draw_text_bold(draw, (elem['x'], elem['y']), elem['text'], font, elem['color'], "lm", is_mincho_bold)
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        frames.append(buffer.getvalue())
    
    return frames

def create_corner_icon_blink_frames(width, height, text_elements, annotation_elements, uploaded_image, image_config, icon_name="check.png", icon_size=85, num_frames=5):
    frames = []
    
    for i in range(num_frames):
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        if uploaded_image is not None and image_config is not None:
            img_scale = image_config.get('scale', 1.0)
            original_width = image_config.get('original_width', 100)
            original_height = image_config.get('original_height', 100)
            
            img_width = int(original_width * img_scale)
            img_height = int(original_height * img_scale)
            img_x = image_config.get('x', width // 2)
            img_y = image_config.get('y', height // 2)
            
            resized_img = uploaded_image.resize((img_width, img_height), Image.Resampling.LANCZOS)
            paste_x = img_x - img_width // 2
            paste_y = img_y - img_height // 2
            
            if uploaded_image.mode == 'RGBA':
                img.paste(resized_img, (paste_x, paste_y), resized_img)
            else:
                img.paste(resized_img, (paste_x, paste_y))
        
        if i % 2 == 0:
            icon_img = load_icon_image(icon_name, icon_size)
            
            if icon_img:
                positions = [(10, 10), (width - icon_size - 10, 10),
                            (10, height - icon_size - 10), (width - icon_size - 10, height - icon_size - 10)]
                for pos in positions:
                    img.paste(icon_img, pos, icon_img)
        
        for elem in text_elements:
            if elem.get('enabled', True):
                font = get_font(elem['font'], elem.get('weight', 'W7'), elem['size'])
                is_mincho_bold = elem['font'] == "明朝" and elem.get('weight', 'W7') in ["W7", "W8", "W9"]
                draw_text_with_spacing(img, draw, elem['text'], elem['x'], elem['y'], font, elem['color'],
                                     char_spacing=elem.get('char_spacing', 0),
                                     line_spacing=elem.get('line_spacing', 0),
                                     aspect_ratio=elem.get('aspect_ratio', 1.0),
                                     is_mincho_bold=is_mincho_bold)
        
        for elem in annotation_elements:
            if elem.get('enabled', True):
                font = get_font(elem['font'], elem.get('weight', 'W7'), elem['size'])
                is_mincho_bold = elem['font'] == "明朝" and elem.get('weight', 'W7') in ["W7", "W8", "W9"]
                draw_text_bold(draw, (elem['x'], elem['y']), elem['text'], font, elem['color'], "lm", is_mincho_bold)
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        frames.append(buffer.getvalue())
    
    return frames

def create_icon_increase_frames(width, height, icon_text_config, annotation_elements, uploaded_image, image_config, icon_name="check.png", icon_size=60, num_frames=5):
    frames = []
    
    text_content = icon_text_config.get('text', 'サンプルテキスト').replace('\n', '')
    text_font_type = icon_text_config.get('font', 'ゴシック')
    text_weight = icon_text_config.get('weight', 'W7')
    text_size = icon_text_config.get('icon_size', 40)
    text_color = icon_text_config.get('color', '#000000')
    text_x = icon_text_config.get('icon_x', 74)
    text_y_base = icon_text_config.get('icon_y', 320)
    char_spacing = icon_text_config.get('icon_char_spacing', 0)
    aspect_ratio = icon_text_config.get('icon_aspect_ratio', 1.0)
    row_spacing = icon_text_config.get('icon_row_spacing', 62)
    
    is_mincho_bold = text_font_type == "明朝" and text_weight in ["W7", "W8", "W9"]
    
    for frame_idx in range(num_frames):
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        if uploaded_image is not None and image_config is not None:
            img_scale = image_config.get('scale', 1.0)
            original_width = image_config.get('original_width', 100)
            original_height = image_config.get('original_height', 100)
            
            img_width = int(original_width * img_scale)
            img_height = int(original_height * img_scale)
            img_x = image_config.get('x', width // 2)
            img_y = image_config.get('y', height // 2)
            
            resized_img = uploaded_image.resize((img_width, img_height), Image.Resampling.LANCZOS)
            paste_x = img_x - img_width // 2
            paste_y = img_y - img_height // 2
            
            if uploaded_image.mode == 'RGBA':
                img.paste(resized_img, (paste_x, paste_y), resized_img)
            else:
                img.paste(resized_img, (paste_x, paste_y))
        
        num_lines = frame_idx + 1
        start_y = text_y_base - ((num_lines - 1) * row_spacing)
        
        icon_img = load_icon_image(icon_name, icon_size)
        font = get_font(text_font_type, text_weight, text_size)
        
        for line_idx in range(num_lines):
            current_y = start_y + (line_idx * row_spacing)
            
            if char_spacing != 0 or aspect_ratio != 1.0:
                first_char_left_edge = None
                current_x = text_x
                
                for char_idx, char in enumerate(text_content):
                    temp_size = int(font.size * 3)
                    temp_img = Image.new('RGBA', (temp_size, temp_size), (255, 255, 255, 0))
                    temp_draw = ImageDraw.Draw(temp_img)
                    
                    if is_mincho_bold:
                        offsets = [(0, 0), (1, 0), (0, 1), (1, 1)]
                        for dx, dy in offsets:
                            temp_draw.text((temp_size // 2 + dx, temp_size // 2 + dy), char, fill=text_color, font=font, anchor="mm")
                    else:
                        temp_draw.text((temp_size // 2, temp_size // 2), char, fill=text_color, font=font, anchor="mm")
                    
                    bbox = temp_draw.textbbox((0, 0), char, font=font)
                    original_char_width = bbox[2] - bbox[0]
                    scaled_char_width = original_char_width * aspect_ratio
                    
                    if aspect_ratio != 1.0:
                        new_width = int(temp_img.width * aspect_ratio)
                        temp_img = temp_img.resize((new_width, temp_img.height), Image.Resampling.LANCZOS)
                    
                    bbox_img = temp_img.getbbox()
                    if bbox_img:
                        cropped = temp_img.crop(bbox_img)
                        paste_x = int(current_x + bbox_img[0])
                        paste_y = int(current_y - temp_img.height // 2 + bbox_img[1])
                        
                        if char_idx == 0:
                            first_char_left_edge = paste_x
                        
                        img.paste(cropped, (paste_x, paste_y), cropped)
                        current_x += scaled_char_width + char_spacing
                    else:
                        current_x += scaled_char_width + char_spacing
                        if char_idx == 0:
                            first_char_left_edge = current_x
                
                if first_char_left_edge is not None:
                    icon_x_pos = int(first_char_left_edge - icon_size - 5)
                else:
                    icon_x_pos = text_x - icon_size - 5
            else:
                draw_text_bold(draw, (text_x, current_y), text_content, font, text_color, "lm", is_mincho_bold)
                icon_x_pos = text_x - icon_size - 5
            
            icon_y_pos = current_y - icon_size // 2
            
            if icon_img:
                img.paste(icon_img, (icon_x_pos, icon_y_pos), icon_img)
        
        for elem in annotation_elements:
            if elem.get('enabled', True):
                font_annot = get_font(elem['font'], elem.get('weight', 'W7'), elem['size'])
                is_mincho_bold_annot = elem['font'] == "明朝" and elem.get('weight', 'W7') in ["W7", "W8", "W9"]
                draw_text_bold(draw, (elem['x'], elem['y']), elem['text'], font_annot, elem['color'], "lm", is_mincho_bold_annot)
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        frames.append(buffer.getvalue())
    
    return frames

def save_apng(frames, num_frames, num_plays=4):
    frame_delay = 1000 // num_frames
    apng_obj = APNG()
    for frame_data in frames:
        apng_obj.append_file(io.BytesIO(frame_data), delay=frame_delay)
    apng_obj.num_plays = num_plays
    output = io.BytesIO()
    apng_obj.save(output)
    output.seek(0)
    return output.getvalue()

def create_preview_image(text_elements, annotation_elements, uploaded_image, image_config, template_type, scale=0.5, **kwargs):
    preview_width = int(WIDTH * scale)
    preview_height = int(HEIGHT * scale)
    
    img = Image.new('RGB', (preview_width, preview_height), 'white')
    draw = ImageDraw.Draw(img)
    
    if uploaded_image is not None and image_config is not None:
        img_scale = image_config.get('scale', 1.0)
        original_width = image_config.get('original_width', 100)
        original_height = image_config.get('original_height', 100)
        
        img_width = int(original_width * img_scale * scale)
        img_height = int(original_height * img_scale * scale)
        img_x = int(image_config.get('x', WIDTH // 2) * scale)
        img_y = int(image_config.get('y', HEIGHT // 2) * scale)
        
        resized_img = uploaded_image.resize((img_width, img_height), Image.Resampling.LANCZOS)
        paste_x = img_x - img_width // 2
        paste_y = img_y - img_height // 2
        
        if uploaded_image.mode == 'RGBA':
            img.paste(resized_img, (paste_x, paste_y), resized_img)
        else:
            img.paste(resized_img, (paste_x, paste_y))
    
    if template_type == "赤枠点滅":
        border_width = max(1, int(kwargs.get('border_width', 13) * scale))
        border_color = kwargs.get('border_color', 'red')
        color_map = {"red": "#FF0000", "blue": "#0000FF", "green": "#00FF00", "black": "#000000", "orange": "#FF6600"}
        draw.rectangle([0, 0, preview_width-1, preview_height-1], outline=color_map.get(border_color, "#FF0000"), width=border_width)
    
    elif template_type == "4隅アイコン点滅":
        icon_size = int(kwargs.get('icon_size', 85) * scale)
        icon_name = kwargs.get('icon_name', 'check.png')
        icon_img = load_icon_image(icon_name, icon_size)
        
        if icon_img:
            positions = [(10, 10), (preview_width - icon_size - 10, 10),
                        (10, preview_height - icon_size - 10), (preview_width - icon_size - 10, preview_height - icon_size - 10)]
            for pos in positions:
                img.paste(icon_img, pos, icon_img)
    
    elif template_type == "アイコン増加":
        icon_text_config = text_elements[0]
        text_content = icon_text_config.get('text', 'サンプルテキスト').replace('\n', '')
        text_font_type = icon_text_config.get('font', 'ゴシック')
        text_weight = icon_text_config.get('weight', 'W7')
        text_size = int(icon_text_config.get('icon_size', 40) * scale)
        text_color = icon_text_config.get('color', '#000000')
        text_x = int(icon_text_config.get('icon_x', 74) * scale)
        text_y_base = int(icon_text_config.get('icon_y', 320) * scale)
        char_spacing = int(icon_text_config.get('icon_char_spacing', 0) * scale)
        aspect_ratio = icon_text_config.get('icon_aspect_ratio', 1.0)
        row_spacing = int(icon_text_config.get('icon_row_spacing', 62) * scale)
        
        icon_size_val = int(kwargs.get('icon_size', 60) * scale)
        icon_name = kwargs.get('icon_name', 'check.png')
        
        is_mincho_bold = text_font_type == "明朝" and text_weight in ["W7", "W8", "W9"]
        
        num_lines = 5
        start_y = text_y_base - ((num_lines - 1) * row_spacing)
        
        icon_img = load_icon_image(icon_name, icon_size_val)
        font = get_font(text_font_type, text_weight, text_size)
        
        for line_idx in range(num_lines):
            current_y = start_y + (line_idx * row_spacing)
            
            if char_spacing != 0 or aspect_ratio != 1.0:
                first_char_left_edge = None
                current_x = text_x
                
                for char_idx, char in enumerate(text_content):
                    temp_size = int(font.size * 3)
                    temp_img = Image.new('RGBA', (temp_size, temp_size), (255, 255, 255, 0))
                    temp_draw = ImageDraw.Draw(temp_img)
                    
                    if is_mincho_bold:
                        offsets = [(0, 0), (1, 0), (0, 1), (1, 1)]
                        for dx, dy in offsets:
                            temp_draw.text((temp_size // 2 + dx, temp_size // 2 + dy), char, fill=text_color, font=font, anchor="mm")
                    else:
                        temp_draw.text((temp_size // 2, temp_size // 2), char, fill=text_color, font=font, anchor="mm")
                    
                    bbox_text = temp_draw.textbbox((0, 0), char, font=font)
                    original_char_width = bbox_text[2] - bbox_text[0]
                    scaled_char_width = original_char_width * aspect_ratio
                    
                    if aspect_ratio != 1.0:
                        new_width = int(temp_img.width * aspect_ratio)
                        temp_img = temp_img.resize((new_width, temp_img.height), Image.Resampling.LANCZOS)
                    
                    bbox_img = temp_img.getbbox()
                    if bbox_img:
                        cropped = temp_img.crop(bbox_img)
                        paste_x = int(current_x + bbox_img[0])
                        paste_y = int(current_y - temp_img.height // 2 + bbox_img[1])
                        
                        if char_idx == 0:
                            first_char_left_edge = paste_x
                        
                        img.paste(cropped, (paste_x, paste_y), cropped)
                        current_x += scaled_char_width + char_spacing
                    else:
                        current_x += scaled_char_width + char_spacing
                        if char_idx == 0:
                            first_char_left_edge = current_x
                
                if first_char_left_edge is not None:
                    icon_x = int(first_char_left_edge - icon_size_val - int(5 * scale))
                else:
                    icon_x = text_x - icon_size_val - int(5 * scale)
            else:
                draw_text_bold(draw, (text_x, current_y), text_content, font, text_color, "lm", is_mincho_bold)
                icon_x = text_x - icon_size_val - int(5 * scale)
            
            icon_y = current_y - icon_size_val // 2
            
            if icon_img:
                img.paste(icon_img, (icon_x, icon_y), icon_img)
    
    if template_type != "アイコン増加":
        for elem in text_elements:
            if elem.get('enabled', True):
                font = get_font(elem['font'], elem.get('weight', 'W7'), int(elem['size'] * scale))
                scaled_x = int(elem['x'] * scale)
                scaled_y = int(elem['y'] * scale)
                scaled_char_spacing = int(elem.get('char_spacing', 0) * scale)
                scaled_line_spacing = int(elem.get('line_spacing', 0) * scale)
                is_mincho_bold = elem['font'] == "明朝" and elem.get('weight', 'W7') in ["W7", "W8", "W9"]
                draw_text_with_spacing(img, draw, elem['text'], scaled_x, scaled_y, font, elem['color'],
                                     char_spacing=scaled_char_spacing,
                                     line_spacing=scaled_line_spacing,
                                     aspect_ratio=elem.get('aspect_ratio', 1.0),
                                     is_mincho_bold=is_mincho_bold)
    
    for elem in annotation_elements:
        if elem.get('enabled', True):
            font = get_font(elem['font'], elem.get('weight', 'W7'), int(elem['size'] * scale))
            is_mincho_bold = elem['font'] == "明朝" and elem.get('weight', 'W7') in ["W7", "W8", "W9"]
            draw_text_bold(draw, (int(elem['x'] * scale), int(elem['y'] * scale)), elem['text'], font, elem['color'], "lm", is_mincho_bold)
    
    return img

# メインアプリ
st.title("APNG Generator")

# セッション状態の初期化
if 'text_variations' not in st.session_state:
    st.session_state.text_variations = [{
        'text': 'サンプルテキスト',
        'font': 'ゴシック',
        'weight': 'W7',
        'size': 100,
        'color': '#000000',
        'char_spacing': 0,
        'line_spacing': 0,
        'aspect_ratio': 1.0,
        'x': WIDTH // 2,
        'y': HEIGHT // 2,
        'enabled': True,
        'icon_size': 40,
        'icon_x': 74,
        'icon_y': 320,
        'icon_char_spacing': 0,
        'icon_aspect_ratio': 1.0,
        'icon_row_spacing': 62
    }]

if 'annotation_variations' not in st.session_state:
    st.session_state.annotation_variations = [{
        'text': '※注釈テキスト',
        'font': 'ゴシック',
        'weight': 'W7',
        'size': 10,
        'color': '#000000',
        'x': 10,
        'y': 390,
        'enabled': True,
        'is_neumo': False
    }]

if 'image_variations' not in st.session_state:
    st.session_state.image_variations = [{
        'image': None,
        'original_width': 100,
        'original_height': 100,
        'scale': 1.0,
        'x': WIDTH // 2,
        'y': HEIGHT // 2
    }]

if 'use_red_border' not in st.session_state:
    st.session_state.use_red_border = True

if 'use_corner_icon' not in st.session_state:
    st.session_state.use_corner_icon = False

if 'use_icon_increase' not in st.session_state:
    st.session_state.use_icon_increase = False

# レイアウト：左右分割（比率調整）
col_settings, col_preview = st.columns([1.2, 1])

# ==========================================
# 左カラム：設定エリア（タブ化による整理）
# ==========================================
with col_settings:
    # タブの作成
    tab_template, tab_text, tab_image, tab_annot, tab_output = st.tabs([
        "テンプレート選択", "テキスト設定", "画像設定", "注釈設定", "出力・保存"
    ])
    
    # --- タブ1: テンプレート選択 ---
    with tab_template:
        st.markdown('<div class="simple-header">使用するテンプレート</div>', unsafe_allow_html=True)
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            use_red_border = st.checkbox("赤枠点滅", value=st.session_state.use_red_border, key="chk_red")
        with col_t2:
            use_corner_icon = st.checkbox("4隅アイコン", value=st.session_state.use_corner_icon, key="chk_corner")
        with col_t3:
            use_icon_increase = st.checkbox("アイコン増加", value=st.session_state.use_icon_increase, key="chk_increase")
        
        st.session_state.use_red_border = use_red_border
        st.session_state.use_corner_icon = use_corner_icon
        st.session_state.use_icon_increase = use_icon_increase
        
        st.markdown('<div class="simple-header">詳細パラメータ</div>', unsafe_allow_html=True)
        if use_red_border:
            st.caption("赤枠点滅の設定")
            col1, col2 = st.columns(2)
            with col1: border_width_red = st.slider("枠線の太さ", 1, 20, 13, key="border_width_red")
            with col2: border_colors = st.multiselect("枠線の色", ["red", "blue", "green", "black", "orange"], default=["red"], key="border_colors")
            col3, col4 = st.columns(2)
            with col3: num_frames_red = st.slider("フレーム数 (赤枠)", 5, 20, 5, key="num_frames_red")
            with col4: loop_count_red = st.selectbox("ループ数 (赤枠)", [1, 2, 3, 4], index=3, key="loop_count_red")
            st.divider()
        
        if use_corner_icon:
            st.caption("4隅アイコンの設定")
            col1, col2 = st.columns(2)
            with col1: icon_size_corner = st.slider("アイコンサイズ", 20, 150, 85, key="icon_size_corner")
            with col2: icon_names = st.multiselect("アイコン種類", ["check.png", "red_check.png", "！.png", "！？.png"], default=["check.png"], key="icon_names")
            col3, col4 = st.columns(2)
            with col3: num_frames_corner = st.slider("フレーム数 (4隅)", 5, 20, 5, key="num_frames_corner")
            with col4: loop_count_corner = st.selectbox("ループ数 (4隅)", [1, 2, 3, 4], index=3, key="loop_count_corner")
            st.divider()
        
        if use_icon_increase:
            st.caption("アイコン増加の設定")
            col1, col2 = st.columns(2)
            with col1: icon_size_increase = st.slider("アイコンサイズ(増)", 20, 100, 60, key="icon_size_increase")
            with col2: icon_names_increase = st.multiselect("アイコン種類(増)", ["check.png", "red_check.png", "！.png", "！？.png"], default=["check.png"], key="icon_names_increase")
            col3, col4 = st.columns(2)
            with col3: num_frames_increase = st.slider("フレーム数 (増加)", 3, 10, 5, key="num_frames_increase")
            with col4: loop_count_increase = st.selectbox("ループ数 (増加)", [1, 2, 3, 4], index=3, key="loop_count_increase")
    
    # --- タブ2: テキスト設定 ---
    with tab_text:
        # テキスト追加ボタンエリア
        col_add_btn, _ = st.columns([1, 2])
        with col_add_btn:
            if st.button("テキストを追加", key="tab_btn_add", use_container_width=True):
                st.session_state.text_variations.append({
                    'text': '新しいテキスト',
                    'font': 'ゴシック',
                    'weight': 'W7',
                    'size': 100,
                    'color': '#000000',
                    'char_spacing': 0,
                    'line_spacing': 0,
                    'aspect_ratio': 1.0,
                    'x': WIDTH // 2,
                    'y': HEIGHT // 2,
                    'enabled': True,
                    'icon_size': 40,
                    'icon_x': 74,
                    'icon_y': 320,
                    'icon_char_spacing': 0,
                    'icon_aspect_ratio': 1.0,
                    'icon_row_spacing': 62
                })
                st.session_state.selected_text_tab = len(st.session_state.text_variations) - 1
                st.rerun()

        # テキスト選択用ラジオボタン（横並び）
        text_options = [f"Text {i+1}" for i in range(len(st.session_state.text_variations))]
        selected_text_idx = st.radio("編集するテキストを選択", range(len(text_options)), format_func=lambda x: text_options[x], horizontal=True, index=st.session_state.get('selected_text_tab', 0))
        st.session_state.selected_text_tab = selected_text_idx
        
        text_var = st.session_state.text_variations[selected_text_idx]
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # テキスト入力と表示スイッチ
        col_txt_main, col_txt_sw = st.columns([4, 1])
        with col_txt_main:
            new_text = st.text_area("テキスト内容", value=text_var['text'], height=80, key=f"textarea_{selected_text_idx}", label_visibility="collapsed", placeholder="テキストを入力...")
            st.session_state.text_variations[selected_text_idx]['text'] = new_text
        with col_txt_sw:
            enabled = st.checkbox("表示", value=text_var.get('enabled', True), key=f"text_en_{selected_text_idx}")
            st.session_state.text_variations[selected_text_idx]['enabled'] = enabled
        
        # フォント設定など
        with st.expander("フォント・デザイン設定", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                font = st.selectbox("フォント", ["ゴシック", "明朝"],
                                    index=["ゴシック", "明朝"].index(text_var.get('font', 'ゴシック')),
                                   key=f"font_{selected_text_idx}")
                st.session_state.text_variations[selected_text_idx]['font'] = font
            with col2:
                weight = st.selectbox("ウェイト", ["W3", "W4", "W5", "W6", "W7", "W8", "W9"],
                                     index=["W3", "W4", "W5", "W6", "W7", "W8", "W9"].index(text_var.get('weight', 'W7')),
                                     key=f"weight_{selected_text_idx}")
                st.session_state.text_variations[selected_text_idx]['weight'] = weight
            
            col3, col4 = st.columns([2, 1])
            with col3:
                size = st.slider("サイズ", 50, 200, text_var.get('size', 100), key=f"size_{selected_text_idx}")
                st.session_state.text_variations[selected_text_idx]['size'] = size
            with col4:
                color = st.color_picker("色", text_var.get('color', '#000000'), key=f"color_{selected_text_idx}")
                st.session_state.text_variations[selected_text_idx]['color'] = color
            
            col5, col6, col7 = st.columns(3)
            with col5:
                char_spacing = st.slider("文字間", -10, 50, text_var.get('char_spacing', 0), key=f"char_{selected_text_idx}")
                st.session_state.text_variations[selected_text_idx]['char_spacing'] = char_spacing
            with col6:
                line_spacing = st.slider("行間", -10, 50, text_var.get('line_spacing', 0), key=f"line_{selected_text_idx}")
                st.session_state.text_variations[selected_text_idx]['line_spacing'] = line_spacing
            with col7:
                aspect_ratio = st.slider("縦横比", 50, 200, int(text_var.get('aspect_ratio', 1.0) * 100), key=f"aspect_{selected_text_idx}") / 100
                st.session_state.text_variations[selected_text_idx]['aspect_ratio'] = aspect_ratio

        # 位置設定
        with st.expander("位置調整", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                pos_x = st.slider("X座標", 0, WIDTH, text_var.get('x', WIDTH // 2), key=f"x_{selected_text_idx}")
                st.session_state.text_variations[selected_text_idx]['x'] = pos_x
            with col2:
                pos_y = st.slider("Y座標", 0, HEIGHT, text_var.get('y', HEIGHT // 2), key=f"y_{selected_text_idx}")
                st.session_state.text_variations[selected_text_idx]['y'] = pos_y
            
            if st.button("中央に配置", key=f"center_{selected_text_idx}", use_container_width=True):
                st.session_state.text_variations[selected_text_idx]['x'] = WIDTH // 2
                st.session_state.text_variations[selected_text_idx]['y'] = HEIGHT // 2
                st.rerun()

        # アイコン増加専用
        if use_icon_increase:
            with st.expander("アイコン増加専用設定", expanded=True):
                st.caption("※ アイコン増加テンプレート使用時のみ有効")
                col1, col2 = st.columns(2)
                with col1:
                    icon_size = st.slider("文字サイズ", 20, 80, text_var.get('icon_size', 40), key=f"icon_size_{selected_text_idx}")
                    st.session_state.text_variations[selected_text_idx]['icon_size'] = icon_size
                    icon_char_spacing = st.slider("文字間", -10, 50, text_var.get('icon_char_spacing', 0), key=f"icon_char_{selected_text_idx}")
                    st.session_state.text_variations[selected_text_idx]['icon_char_spacing'] = icon_char_spacing
                with col2:
                    icon_row_spacing = st.slider("行間隔", 30, 100, text_var.get('icon_row_spacing', 50), key=f"icon_row_{selected_text_idx}")
                    st.session_state.text_variations[selected_text_idx]['icon_row_spacing'] = icon_row_spacing
                    icon_x = st.slider("開始X座標", 0, WIDTH, text_var.get('icon_x', 120), key=f"icon_x_{selected_text_idx}")
                    st.session_state.text_variations[selected_text_idx]['icon_x'] = icon_x
                    icon_y = st.slider("開始Y座標", 0, HEIGHT, text_var.get('icon_y', 300), key=f"icon_y_{selected_text_idx}")
                    st.session_state.text_variations[selected_text_idx]['icon_y'] = icon_y

        # 削除ボタン
        if len(st.session_state.text_variations) > 1:
            st.markdown("<hr style='margin: 10px 0; border-color: #333;'>", unsafe_allow_html=True)
            if st.button("このテキスト設定を削除", key=f"del_{selected_text_idx}", use_container_width=True):
                st.session_state.text_variations.pop(selected_text_idx)
                st.session_state.selected_text_tab = max(0, selected_text_idx - 1)
                st.rerun()

    # --- タブ3: 画像設定 ---
    with tab_image:
        st.markdown('<div class="simple-header">画像のアップロードと調整</div>', unsafe_allow_html=True)
        for var_idx, img_var in enumerate(st.session_state.image_variations):
            uploaded_file = st.file_uploader(
                "画像を選択", 
                type=['png', 'jpg', 'jpeg', 'webp'],
                key=f"img_{var_idx}"
            )
            
            if uploaded_file is not None:
                uploaded_img = Image.open(uploaded_file)
                st.session_state.image_variations[var_idx]['image'] = uploaded_img
                
                if st.session_state.image_variations[var_idx]['original_width'] == 100:
                    st.session_state.image_variations[var_idx]['original_width'] = uploaded_img.width
                    st.session_state.image_variations[var_idx]['original_height'] = uploaded_img.height
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    img_scale = st.slider("サイズ倍率", 10, 200, int(img_var.get('scale', 1.0) * 100), key=f"img_scale_{var_idx}") / 100
                    st.session_state.image_variations[var_idx]['scale'] = img_scale
                with col2:
                    pos_x = st.slider("X座標", 0, WIDTH, img_var.get('x', WIDTH // 2), key=f"img_x_{var_idx}")
                    st.session_state.image_variations[var_idx]['x'] = pos_x
                with col3:
                    pos_y = st.slider("Y座標", 0, HEIGHT, img_var.get('y', HEIGHT // 2), key=f"img_y_{var_idx}")
                    st.session_state.image_variations[var_idx]['y'] = pos_y

    # --- タブ4: 注釈設定 ---
    with tab_annot:
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("＋ 通常注釈追加", use_container_width=True):
                st.session_state.annotation_variations.append({
                    'text': '新しい注釈', 'font': 'ゴシック', 'weight': 'W7', 'size': 10,
                    'color': '#000000', 'x': 10, 'y': 390, 'enabled': True, 'is_neumo': False
                })
                st.rerun()
        with col_btn2:
            if st.button("＋ ニューモV専用追加", use_container_width=True):
                st.session_state.annotation_variations.append({
                    'text': '※初回限定500円（税込）', 'font': 'ゴシック', 'weight': 'W7', 'size': 10,
                    'color': '#000000', 'x': 10, 'y': 390, 'enabled': True, 'is_neumo': True
                })
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)

        # 注釈リストループ
        for var_idx, annot_var in enumerate(st.session_state.annotation_variations):
            st.markdown(f'<div class="annotation-item">', unsafe_allow_html=True)
            
            col_head_title, col_head_sw = st.columns([3, 1])
            with col_head_title:
                title_text = "ニューモV専用注釈" if annot_var.get('is_neumo', False) else f"注釈 #{var_idx + 1}"
                st.markdown(f"**{title_text}**")
            with col_head_sw:
                enabled = st.toggle("有効", value=annot_var['enabled'], key=f"annot_en_{var_idx}")
                st.session_state.annotation_variations[var_idx]['enabled'] = enabled

            col1, col2 = st.columns([3, 1])
            with col1:
                new_text = st.text_input("テキスト内容", value=annot_var['text'], key=f"annot_{var_idx}", label_visibility="collapsed")
                st.session_state.annotation_variations[var_idx]['text'] = new_text
            with col2:
                if len(st.session_state.annotation_variations) > 1:
                    if st.button("削除", key=f"del_annot_{var_idx}", use_container_width=True):
                        st.session_state.annotation_variations.pop(var_idx)
                        st.rerun()

            col3, col4, col5, col6 = st.columns(4)
            with col3:
                font = st.selectbox("フォント", ["ゴシック", "明朝"],
                                    index=["ゴシック", "明朝"].index(annot_var.get('font', 'ゴシック')),
                                   key=f"annot_font_{var_idx}")
                st.session_state.annotation_variations[var_idx]['font'] = font
            with col4:
                size = st.number_input("サイズ", 5, 100, annot_var.get('size', 10), key=f"annot_size_{var_idx}")
                st.session_state.annotation_variations[var_idx]['size'] = size
            with col5:
                pos_x = st.number_input("X", 0, WIDTH, annot_var.get('x', 10), key=f"annot_x_{var_idx}")
                st.session_state.annotation_variations[var_idx]['x'] = pos_x
            with col6:
                pos_y = st.number_input("Y", 0, HEIGHT, annot_var.get('y', 390), key=f"annot_y_{var_idx}")
                st.session_state.annotation_variations[var_idx]['y'] = pos_y
            
            st.markdown('</div>', unsafe_allow_html=True)

    # --- タブ5: 出力設定 ---
    with tab_output:
        col_name1, col_name2 = st.columns(2)
        with col_name1:
            product_name = st.text_input("商材名", value="商材名", placeholder="商材名を入力")
        with col_name2:
            custom_name = st.text_input("ファイル識別名", value="名前", placeholder="識別名を入力")
        
        st.caption(f"出力例: {datetime.now().strftime('%y%m%d')}_{product_name}_APNG_枠点滅_素材_{custom_name}_01.png")
        
        has_neumo_annot = any(annot.get('is_neumo', False) for annot in st.session_state.annotation_variations)
        if has_neumo_annot:
            st.info("ニューモV専用注釈が含まれているため、一部ファイルの商材名は「new5」になります。")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 生成ボタン
        if st.button("APNGを一括生成する", type="primary", disabled=not (use_red_border or use_corner_icon or use_icon_increase), use_container_width=True):
            generated_files = []
            date_str = datetime.now().strftime("%y%m%d")
            
            # パラメータ取得（デフォルト値付き）
            border_width_red = st.session_state.get('border_width_red', 13)
            border_colors = st.session_state.get('border_colors', ["red"])
            num_frames_red = st.session_state.get('num_frames_red', 5)
            loop_count_red = st.session_state.get('loop_count_red', 4)
            
            icon_size_corner = st.session_state.get('icon_size_corner', 85)
            icon_names = st.session_state.get('icon_names', ["check.png"])
            num_frames_corner = st.session_state.get('num_frames_corner', 5)
            loop_count_corner = st.session_state.get('loop_count_corner', 4)
            
            icon_size_increase = st.session_state.get('icon_size_increase', 60)
            icon_names_increase = st.session_state.get('icon_names_increase', ["check.png"])
            num_frames_increase = st.session_state.get('num_frames_increase', 5)
            loop_count_increase = st.session_state.get('loop_count_increase', 4)
            
            enabled_annotations = [annot for annot in st.session_state.annotation_variations if annot.get('enabled', True)]
            enabled_texts = [text for text in st.session_state.text_variations if text.get('enabled', True)]
            
            if len(enabled_annotations) == 0:
                st.error("有効な注釈がありません。注釈リストでスイッチをONにしてください。")
            elif len(enabled_texts) == 0:
                st.error("有効なテキストがありません。テキスト設定でスイッチをONにしてください。")
            else:
                with st.spinner("APNGを生成中..."):
                    for annot_var in enabled_annotations:
                        prod_name = "new5" if annot_var.get('is_neumo', False) else product_name
                        
                        border_counter = 1
                        icon_counter = 1
                        increase_counter = 1
                        
                        for text_var in enabled_texts:
                            for img_idx in range(len(st.session_state.image_variations)):
                                variant_text_elements = [text_var]
                                variant_annotation_elements = [annot_var]
                                variant_uploaded_image = st.session_state.image_variations[img_idx]['image']
                                variant_image_config = st.session_state.image_variations[img_idx]
                                
                                # 赤枠点滅生成
                                if use_red_border:
                                    for border_color in border_colors:
                                        frames = create_red_border_blink_frames(
                                            WIDTH, HEIGHT, variant_text_elements, variant_annotation_elements,
                                            variant_uploaded_image, variant_image_config,
                                            border_width=border_width_red, 
                                            border_color=border_color, 
                                            num_frames=num_frames_red
                                        )
                                        apng_data = save_apng(frames, num_frames=num_frames_red, num_plays=loop_count_red)
                                        filename = f"{date_str}_{prod_name}_APNG_枠点滅_素材_{custom_name}_{border_counter:02d}.png"
                                        generated_files.append((filename, apng_data))
                                        border_counter += 1
                                
                                # 4隅アイコン生成
                                if use_corner_icon:
                                    for icon_name in icon_names:
                                        frames = create_corner_icon_blink_frames(
                                            WIDTH, HEIGHT, variant_text_elements, variant_annotation_elements,
                                            variant_uploaded_image, variant_image_config,
                                            icon_name=icon_name,
                                            icon_size=icon_size_corner,
                                            num_frames=num_frames_corner
                                        )
                                        apng_data = save_apng(frames, num_frames=num_frames_corner, num_plays=loop_count_corner)
                                        filename = f"{date_str}_{prod_name}_APNG_ikon点滅_素材_{custom_name}_{icon_counter:02d}.png"
                                        generated_files.append((filename, apng_data))
                                        icon_counter += 1
                                
                                # アイコン増加生成
                                if use_icon_increase:
                                    for icon_name in icon_names_increase:
                                        frames = create_icon_increase_frames(
                                            WIDTH, HEIGHT, text_var, variant_annotation_elements,
                                            variant_uploaded_image, variant_image_config,
                                            icon_name=icon_name,
                                            icon_size=icon_size_increase,
                                            num_frames=num_frames_increase
                                        )
                                        apng_data = save_apng(frames, num_frames=num_frames_increase, num_plays=loop_count_increase)
                                        filename = f"{date_str}_{prod_name}_APNG_ikon増加_素材_{custom_name}_{increase_counter:02d}.png"
                                        generated_files.append((filename, apng_data))
                                        increase_counter += 1
                    
                    st.success(f"{len(generated_files)}個のAPNGが完成しました！")
                    
                    # ZIPダウンロードボタン
                    if len(generated_files) > 0:
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                            for filename, data in generated_files:
                                zip_file.writestr(filename, data)
                        
                        zip_buffer.seek(0)
                        st.download_button(
                            label=f"まとめてZIPでダウンロード ({len(generated_files)}個)",
                            data=zip_buffer.getvalue(),
                            file_name=f"{date_str}_{product_name}_APNG_all.zip",
                            mime="application/zip",
                            use_container_width=True,
                            type="primary"
                        )

                    # 個別リスト
                    with st.expander("個別ファイルダウンロード", expanded=False):
                        for file_idx, (filename, data) in enumerate(generated_files):
                            file_size_kb = len(data) / 1024
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.text(f"{filename} ({file_size_kb:.1f} KB)")
                            with col2:
                                st.download_button("DL", data=data, file_name=filename, mime="image/png", key=f"dl_{file_idx}", use_container_width=True)

# ==========================================
# 右カラム：プレビューエリア（Sticky）
# ==========================================
with col_preview:
    st.markdown('<div class="preview-box">', unsafe_allow_html=True)
    st.markdown("### PREVIEW")
    st.caption("設定変更はリアルタイムに反映されます")
    
    preview_annotation_elements = [annot for annot in st.session_state.annotation_variations if annot['enabled']]
    
    preview_count = sum([use_red_border, use_corner_icon, use_icon_increase])
    
    if preview_count == 0:
        st.warning("左側の「テンプレート選択」タブで作成したい種類を選択してください")
    else:
        enabled_text_variations = [tv for tv in st.session_state.text_variations if tv.get('enabled', True)]
        
        # 赤枠点滅プレビュー
        if use_red_border:
            st.markdown("##### 赤枠点滅")
            cols = st.columns(2) # プレビューを少し大きく見せるため2列に変更
            for idx, text_var in enumerate(enabled_text_variations):
                with cols[idx % 2]:
                    st.caption(f"Text {st.session_state.text_variations.index(text_var) + 1}")
                    preview_img = create_preview_image(
                        [text_var], preview_annotation_elements,
                        st.session_state.image_variations[0]['image'],
                        st.session_state.image_variations[0],
                        "赤枠点滅", scale=0.5, border_width=13, border_color="red"
                    )
                    st.image(preview_img, use_container_width=True)
        
        # 4隅アイコンプレビュー
        if use_corner_icon:
            st.markdown("##### 4隅アイコン")
            cols = st.columns(2)
            for idx, text_var in enumerate(enabled_text_variations):
                with cols[idx % 2]:
                    st.caption(f"Text {st.session_state.text_variations.index(text_var) + 1}")
                    preview_img = create_preview_image(
                        [text_var], preview_annotation_elements,
                        st.session_state.image_variations[0]['image'],
                        st.session_state.image_variations[0],
                        "4隅アイコン点滅", scale=0.5, icon_size=85, icon_name="check.png"
                    )
                    st.image(preview_img, use_container_width=True)
        
        # アイコン増加プレビュー
        if use_icon_increase:
            st.markdown("##### アイコン増加")
            current_icon_size = st.session_state.get('icon_size_increase', 60)
            current_icon_names = st.session_state.get('icon_names_increase', ["check.png"])
            preview_icon_name = current_icon_names[0] if current_icon_names else "check.png"
            
            cols = st.columns(2)
            for idx, text_var in enumerate(enabled_text_variations):
                with cols[idx % 2]:
                    st.caption(f"Text {st.session_state.text_variations.index(text_var) + 1}")
                    preview_img = create_preview_image(
                        [text_var], preview_annotation_elements,
                        st.session_state.image_variations[0]['image'],
                        st.session_state.image_variations[0],
                        "アイコン増加", 
                        scale=0.5, 
                        icon_size=current_icon_size,
                        icon_name=preview_icon_name
                    )
                    st.image(preview_img, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)