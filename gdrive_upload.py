"""
Google Drive 圖片上傳工具
上傳圖片到 Google Drive 並獲取公開分享連結
"""
import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Google Drive API 權限範圍
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# 憑證檔案路徑
CREDENTIALS_FILE = "/Users/yuan/AIGC-system/oauth_credentials.json"
TOKEN_FILE = "/Users/yuan/comfyui_tools/gdrive_token.pickle"

# Google Drive 目標資料夾 ID（可選）
FOLDER_ID = "1TwiNq2RcuakSaXHIrwwizttSpBNgAkLb"  # 從 CLAUDE.md


def get_drive_service():
    """獲取 Google Drive API 服務"""
    creds = None

    # 檢查是否有已儲存的 token
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # 如果沒有有效憑證，重新授權
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # 儲存憑證供下次使用
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)


def upload_image(image_path: str, folder_id: str = None) -> dict:
    """
    上傳圖片到 Google Drive

    Args:
        image_path: 本地圖片路徑
        folder_id: Google Drive 資料夾 ID（可選）

    Returns:
        dict: 包含 file_id, web_view_link, direct_link
    """
    service = get_drive_service()

    file_name = Path(image_path).name

    # 檔案 metadata
    file_metadata = {
        'name': file_name,
    }

    if folder_id:
        file_metadata['parents'] = [folder_id]

    # 上傳檔案
    media = MediaFileUpload(
        image_path,
        mimetype='image/png',
        resumable=True
    )

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink, webContentLink'
    ).execute()

    file_id = file.get('id')

    # 設定為公開可訪問
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }

    service.permissions().create(
        fileId=file_id,
        body=permission
    ).execute()

    # 建立直接訪問連結
    direct_link = f"https://drive.google.com/uc?id={file_id}"

    return {
        'file_id': file_id,
        'web_view_link': file.get('webViewLink'),
        'web_content_link': file.get('webContentLink'),
        'direct_link': direct_link
    }


def upload_multiple_images(image_paths: list, folder_id: str = None) -> list:
    """
    批次上傳多張圖片

    Args:
        image_paths: 圖片路徑列表
        folder_id: Google Drive 資料夾 ID

    Returns:
        list: 上傳結果列表
    """
    results = []

    for image_path in image_paths:
        try:
            result = upload_image(image_path, folder_id)
            result['local_path'] = image_path
            result['success'] = True
            results.append(result)
            print(f"✓ {Path(image_path).name}")
        except Exception as e:
            results.append({
                'local_path': image_path,
                'success': False,
                'error': str(e)
            })
            print(f"✗ {Path(image_path).name}: {e}")

    return results


if __name__ == "__main__":
    # 測試上傳
    import sys

    if len(sys.argv) > 1:
        test_image = sys.argv[1]

        if os.path.exists(test_image):
            print(f"上傳圖片: {test_image}")
            result = upload_image(test_image, FOLDER_ID)

            print(f"\n✅ 上傳成功！")
            print(f"File ID: {result['file_id']}")
            print(f"直接連結: {result['direct_link']}")
        else:
            print(f"❌ 檔案不存在: {test_image}")
    else:
        print("用法: python gdrive_upload.py <圖片路徑>")
