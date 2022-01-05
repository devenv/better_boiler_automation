import json
import os
import sys

import click
import google.auth.transport.grpc
import google.auth.transport.requests
import google.oauth2.credentials

from google.assistant.embedded.v1alpha2 import embedded_assistant_pb2, embedded_assistant_pb2_grpc

from logger import get_logger


ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'
DEFAULT_GRPC_DEADLINE = 60 * 3 + 5

def load_config():
    with open(os.path.join(sys.path[0], "assistant/device_config.json"), "r") as f:
        return json.load(f)


class Assistant(object):

    config = load_config()

    def __init__(self):
        self.device_model_id = self.config['device_model_id']
        self.device_id = self.config['device_id']

        try:
            with open(os.path.join(click.get_app_dir('google-oauthlib-tool'), 'credentials.json'), 'r') as f:
                credentials = google.oauth2.credentials.Credentials(token=None, **json.load(f))
                http_request = google.auth.transport.requests.Request()
                credentials.refresh(http_request)
        except Exception as e:
            get_logger().exception(e)
            return

        channel = google.auth.transport.grpc.secure_authorized_channel(credentials, http_request, ASSISTANT_API_ENDPOINT)

        self.assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(channel)

    def __enter__(self):
        return self

    def __exit__(self, etype, e, traceback):
        if e:
            return False

    def ask(self, text_query: str):
        def iter_assist_requests():
            config = embedded_assistant_pb2.AssistConfig(
                audio_out_config=embedded_assistant_pb2.AudioOutConfig(
                    encoding='LINEAR16',
                    sample_rate_hertz=16000,
                    volume_percentage=100,
                ),
                dialog_state_in=embedded_assistant_pb2.DialogStateIn(
                    language_code='en-US',
                    conversation_state=None,
                    is_new_conversation=True,
                ),
                device_config=embedded_assistant_pb2.DeviceConfig(
                    device_id=self.device_id,
                    device_model_id=self.device_model_id,
                ),
                text_query=text_query,
            )
            config.screen_out_config.screen_mode = embedded_assistant_pb2.ScreenOutConfig.PLAYING
            req = embedded_assistant_pb2.AssistRequest(config=config)
            yield req

        return list(self.assistant.Assist(iter_assist_requests(), DEFAULT_GRPC_DEADLINE))
        