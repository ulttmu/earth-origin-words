#!/usr/bin/env python3
"""
為 Airtable 廣告文案批次生成配圖
- 每篇文案 3 個視覺方向 × 2 張圖 = 6 張圖
- 1:1 正方形格式 (1024x1024)
- 自動記錄 prompt 和圖片到 Airtable
"""

import requests
import json
import time
import base64
from pathlib import Path
from datetime import datetime
import urllib.parse
import sys

# 匯入 Google Drive 上傳模組
sys.path.insert(0, str(Path(__file__).parent))
from gdrive_upload import upload_image as gdrive_upload_image

# === 配置 ===
import os

COMFYUI_URL = os.getenv("COMFYUI_URL", "http://100.107.71.38:8188")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "app4TFGAUw3fVvsAd")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "Ads_Creatives")
AIRTABLE_API_TOKEN = os.getenv("AIRTABLE_API_TOKEN")  # 從環境變數讀取

if not AIRTABLE_API_TOKEN:
    raise ValueError("請設定 AIRTABLE_API_TOKEN 環境變數")

OUTPUT_DIR = Path("/Users/yuan/comfyui_tools/output/airtable_batch")
GOOGLE_DRIVE_OUTPUT = Path("/Users/yuan/Library/CloudStorage/GoogleDrive-soapberryearth@gmail.com/我的雲端硬碟/大地起源圖文/ai_generated")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
GOOGLE_DRIVE_OUTPUT.mkdir(parents=True, exist_ok=True)

headers = {
    "Authorization": f"Bearer {AIRTABLE_API_TOKEN}",
    "Content-Type": "application/json"
}

# === Earth Origin 風格核心 prompt 元素 ===
STYLE_CORE = """shot on Kodak Portra 400, warm muted earth tones, soft natural light,
subtle film grain, shallow depth of field, intimate atmosphere, minimalist composition,
in the style of Rinko Kawauchi, editorial lifestyle photography"""

# === 根據產品和角色設計視覺方向 ===
def design_visual_directions(ad_data):
    """為每篇廣告設計 3 個視覺方向"""
    fields = ad_data["fields"]
    name = fields.get("Name", "")
    primary_text = fields.get("Primary_Text", "")
    product = fields.get("Product_Focus", "")
    hook_type = fields.get("Hook_Type", "")

    # 根據產品類型設定主視覺元素
    product_visuals = {
        "草本精釀洗髮露": {
            "A": "hands massaging shampoo into hair, warm water flowing, soft bathroom light",
            "B": "healthy scalp and hair close-up, clean minimalist aesthetic",
            "C": "shampoo bottle with fresh green leaves and water droplets"
        },
        "慢時間淨化平衡沐浴露": {
            "A": "body silhouette in soft shower light, water droplets on skin",
            "B": "bath product with natural wood texture, minimalist zen",
            "C": "hands touching water surface, gentle ripples"
        },
        "éclipse舒眠噴霧": {
            "A": "pillow and bedside ritual, soft evening light",
            "B": "spray bottle in moonlight, dreamy atmosphere",
            "C": "person's relaxed silhouette in soft backlight"
        },
        "秘魯聖木": {
            "A": "burning palo santo with gentle smoke rising, golden hour",
            "B": "hands holding palo santo stick, intimate close-up",
            "C": "palo santo on wooden surface, minimalist still life"
        },
        "護手碗盤洗潔液": {
            "A": "hands washing dishes with gentle bubbles, kitchen window light",
            "B": "clean ceramic bowl with water droplets, natural light",
            "C": "product bottle with kitchen herbs, warm domestic scene"
        }
    }

    # 獲取該產品的視覺方向
    visuals = product_visuals.get(product, {
        "A": "natural product on simple surface, soft daylight",
        "B": "hands interacting with natural element, warm light",
        "C": "minimalist still life with organic texture"
    })

    # 組合完整 prompt
    directions = {}
    for key, scene in visuals.items():
        prompt = f"{scene}, {STYLE_CORE}"
        directions[f"方向{key}"] = {
            "prompt": prompt,
            "scene_description": scene
        }

    return directions

