"""
ComfyUI img2img 圖片風格遷移
使用參考圖生成相似風格的新圖片
"""
import json
import urllib.request
import time
import shutil
import os
from pathlib import Path
from datetime import datetime

# 設定
COMFYUI_URL = "http://100.107.71.38:8188"
GOOGLE_DRIVE_OUTPUT = Path("/Users/yuan/Library/CloudStorage/GoogleDrive-soapberryearth@gmail.com/我的雲端硬碟/ComfyUI_Output")
LOCAL_OUTPUT = Path("/Users/yuan/comfyui_tools/output")
REFERENCE_PATH = Path("/Users/yuan/Downloads/pinterest-downloads/earthorigin-lora/_processed")

# 確保資料夾存在
GOOGLE_DRIVE_OUTPUT.mkdir(parents=True, exist_ok=True)
LOCAL_OUTPUT.mkdir(parents=True, exist_ok=True)


def upload_image(image_path: str) -> str:
    """
    上傳圖片到 ComfyUI

    Returns:
        上傳後的檔名
    """
    import mimetypes

    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"找不到圖片: {image_path}")

    # 準備 multipart form data
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'

    with open(image_path, 'rb') as f:
        file_data = f.read()

    filename = image_path.name
    content_type = mimetypes.guess_type(filename)[0] or 'image/png'

    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
        f'Content-Type: {content_type}\r\n\r\n'
    ).encode('utf-8') + file_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')

    req = urllib.request.Request(
        f"{COMFYUI_URL}/upload/image",
        data=body,
        headers={
            'Content-Type': f'multipart/form-data; boundary={boundary}'
        }
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read())
        return result.get('name', filename)


def img2img(
    prompt: str,
    reference_image: str,
    denoise: float = 0.6,
    width: int = 768,
    height: int = 1024,
    steps: int = 8,
    seed: int = None
) -> str:
    """
    使用參考圖進行風格遷移

    Args:
        prompt: 圖片描述（會影響生成方向）
        reference_image: 參考圖路徑
        denoise: 去噪強度 (0.0-1.0)
                 - 0.3: 非常像原圖
                 - 0.5: 中等風格遷移
                 - 0.7: 較大改變
        width: 輸出寬度
        height: 輸出高度
        steps: 生成步數
        seed: 隨機種子

    Returns:
        生成圖片的路徑
    """
    if seed is None:
        seed = int(time.time() * 1000) % 2147483647

    print(f"📤 上傳參考圖...")
    uploaded_name = upload_image(reference_image)
    print(f"   已上傳: {uploaded_name}")

    # img2img 工作流
    workflow = {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "z_image_turbo_bf16.safetensors",
                "weight_dtype": "default"
            }
        },
        "2": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": "qwen_3_4b.safetensors",
                "type": "sd3"
            }
        },
        "3": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "ae.safetensors"
            }
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["2", 0],
                "text": prompt
            }
        },
        "5": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["2", 0],
                "text": ""
            }
        },
        # 載入參考圖
        "10": {
            "class_type": "LoadImage",
            "inputs": {
                "image": uploaded_name
            }
        },
        # 調整圖片尺寸
        "11": {
            "class_type": "ImageScale",
            "inputs": {
                "image": ["10", 0],
                "width": width,
                "height": height,
                "upscale_method": "lanczos",
                "crop": "center"
            }
        },
        # 編碼為 latent
        "12": {
            "class_type": "VAEEncode",
            "inputs": {
                "pixels": ["11", 0],
                "vae": ["3", 0]
            }
        },
        # KSampler - 使用參考圖的 latent
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["4", 0],
                "negative": ["5", 0],
                "latent_image": ["12", 0],  # 使用編碼後的參考圖
                "seed": seed,
                "steps": steps,
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": denoise  # 關鍵參數！
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["6", 0],
                "vae": ["3", 0]
            }
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["8", 0],
                "filename_prefix": "img2img"
            }
        }
    }

    print(f"🚀 開始 img2img 生成...")
    print(f"   參考圖: {Path(reference_image).name}")
    print(f"   提示詞: {prompt[:50]}...")
    print(f"   去噪強度: {denoise}")
    print(f"   尺寸: {width}x{height}")

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

    print(f"   任務 ID: {prompt_id}")

    # 等待完成
    start_time = time.time()
    while time.time() - start_time < 300:
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
                raise Exception(f"生成失敗: {error_msg}")

            outputs = history[prompt_id].get('outputs', {})
            if outputs:
                elapsed = time.time() - start_time
                print(f"\n✅ img2img 完成！耗時: {elapsed:.1f} 秒")

                for node_id, output in outputs.items():
                    if 'images' in output:
                        for img in output['images']:
                            filename = img['filename']

                            # 下載圖片
                            img_url = f"{COMFYUI_URL}/view?filename={filename}&type=output"
                            with urllib.request.urlopen(img_url, timeout=30) as img_resp:
                                image_data = img_resp.read()

                            # 儲存到本地
                            local_path = LOCAL_OUTPUT / filename
                            with open(local_path, 'wb') as f:
                                f.write(image_data)

                            # 複製到 Google Drive
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            gdrive_filename = f"img2img_{timestamp}.png"
                            gdrive_path = GOOGLE_DRIVE_OUTPUT / gdrive_filename
                            shutil.copy(local_path, gdrive_path)

                            print(f"📷 已儲存:")
                            print(f"   本地: {local_path}")
                            print(f"   Google Drive: {gdrive_path}")

                            return str(gdrive_path)

        elapsed = time.time() - start_time
        print(f"\r⏳ 等待中... {elapsed:.0f}秒", end='', flush=True)
        time.sleep(2)

    raise TimeoutError("生成超時")


def img2img_with_search(
    prompt: str,
    search_query: str = None,
    denoise: float = 0.6,
    **kwargs
) -> str:
    """
    自動搜尋參考圖並進行風格遷移

    Args:
        prompt: 生成提示詞
        search_query: 搜尋關鍵詞（如果不提供，使用 prompt）
        denoise: 去噪強度
    """
    # 載入搜尋系統
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from reference_search import search

    query = search_query or prompt
    print(f"🔍 搜尋參考圖: {query}")

    results = search(query, top_k=1)
    if not results:
        raise ValueError(f"找不到相關參考圖: {query}")

    ref = results[0]
    print(f"   找到: {ref['filename']} (score: {ref['score']:.1f})")
    print(f"   描述: {ref['caption'][:60]}...")

    return img2img(
        prompt=prompt,
        reference_image=ref['path'],
        denoise=denoise,
        **kwargs
    )


if __name__ == "__main__":
    # 測試 1: 直接指定參考圖
    print("\n" + "="*50)
    print("測試 1: 直接指定參考圖")
    print("="*50)

    # 找一張參考圖
    ref_images = list(REFERENCE_PATH.glob("*.jpg"))[:1]
    if ref_images:
        result = img2img(
            prompt="earthorigin style, handmade soap bar with natural herbs, soft morning light, cream and brown tones",
            reference_image=str(ref_images[0]),
            denoise=0.6,
            steps=8
        )
        print(f"\n🎉 完成！")

    # 測試 2: 自動搜尋參考圖
    print("\n" + "="*50)
    print("測試 2: 自動搜尋參考圖")
    print("="*50)

    result = img2img_with_search(
        prompt="earthorigin style, woman reading book by window, warm afternoon light",
        search_query="reading book warm light",
        denoise=0.5,
        steps=8
    )
    print(f"\n🎉 完成！")
