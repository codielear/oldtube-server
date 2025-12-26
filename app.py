from flask import Flask, jsonify, request, Response
import yt_dlp
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "OldTube Proxy Server Running"})

@app.route('/video/<video_id>')
def get_video_url(video_id):
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {'format': 'b', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            return jsonify({
                "success": True,
                "video_url": video_url,
                "title": info.get('title')
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/stream/<video_id>')
def stream_video(video_id):
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {'format': 'b', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            
            if not video_url:
                return jsonify({"success": False, "error": "No URL"}), 500
        
        # Use ffmpeg to convert HLS to MP4 and stream
        cmd = [
            'ffmpeg',
            '-i', video_url,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-movflags', 'frag_keyframe+empty_moov',
            '-f', 'mp4',
            'pipe:1'
        ]
        
        def generate():
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            while True:
                chunk = process.stdout.read(8192)
                if not chunk:
                    break
                yield chunk
            process.wait()
        
        return Response(generate(), mimetype='video/mp4')
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"success": False, "error": "No query"}), 400
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
                        'thumbnail': f"https://i.ytimg.com/vi/{entry.get('id')}/mqdefault.jpg"
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
                        'thumbnail': f"https://i.ytimg.com/vi/{entry.get('id')}/mqdefault.jpg"
                    })
            return jsonify({"success": True, "videos": videos})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
