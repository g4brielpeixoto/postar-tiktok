import os
import boto3
import re
from tiktok_uploader.upload import TikTokUploader

# Configuration from environment variables
S3_BUCKET = os.getenv('S3_BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
# Keys are optional if running on EC2 with IAM Role
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
COOKIES_FILE = 'cookies.txt'

PRONTOS_PREFIX = 'biblia/videos/prontos/'
POSTADOS_PREFIX = 'biblia/videos/postados/'

# Initialize S3 client. Boto3 will automatically use EC2 Instance Profile 
# if credentials are not explicitly passed.
s3_params = {'region_name': AWS_REGION}
if AWS_ACCESS_KEY and AWS_SECRET_KEY:
    s3_params['aws_access_key_id'] = AWS_ACCESS_KEY
    s3_params['aws_secret_access_key'] = AWS_SECRET_KEY

s3 = boto3.client('s3', **s3_params)

def get_oldest_video():
    response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=PRONTOS_PREFIX)
    if 'Contents' not in response:
        return None
    
    # Filter out the prefix itself and ensure we only get .mp4 files
    videos = [obj for obj in response['Contents'] if obj['Key'] != PRONTOS_PREFIX and obj['Key'].lower().endswith('.mp4')]
    if not videos:
        return None
    
    # Sort by LastModified (ascending) to get the oldest
    videos.sort(key=lambda x: x['LastModified'])
    return videos[0]['Key']

def extract_chapter(filename):
    # Pattern: Gênesis_1_1771864627132.mp4
    # Split by '_' and take the second part
    try:
        parts = filename.split('_')
        if len(parts) > 1:
            return parts[1]
    except Exception:
        pass
    return "1" # Fallback

def move_to_postados(video_key):
    filename = os.path.basename(video_key)
    new_key = f"{POSTADOS_PREFIX}{filename}"
    
    # Copy to new location
    s3.copy_object(
        Bucket=S3_BUCKET,
        CopySource={'Bucket': S3_BUCKET, 'Key': video_key},
        Key=new_key
    )
    # Delete from old location
    s3.delete_object(Bucket=S3_BUCKET, Key=video_key)
    print(f"Moved {video_key} to {new_key}")

def main():
    if not S3_BUCKET:
        print("Error: S3_BUCKET_NAME environment variable not set.")
        return

    if not os.path.exists(COOKIES_FILE):
        print(f"Error: {COOKIES_FILE} not found. Please provide your TikTok cookies.")
        return

    print("Checking for videos...")
    video_key = get_oldest_video()
    
    if not video_key:
        print("No videos found in 'prontos' folder.")
        return

    filename = os.path.basename(video_key)
    print(f"Found oldest video: {filename}")
    
    local_filename = 'video_to_upload.mp4'
    s3.download_file(S3_BUCKET, video_key, local_filename)
    
    chapter = extract_chapter(filename)
    description = f"Hoje vamos ler Genesis {chapter}..."
    
    print(f"Uploading to TikTok with description: {description}")
    
    try:
        uploader = TikTokUploader(cookies=COOKIES_FILE)
        # Set headless=True for Docker compatibility
        uploader.upload_video(local_filename, description=description, headless=True)
        
        print("Upload successful!")
        move_to_postados(video_key)
        
    except Exception as e:
        print(f"Error during upload: {e}")
    finally:
        if os.path.exists(local_filename):
            os.remove(local_filename)

if __name__ == "__main__":
    main()

