from pydub import AudioSegment
from pydub.generators import Sine
import sys

def main():
    try:
        print("Generating test_audio.wav...")
        # Generate 1 second tones
        tone = Sine(440).to_audio_segment(duration=1000).apply_gain(-10) # 1 sec, -10 dB
        
        # Silences
        short_silence = AudioSegment.silent(duration=100) # 0.1s
        long_silence = AudioSegment.silent(duration=800) # 0.8s
        
        # Combine
        test_audio = tone + short_silence + tone + long_silence + tone
        
        # Export
        test_audio.export("test_audio.wav", format="wav")
        print(f"Success! Generated test_audio.wav with duration: {len(test_audio)} ms")
        print("Structure: 1.0s tone -> 0.1s silence -> 1.0s tone -> 0.8s silence -> 1.0s tone")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
