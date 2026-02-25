import os
import sys
import boto3
import json
import time

def inject_local_storage(browser_context, storage_file):
    if os.path.exists(storage_file):
        with open(storage_file, 'r') as f:
            storage_data = json.load(f)
        
        # O Playwright exige que estejamos na página correta para injetar localStorage
        page = browser_context.new_page()
        page.goto("https://www.tiktok.com")
        
        script = "() => {"
        for key, value in storage_data.items():
            # Escapa aspas para o JS
            safe_value = value.replace('"', '\\"')
            script += f'localStorage.setItem("{key}", "{safe_value}");'
        script += "}"
        
        page.evaluate(script)
        page.close()
        print("LocalStorage injetado com sucesso.")
    else:
        print("Aviso: localStorage.json não encontrado. Prosseguindo apenas com cookies.")

# ... (funções extract_chapter, get_oldest_video, move_to_postados iguais) ...

def extract_chapter(filename):
    try:
        parts = filename.split('_')
        if len(parts) > 1: return parts[1]
    except: pass
    return "1"

def get_oldest_video(s3, bucket, prefix):
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if 'Contents' not in response: return None
    videos = [obj for obj in response['Contents'] if obj['Key'] != prefix and obj['Key'].lower().endswith('.mp4')]
    if not videos: return None
    videos.sort(key=lambda x: x['LastModified'])
    return videos[0]['Key']

def move_to_postados(s3, bucket, video_key, postados_prefix):
    filename = os.path.basename(video_key)
    new_key = f"{postados_prefix}{filename}"
    s3.copy_object(Bucket=bucket, CopySource={'Bucket': bucket, 'Key': video_key}, Key=new_key)
    s3.delete_object(Bucket=bucket, Key=video_key)
    print(f"Moved {video_key} to {new_key}")

def main():
    print("Main script started...")
    sys.stdout.flush()

    S3_BUCKET = os.getenv('S3_BUCKET_NAME')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    COOKIES_FILE = 'cookies.txt'
    STORAGE_FILE = 'localStorage.json'
    PRONTOS_PREFIX = 'biblia/videos/prontos/'
    POSTADOS_PREFIX = 'biblia/videos/postados/'

    s3_params = {'region_name': AWS_REGION}
    if AWS_ACCESS_KEY and AWS_SECRET_KEY:
        s3_params['aws_access_key_id'] = AWS_ACCESS_KEY
        s3_params['aws_secret_access_key'] = AWS_SECRET_KEY
    s3 = boto3.client('s3', **s3_params)

    video_key = get_oldest_video(s3, S3_BUCKET, PRONTOS_PREFIX)
    if not video_key:
        print("No videos found.")
        return

    local_filename = 'video_to_upload.mp4'
    s3.download_file(S3_BUCKET, video_key, local_filename)
    
    description = f"Hoje vamos ler Genesis {extract_chapter(os.path.basename(video_key))}"
    
    try:
        from tiktok_uploader.upload import TikTokUploader
        
        # Para injetar o localStorage, teríamos que hackear a lib mais a fundo.
        # Infelizmente a lib cria o próprio browser e contexto internamente.
        # Vou tentar passar o localStorage via cookies, que é o que ela aceita.
        
        uploader = TikTokUploader(cookies=COOKIES_FILE)
        print("Iniciando upload...")
        success = uploader.upload_video(local_filename, description=description)
        
        if success:
            print("Upload successful!")
            move_to_postados(s3, S3_BUCKET, video_key, POSTADOS_PREFIX)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if os.path.exists(local_filename): os.remove(local_filename)

if __name__ == "__main__":
    main()
