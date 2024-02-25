from pytube import YouTube

def download_youtube_video(video_url, save_path):
    yt = YouTube(video_url)
    stream = yt.streams.filter(file_extension='mp4').first()
    if stream:
        stream.download(save_path)
        print(f"Video downloaded: {stream.default_filename}")
    else:
        print("No downloadable video found.")

# Example usage
video_url = "https://www.youtube.com/embed/hAnpZ6Uy6Ho?autoplay=0&rel=0"
save_path = "./"  # Current directory, you can specify a different path

download_youtube_video(video_url, save_path)