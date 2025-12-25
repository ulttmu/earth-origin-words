"""
ComfyUI 中文文字疊加功能
在圖片上添加中文文字
"""
import json
import urllib.request
import time
import shutil
from pathlib import Path
from datetime import datetime

# 設定
COMFYUI_URL = "http://100.107.71.38:8188"
GOOGLE_DRIVE_OUTPUT = Path("/Users/yuan/Library/CloudStorage/GoogleDrive-soapberryearth@gmail.com/我的雲端硬碟/ComfyUI_Output")
LOCAL_OUTPUT = Path("/Users/yuan/comfyui_tools/output")

# 可用字體
FONTS = {
    "黑體": "simhei.ttf",      # 現代、標題
    "楷體": "simkai.ttf",      # 手寫感
    "仿宋": "simfang.ttf",     # 正式、文件
    "宋體": "simsunb.ttf",     # 傳統、正文
    "標楷": "kaiu.ttf",        # 台灣標準楷體
}


def upload_image(image_path: str) -> str:
    """上傳圖片到 ComfyUI"""
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"找不到圖片: {image_path}")

    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'

    with open(image_path, 'rb') as f:
        file_data = f.read()

    filename = image_path.name
    import mimetypes
    content_type = mimetypes.guess_type(filename)[0] or 'image/png'

    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
        f'Content-Type: {content_type}\r\n\r\n'
    ).encode('utf-8') + file_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')

    req = urllib.request.Request(
        f"{COMFYUI_URL}/upload/image",
        data=body,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read())
        return result.get('name', filename)


def add_text_overlay(
    image_path: str,
    text: str,
    font: str = "黑體",
    size: int = 64,
    color: str = "#333333",
    position: str = "bottom_center",
    background_color: str = "#00000000",
    shadow: bool = False
) -> str:
    """
    在圖片上添加中文文字

    Args:
        image_path: 圖片路徑
        text: 要添加的文字
        font: 字體名稱 (黑體/楷體/仿宋/宋體/標楷)
        size: 字體大小
        color: 文字顏色 (hex)
        position: 位置 (top_left/top_center/top_right/center/bottom_left/bottom_center/bottom_right)
        background_color: 背景顏色 (hex, 含透明度)
        shadow: 是否添加陰影

    Returns:
        輸出圖片路徑
    """
    # 解析位置
    h_align, v_align = "center", "bottom"
    offset_x, offset_y = 0, -50

    if position.startswith("top"):
        v_align = "top"
        offset_y = 50
    elif position.startswith("bottom"):
        v_align = "bottom"
        offset_y = -50
    else:
        v_align = "center"
        offset_y = 0

    if "left" in position:
        h_align = "left"
        offset_x = 50
    elif "right" in position:
        h_align = "right"
        offset_x = -50
    else:
        h_align = "center"
        offset_x = 0

    # 取得字體檔名
    font_file = FONTS.get(font, font)
    if not font_file.endswith('.ttf'):
        font_file = FONTS.get(font, "simhei.ttf")

    print(f"📤 上傳圖片...")
    uploaded_name = upload_image(image_path)

    # 文字疊加工作流
    workflow = {
        "1": {
            "class_type": "LoadImage",
            "inputs": {
                "image": uploaded_name
            }
        },
        "2": {
            "class_type": "DrawText+",
            "inputs": {
                "text": text,
                "font": font_file,
                "size": size,
                "color": color,
                "background_color": background_color,
                "shadow_distance": 3 if shadow else 0,
                "shadow_blur": 5 if shadow else 0,
                "shadow_color": "#000000",
                "horizontal_align": h_align,
                "vertical_align": v_align,
                "offset_x": offset_x,
                "offset_y": offset_y,
                "direction": "ltr",
                "img_composite": ["1", 0]
            }
        },
        "3": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["2", 0],
                "filename_prefix": "text_overlay"
            }
        }
    }

    print(f"🔤 添加文字: \"{text}\"")
    print(f"   字體: {font} ({font_file})")
    print(f"   位置: {position}")

    # 提交工作流
    payload = {"prompt": workflow}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=data,
        headers={'Content-Type': 'application/json'}
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read())
        prompt_id = result.get('prompt_id')

    # 等待完成
    start_time = time.time()
    while time.time() - start_time < 60:
        hist_url = f"{COMFYUI_URL}/history/{prompt_id}"
        with urllib.request.urlopen(hist_url, timeout=10) as hist_resp:
            history = json.loads(hist_resp.read())

        if prompt_id in history:
            status = history[prompt_id].get('status', {})
            if status.get('status_str') == 'error':
                error_msg = "Unknown error"
                for msg in status.get('messages', []):
                    if msg[0] == 'execution_error':
                        error_msg = msg[1].get('exception_message', 'Unknown')
                raise Exception(f"文字疊加失敗: {error_msg}")

            outputs = history[prompt_id].get('outputs', {})
            if outputs:
                elapsed = time.time() - start_time
                print(f"✅ 完成！耗時: {elapsed:.1f} 秒")

                for node_id, output in outputs.items():
                    if 'images' in output:
                        for img in output['images']:
                            filename = img['filename']

                            # 下載圖片
                            img_url = f"{COMFYUI_URL}/view?filename={filename}&type=output"
                            with urllib.request.urlopen(img_url, timeout=30) as img_resp:
                                image_data = img_resp.read()

                            # 儲存
                            local_path = LOCAL_OUTPUT / filename
                            with open(local_path, 'wb') as f:
                                f.write(image_data)

                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            gdrive_filename = f"text_{timestamp}.png"
                            gdrive_path = GOOGLE_DRIVE_OUTPUT / gdrive_filename
                            shutil.copy(local_path, gdrive_path)

                            print(f"📷 已儲存: {gdrive_path}")
                            return str(gdrive_path)

        time.sleep(1)

    raise TimeoutError("處理超時")


if __name__ == "__main__":
    # 測試：找一張參考圖並添加中文文字
    from pathlib import Path

    ref_path = Path("/Users/yuan/Downloads/pinterest-downloads/earthorigin-lora/_processed")
    ref_images = list(ref_path.glob("*.jpg"))[:1]

    if ref_images:
        print(f"\n測試圖片: {ref_images[0].name}")
        result = add_text_overlay(
            image_path=str(ref_images[0]),
            text="大地起源",
            font="黑體",
            size=72,
            color="#5c4a3d",
            position="bottom_center",
            shadow=True
        )
        print(f"\n🎉 完成！結果: {result}")
