import requests
import sys

def verify():
    url = 'http://127.0.0.1:5000/process'
    print("Testing against Flask backend...")
    
    try:
        with open('test_audio.wav', 'rb') as f:
            files = {'audio': ('test_audio.wav', f, 'audio/wav')}
            data = {'threshold': -40, 'duration': 0.3}
            
            response = requests.post(url, files=files, data=data)
            
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Response:", result)
            
            original_duration = result.get('original_duration')
            new_duration = result.get('new_duration')
            
            # Original should be 3.9s
            # We expect the 0.8s silence to be removed, but the 0.1s silence to stay.
            # So new duration should be ~3.1s
            if 3.0 < new_duration < 3.2:
                print("TEST PASSED: The new duration is correct!")
                sys.exit(0)
            else:
                print(f"TEST FAILED: Expected new_duration close to 3.1, got {new_duration}")
                sys.exit(1)
        else:
            print("TEST FAILED: API error:", response.text)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error connecting to Flask app: {e}")
        print("Please ensure app.py is running on port 5000.")
        sys.exit(1)

if __name__ == '__main__':
    verify()
