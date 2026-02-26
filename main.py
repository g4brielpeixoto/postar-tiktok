import os
import sys
import boto3
import json
import random
import time

def inject_local_storage(browser_context, storage_file):
    if os.path.exists(storage_file):
        with open(storage_file, 'r') as f:
            storage_data = json.load(f)
        
        page = browser_context.new_page()
        page.goto("https://www.tiktok.com")
        
        script = "() => {"
        for key, value in storage_data.items():
            safe_value = value.replace('"', '\\"')
            script += f'localStorage.setItem("{key}", "{safe_value}");'
        script += "}"
        
        page.evaluate(script)
        page.close()
        print("LocalStorage injetado com sucesso.")
    else:
        print("Aviso: localStorage.json não encontrado. Prosseguindo apenas com cookies.")

def generate_description(filename):
    # Extrai o Livro e o Capítulo do nome do arquivo
    # Exemplo: Gênesis_4_1771868799092.mp4
    # parts[0] = Gênesis, parts[1] = 4
    parts = filename.split('_')
    book = parts[0] if len(parts) > 0 else "Bíblia"
    chapter = parts[1] if len(parts) > 1 else "1"
    
    # Limpa extensões se estiverem presentes
    book = book.replace('.mp4', '')
    chapter = chapter.replace('.mp4', '')

    templates = [
        "📖🔥 Hoje vamos ler [Livro] [Capítulo] — Prepare seu coração, porque essa Palavra pode transformar o seu dia!",
        "✨📜 Está pronto? Hoje a leitura é [Livro] [Capítulo] — Deus pode falar com você através desse capítulo!",
        "🙏📖 Vamos mergulhar juntos em [Livro] [Capítulo] — Ouça com fé e atenção!",
        "🔥👀 Você precisa ouvir isso! Hoje estamos em [Livro] [Capítulo] — Palavra poderosa!",
        "📚💡 Mais um dia na presença de Deus! Leitura de [Livro] [Capítulo] começa agora!",
        "🌅📖 Comece o dia com propósito: [Livro] [Capítulo] — deixe Deus conduzir seus passos!",
        "⚔️🔥 Capítulo forte hoje! Vamos ler [Livro] [Capítulo] — prepare-se!",
        "🕊️📜 Palavra viva para sua vida: [Livro] [Capítulo] — escute até o final!",
        "⏳📖 Tire alguns minutos para Deus — hoje é [Livro] [Capítulo]!",
        "💛📚 Se essa Palavra tocar você, compartilhe! Leitura de [Livro] [Capítulo] começa agora!",
        "📖🌟 Deus ainda fala! Hoje vamos ler [Livro] [Capítulo] — fique comigo!",
        "🔥📜 Um capítulo que pode mudar sua história: [Livro] [Capítulo]!",
        "🙌📖 Vamos crescer espiritualmente juntos — hoje é [Livro] [Capítulo]!",
        "👂✨ Ouça com atenção: [Livro] [Capítulo] — pode ser a resposta que você precisava!",
        "💬📜 Deus tem algo pra te dizer hoje em [Livro] [Capítulo]!",
        "📖❤️ Um capítulo por dia, alimentando a alma — [Livro] [Capítulo]!",
        "🔔📚 Pare tudo e venha ouvir [Livro] [Capítulo] — Palavra que edifica!",
        "🕯️📖 Momento de paz e reflexão: [Livro] [Capítulo] começa agora!",
        "🌊📜 Mergulhe fundo na Palavra: hoje é [Livro] [Capítulo]!",
        "🔥🙏 Fé renovada com [Livro] [Capítulo] — ouça até o fim!",
        "📖💥 Capítulo impactante hoje! Vamos para [Livro] [Capítulo]!",
        "🌿📚 Alimente seu espírito com [Livro] [Capítulo]!",
        "✝️📖 Se você ama a Palavra, acompanhe [Livro] [Capítulo] comigo!",
        "💫📜 Um novo capítulo, uma nova direção — [Livro] [Capítulo]!",
        "🛐📖 Tempo de ouvir Deus através de [Livro] [Capítulo]!",
        "🔥📚 Palavra forte, direta e viva — hoje: [Livro] [Capítulo]!",
        "🌞📖 Começando mais um dia com [Livro] [Capítulo] — que Deus fale ao seu coração!",
        "👑📜 A Bíblia é viva! Hoje vamos ler [Livro] [Capítulo]!",
        "🙏✨ Capítulo do dia: [Livro] [Capítulo] — receba essa Palavra!",
        "📖🚀 Projeto Bíblia completa! Hoje estamos em [Livro] [Capítulo] — vem comigo!"
    ]
    
    hashtags = "#biblia #fe #devocional #jesus #oracao"
    
    # Escolhe um template aleatório
    template = random.choice(templates)
    
    # Substitui os placeholders
    final_desc = template.replace("[Livro]", book).replace("[Capítulo]", chapter)
    
    return f"{final_desc}\n\n{hashtags}"

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
    
    filename_base = os.path.basename(video_key)
    description = generate_description(filename_base)
    
    print(f"Uploading: {filename_base}")
    print(f"Description: {description}")
    sys.stdout.flush()
    
    try:
        from tiktok_uploader.upload import TikTokUploader
        
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
