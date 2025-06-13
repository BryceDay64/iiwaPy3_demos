from python_client.EMG_trigger import EmgTrigger
import time


server_ip = "127.0.0.1"
port = 9220

emg = EmgTrigger(server_ip, port)

emg.get_emg_channel()

trigger = False
while not trigger:
    samples = emg.sample_get()
    for ch in samples['channels']:
        trigger = emg.emg_trigger_boolean(ch, 125)
    time.sleep(0.2)
print('trigger')