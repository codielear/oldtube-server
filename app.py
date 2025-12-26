from flask import Flask, jsonify, request, redirect, Response
import yt_dlp
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "OldTube Proxy Server Running"})

@app.route('/video/<video_id>')
def get_video_url(video_id):
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        # Try format 18 first (360p with audio), fallback to best single format
        ydl_opts = {
            'format': 'best[ext=mp4][height<=480]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # For merged formats, url might be in requested_formats
            video_url = info.get('url')
            if not video_url and 'requested_formats' in info:
                video_url = info['requested_formats'][0].get('url')
            return jsonify({
                "success": True,
                "video_url": video_url,
                "title": info.get('title'),
                "duration": info.get('duration'),
                "format": info.get('format')
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/stream/<video_id>')
def stream_video(video_id):
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {
            'format': 'best[ext=mp4][height<=480]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            if not video_url and 'requested_formats' in info:
                video_url = info['requested_formats'][0].get('url')
            
            if not video_url:
                return jsonify({"success": False, "error": "No URL found"}), 500
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            def generate():
                with requests.get(video_url, stream=True, headers=headers) as r:
                    for chunk in r.iter_content(chunk_size=8192):
                        yield chunk
            
            return Response(generate(), mimetype='video/mp4')
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"success": False, "error": "No query provided"}), 400
    
    try:
        ydl_opts = {'quiet': True, 'extract_flat': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(f"ytsearch20:{query}", download=False)
            videos = []
            for entry in results.get('entries', []):
                if entry:
                    videos.append({
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'channel': entry.get('channel') or entry.get('uploader'),
                        'thumbnail': f"https://i.ytimg.com/vi/{entry.get('id')}/mqdefault.jpg",
                        'duration': entry.get('duration')
                    })
            return jsonify({"success": True, "videos": videos})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/trending')
def trending():
    try:
        ydl_opts = {'quiet': True, 'extract_flat': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info("ytsearch20:music 2024", download=False)
            videos = []
            for entry in results.get('entries', [])[:20]:
                if entry:
                    videos.append({
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'channel': entry.get('channel') or entry.get('uploader'),
                        'thumbnail': f"https://i.ytimg.com/vi/{entry.get('id')}/mqdefault.jpg",
                        'duration': entry.get('duration')
                    })
            return jsonify({"success": True, "videos": videos})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
