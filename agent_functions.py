import requests
import PyPDF2
from io import BytesIO

###############################

# JSON schema for function calls to be used by assistant creations

###############################


fcn_call_tools = [
    {
        "type": "function",
        "function": {
            "name": "Look_Up_AC",
            "description": "Retrieves an advisory circular from the FAA website for use by model based on the AC's ID as an input.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ac_id": {
                        "type": "string",
                        "description": "The ID of the advisory circular to retrieve where input string to function must look like these examples to work: 'AC_25_1309-1A', 'AC_20-156', 'AC_20-152A'. "
                    }
                },
                "required": ["ac_id"]
            }
        }
    }
]

###############################

# HELPER FUNCTIONS

###############################

def extract_text_from_pdf(url):
    """
    Extracts text from a PDF file located at the given URL.

    Parameters:
    url (str): The URL of the PDF file.

    Returns:
    str: The extracted text from the PDF.
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code

        # Get the content of the response
        content = response.content

        # Create a BytesIO object from the content
        file = BytesIO(content)

        # Create a PDF file reader
        pdf_reader = PyPDF2.PdfReader(file)

        # Initialize an empty string to hold the text
        text = ''

        # Loop over the pages and extract the text
        for page_number in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_number]
            text += page.extract_text()
        
        return text
    
    except requests.RequestException as e:
        return f"An error occurred while fetching the PDF: {e}"
    except PyPDF2.utils.PdfReadError as e:
        return f"An error occurred while reading the PDF: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

###############################

# AGENT FUNCTIONS

###############################

def Look_Up_AC(ac_id):
    url = "https://www.faa.gov/documentLibrary/media/Advisory_Circular/" + ac_id + ".pdf"
    text = extract_text_from_pdf(url)
    return text
