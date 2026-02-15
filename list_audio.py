import pyaudio

p = pyaudio.PyAudio()
print("Available Audio Devices:\n")
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    if dev.get('maxInputChannels') > 0:
        print(f"Index {i}: {dev.get('name')}")
        print(f"  Default Sample Rate: {dev.get('defaultSampleRate')}")
        print(f"  Input Channels: {dev.get('maxInputChannels')}")
        
        # Test 16000
        try:
            if p.is_format_supported(16000, input_device=i, input_format=pyaudio.paInt16, input_channels=1):
                print("  16000 Hz: Supported")
            else:
                print("  16000 Hz: Not Supported")
        except Exception:
            print("  16000 Hz: Error testing")
        print("-" * 20)

default_input = p.get_default_input_device_info()
print(f"\nDefault Input Device: Index {default_input['index']} - {default_input['name']}")
p.terminate()
