#!/usr/bin/env python3
"""
IP-Adapter 模型下載腳本

用途: 自動下載 ComfyUI IP-Adapter 所需的所有模型檔案
作者: Claude Code
日期: 2025-12-26

使用方式:
    python download_ipadapter_models.py --basic     # 只下載基礎模型
    python download_ipadapter_models.py --full      # 下載所有模型 (包含 FaceID)
    python download_ipadapter_models.py --check     # 檢查已下載的模型
"""

import os
import sys
import argparse
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple

# 顏色輸出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

# ComfyUI 模型目錄 (需根據實際 Windows 路徑調整)
# 這些路徑需要透過網路存取或遠端桌面在 Windows PC 上執行
COMFYUI_BASE = "D:/ComfyUI_windows_portable/ComfyUI"
CLIP_VISION_DIR = f"{COMFYUI_BASE}/models/clip_vision"
IPADAPTER_DIR = f"{COMFYUI_BASE}/models/ipadapter"
LORAS_DIR = f"{COMFYUI_BASE}/models/loras"

# 模型下載清單
MODELS = {
    "clip_vision": {
        "dir": CLIP_VISION_DIR,
        "files": [
            {
                "name": "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors",
                "url": "https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors",
                "size": "2.5 GB",
                "required": True
            },
            {
                "name": "CLIP-ViT-bigG-14-laion2B-39B-b160k.safetensors",
                "url": "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/image_encoder/model.safetensors",
                "size": "3.7 GB",
                "required": True
            }
        ]
    },
    "ipadapter_basic": {
        "dir": IPADAPTER_DIR,
        "files": [
            {
                "name": "ip-adapter_sd15.safetensors",
                "url": "https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter_sd15.safetensors",
                "size": "~90 MB",
                "required": True
            },
            {
                "name": "ip-adapter-plus_sd15.safetensors",
                "url": "https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-plus_sd15.safetensors",
                "size": "~90 MB",
                "required": True
            },
            {
                "name": "ip-adapter_sdxl_vit-h.safetensors",
                "url": "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl_vit-h.safetensors",
                "size": "~700 MB",
                "required": False
            },
            {
                "name": "ip-adapter-plus_sdxl_vit-h.safetensors",
                "url": "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors",
                "size": "~700 MB",
                "required": False
            }
        ]
    },
    "ipadapter_faceid": {
        "dir": IPADAPTER_DIR,
        "files": [
            {
                "name": "ip-adapter-faceid_sd15.bin",
                "url": "https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid_sd15.bin",
                "size": "~22 MB",
                "required": False
            },
            {
                "name": "ip-adapter-faceid-plusv2_sd15.bin",
                "url": "https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid-plusv2_sd15.bin",
                "size": "~22 MB",
                "required": False
            },
            {
                "name": "ip-adapter-faceid_sdxl.bin",
                "url": "https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid_sdxl.bin",
                "size": "~22 MB",
                "required": False
            }
        ]
    }
}

