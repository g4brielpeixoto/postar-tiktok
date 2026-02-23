from tiktok_uploader.upload import TikTokUploader

# single video
uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_video('video.mp4', description='Vìdeo de teste')