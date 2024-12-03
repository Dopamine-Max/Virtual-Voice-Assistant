import urllib.request
import re
import webbrowser

def play_video(title):
    html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={title}")
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    url = "https://www.youtube.com/watch?v=" + video_ids[0]
    webbrowser.open(url)
