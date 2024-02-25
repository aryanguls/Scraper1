import requests

def download_mp4(url, save_path):
    # Send a GET request to the URL
    response = requests.get(url, stream=True)
    
    # Open a local file with write-binary mode
    with open(save_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                file.write(chunk)
    
    print(f"Video downloaded: {save_path}")

# Example usage
video_url = "https://video.adsoftheworld.com/ze5froq9qpulugbvprn00vnpsnr4"
save_path = "downloaded_video.mp4"
download_mp4(video_url, save_path)
