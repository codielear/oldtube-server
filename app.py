from flask import Flask, jsonify, request, redirect
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "OldTube Proxy Server Running"})

@app.route('/video/<video_id>')
def get_video_url(video_id):
    """Extract direct video URL for a YouTube video"""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        ydl_opts = {
            'format': 'best[height<=360][ext=mp4]/best[height<=480][ext=mp4]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            
            return jsonify({
                "success": True,
                "video_url": video_url,
                "title": info.get('title'),
                "duration": info.get('duration')
            })
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/play/<video_id>')
def play_video(video_id):
    """Redirect to direct video URL (for VideoView)"""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        ydl_opts = {
            'format': 'best[height<=360][ext=mp4]/best[height<=480][ext=mp4]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            
            if video_url:
                return redirect(video_url)
            else:
                return jsonify({"success": False, "error": "No URL found"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/search')
def search():
    """Search YouTube videos"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({"success": False, "error": "No query provided"}), 400
    
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(f"ytsearch20:{query}", download=False)
            
            videos = []
            for entry in results.get('entries', []):
                if entry:
                    videos.append({
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'channel': entry.get('channel') or entry.get('uploader'),
                        'thumbnail': entry.get('thumbnail') or f"https://i.ytimg.com/vi/{entry.get('id')}/mqdefault.jpg",
                        'duration': entry.get('duration')
                    })
            
            return jsonify({"success": True, "videos": videos})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/trending')
def trending():
    """Get popular videos"""
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
        }
        
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
