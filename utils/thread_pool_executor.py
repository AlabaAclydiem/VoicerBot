from concurrent.futures import ThreadPoolExecutor
from service.amplitude_analytics import send_event_to_amplitude

executor = ThreadPoolExecutor(max_workers=10)

def process_event(event_name, user_id, description):
    executor.submit(send_event_to_amplitude, event_name, user_id, description)