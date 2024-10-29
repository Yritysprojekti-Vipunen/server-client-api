import fitz  # PyMuPDF
from PIL import Image
import io
import pymupdf
import base64

class PDFTool:
    def __init__(self):
        self.page_count = 0
        self.page_contents_by_page_number = {}
        self.images = {}
        self.ordered_contents = []

    def extract_text_and_images(self, pdf_path, is_stream: bool):
        doc = None

        if is_stream == True:
            doc = fitz.open(stream=pdf_path, filetype="pdf")
        else:
            doc = fitz.open(pdf_path)

        self.page_count = doc.page_count

        temp_page = []
        for page_num in range(self.page_count):
            page = doc.load_page(page_num)
            print(f"\n--- Page {page_num + 1} ---\n")

            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if block["type"] == 0: #text block
                    text = ""
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text += span["text"] #concatenate all text spans

                    temp_page.append(text)

                elif block["type"] == 1: #image block
                    image_list = page.get_images(full=True)
                    
                    if image_list:
                        for img in image_list:
                            xref = img[0]  #image xref (reference number)
                            base_image = doc.extract_image(xref)
                            image_bytes = base_image["image"]
                            image_ext = base_image["ext"]

                            base64_image = base64.b64encode(image_bytes).decode('utf-8')

                            data_uri = f"data:image/jpeg;base64,{base64_image}"

                            self.images.update(
                                {
                                    f"{page_num}": data_uri,
                                }
                            )

            self.page_contents_by_page_number.update(
                {
                    f"{page_num}": temp_page
                }
            )

            temp_page = []

        doc.close()

    def order_contents(self):
        for page_num in range(self.page_count):
            for piece_of_text in self.page_contents_by_page_number[f"{page_num}"]:
                self.ordered_contents.append(
                    {
                        "type": "text",
                        "text": piece_of_text
                    }
                )
            if page_num in self.images:
                self.ordered_contents.append(
                    {
                        "type": "image_url",
                        "image_url": self.images[f"{page_num}"]
                    }
            )

        return self.ordered_contents

    def create_system_message(self, extracted_pdf_content):
        context = []
        
        #instructions as the system message
        instructions = (open(file="./context_for_pdf.txt", mode="rt")).read()
        
        system_message_1_of_2 = {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": instructions
                }
            ]
        }

        #context.append(system_message_1_of_2)

        #extracted data from pdf
        content = []

        content.append(
            {
                "type": "text",
                "text": "BEGIN CONTEXT"
            }
        )

        for data in extracted_pdf_content:
            content.append(data)

        content.append(
            {
                "type": "text",
                "text": "END CONTEXT"
            }
        )

        system_message_2_of_2=[
            {
                "role": "user",
                "content": content
            }
        ]

        print(system_message_2_of_2)

        context.append(system_message_1_of_2)
        context.extend(system_message_2_of_2)

        return context

    def context_from_pdf_contents(self, pdf_path_or_stream, is_stream: bool):
        self.extract_text_and_images(pdf_path=pdf_path_or_stream, is_stream=is_stream)
        contents = self.order_contents() #also format
        context = self.create_system_message(extracted_pdf_content=contents)
        return context



#x = PDFTool()
#y = x.context_from_pdf_contents(pdf_path="..\\Ohjaussuunnitelma_011021.pdf")

#print(y)