# === 呼叫 ComfyUI 生成圖片 ===
def generate_image(prompt, seed=None):
    """呼叫 ComfyUI text2img 生成圖片（使用 Z-Image Turbo）"""
    if seed is None:
        seed = int(time.time() * 1000) % 2147483647

    # Z-Image Turbo workflow (text2img)
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
        "10": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1
            }
        },
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["4", 0],
                "negative": ["5", 0],
                "latent_image": ["10", 0],
                "seed": seed,
                "steps": 8,
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0
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
                "filename_prefix": "airtable_batch"
            }
        }
    }

    # 送出請求
    try:
        response = requests.post(
            f"{COMFYUI_URL}/prompt",
            json={"prompt": workflow},
            timeout=300
        )

        if response.status_code == 200:
            prompt_id = response.json()["prompt_id"]
            print(f"  ✓ 生成任務已送出: {prompt_id}")

            # 等待生成完成
            while True:
                time.sleep(2)
                queue = requests.get(f"{COMFYUI_URL}/history/{prompt_id}").json()

                if prompt_id in queue:
                    outputs = queue[prompt_id].get("outputs", {})
                    if "9" in outputs:  # SaveImage node
                        images = outputs["9"]["images"]
                        if images:
                            filename = images[0]["filename"]
                            subfolder = images[0].get("subfolder", "")
                            img_type = images[0].get("type", "output")

                            # 下載圖片
                            params = {
                                "filename": filename,
                                "subfolder": subfolder,
                                "type": img_type
                            }
                            img_url = f"{COMFYUI_URL}/view"
                            img_response = requests.get(img_url, params=params, timeout=30)

                            if img_response.status_code == 200:
                                # 儲存到本地
                                local_path = OUTPUT_DIR / filename
                                with open(local_path, 'wb') as f:
                                    f.write(img_response.content)

                                # 複製到 Google Drive
                                import shutil
                                from datetime import datetime

                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                gdrive_filename = f"airtable_{timestamp}_{filename}"
                                gdrive_path = GOOGLE_DRIVE_OUTPUT / gdrive_filename
                                shutil.copy(local_path, gdrive_path)

                                print(f"  ✓ 圖片已下載: {filename}")
                                print(f"    Drive: {gdrive_path.name}")

                                return str(gdrive_path)
                            else:
                                print(f"  ❌ 下載圖片失敗: {img_response.status_code}")
                                return None
                time.sleep(1)
        else:
            print(f"  ❌ 生成失敗: {response.status_code}")
            return None

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
        return None

# === 上傳圖片到 Airtable ===
def upload_to_airtable(record_id, images_data, prompts):
    """更新 Airtable 記錄，加入圖片和 prompt"""

    # 組合視覺方向描述
    visual_directions = "\n".join([
        f"{direction}: {data['scene_description']}"
        for direction, data in prompts.items()
    ])

    # 組合完整 prompt
    full_prompts = "\n\n".join([
        f"{direction}:\n{data['prompt']}"
        for direction, data in prompts.items()
    ])

    # 準備更新資料
    update_fields = {
        "AI_Visual_Directions": visual_directions,
        "AI_Full_Prompts": full_prompts,
    }

    # 上傳圖片到 Google Drive 並獲取公開連結
    if images_data:
        print(f"  📤 上傳 {len(images_data)} 張圖片到 Google Drive...")

        image_attachments = []
        folder_id = "1TwiNq2RcuakSaXHIrwwizttSpBNgAkLb"  # 從 CLAUDE.md

        for img_path in images_data:
            try:
                result = gdrive_upload_image(img_path, folder_id)
                image_attachments.append({"url": result['direct_link']})
                print(f"    ✓ {Path(img_path).name}")
            except Exception as e:
                print(f"    ✗ {Path(img_path).name}: {e}")

        if image_attachments:
            update_fields["Generated_Images"] = image_attachments
            update_fields["Image_Generation_Status"] = "已完成"
            print(f"  ✓ 已上傳 {len(image_attachments)} 張圖片")
        else:
            update_fields["Image_Generation_Status"] = "上傳失敗"
    else:
        update_fields["Image_Generation_Status"] = "生成失敗"

    # 更新記錄
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}/{record_id}"

    update_data = {"fields": update_fields}

    try:
        response = requests.patch(url, headers=headers, json=update_data)
        if response.status_code == 200:
            print(f"  ✅ Airtable 記錄已更新（含圖片預覽）")
            return True
        else:
            print(f"  ❌ Airtable 更新失敗: {response.status_code}")
            print(f"     {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
        return False

# === 主流程 ===
def main():
    print("🎨 大地起源 Meta 廣告配圖批次生成\n")

    # 1. 讀取 Airtable 資料
    print("📥 讀取 Airtable 廣告文案...")
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    params = {
        "filterByFormula": "{Status} = 'Draft'",
        "maxRecords": 5  # 先測試 5 篇
    }

    response = requests.get(url, headers=headers, params=params)
    records = response.json().get("records", [])

    print(f"找到 {len(records)} 篇廣告\n")

    # 2. 為每篇廣告生成圖片
    for i, record in enumerate(records, 1):
        record_id = record["id"]
        fields = record["fields"]
        name = fields.get("Name", f"廣告_{i}")

        print(f"\n{'='*60}")
        print(f"[{i}/{len(records)}] {name}")
        print(f"{'='*60}")

        # 設計 3 個視覺方向
        directions = design_visual_directions(record)

        print("\n📐 視覺方向設計:")
        for direction, data in directions.items():
            print(f"  {direction}: {data['scene_description'][:60]}...")

        # 生成圖片（每個方向 2 張）
        generated_images = []

        for direction, data in directions.items():
            print(f"\n🎨 生成 {direction}...")

            for j in range(2):
                print(f"  第 {j+1} 張:")
                img_file = generate_image(data["prompt"])

                if img_file:
                    generated_images.append(img_file)
                    time.sleep(1)  # 避免過載

        # 更新 Airtable
        print(f"\n📤 更新 Airtable 記錄...")
        upload_to_airtable(record_id, generated_images, directions)

        print(f"\n✅ {name} 完成！生成了 {len(generated_images)} 張圖")

    print(f"\n{'='*60}")
    print(f"🎉 全部完成！")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
