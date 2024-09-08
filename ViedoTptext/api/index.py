from flask import Flask, request, render_template, jsonify
import youtube_dl

app = Flask(__name__)

# Extract subtitles from YouTube video
def extract_subtitles(video_url):
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'subtitleslangs': ['en'],
        'outtmpl': '%(id)s.%(ext)s'
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        subtitles = info_dict.get('subtitles', {}).get('en', [])
        if subtitles:
            return subtitles[0].get('url')
        else:
            return None

# Root route for form
@app.route('/')
def index():
    return '''
    <form method="POST" action="/subtitles">
      <label for="url">YouTube Video URL:</label>
      <input type="text" name="url" id="url" required>
      <button type="submit">Get Subtitles</button>
    </form>
    '''

# Route to get subtitles
@app.route('/subtitles', methods=['POST'])
def get_subtitles():
    video_url = request.form.get('url')
    
    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400
    
    subtitles_url = extract_subtitles(video_url)
    
    if subtitles_url:
        return render_template('result.html', data=subtitles_url)
    else:
        return jsonify({"error": "No subtitles available for this video"}), 404

if __name__ == "__main__":
    app.run()
