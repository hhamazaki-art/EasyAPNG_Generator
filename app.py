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

# モダンなダークモードCSS
st.markdown("""
<style>
    /* グローバル設定 */
    * {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* 背景 */
    .stApp {
        background-color: #0a0a0a;
        color: #e8e8e8;
    }
    
    /* メインコンテナ */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 100%;
    }
    
    /* タイトル */
    h1 {
        font-size: 28px;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    h2, h3 {
        font-size: 16px;
        font-weight: 600;
        color: #ffffff;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    /* 入力フィールド */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background-color: #1a1a1a;
        color: #e8e8e8;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 14px;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #4a4a4a;
        box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.05);
    }
    
    /* セレクトボックス */
    .stSelectbox > div > div {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
    }
    
    /* スライダー */
    .stSlider {
        padding: 0;
    }
    
    .stSlider > div > div > div > div {
        background-color: #2a2a2a;
    }
    
    .stSlider > div > div > div > div > div {
        background-color: #ffffff;
    }
    
    /* カラーピッカー */
    .stColorPicker > div > div {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
    }
    
    /* チェックボックス */
    .stCheckbox {
        color: #e8e8e8;
    }
    
    .stCheckbox > label {
        font-size: 14px;
        font-weight: 500;
    }
    
    /* ボタン */
    .stButton > button {
        background-color: #1a1a1a;
        color: #e8e8e8;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #252525;
        border-color: #3a3a3a;
    }
    
    /* プライマリボタン */
    .stButton > button[kind="primary"] {
        background-color: #ffffff;
        color: #0a0a0a;
        border: none;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #f0f0f0;
    }
    
    /* セカンダリボタン */
    .stButton > button[kind="secondary"] {
        background-color: transparent;
        border: 1px solid #2a2a2a;
    }
    
    /* エキスパンダー */
    .streamlit-expanderHeader {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
    }
    
    .streamlit-expanderContent {
        background-color: transparent;
        border: none;
    }
    
    /* セクション */
    .section-title {
        font-size: 14px;
        font-weight: 600;
        color: #a0a0a0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 16px;
    }
    
    /* プレビューエリア */
    .preview-container {
        background-color: #0f0f0f;
        border: 1px solid #1a1a1a;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .preview-label {
        font-size: 12px;
        color: #808080;
        margin-bottom: 8px;
    }
    
    /* スクロールバー */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #2a2a2a;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #3a3a3a;
    }
    
    /* キャプション */
    .stCaption {
        color: #808080;
        font-size: 12px;
    }
    
    /* Info/Warning */
    .stAlert {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# グローバル設定
WIDTH = 600
HEIGHT = 400
FRAME_DELAY = 100

# 日本語フォント読み込み関数（明朝太字対応・疑似太字版）
def get_font(font_type="ゴシック", weight="W7", size=40):
    """日本語フォントを取得（明朝ウェイト対応）"""
    font_paths = []
    
    if font_type == "ゴシック":
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
        # 明朝は全ウェイトで同じフォントを使用
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
        except:
            continue
    
    return ImageFont.load_default()

# 明朝太字用の疑似太字描画関数
def draw_text_bold(draw, position, text, font, fill, anchor="mm", is_mincho_bold=False):
    """明朝W7以上の場合、疑似太字で描画"""
    x, y = position
    
    if is_mincho_bold:
        # 疑似太字：少しずらして4回描画
        offsets = [(0, 0), (1, 0), (0, 1), (1, 1)]
        for dx, dy in offsets:
            draw.text((x + dx, y + dy), text, fill=fill, font=font, anchor=anchor)
    else:
        draw.text((x, y), text, fill=fill, font=font, anchor=anchor)

# アイコン画像の読み込み
def load_icon_image(icon_name, size):
    """アイコン画像を読み込む"""
    icon_path = f"icons/{icon_name}"
    if os.path.exists(icon_path):
        icon = Image.open(icon_path).convert("RGBA")
        icon = icon.resize((size, size), Image.Resampling.LANCZOS)
        return icon
    return None

# 文字間・行間・縦横比対応テキスト描画関数（明朝太字対応）
def draw_text_with_spacing(img, draw, text, x, y, font, color, char_spacing=0, line_spacing=0, aspect_ratio=1.0, is_mincho_bold=False):
    """文字間・行間・縦横比を考慮したテキスト描画（位置固定）"""
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
                
                # 明朝太字の場合、疑似太字で描画
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

# テンプレート関数：赤枠点滅（明朝太字対応）
def create_red_border_blink_frames(width, height, text_elements, annotation_elements, uploaded_image, image_config, border_width=13, border_color="red", num_frames=5):
    """赤枠が点滅するテンプレート"""
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

# テンプレート関数：4隅アイコン点滅（明朝太字対応）
def create_corner_icon_blink_frames(width, height, text_elements, annotation_elements, uploaded_image, image_config, icon_name="check.png", icon_size=85, num_frames=5):
    """4隅にアイコンが点滅するテンプレート"""
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

# テンプレート関数：アイコン増加（スペース完全解消版）
def create_icon_increase_frames(width, height, icon_text_config, annotation_elements, uploaded_image, image_config, icon_name="check.png", icon_size=60, num_frames=5):
    """アイコン+テキストが下から増えていくテンプレート（1文字目基準・改行禁止）"""
    frames = []
    
    text_content = icon_text_config.get('text', 'サンプルテキスト').replace('\n', '')
    text_font_type = icon_text_config.get('font', 'ゴシック')
    text_weight = icon_text_config.get('weight', 'W7')
    text_size = icon_text_config.get('icon_size', 40)
    text_color = icon_text_config.get('color', '#000000')
    text_x = icon_text_config.get('icon_x', 120)
    text_y_base = icon_text_config.get('icon_y', 300)
    char_spacing = icon_text_config.get('icon_char_spacing', 0)
    aspect_ratio = icon_text_config.get('icon_aspect_ratio', 1.0)
    row_spacing = icon_text_config.get('icon_row_spacing', 50)
    
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
            
            # アイコン位置（テキストの左5px）
            icon_x_pos = text_x - icon_size - 5
            icon_y_pos = current_y - icon_size // 2
            
            if icon_img:
                img.paste(icon_img, (icon_x_pos, icon_y_pos), icon_img)
            
            # テキスト描画（aspect_ratioに関わらず左端をtext_xに固定）
            if char_spacing != 0 or aspect_ratio != 1.0:
                current_x = text_x  # 常にtext_xから開始
                
                for char in text_content:
                    temp_size = int(font.size * 3)
                    temp_img = Image.new('RGBA', (temp_size, temp_size), (255, 255, 255, 0))
                    temp_draw = ImageDraw.Draw(temp_img)
                    
                    # 明朝太字の場合、疑似太字で描画
                    if is_mincho_bold:
                        offsets = [(0, 0), (1, 0), (0, 1), (1, 1)]
                        for dx, dy in offsets:
                            temp_draw.text((temp_size // 2 + dx, temp_size // 2 + dy), char, fill=text_color, font=font, anchor="mm")
                    else:
                        temp_draw.text((temp_size // 2, temp_size // 2), char, fill=text_color, font=font, anchor="mm")
                    
                    # 元の文字幅を取得
                    bbox = temp_draw.textbbox((0, 0), char, font=font)
                    original_char_width = bbox[2] - bbox[0]
                    
                    if aspect_ratio != 1.0:
                        new_width = int(temp_img.width * aspect_ratio)
                        temp_img = temp_img.resize((new_width, temp_img.height), Image.Resampling.LANCZOS)
                    
                    # 左端基準で貼り付け（anchor="lm"相当）
                    paste_x = int(current_x)
                    paste_y = int(current_y - temp_img.height // 2)
                    img.paste(temp_img, (paste_x, paste_y), temp_img)
                    
                    # 次の文字位置を計算（縦横比適用後の幅）
                    char_width = original_char_width * aspect_ratio
                    current_x += char_width + char_spacing
            else:
                draw_text_bold(draw, (text_x, current_y), text_content, font, text_color, "lm", is_mincho_bold)
        
        for elem in annotation_elements:
            if elem.get('enabled', True):
                font_annot = get_font(elem['font'], elem.get('weight', 'W7'), elem['size'])
                is_mincho_bold_annot = elem['font'] == "明朝" and elem.get('weight', 'W7') in ["W7", "W8", "W9"]
                draw_text_bold(draw, (elem['x'], elem['y']), elem['text'], font_annot, elem['color'], "lm", is_mincho_bold_annot)
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        frames.append(buffer.getvalue())
    
    return frames

# APNG保存関数
def save_apng(frames, frame_delay=FRAME_DELAY, num_plays=4):
    """フレームからAPNGファイルを作成"""
    apng_obj = APNG()
    for frame_data in frames:
        apng_obj.append_file(io.BytesIO(frame_data), delay=frame_delay)
    apng_obj.num_plays = num_plays
    output = io.BytesIO()
    apng_obj.save(output)
    output.seek(0)
    return output.getvalue()

# プレビュー画像生成（サイズ縮小版・明朝太字対応）
def create_preview_image(text_elements, annotation_elements, uploaded_image, image_config, template_type, scale=0.5, **kwargs):
    """プレビュー用の1フレーム静止画を生成（縮小版）"""
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
        text_x = int(icon_text_config.get('icon_x', 120) * scale)
        text_y_base = int(icon_text_config.get('icon_y', 300) * scale)
        char_spacing = int(icon_text_config.get('icon_char_spacing', 0) * scale)
        aspect_ratio = icon_text_config.get('icon_aspect_ratio', 1.0)
        row_spacing = int(icon_text_config.get('icon_row_spacing', 50) * scale)
        
        icon_size_val = int(kwargs.get('icon_size', 60) * scale)
        icon_name = kwargs.get('icon_name', 'check.png')
        
        is_mincho_bold = text_font_type == "明朝" and text_weight in ["W7", "W8", "W9"]
        
        num_lines = 5
        start_y = text_y_base - ((num_lines - 1) * row_spacing)
        
        icon_img = load_icon_image(icon_name, icon_size_val)
        font = get_font(text_font_type, text_weight, text_size)
        
        for line_idx in range(num_lines):
            current_y = start_y + (line_idx * row_spacing)
            
            icon_x = text_x - icon_size_val - int(5 * scale)
            icon_y = current_y - icon_size_val // 2
            
            if icon_img:
                img.paste(icon_img, (icon_x, icon_y), icon_img)
            
            if char_spacing != 0 or aspect_ratio != 1.0:
                current_x = text_x
                
                for char in text_content:
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
                    
                    if aspect_ratio != 1.0:
                        new_width = int(temp_img.width * aspect_ratio)
                        temp_img = temp_img.resize((new_width, temp_img.height), Image.Resampling.LANCZOS)
                    
                    img.paste(temp_img, (int(current_x), int(current_y - temp_img.height // 2)), temp_img)
                    
                    char_width = original_char_width * aspect_ratio
                    current_x += char_width + char_spacing
            else:
                draw_text_bold(draw, (text_x, current_y), text_content, font, text_color, "lm", is_mincho_bold)
    
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
        'icon_x': 120,
        'icon_y': 300,
        'icon_char_spacing': 0,
        'icon_aspect_ratio': 1.0,
        'icon_row_spacing': 50
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

# レイアウト：左右分割
col_settings, col_preview = st.columns([1, 1])

with col_settings:
    # テンプレート選択
    st.markdown('<div class="section-title">TEMPLATE</div>', unsafe_allow_html=True)
    
    use_red_border = st.checkbox("赤枠点滅", value=st.session_state.use_red_border, key="chk_red")
    use_corner_icon = st.checkbox("4隅アイコン点滅", value=st.session_state.use_corner_icon, key="chk_corner")
    use_icon_increase = st.checkbox("アイコン増加", value=st.session_state.use_icon_increase, key="chk_increase")
    
    st.session_state.use_red_border = use_red_border
    st.session_state.use_corner_icon = use_corner_icon
    st.session_state.use_icon_increase = use_icon_increase
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # テキストバリエーション
    st.markdown('<div class="section-title">TEXT</div>', unsafe_allow_html=True)
    
    # タブボタン（+を見やすく）
    num_tabs = len(st.session_state.text_variations)
    cols_per_row = 4
    
    for row_start in range(0, num_tabs + 1, cols_per_row):
        row_end = min(row_start + cols_per_row, num_tabs + 1)
        tab_cols = st.columns(cols_per_row)
        
        for idx in range(row_start, row_end):
            col_idx = idx - row_start
            
            if idx == num_tabs:
                # +ボタン
                with tab_cols[col_idx]:
                    if st.button("+ 追加", key=f"tab_btn_add", use_container_width=True):
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
                            'icon_x': 120,
                            'icon_y': 300,
                            'icon_char_spacing': 0,
                            'icon_aspect_ratio': 1.0,
                            'icon_row_spacing': 50
                        })
                        st.session_state.selected_text_tab = len(st.session_state.text_variations) - 1
                        st.rerun()
            else:
                # 通常のタブボタン
                selected_tab = st.session_state.get('selected_text_tab', 0)
                with tab_cols[col_idx]:
                    btn_type = "primary" if selected_tab == idx else "secondary"
                    if st.button(f"テキスト {idx + 1}", key=f"tab_btn_{idx}", type=btn_type, use_container_width=True):
                        st.session_state.selected_text_tab = idx
                        st.rerun()
    
    # 選択中のタブの内容
    selected_tab = st.session_state.get('selected_text_tab', 0)
    if selected_tab < len(st.session_state.text_variations):
        text_var = st.session_state.text_variations[selected_tab]
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        new_text = st.text_area("テキスト内容", value=text_var['text'], height=80, key=f"textarea_{selected_tab}", label_visibility="collapsed", placeholder="テキストを入力...")
        st.session_state.text_variations[selected_tab]['text'] = new_text
        
        enabled = st.checkbox("表示する", value=text_var.get('enabled', True), key=f"text_en_{selected_tab}")
        st.session_state.text_variations[selected_tab]['enabled'] = enabled
        
        # フォント設定
        with st.expander("フォント設定"):
            col1, col2 = st.columns(2)
            with col1:
                font = st.selectbox("フォント", ["ゴシック", "明朝"], 
                                   index=["ゴシック", "明朝"].index(text_var.get('font', 'ゴシック')),
                                   key=f"font_{selected_tab}", label_visibility="collapsed")
                st.session_state.text_variations[selected_tab]['font'] = font
                st.caption("フォント")
            with col2:
                weight = st.selectbox("ウェイト", ["W3", "W4", "W5", "W6", "W7", "W8", "W9"],
                                     index=["W3", "W4", "W5", "W6", "W7", "W8", "W9"].index(text_var.get('weight', 'W7')),
                                     key=f"weight_{selected_tab}", label_visibility="collapsed")
                st.session_state.text_variations[selected_tab]['weight'] = weight
                st.caption("ウェイト")
            
            size = st.slider("サイズ", 50, 200, text_var.get('size', 100), key=f"size_{selected_tab}")
            st.session_state.text_variations[selected_tab]['size'] = size
            
            color = st.color_picker("色", text_var.get('color', '#000000'), key=f"color_{selected_tab}")
            st.session_state.text_variations[selected_tab]['color'] = color
            
            char_spacing = st.slider("文字間", -10, 50, text_var.get('char_spacing', 0), key=f"char_{selected_tab}")
            st.session_state.text_variations[selected_tab]['char_spacing'] = char_spacing
            
            line_spacing = st.slider("行間", -10, 50, text_var.get('line_spacing', 0), key=f"line_{selected_tab}")
            st.session_state.text_variations[selected_tab]['line_spacing'] = line_spacing
            
            aspect_ratio = st.slider("縦横比 (%)", 50, 200, int(text_var.get('aspect_ratio', 1.0) * 100), key=f"aspect_{selected_tab}") / 100
            st.session_state.text_variations[selected_tab]['aspect_ratio'] = aspect_ratio
        
        # 位置設定
        with st.expander("位置設定"):
            col1, col2 = st.columns(2)
            with col1:
                pos_x = st.slider("X", 0, WIDTH, text_var.get('x', WIDTH // 2), key=f"x_{selected_tab}")
                st.session_state.text_variations[selected_tab]['x'] = pos_x
            with col2:
                pos_y = st.slider("Y", 0, HEIGHT, text_var.get('y', HEIGHT // 2), key=f"y_{selected_tab}")
                st.session_state.text_variations[selected_tab]['y'] = pos_y
            
            if st.button("中央に配置", key=f"center_{selected_tab}", use_container_width=True):
                st.session_state.text_variations[selected_tab]['x'] = WIDTH // 2
                st.session_state.text_variations[selected_tab]['y'] = HEIGHT // 2
                st.rerun()
        
        # アイコン増加専用設定
        with st.expander("アイコン増加専用設定"):
            st.caption("※ テキスト・フォント・ウェイト・色は上記の設定を使用")
            st.caption("※ アイコン増加では改行は無視されます")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                icon_size = st.slider("文字サイズ", 20, 80, text_var.get('icon_size', 40), key=f"icon_size_{selected_tab}")
                st.session_state.text_variations[selected_tab]['icon_size'] = icon_size
            with col2:
                icon_char_spacing = st.slider("文字間", -10, 50, text_var.get('icon_char_spacing', 0), key=f"icon_char_{selected_tab}")
                st.session_state.text_variations[selected_tab]['icon_char_spacing'] = icon_char_spacing
            with col3:
                icon_aspect_ratio = st.slider("縦横比%", 50, 200, int(text_var.get('icon_aspect_ratio', 1.0) * 100), key=f"icon_aspect_{selected_tab}") / 100
                st.session_state.text_variations[selected_tab]['icon_aspect_ratio'] = icon_aspect_ratio
            
            col4, col5, col6 = st.columns(3)
            with col4:
                icon_row_spacing = st.slider("行間隔", 30, 100, text_var.get('icon_row_spacing', 50), key=f"icon_row_{selected_tab}")
                st.session_state.text_variations[selected_tab]['icon_row_spacing'] = icon_row_spacing
            with col5:
                icon_x = st.slider("X座標", 0, WIDTH, text_var.get('icon_x', 120), key=f"icon_x_{selected_tab}")
                st.session_state.text_variations[selected_tab]['icon_x'] = icon_x
            with col6:
                icon_y = st.slider("Y基準", 0, HEIGHT, text_var.get('icon_y', 300), key=f"icon_y_{selected_tab}")
                st.session_state.text_variations[selected_tab]['icon_y'] = icon_y
        
        # 削除ボタン
        if len(st.session_state.text_variations) > 1:
            if st.button("このテキストを削除", key=f"del_{selected_tab}", use_container_width=True):
                st.session_state.text_variations.pop(selected_tab)
                st.session_state.selected_text_tab = max(0, selected_tab - 1)
                st.rerun()

# 画像アップロード
with col_settings:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("画像アップロード"):
        for var_idx, img_var in enumerate(st.session_state.image_variations):
            uploaded_file = st.file_uploader(
                "画像を選択", 
                type=['png', 'jpg', 'jpeg', 'webp'],
                key=f"img_{var_idx}",
                label_visibility="collapsed"
            )
            
            if uploaded_file is not None:
                uploaded_img = Image.open(uploaded_file)
                st.session_state.image_variations[var_idx]['image'] = uploaded_img
                
                if st.session_state.image_variations[var_idx]['original_width'] == 100:
                    st.session_state.image_variations[var_idx]['original_width'] = uploaded_img.width
                    st.session_state.image_variations[var_idx]['original_height'] = uploaded_img.height
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    img_scale = st.slider("サイズ", 10, 200, int(img_var.get('scale', 1.0) * 100), key=f"img_scale_{var_idx}") / 100
                    st.session_state.image_variations[var_idx]['scale'] = img_scale
                with col2:
                    pos_x = st.slider("X", 0, WIDTH, img_var.get('x', WIDTH // 2), key=f"img_x_{var_idx}")
                    st.session_state.image_variations[var_idx]['x'] = pos_x
                with col3:
                    pos_y = st.slider("Y", 0, HEIGHT, img_var.get('y', HEIGHT // 2), key=f"img_y_{var_idx}")
                    st.session_state.image_variations[var_idx]['y'] = pos_y

# 注釈
with col_settings:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("注釈"):
        # ボタン
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("通常注釈を追加", use_container_width=True):
                st.session_state.annotation_variations.append({
                    'text': '新しい注釈',
                    'font': 'ゴシック',
                    'weight': 'W7',
                    'size': 10,
                    'color': '#000000',
                    'x': 10,
                    'y': 390,
                    'enabled': True,
                    'is_neumo': False
                })
                st.rerun()
        with col_btn2:
            if st.button("ニューモV専用", use_container_width=True):
                st.session_state.annotation_variations.append({
                    'text': '※初回限定500円（税込）',
                    'font': 'ゴシック',
                    'weight': 'W7',
                    'size': 10,
                    'color': '#000000',
                    'x': 10,
                    'y': 390,
                    'enabled': True,
                    'is_neumo': True
                })
                st.rerun()
        
        st.caption("※ ニューモV専用注釈のAPNGは商材名が「new5」で固定されます")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        for var_idx, annot_var in enumerate(st.session_state.annotation_variations):
            if annot_var.get('is_neumo', False):
                st.markdown(f"**ニューモV専用注釈 {var_idx + 1}**")
            else:
                st.markdown(f"**注釈 {var_idx + 1}**")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                new_text = st.text_input("テキスト", value=annot_var['text'], key=f"annot_{var_idx}", label_visibility="collapsed")
                st.session_state.annotation_variations[var_idx]['text'] = new_text
            with col2:
                enabled = st.checkbox("表示", value=annot_var['enabled'], key=f"annot_en_{var_idx}")
                st.session_state.annotation_variations[var_idx]['enabled'] = enabled
            
            col3, col4, col5, col6 = st.columns(4)
            with col3:
                font = st.selectbox("", ["ゴシック", "明朝"], 
                                   index=["ゴシック", "明朝"].index(annot_var.get('font', 'ゴシック')),
                                   key=f"annot_font_{var_idx}", label_visibility="collapsed")
                st.session_state.annotation_variations[var_idx]['font'] = font
                st.caption("フォント")
            with col4:
                size = st.slider("", 10, 96, annot_var.get('size', 10), key=f"annot_size_{var_idx}", label_visibility="collapsed")
                st.session_state.annotation_variations[var_idx]['size'] = size
                st.caption("サイズ")
            with col5:
                pos_x = st.number_input("", 0, WIDTH, annot_var.get('x', 10), key=f"annot_x_{var_idx}", label_visibility="collapsed")
                st.session_state.annotation_variations[var_idx]['x'] = pos_x
                st.caption("X")
            with col6:
                pos_y = st.number_input("", 0, HEIGHT, annot_var.get('y', 390), key=f"annot_y_{var_idx}", label_visibility="collapsed")
                st.session_state.annotation_variations[var_idx]['y'] = pos_y
                st.caption("Y")
            
            if len(st.session_state.annotation_variations) > 1:
                if st.button("削除", key=f"del_annot_{var_idx}"):
                    st.session_state.annotation_variations.pop(var_idx)
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)

# アニメーション詳細設定
with col_settings:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("アニメーション詳細設定"):
        if use_red_border:
            st.markdown("**赤枠点滅**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                border_width_red = st.slider("太さ", 1, 20, 13, key="border_width_red")
            with col2:
                border_colors = st.multiselect("色", ["red", "blue", "green", "black", "orange"], default=["red"], key="border_colors")
            with col3:
                num_frames_red = st.slider("フレーム", 5, 20, 5, key="num_frames_red")
            with col4:
                loop_count_red = st.selectbox("ループ", [1, 2, 3, 4], index=3, key="loop_count_red")
            st.markdown("<br>", unsafe_allow_html=True)
        
        if use_corner_icon:
            st.markdown("**4隅アイコン点滅**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                icon_size_corner = st.slider("サイズ", 20, 150, 85, key="icon_size_corner")
            with col2:
                icon_names = st.multiselect("種類", ["check.png", "！.png", "！？.png"], default=["check.png"], key="icon_names")
            with col3:
                num_frames_corner = st.slider("フレーム", 5, 20, 5, key="num_frames_corner")
            with col4:
                loop_count_corner = st.selectbox("ループ", [1, 2, 3, 4], index=3, key="loop_count_corner")
            st.markdown("<br>", unsafe_allow_html=True)
        
        if use_icon_increase:
            st.markdown("**アイコン増加**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                icon_size_increase = st.slider("サイズ", 20, 100, 60, key="icon_size_increase")
            with col2:
                icon_names_increase = st.multiselect("種類", ["check.png", "！.png", "！？.png"], default=["check.png"], key="icon_names_increase")
            with col3:
                num_frames_increase = st.slider("フレーム", 3, 10, 5, key="num_frames_increase")
            with col4:
                loop_count_increase = st.selectbox("ループ", [1, 2, 3, 4], index=3, key="loop_count_increase")

# ファイル名設定
with col_settings:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">OUTPUT</div>', unsafe_allow_html=True)
    
    col_name1, col_name2 = st.columns(2)
    with col_name1:
        product_name = st.text_input("商材名", value="商材名", label_visibility="collapsed", placeholder="商材名")
        st.caption("商材名")
    with col_name2:
        custom_name = st.text_input("名前", value="名前", label_visibility="collapsed", placeholder="名前")
        st.caption("名前")
    
    st.caption(f"例: {datetime.now().strftime('%y%m%d')}_{product_name}_APNG_枠点滅_素材_{custom_name}_01.png")
    
    # ニューモV専用注釈がある場合の表示
    has_neumo_annot = any(annot.get('is_neumo', False) for annot in st.session_state.annotation_variations)
    if has_neumo_annot:
        st.info("ニューモV専用注釈のAPNGは商材名が「new5」で固定されます")

# APNG一括生成
with col_settings:
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("APNG一括生成", type="primary", disabled=not use_red_border and not use_corner_icon and not use_icon_increase, use_container_width=True):
        generated_files = []
        date_str = datetime.now().strftime("%y%m%d")
        
        # デフォルト設定
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
        
        with st.spinner("APNG生成中..."):
            # 注釈バリエーションごとにループ
            for annot_idx, annot_var in enumerate(st.session_state.annotation_variations):
                if not annot_var['enabled']:
                    continue
                
                # ニューモV専用の場合は商材名を"new5"に固定
                if annot_var.get('is_neumo', False):
                    prod_name = "new5"
                else:
                    prod_name = product_name
                
                border_counter = 1
                icon_counter = 1
                increase_counter = 1
                
                for text_idx in range(len(st.session_state.text_variations)):
                    for img_idx in range(len(st.session_state.image_variations)):
                        variant_text_elements = [st.session_state.text_variations[text_idx]]
                        variant_annotation_elements = [annot_var]
                        variant_uploaded_image = st.session_state.image_variations[img_idx]['image']
                        variant_image_config = st.session_state.image_variations[img_idx]
                        
                        # 赤枠点滅
                        if use_red_border:
                            for border_color in border_colors:
                                frames = create_red_border_blink_frames(
                                    WIDTH, HEIGHT, variant_text_elements, variant_annotation_elements,
                                    variant_uploaded_image, variant_image_config,
                                    border_width=border_width_red, 
                                    border_color=border_color, 
                                    num_frames=num_frames_red
                                )
                                apng_data = save_apng(frames, frame_delay=FRAME_DELAY, num_plays=loop_count_red)
                                filename = f"{date_str}_{prod_name}_APNG_枠点滅_素材_{custom_name}_{border_counter:02d}.png"
                                generated_files.append((filename, apng_data))
                                border_counter += 1
                        
                        # 4隅アイコン点滅
                        if use_corner_icon:
                            for icon_name in icon_names:
                                frames = create_corner_icon_blink_frames(
                                    WIDTH, HEIGHT, variant_text_elements, variant_annotation_elements,
                                    variant_uploaded_image, variant_image_config,
                                    icon_name=icon_name,
                                    icon_size=icon_size_corner,
                                    num_frames=num_frames_corner
                                )
                                apng_data = save_apng(frames, frame_delay=FRAME_DELAY, num_plays=loop_count_corner)
                                filename = f"{date_str}_{prod_name}_APNG_ikon点滅_素材_{custom_name}_{icon_counter:02d}.png"
                                generated_files.append((filename, apng_data))
                                icon_counter += 1
                        
                        # アイコン増加
                        if use_icon_increase:
                            for icon_name in icon_names_increase:
                                frames = create_icon_increase_frames(
                                    WIDTH, HEIGHT, st.session_state.text_variations[text_idx], variant_annotation_elements,
                                    variant_uploaded_image, variant_image_config,
                                    icon_name=icon_name,
                                    icon_size=icon_size_increase,
                                    num_frames=num_frames_increase
                                )
                                apng_data = save_apng(frames, frame_delay=FRAME_DELAY, num_plays=loop_count_increase)
                                filename = f"{date_str}_{prod_name}_APNG_ikon増加_素材_{custom_name}_{increase_counter:02d}.png"
                                generated_files.append((filename, apng_data))
                                increase_counter += 1
        
        st.success(f"{len(generated_files)}個のAPNGを生成しました")
        
        # 個別ダウンロード
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**個別ダウンロード**")
        for file_idx, (filename, data) in enumerate(generated_files):
            file_size_kb = len(data) / 1024
            col1, col2 = st.columns([4, 1])
            with col1:
                if file_size_kb > 300:
                    st.warning(f"{filename} ({file_size_kb:.1f} KB)")
                else:
                    st.text(f"{filename} ({file_size_kb:.1f} KB)")
            with col2:
                st.download_button("DL", data=data, file_name=filename, mime="image/png", key=f"dl_{file_idx}", use_container_width=True)
        
        # ZIP一括ダウンロード
        if len(generated_files) > 1:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**ZIP一括ダウンロード**")
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for filename, data in generated_files:
                    zip_file.writestr(filename, data)
            
            zip_buffer.seek(0)
            st.download_button(
                label=f"全{len(generated_files)}個をZIPでダウンロード",
                data=zip_buffer.getvalue(),
                file_name=f"{date_str}_{product_name}_APNG_all.zip",
                mime="application/zip",
                use_container_width=True
            )

# プレビュー側
with col_preview:
    st.markdown('<div class="section-title">PREVIEW</div>', unsafe_allow_html=True)
    
    # 有効な注釈を収集
    preview_annotation_elements = []
    for annot in st.session_state.annotation_variations:
        if annot['enabled']:
            preview_annotation_elements.append(annot)
    
    # 選択されたアニメーションのプレビューを表示
    preview_count = sum([use_red_border, use_corner_icon, use_icon_increase])
    
    if preview_count == 0:
        st.info("左側でテンプレートを選択してください")
    else:
        # 有効なテキストバリエーションを収集
        enabled_text_variations = [tv for tv in st.session_state.text_variations if tv.get('enabled', True)]
        
        # 赤枠点滅
        if use_red_border:
            st.markdown("**赤枠点滅**")
            cols = st.columns(len(enabled_text_variations))
            for idx, (col, text_var) in enumerate(zip(cols, enabled_text_variations)):
                with col:
                    st.caption(f"テキスト {st.session_state.text_variations.index(text_var) + 1}")
                    preview_img = create_preview_image(
                        [text_var], preview_annotation_elements,
                        st.session_state.image_variations[0]['image'],
                        st.session_state.image_variations[0],
                        "赤枠点滅", scale=0.5, border_width=13, border_color="red"
                    )
                    st.image(preview_img, use_container_width=True)
        
        # 4隅アイコン点滅
        if use_corner_icon:
            st.markdown("**4隅アイコン点滅**")
            cols = st.columns(len(enabled_text_variations))
            for idx, (col, text_var) in enumerate(zip(cols, enabled_text_variations)):
                with col:
                    st.caption(f"テキスト {st.session_state.text_variations.index(text_var) + 1}")
                    preview_img = create_preview_image(
                        [text_var], preview_annotation_elements,
                        st.session_state.image_variations[0]['image'],
                        st.session_state.image_variations[0],
                        "4隅アイコン点滅", scale=0.5, icon_size=85, icon_name="check.png"
                    )
                    st.image(preview_img, use_container_width=True)
        
        # アイコン増加
        if use_icon_increase:
            st.markdown("**アイコン増加**")
            cols = st.columns(len(enabled_text_variations))
            for idx, (col, text_var) in enumerate(zip(cols, enabled_text_variations)):
                with col:
                    st.caption(f"テキスト {st.session_state.text_variations.index(text_var) + 1}")
                    preview_img = create_preview_image(
                        [text_var], preview_annotation_elements,
                        st.session_state.image_variations[0]['image'],
                        st.session_state.image_variations[0],
                        "アイコン増加", scale=0.5, icon_size=60, icon_name="check.png"
                    )
                    st.image(preview_img, use_container_width=True)
