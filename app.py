import os
import requests
from dotenv import load_dotenv
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip
from PIL import Image, ImageDraw, ImageFont
import PyPDF2
import docx
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

# Validate API Key
api_key = os.getenv("AZURE_OPENAI_API_KEY")  # Using the same API key
api_endpoint = "https://ai-proxy.lab.epam.com"

if not api_key:
    raise ValueError("AZURE_OPENAI_API_KEY is not set. Check your .env file.")

# Headers for API request
HEADERS = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text.strip()


def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file."""
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs]).strip()


def summarize_and_split_text(text):
    """Use Claude Instant v1 to summarize and divide text into slide content."""
    # Limit input size to prevent API overload
    client = AzureOpenAI(
        api_key=api_key,
        azure_endpoint="https://ai-proxy.lab.epam.com",
        api_version="2024-02-01-preview",
    )

    try:
        response = client.chat.completions.create(
            model="anthropic.claude-instant-v1",  # Using Claude Instant
            messages=[
                {"role": "system", "content": "You are an AI that converts text into slide-friendly summaries."},
                {"role": "user", "content": f"Summarize the following text and split it into slide-friendly content:\n\n{text}"}
                ],
            max_tokens=1024,
            )

# Extract and format the response
        slides = response.choices[0].message.content.strip().split("\n\n")
        print(slides)
        return slides

    except requests.exceptions.RequestException as e:
        print(f"Error in summarize_and_split_text: {e}")
        return []


def create_text_slide(
    text, image_path, font_path="arial.ttf", image_size=(1280, 720), font_size=50
):
    """Create an image with centered text for each slide."""
    img = Image.new("RGB", image_size, "black")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print("Font file not found. Using default font.")
        font = ImageFont.load_default()

    max_width = image_size[0] - 100
    lines = []
    words = text.split()
    line = ""

    for word in words:
        test_line = line + " " + word if line else word
        if draw.textlength(test_line, font=font) < max_width:
            line = test_line
        else:
            lines.append(line)
            line = word

    if line:
        lines.append(line)

    y_position = (image_size[1] - (len(lines) * font_size)) // 2
    for line in lines:
        text_width = draw.textlength(line, font=font)
        x_position = (image_size[0] - text_width) // 2
        draw.text((x_position, y_position), line, font=font, fill="white")
        y_position += font_size + 10

    img.save(image_path)


def create_slideshow(text_slides, output_video="output.mp4"):
    """Create a video slideshow with text slides."""
    images = []
    for i, slide in enumerate(text_slides):
        image_path = f"slide_{i}.png"
        create_text_slide(slide, image_path)
        images.append(ImageClip(image_path).with_duration(5))  # Use with_duration()

    try:
        video = concatenate_videoclips(images, method="compose")
        video.write_videofile(output_video, fps=24, codec="libx264")
    except Exception as e:
        print(f"Error in create_slideshow: {e}")


def main(input_file):
    """Main function to process document and generate tutorial video."""
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"File '{input_file}' not found.")

    if input_file.endswith(".pdf"):
        text = extract_text_from_pdf(input_file)
    elif input_file.endswith(".docx"):
        text = extract_text_from_docx(input_file)
    else:
        raise ValueError("Unsupported file format. Use PDF or DOCX.")

    if not text:
        raise ValueError("Extracted text is empty. Check the input document.")

    slides = summarize_and_split_text(text)
    if not slides:
        print("Failed to generate slides. Exiting.")
        return

    create_slideshow(slides)
    print("✅ Tutorial video generated successfully!")


if __name__ == "__main__":
    main(r"C:\Users\saksham_poply\Downloads\Conversational AI for Media Search- A Retrieval-Augmented Generation Approach with LangChain (1).pdf")
