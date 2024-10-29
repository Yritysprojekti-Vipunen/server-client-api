from openai import OpenAI
from dotenv import load_dotenv
import os
import base64
from IPython.display import display, Image, Audio
import cv2
import time

load_dotenv()

class ChatBot:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get("API_KEY")
        )
        self.system_message = "You are an helpful assistant who receives instructions and helps to analyze data. The data can be in image, audio or video form. You answer in the language of the question."
        self.model: None|str = None
        self.max_tokens: int = 200



    def handle_no_attachment(self, messages: list, question):
        messages.append(
                {
                    "role": "user",
                    "content": question
                }
            )

    def handle_image(self, attachment, messages: list, question):
        image_path = attachment
        image_data = ""

        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": question
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            }
        )

    def handle_audio(self, attachment, messages: list, question):

        audio_transcription = ""
            
        with open(attachment, "rb") as audio_file:
            audio_transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )

        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": question
                    },
                    {
                        "type": "text",
                        "text": "Here are the contents of a transcribed audio file: " + audio_transcription
                    }
                ]
            }
        )

    def handle_video(self, attachment, messages, question):
        video = cv2.VideoCapture(attachment)

        base64Frames = []
        while video.isOpened():
            success, frame = video.read()
            if not success:
                break
            _, buffer = cv2.imencode(".jpg", frame)
            base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

        video.release()

        display_handle = display(display_id=True)
        try:
            for img in base64Frames:
                display_handle.update(Image(data=base64.b64decode(img.encode("utf-8"))))
                time.sleep(0.025)
        except AttributeError:
            pass

        content = []
        content.append(
            {
                "type": "text", 
                "text": "Here are the frames of a video"
            }
        )

        temp1 = base64Frames[0:2]
        temp2 = base64Frames[-2:-1]
        base64Frames = []
        base64Frames.extend(temp1)
        base64Frames.extend(temp2)

        for frame in base64Frames:
            content.append(
                {
                    
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{frame}"
                    }
                }
            )

        messages.append(
            {
                "role": "user",
                "content": content
            }
        )



    def get_response(self, question: str, previous_messages: list[dict[str,str]], attachment_type: None|str, attachment):

        if attachment_type == None or attachment_type == "audio":
            self.model = "gpt-3.5-turbo"
        elif attachment_type == "image" or attachment_type == "screenshot":
            self.model = "gpt-4o-mini"
        elif attachment_type == "video":
            self.model = "gpt-4-vision-preview"
            self.max_tokens = 2000

        messages = []

        messages.append(
            {
                "role": "system",
                "content": self.system_message
            }
        )

        for message in previous_messages:
            messages.append(
                {
                    "role": message["sender"],
                    "content": message["message"]
                }
            )

        if attachment_type == None:
            self.handle_no_attachment(messages=messages, question=question)
        elif attachment_type == "image" or attachment_type == "screenshot":
            self.handle_image(attachment=attachment, messages=messages, question=question)
        elif attachment_type == "audio":
            self.handle_audio(attachment=attachment, messages=messages, question=question)
        elif attachment_type == "video":
            self.handle_video(attachment=attachment, messages=messages, question=question)

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            n=1,
            max_tokens=self.max_tokens
        )

        return completion.choices[0].message.content

    def prompt_custom_coversation(self, system_message, other_messages):
        messages = []

        messages.extend(system_message)
        messages.extend(other_messages)

        print("\n\n\n\n\n",messages[2],"\n\n\n\n\n")

        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            n=1,
            max_tokens=4096
        )

        return completion.choices[0].message.content