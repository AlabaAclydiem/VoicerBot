from service.amplitude_analytics import send_event_to_amplitude
from settings import executor

def process_event(event_name, user_id, description):
    executor.submit(send_event_to_amplitude, event_name, user_id, description)