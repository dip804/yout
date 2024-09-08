from flask import Flask, request, render_template, jsonify
import requests
import youtube_dl

app = Flask(__name__)

# Function to extract subtitles from YouTube video
def extract_subtitles(video_url):
    try:
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'skip_download': True,
            'outtmpl': '%(id)s.%(ext)s',
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            subtitles = info.get("requested_subtitles")
            if subtitles:
                return {"subtitles": subtitles, "title": info.get("title")}
            else:
                return {"error": "Subtitles not available."}

    except Exception as e:
        return {"error": str(e)}

@app.route('/subtitles', methods=['POST'])
def get_subtitles():
    video_url = request.form.get('url')
    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400
    
    subtitles_data = extract_subtitles(video_url)
    
    return render_template('result.html', data=subtitles_data)

@app.route('/')
def index():
    return '''
    <form method="POST" action="/subtitles">
      <label for="url">YouTube Video URL:</label>
      <input type="text" name="url" id="url" required>
      <button type="submit">Get Subtitles</button>
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)

