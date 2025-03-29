import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pytube import YouTube
import instaloader
import yt_dlp as youtube_dl
import glob

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create downloads directory and subdirectories
DOWNLOAD_DIR = Path('downloads')
DOWNLOAD_DIR.mkdir(exist_ok=True)
(DOWNLOAD_DIR / 'instagram').mkdir(exist_ok=True)
(DOWNLOAD_DIR / 'facebook').mkdir(exist_ok=True)
(DOWNLOAD_DIR / 'x').mkdir(exist_ok=True)
(DOWNLOAD_DIR / 'tiktok').mkdir(exist_ok=True)

# Mount static files directory
app.mount("/files", StaticFiles(directory=str(DOWNLOAD_DIR)), name="downloads")

@app.get('/download/tiktok')
def download_tiktok(url: str):
    try:
        ydl_opts = {'outtmpl': str(DOWNLOAD_DIR / 'tiktok' / 'tiktok_video.%(ext)s')}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Encontrar o arquivo baixado
            downloaded_files = glob.glob(str(DOWNLOAD_DIR / 'tiktok' / '*'))
            if not downloaded_files:
                raise HTTPException(status_code=404, detail="Arquivo não encontrado")
            latest_file = max(downloaded_files, key=os.path.getctime)
            filename = os.path.basename(latest_file)
            return {
                "message": "Arquivo baixado com sucesso",
                "file_path": str(latest_file),
                "download_url": f"/files/tiktok/{filename}"
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/download/instagram')
def download_instagram(url: str):
    try:
        L = instaloader.Instaloader(dirname_pattern=str(DOWNLOAD_DIR / 'instagram'))
        post = instaloader.Post.from_shortcode(L.context, url.split('/')[-2])
        L.download_post(post, target=str(DOWNLOAD_DIR / 'instagram'))
        # Encontrar o arquivo de vídeo ou imagem baixado
        downloaded_files = glob.glob(str(DOWNLOAD_DIR / 'instagram' / '*'))
        if not downloaded_files:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        media_file = next((f for f in downloaded_files if not f.endswith('.txt')), None)
        if not media_file:
            raise HTTPException(status_code=404, detail="Arquivo de mídia não encontrado")
        filename = os.path.basename(media_file)
        return {
            "message": "Arquivo baixado com sucesso",
            "file_path": str(media_file),
            "download_url": f"/files/instagram/{filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/download/facebook')
def download_facebook(url: str):
    try:
        ydl_opts = {'outtmpl': str(DOWNLOAD_DIR / 'facebook' / 'facebook_video.%(ext)s')}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Encontrar o arquivo baixado
            downloaded_files = glob.glob(str(DOWNLOAD_DIR / 'facebook' / '*'))
            if not downloaded_files:
                raise HTTPException(status_code=404, detail="Arquivo não encontrado")
            latest_file = max(downloaded_files, key=os.path.getctime)
            filename = os.path.basename(latest_file)
            return {
                "message": "Arquivo baixado com sucesso",
                "file_path": str(latest_file),
                "download_url": f"/files/facebook/{filename}"
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/download/x')
def download_x(url: str):
    try:
        ydl_opts = {'outtmpl': str(DOWNLOAD_DIR / 'x' / 'x_video.%(ext)s')}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Encontrar o arquivo baixado
            downloaded_files = glob.glob(str(DOWNLOAD_DIR / 'x' / '*'))
            if not downloaded_files:
                raise HTTPException(status_code=404, detail="Arquivo não encontrado")
            latest_file = max(downloaded_files, key=os.path.getctime)
            filename = os.path.basename(latest_file)
            return {
                "message": "Arquivo baixado com sucesso",
                "file_path": str(latest_file),
                "download_url": f"/files/x/{filename}"
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/download/{filename}')
async def download_file(filename: str):
    """Download endpoint for converted files"""
    # Procurar o arquivo em todas as pastas de download
    for platform in ['instagram', 'facebook', 'x', 'tiktok']:
        file_path = DOWNLOAD_DIR / platform / filename
        if file_path.exists():
            # Configurar o callback para deletar o arquivo após o download
            def cleanup():
                try:
                    os.remove(str(file_path))
                    print(f"Arquivo {filename} deletado com sucesso")
                except Exception as e:
                    print(f"Erro ao deletar arquivo {filename}: {str(e)}")

            return FileResponse(
                path=str(file_path),
                filename=filename,
                media_type='application/octet-stream',
                headers={"Content-Disposition": f"attachment; filename={filename}"},
                background=cleanup  # FastAPI executará esta função após enviar o arquivo
            )
    
    # Se o arquivo não for encontrado em nenhuma pasta
    raise HTTPException(
        status_code=404,
        detail="Arquivo não encontrado ou expirado"
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))  # Padrão da Render é 10000, não 8000
    uvicorn.run(app, port=port)