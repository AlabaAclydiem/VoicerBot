from amplitude import Amplitude, BaseEvent
from settings import settings

amplitude = Amplitude(settings.AMPLITUDE_API)

def send_event_to_amplitude(event_name, user_id, properties):
    amplitude.track(
        BaseEvent(
            event_type=event_name,
            user_id=user_id,
            event_properties={
                "info": properties 
            }
        )
    )