def print_header():
    """列印歡迎訊息"""
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}  ComfyUI IP-Adapter 模型下載工具{Colors.RESET}")
    print(f"{Colors.BLUE}  目標 Windows PC: 100.107.71.38{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def check_models() -> Dict[str, List[Tuple[str, bool]]]:
    """檢查已下載的模型"""
    print(f"{Colors.YELLOW}檢查已下載模型...{Colors.RESET}\n")

    results = {}

    for category, data in MODELS.items():
        model_dir = data["dir"]
        results[category] = []

        print(f"\n{Colors.BLUE}[{category}]{Colors.RESET}")
        print(f"  目錄: {model_dir}")

        for file_info in data["files"]:
            filename = file_info["name"]
            filepath = os.path.join(model_dir, filename)
            exists = os.path.exists(filepath)

            status = f"{Colors.GREEN}✓ 已下載{Colors.RESET}" if exists else f"{Colors.RED}✗ 未下載{Colors.RESET}"
            required = f"{Colors.RED}[必需]{Colors.RESET}" if file_info["required"] else "[選用]"

            print(f"  {status} {required} {filename} ({file_info['size']})")
            results[category].append((filename, exists))

    return results

def download_file(url: str, dest_path: str, filename: str):
    """下載單個檔案 (帶進度條)"""

    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(downloaded * 100 / total_size, 100)
        bar_length = 40
        filled = int(bar_length * percent / 100)
        bar = '█' * filled + '-' * (bar_length - filled)

        size_mb = total_size / (1024 * 1024)
        downloaded_mb = downloaded / (1024 * 1024)

        print(f'\r  [{bar}] {percent:.1f}% ({downloaded_mb:.1f}/{size_mb:.1f} MB)', end='')

    try:
        print(f"\n{Colors.YELLOW}正在下載: {filename}{Colors.RESET}")
        urllib.request.urlretrieve(url, dest_path, progress_hook)
        print(f"\n{Colors.GREEN}✓ 下載完成{Colors.RESET}")
        return True
    except Exception as e:
        print(f"\n{Colors.RED}✗ 下載失敗: {e}{Colors.RESET}")
        return False

def download_models(mode: str = "basic"):
    """下載模型檔案"""

    categories = ["clip_vision", "ipadapter_basic"]
    if mode == "full":
        categories.append("ipadapter_faceid")

    print(f"\n{Colors.YELLOW}開始下載模型 (模式: {mode})...{Colors.RESET}")

    total_downloaded = 0
    total_failed = 0

    for category in categories:
        data = MODELS[category]
        model_dir = data["dir"]

        print(f"\n{Colors.BLUE}[{category}]{Colors.RESET}")

        # 確保目錄存在
        os.makedirs(model_dir, exist_ok=True)

        for file_info in data["files"]:
            filename = file_info["name"]
            filepath = os.path.join(model_dir, filename)

            # 檢查檔案是否已存在
            if os.path.exists(filepath):
                print(f"\n{Colors.GREEN}✓ 已存在: {filename}{Colors.RESET}")
                continue

            # 下載檔案
            success = download_file(file_info["url"], filepath, filename)

            if success:
                total_downloaded += 1
            else:
                total_failed += 1

    # 總結
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.GREEN}下載完成: {total_downloaded} 個檔案{Colors.RESET}")
    if total_failed > 0:
        print(f"{Colors.RED}下載失敗: {total_failed} 個檔案{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_next_steps():
    """列印後續步驟"""
    print(f"\n{Colors.YELLOW}後續步驟:{Colors.RESET}")
    print(f"  1. 確認所有檔案已下載到 Windows PC")
    print(f"  2. 重啟 ComfyUI: http://100.107.71.38:8188")
    print(f"  3. 檢查節點是否出現: 右鍵 → Add Node → ipadapter")
    print(f"  4. 匯入範例工作流測試")
    print(f"\n{Colors.BLUE}參考文件: /Users/yuan/comfyui_tools/IP_ADAPTER_INSTALLATION_GUIDE.md{Colors.RESET}\n")

def main():
    parser = argparse.ArgumentParser(
        description="ComfyUI IP-Adapter 模型下載工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  python download_ipadapter_models.py --check      # 檢查已下載模型
  python download_ipadapter_models.py --basic      # 下載基礎模型 (CLIP + SD1.5)
  python download_ipadapter_models.py --full       # 下載所有模型 (含 FaceID)
        """
    )

    parser.add_argument("--check", action="store_true", help="檢查已下載的模型")
    parser.add_argument("--basic", action="store_true", help="下載基礎模型")
    parser.add_argument("--full", action="store_true", help="下載所有模型")

    args = parser.parse_args()

    print_header()

    # 警告: 此腳本需要在 Windows PC 上執行或透過網路掛載
    print(f"{Colors.RED}⚠ 重要提醒:{Colors.RESET}")
    print(f"  此腳本需要在 Windows PC (100.107.71.38) 上執行")
    print(f"  或透過遠端桌面/SSH 存取 Windows PC 的檔案系統\n")

    if args.check:
        check_models()
        print_next_steps()

    elif args.basic:
        download_models(mode="basic")
        print_next_steps()

    elif args.full:
        download_models(mode="full")
        print_next_steps()

    else:
        parser.print_help()
        print(f"\n{Colors.YELLOW}提示: 請選擇 --check, --basic 或 --full{Colors.RESET}\n")

if __name__ == "__main__":
    main()
