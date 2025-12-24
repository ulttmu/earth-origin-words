"""
ComfyUI API Client - 連接到 Windows PC 的 ComfyUI
"""
import json
import urllib.request
import urllib.parse
import uuid
import time
from pathlib import Path

COMFYUI_URL = "http://100.107.71.38:8188"

def get_system_stats():
    """取得系統狀態"""
    url = f"{COMFYUI_URL}/system_stats"
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read())

def get_queue():
    """取得任務佇列狀態"""
    url = f"{COMFYUI_URL}/queue"
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read())

def get_history(prompt_id=None):
    """取得歷史記錄"""
    url = f"{COMFYUI_URL}/history"
    if prompt_id:
        url += f"/{prompt_id}"
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read())

def upload_image(image_path, subfolder="", overwrite=False):
    """上傳圖片到 ComfyUI"""
    import mimetypes

    url = f"{COMFYUI_URL}/upload/image"

    filename = Path(image_path).name
    content_type = mimetypes.guess_type(image_path)[0] or 'image/png'

    with open(image_path, 'rb') as f:
        image_data = f.read()

    boundary = uuid.uuid4().hex

    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
        f'Content-Type: {content_type}\r\n\r\n'
    ).encode() + image_data + (
        f'\r\n--{boundary}\r\n'
        f'Content-Disposition: form-data; name="subfolder"\r\n\r\n{subfolder}\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="overwrite"\r\n\r\n{str(overwrite).lower()}\r\n'
        f'--{boundary}--\r\n'
    ).encode()

    req = urllib.request.Request(
        url,
        data=body,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read())

def queue_prompt(workflow):
    """提交工作流到佇列"""
    url = f"{COMFYUI_URL}/prompt"
    client_id = str(uuid.uuid4())

    payload = {
        "prompt": workflow,
        "client_id": client_id
    }

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'}
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read())
        result['client_id'] = client_id
        return result

def wait_for_completion(prompt_id, timeout=300, check_interval=1):
    """等待任務完成"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        history = get_history(prompt_id)

        if prompt_id in history:
            outputs = history[prompt_id].get('outputs', {})
            if outputs:
                return outputs

        time.sleep(check_interval)

    raise TimeoutError(f"任務 {prompt_id} 超時")

def download_image(filename, subfolder="", output_path=None):
    """下載生成的圖片"""
    params = urllib.parse.urlencode({
        "filename": filename,
        "subfolder": subfolder,
        "type": "output"
    })
    url = f"{COMFYUI_URL}/view?{params}"

    with urllib.request.urlopen(url, timeout=30) as response:
        image_data = response.read()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(image_data)
        return output_path

    return image_data


if __name__ == "__main__":
    print("=== ComfyUI 連線測試 ===\n")

    # 測試連線
    try:
        stats = get_system_stats()
        print("✅ 連線成功！")
        print(f"   ComfyUI 版本: {stats['system']['comfyui_version']}")
        print(f"   GPU: {stats['devices'][0]['name'].split(':')[1].strip()}")
        print(f"   VRAM: {stats['devices'][0]['vram_total'] / 1024**3:.1f} GB")
        print(f"   VRAM 可用: {stats['devices'][0]['vram_free'] / 1024**3:.1f} GB")
    except Exception as e:
        print(f"❌ 連線失敗: {e}")
        exit(1)

    # 檢查佇列
    print("\n=== 佇列狀態 ===")
    queue = get_queue()
    print(f"   執行中: {len(queue.get('queue_running', []))} 個任務")
    print(f"   等待中: {len(queue.get('queue_pending', []))} 個任務")

    print("\n✅ 準備就緒，可以提交工作流！")
