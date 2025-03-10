import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import AudioFileClip, ImageSequenceClip
from gtts import gTTS
import PyPDF2
import docx


# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text.split(". ")  # Split text into sentences


# Function to extract text from DOCX
def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.split(". ")  # Split text into sentences


# Function to generate audio narration
def generate_audio(text_slides, output_audio="audio.mp3", lang="en"):
    text = " ".join(text_slides)  # Combine all text slides into a single narration
    tts = gTTS(text=text, lang=lang)
    tts.save(output_audio)
    return output_audio


# Function to create slides using Pillow
def create_text_slide(text, image_path, size=(1280, 720)):
    img = Image.new("RGB", size, "black")  # Create a black background
    draw = ImageDraw.Draw(img)

    # Load a font (ensure a font is available)
    font_path = (
        "/System/Library/Fonts/Supplemental/Arial.ttf"  # Change this for Linux/Windows
    )
    font = ImageFont.truetype(font_path, 50)

    # Center the text
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_w, text_h = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    position = ((size[0] - text_w) // 2, (size[1] - text_h) // 2)

    draw.text(position, text, font=font, fill="white")
    img.save(image_path)


# Function to create a slideshow video
def create_slideshow(text_slides, output_video="output.mp4", fps=1):
    audio_path = generate_audio(text_slides)  # Generate audio narration
    image_paths = []

    # Generate slide images
    for i, slide in enumerate(text_slides):
        image_path = f"slide_{i}.png"
        create_text_slide(slide.strip(), image_path)
        image_paths.append(image_path)

    # Create video from images using OpenCV
    frame = cv2.imread(image_paths[0])
    height, width, _ = frame.shape
    video_writer = cv2.VideoWriter(
        "temp_video.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
    )

    for img_path in image_paths:
        frame = cv2.imread(img_path)
        video_writer.write(frame)

    video_writer.release()

    # Merge video and audio using MoviePy
    video_clip = ImageSequenceClip(image_paths, fps=fps)
    audio_clip = AudioFileClip(audio_path)
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(output_video, codec="libx264", fps=fps)

    # Cleanup images
    for img in image_paths:
        os.remove(img)


# Function to process a file (PDF or DOCX) and generate a tutorial video
def process_document(file_path):
    if file_path.endswith(".pdf"):
        text_slides = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text_slides = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide a PDF or DOCX file.")
    create_slideshow(text_slides)


# Example Usage
file_path = "/Users/sakshampoply/Downloads/Saksham_Springer.pdf"  # Change to your actual file path
process_document(file_path)
