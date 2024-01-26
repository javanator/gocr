#!/usr/bin/env python
import io
import os
import sys
from io import BytesIO
from pathlib import Path

import fitz
import magic
from PIL import Image
from dotenv import load_dotenv
from google.api_core.client_options import ClientOptions
from google.cloud import documentai

load_dotenv(dotenv_path=os.path.join(Path.home(), ".gocr.env"))  # take environment variables from gocr.env.

# ARG 0 is the current script
# ARG 1 will be source directory
# ARG 2 will be destionation directory
SOURCE_DIR = os.path.join(os.getcwd(), sys.argv[1])
DEST_DIR = os.path.join(os.getcwd(), sys.argv[2])
print("USING SOURCE: " + SOURCE_DIR)
print("USING DEST: " + DEST_DIR)

# GOOGLE CLOUD Settings
PROJECT_ID = os.environ['PROJECT_ID']
LOCATION = os.environ['LOCATION']  # Format is 'us' or 'eu'
PROCESSOR_ID = os.environ['PROCESSOR_ID']  # Create processor in Cloud Console

# Instantiates a client
docai_client = documentai.DocumentProcessorServiceClient(
    client_options=ClientOptions(api_endpoint=f"{LOCATION}-documentai.googleapis.com")
)


def perform_ocr(input_file):
    print("Performing OCR on: " + input_file)
    source_mime_type = magic.from_file(input_file, mime=True)
    name = docai_client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)
    with open(input_file, "rb") as file:
        file_content = file.read()
        raw_document = documentai.RawDocument(content=file_content, mime_type=source_mime_type)
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)
        response = docai_client.process_document(request=request)
        return response.document


def calculate_line_height(rectHeight, text):
    totallines = text.count('\n')
    lineheight = rectHeight/totallines
    return lineheight


def calculate_font_point_size(area_height_pixels, text):
    line_height = calculate_line_height(area_height_pixels, text)
    fontpointheight = line_height * 0.80
    return fontpointheight


def process_ocr_result(outputDocument, ocr_result):
    img_xref = 0
    ocrText = ocrResult.text
    pageNum = 0
    for ocrPage in ocrResult.pages:
        width = ocrPage.dimension.width
        height = ocrPage.dimension.height
        rect = fitz.Rect(0, 0, width, height)
        pdfPage = outputDocument.new_page(-1, width, height)

        # Re-encode the OCR Page image as a more compressed image for writing
        largeImageBytes = Image.open(BytesIO(ocrPage.image.content))
        compressedImageBytes = io.BytesIO()
        largeImageBytes.save(compressedImageBytes, format="JPEG", optimize=True, compress_level=9, quality=60)
        Image.open(BytesIO(compressedImageBytes.getvalue()))

        pdfPage.insert_image(rect, stream=compressedImageBytes)
        for block in ocrPage.blocks:
            for textSegment in block.layout.text_anchor.text_segments:
                startIndexInt = int(textSegment.start_index)
                endIndexInt = int(textSegment.end_index)
                textString = ocrText[startIndexInt:endIndexInt:1]

                verticesArray = block.layout.bounding_poly.vertices
                upperLeft = fitz.Point(verticesArray[0].x, verticesArray[0].y)
                upperRight = fitz.Point(verticesArray[1].x, verticesArray[1].y)
                lowerRight = fitz.Point(verticesArray[2].x, verticesArray[2].y)
                lowerLeft = fitz.Point(verticesArray[3].x, verticesArray[3].y)

                rect = fitz.Rect(upperLeft, lowerRight)
                fontSize = calculate_font_point_size(rect.height, textString)
                lineHeightPixels = calculate_line_height(rect.height, textString)

                textMetric = "S:" + str(fontSize) + " N:" + str(textString.count('\n')) + " H:" + str(lineHeightPixels)
                # For Debugging. Draw Rectangles on OCR blocks and calculated text offsets
                # pdfPage.draw_rect(rect=rect, color=getColor("RED"))
                # pdfPage.insert_text((rect.x0, rect.y0+lineHeightPixels), textMetric, fontname="courier",
                # fontsize=fontSize)
                descentOffset = fitz.Font("courier").descender * lineHeightPixels
                ascentOffset = fitz.Font("courier").ascender * lineHeightPixels
                pdfPage.insert_text((rect.x0, rect.y0+lineHeightPixels+descentOffset), textString, fontname="courier", fontsize=fontSize,
                                    fill_opacity=0, stroke_opacity=0)
                pageNum += 1
    return outputDocument


# START Main Script Section
for filename in os.listdir(SOURCE_DIR):
    filepath = os.path.join(SOURCE_DIR,filename)
    outputFileName = os.path.join(DEST_DIR, filename)
    if (os.path.exists(outputFileName)):
        print(outputFileName + " exists. Skipping.")
    else:
        ocrResult = perform_ocr(filepath)
        outputDocument = process_ocr_result(fitz.open(),ocrResult)
        outputDocument.ez_save(outputFileName)
        os.remove(filepath)
# END Main Script Section


print("Document processing complete.")
