import os
from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi, CouldNotRetrieveTranscript, NoTranscriptFound
from pytube import YouTube

app = Flask(__name__)

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the video link submission
@app.route('/extract', methods=['POST'])
def extract():
    video_url = request.form['video_url']
    preferred_language = request.form.get('language', 'en')  # Default to English if no language is specified

    try:
        # Extract video ID from the YouTube URL
        yt = YouTube(video_url)
        video_id = yt.video_id

        # Try to fetch the transcript for the preferred language
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[preferred_language])
        extracted_text = "\n".join([t['text'] for t in transcript])
        return render_template('result.html', extracted_text=extracted_text)

    except NoTranscriptFound:
        # If no transcripts are found in the preferred language, try to get any available transcript
        available_transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        
        try:
            # Try to fetch a transcript in any available language (including auto-generated)
            transcript = available_transcripts.find_transcript(['en', 'hi', 'es', 'fr', 'de', 'zh'])
            extracted_text = "\n".join([t['text'] for t in transcript.fetch()])
            return render_template('result.html', extracted_text=extracted_text)
        except Exception:
            error_message = "No transcripts available in any of the requested languages. " \
                            "This video might only have auto-generated subtitles or no subtitles at all."
            return render_template('result.html', extracted_text=error_message)

    except CouldNotRetrieveTranscript:
        error_message = "Could not retrieve transcript for this video. It may not have subtitles available."
        return render_template('result.html', extracted_text=error_message)

    except Exception as e:
        # General error handling (e.g., invalid URL, network issues)
        error_message = f"An error occurred: {str(e)}. Please try another video or check if subtitles are available."
        return render_template('result.html', extracted_text=error_message)

# Main entry point for running the Flask app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
