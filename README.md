# GOKRa PDF (Google-OCR-a)

This is a file processor for PDFs. It is intended to be run as a cron job in order to batch process PDF files through 
Google's Document AI and overlay the OCR text ontop of the original. The PDF page images are re-encoded. Some image
quality loss may occur compared to the original.

This uses Google's Document AI's synchronous API and is limited to PDFs of only 15 pages.

# Potential Improvements
* There is not attempt to match font style. Google's API does not return font information.
* Text alignment is not perfect. It is good enough for my usage, but could be improved with some investment
* If the input PDF already has text on a page, copy the source page directly. 
* Google seems to rotate the PDF image. This may have side effects. There is no handling for this one way or another
* Create a watchdog to ingest once file is added to a directory

This was a weekend project. I did not think about long-term, but if you want to submit a 
pull request to make this tool better, I will consider them on a case by case basis. 

# Installation
```
cd whereever you want this
git clone <this repo>
add ./bin folder to your path
``` 

Create new VENV
```
pip install -r requirements.txt
python -m venv venv
source venv/bin/activate
touch ~/.gocr.env
sudo vi ~/.gocr.env
```

Paste the contents and fill in with meaningful values for your cloud setup:
```
GOOGLE_APPLICATION_CREDENTIALS="/path/to/my/key.json"
PROJECT_ID = "MY_GOOGLE_PROJECT_ID"
PROCESSOR_ID = "MY_DOCUMENTAI_PROCESSOR_ID"  # Create processor in Cloud Console
LOCATION = "us"  # Format is 'us' or 'eu'
```
