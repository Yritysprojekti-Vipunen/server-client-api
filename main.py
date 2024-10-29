
from typing import Union

from chatbot import ChatBot
from conversation_history import save_message, get_convertations, insert_file_into_database, get_file_from_database
from client_api import ClientAPI
from pdf_tool import PDFTool

chatbot = ChatBot()
client_api = ClientAPI()
pdf_tool = PDFTool()

def set_context(file_path):
        insert_file_into_database(file_path=file_path)

def send_question_and_receive_response(question: str, attachment_type: Union[None,str] = None, attachment = None):
        #print(question)
        

        file = get_file_from_database(file_id=1)
        context = pdf_tool.context_from_pdf_contents(pdf_path_or_stream=file, is_stream=True)

        previous_messages = get_convertations()
        print(previous_messages)

        #include user's message in the list
        previous_messages.append(
               {
                      "role": "user",
                      "content": question
               }
        )

        response = chatbot.prompt_custom_coversation(system_message=context, other_messages=previous_messages)

        #user's question and response to database
        save_message(user_id="user_1", message=question, sender="user")
        save_message(user_id="user_1", message=response, sender="assistant")

        return {"response": response}

def main():
        #Initialization
        set_context(file_path="./Ohjaussuunnitelma_011021.pdf")

        client_api.router.add_api_route(path="/response", endpoint=send_question_and_receive_response, methods=["GET"])
        client_api.include_routes()

        #Run the server
        client_api.run()

if __name__ == "__main__":
    main()