"""
ComfyUI 圖片生成腳本 - 自動上傳到 Google Drive
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

# 確保資料夾存在
GOOGLE_DRIVE_OUTPUT.mkdir(parents=True, exist_ok=True)
LOCAL_OUTPUT.mkdir(parents=True, exist_ok=True)


def generate_image(prompt: str, width: int = 1024, height: int = 1024, steps: int = 8, seed: int = None):
    """
    使用 Z-Image-Turbo 生成圖片

    Args:
        prompt: 圖片描述
        width: 圖片寬度
        height: 圖片高度
        steps: 生成步數 (越多越精細，但更慢)
        seed: 隨機種子 (None = 隨機)

    Returns:
        生成的圖片路徑 (Google Drive)
    """
    if seed is None:
        seed = int(time.time() * 1000) % 2147483647

    # 建立工作流
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
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1
            }
        },
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["4", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
                "seed": seed,
                "steps": steps,
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0
            }
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["2", 0],
                "text": ""
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
                "filename_prefix": "earth_origin"
            }
        }
    }

    print(f"🚀 開始生成...")
    print(f"   提示詞: {prompt[:50]}...")
    print(f"   尺寸: {width}x{height}")
    print(f"   步數: {steps}")

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
    while time.time() - start_time < 300:  # 最多 5 分鐘
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
                print(f"\n✅ 生成完成！耗時: {elapsed:.1f} 秒")

                # 下載並儲存圖片
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
                            gdrive_filename = f"earth_origin_{timestamp}.png"
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


if __name__ == "__main__":
    # 測試生成
    result = generate_image(
        prompt="a beautiful product photo of a handmade soap bar with natural herbs and flowers, white background, professional lighting, commercial photography, earth tones",
        width=1024,
        height=1024,
        steps=8
    )
    print(f"\n🎉 完成！圖片已上傳到 Google Drive")
