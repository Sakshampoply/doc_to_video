import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import PyPDF2
import docx

# Load environment variables
load_dotenv()

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint="https://ai-proxy.lab.epam.com",
    api_version="2024-02-01",
)


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text


def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file."""
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])


def summarize_and_split_text(text):
    """Use GPT-4o to summarize and divide text into slide content."""
    response = client.completions.create(
        model="gpt-4o",
        prompt="Summarize the following text and split it into slide-friendly content:\n\n"
        + text,
        max_tokens=1024,
    )

    slides = response.choices[0].text.strip().split("\n\n")
    return slides


def generate_audio(text, output_path):
    """Use Whisper TTS to generate narration audio."""
    response = client.audio.speech.create(
        model="whisper-1",
        input=text,
        voice="alloy",
    )

    with open(output_path, "wb") as audio_file:
        audio_file.write(response.content)


def create_text_slide(
    text, image_path, font_path="arial.ttf", image_size=(1280, 720), font_size=50
):
    """Create an image with centered text for each slide."""
    img = Image.new("RGB", image_size, "black")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, font_size)

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


def create_slideshow(text_slides, audio_path, output_video="output.mp4"):
    """Create a video slideshow with text slides and narration."""
    images = []
    for i, slide in enumerate(text_slides):
        image_path = f"slide_{i}.png"
        create_text_slide(slide, image_path)
        images.append(ImageClip(image_path).set_duration(5))

    audio_clip = AudioFileClip(audio_path)
    video = concatenate_videoclips(images, method="compose")
    video = video.set_audio(audio_clip)
    video.write_videofile(output_video, fps=24, codec="libx264")


def main(input_file):
    """Main function to process document and generate tutorial video."""
    if input_file.endswith(".pdf"):
        text = extract_text_from_pdf(input_file)
    elif input_file.endswith(".docx"):
        text = extract_text_from_docx(input_file)
    else:
        raise ValueError("Unsupported file format")

    slides = summarize_and_split_text(text)
    audio_file = "narration.mp3"
    generate_audio(" ".join(slides), audio_file)
    create_slideshow(slides, audio_file)
    print("Tutorial video generated successfully!")


if __name__ == "__main__":
    main("/Users/sakshampoply/Downloads/Saksham_Springer.pdf")
