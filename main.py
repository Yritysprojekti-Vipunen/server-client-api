
from typing import Union

from chatbot import ChatBot
from message_history import MessageHistory

from client_api import ClientAPI

chatbot = ChatBot()

message_history = MessageHistory(database_name="message_history", current_conversation="1")

#if message_history.is_database_empty():
context = (open(file="./context.txt", mode="rt")).read()
response = chatbot.get_response(question=context, previous_messages=message_history.get_messages(), attachment_type=None, attachment=None)
message_history.insert_message(message={"message": context, "sender": "user"}, attachment=None)
message_history.insert_message(message={"message": response, "sender": "assistant"}, attachment=None)

client_api = ClientAPI()

def send_question_and_receive_response(question: str, attachment_type: Union[None,str] = None, attachment = None):
        print(question)
        
        previous_messages = message_history.get_messages()

        response = chatbot.get_response(question=question, previous_messages=previous_messages, attachment_type=attachment_type, attachment=attachment)

        message_history.insert_message(message={"message": question, "sender": "user"}, attachment=attachment)
        message_history.insert_message(message={"message": response, "sender": "assistant"}, attachment=attachment)

        return {"response": response}

client_api.router.add_api_route(path="/response", endpoint=send_question_and_receive_response, methods=["GET"])
client_api.include_routes()

if __name__ == "__main__":
    client_api.run()