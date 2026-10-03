import os
import uuid
import tempfile
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
from pydub import AudioSegment
from pydub.silence import split_on_silence

app = Flask(__name__)

# Configure directories using system temp directory for safety
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'silence_remover_uploads')
OUTPUT_FOLDER = os.path.join(tempfile.gettempdir(), 'silence_remover_outputs')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB max

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac', 'ogg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Supported formats: MP3, WAV, M4A, FLAC, OGG'}), 400
        
    # Get parameters
    threshold = request.form.get('threshold', -40, type=int)
    duration_s = request.form.get('duration', 0.3, type=float)
    duration_ms = int(duration_s * 1000)
    padding = request.form.get('padding', 200, type=int)
    out_format = request.form.get('format', 'original', type=str)
    
    filename = secure_filename(file.filename)
    unique_id = str(uuid.uuid4())
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{filename}")
    output_filename = f"processed_{filename}"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{unique_id}_{output_filename}")
    
    try:
        file.save(input_path)
        
        # Load audio using pydub
        audio = AudioSegment.from_file(input_path)
        orig_len = len(audio) / 1000.0
        
        # Split on silence
        # keep_silence keeps padding (in ms) of the detected silence segments that are > min_silence_len.
        # Short silences (< duration_ms) are kept automatically because they don't trigger the split.
        audio_chunks = split_on_silence(
            audio,
            min_silence_len=duration_ms,
            silence_thresh=threshold,
            keep_silence=padding
        )
        
        if not audio_chunks:
            return jsonify({'error': 'No audio remaining after removing silence. Please try a higher duration or lower threshold.'}), 400
            
        # Combine non-silent chunks back together
        processed_audio = AudioSegment.empty()
        for chunk in audio_chunks:
            processed_audio += chunk
            
        # Export processed audio
        ext = filename.rsplit('.', 1)[1].lower()
        if out_format and out_format != 'original':
            ext = out_format
            output_filename = f"processed_{filename.rsplit('.', 1)[0]}.{ext}"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{unique_id}_{output_filename}")
            
        format_name = ext if ext != 'm4a' else 'mp4'  # pydub uses mp4 for m4a
        processed_audio.export(output_path, format=format_name)
        
        new_len = len(processed_audio) / 1000.0
        removed = orig_len - new_len
        
        return jsonify({
            'success': True,
            'original_duration': round(orig_len, 2),
            'new_duration': round(new_len, 2),
            'silence_removed': round(removed, 2),
            'download_url': f"/download/{unique_id}_{output_filename}"
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f"Failed to process audio: {str(e)}"}), 500
    finally:
        # Clean up the input file to save space
        if os.path.exists(input_path):
            try:
                os.remove(input_path)
            except:
                pass
        
@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if not os.path.exists(filepath):
        return "File not found", 404
        
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
