import subprocess

def download_vimeo(url, save_path=None):
    command = ['yt-dlp', url]
    if save_path:
        command += ['-o', save_path]
    result = subprocess.run(command, capture_output=True)
    if result.returncode == 0:
        print("Video downloaded successfully.")
    else:
        print("Error downloading video.")

# Example usage
vimeo_url = "https://player.vimeo.com/video/873015036"
download_vimeo(vimeo_url)
