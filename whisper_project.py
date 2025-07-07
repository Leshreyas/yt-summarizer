import whisper
from concurrent.futures import ThreadPoolExecutor
from PIL import Image  # opening and processing image files
from transformers import BlipProcessor, BlipForConditionalGeneration  # provides pre-trained models from hugging face
from collections import defaultdict
from openai import OpenAI
import os
import subprocess
import streamlit as st
from dotenv import load_dotenv
import speech_recognition as sr

load_dotenv()
# api-key from open router
# client = OpenAI(api_key=os.getenv("API_KEY"), base_url="https://openrouter.ai/api/v1")


@st.cache_resource
def load_blip_model():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base", use_fast=True)  # loads the pre-trained processor
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")  # loads the model
    model.eval()
    return processor, model


@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")


def chat_with_gpt(dataset, key):
    client = OpenAI(api_key=key, base_url="https://openrouter.ai/api/v1")

    print("Generating response")
    prompt = '''Summarize this video transcript in a detailed and structured way. Include the following sections:
1.	Summary – a high-level overview in a narrative format, around 150–200 words.
2.	Highlights – a bullet list of key moments, features, or claims (preferably with emojis).
3.	Key Insights – a deeper analysis of 5–7 unique takeaways, each with a short paragraph.
4.  30 Second breakdown - breakdown an summarize every 30 seconds in a short paragraph 
5.	Conclusion – a motivational or strategic wrap-up, emphasizing the core message and future action.


Tone: Clear, motivational, slightly analytical

Audience: Aspiring AI professionals or tech learners

Here’s the video transcript and captions:\n\n'''
    prompt += "\n\n".join(dataset)
    response = client.chat.completions.create(
        model="meta-llama/llama-4-maverick:free",
        messages=[{"role": "user", "content": prompt}]
    )
    prompt += '''Dont mention any discrepancies in the transcript or the captions but if there are issues, choose whichever
              is more accurate and makes sense, if both are too vague just generalize on certain points you picked up but make it as 
              close to the captions and transcripts'''
    return response.choices[0].message.content


def process_frames(directory, interval=10):
    print("Processing frames")
    # Load processor and model
    processor, model = load_blip_model()
    frames = []
    D = {}
    timestamps = []
    # for filename in sorted(os.listdir(directory)):

    def create_caption(image_path):
        # Load the image
        # image_path = os.path.join(directory, filename)
        # print(filename)
        raw_image = Image.open(image_path).convert('RGB')
        frames.append(raw_image)
        ts = int(os.path.basename(image_path)[5:7]) * interval

        # Prepare the Inputs
        # text = "a photograph of"    # prefix prompts to guide model to generate description
        inputs = processor(raw_image, return_tensors="pt")  # converts the image and text to the appropriate format

        # Generate the Caption
        output = model.generate(**inputs)  # runs the model's forward pass to produce textual description
        caption = processor.decode(output[0], skip_special_tokens=True) # decodes the token ID's to readable text
        return ts, caption
        # print(f"Description : {processor.decode(output[0], skip_special_tokens=True)}")
    folder = "frames"
    image_paths = [os.path.join(folder, f) for f in sorted(os.listdir(folder)) if f.endswith(".jpg")]
    with ThreadPoolExecutor() as executor:
        results = executor.map(create_caption, image_paths)

    # Collect the results
    for ts, caption in results:
        D[ts] = caption

    return D


def extract_images(video_path, output_folder, every_seconds=10):
    print("Extracting images")
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"fps=1/{every_seconds}",  # 1 frame every N seconds
        os.path.join(output_folder, "frame%02d.jpg")
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def delete_resources(extensions=(".jpg", ".png")):
    """
    Deletes all image files in the given folder.

    Args:
        folder_path (str): Path to the folder containing frames.
        extensions (tuple): File extensions to delete (default: .jpg, .png)
    """
    folder_path = "frames"
    if not os.path.exists(folder_path):
        print("Folder does not exist.")
        return

    deleted = 0
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(extensions):
            filepath = os.path.join(folder_path, filename)
            os.remove(filepath)
            deleted += 1
    print(f"Deleted {deleted} frame(s) from '{folder_path}'.")

    for filename in os.listdir("audio&video"):
        if filename.endswith(".mp4"):
            filepath = os.path.join("audio&video", filename)
            os.remove(filepath)


def generate_transcript(filepath):
    # biteable for audio extraction
    print("Generating transcript")
    model = load_whisper_model()
    result = model.transcribe(filepath, word_timestamps=False)
    return result["segments"]


def break_segments(segments, interval=10):
    print("Breaking segments")
    timestamps = defaultdict(str)
    for segment in segments:
        ts = int(segment["start"] // interval) * interval
        timestamps[ts] += segment['text']
    # print(timestamps)
    return dict(sorted(timestamps.items()))


def download_video(link):
    folder = "audio&video"
    os.makedirs(folder, exist_ok=True)

    index = len(os.listdir(folder))
    raw_name = f"raw_video{index}.mp4"
    name = f"video{index}.mp4"
    raw_path = os.path.join(folder, raw_name)
    final_path = os.path.join(folder, name)

    yt_cmd = [
        "yt-dlp",
        "-f", "bv*+ba/b",  # best video + best audio
        "-o", raw_path.replace(".mp4", ".%(ext)s"),  # incase not mp4 extension (its mkv ahhh what the flip is that)w
        link
    ]
    print("test1")
    result = subprocess.run(yt_cmd, check=True)

    import glob
    # helps you search files using the * just like in the terminal in case the extension is not mp4
    raw_files = glob.glob(os.path.join(folder, f"raw_video{index}.*"))
    if not raw_files:
        raise RuntimeError("yt-dlp finished but no output file was found.")
    # gets the first matching pair
    raw_path = raw_files[0]

    if result.returncode != 0 or not os.path.exists(raw_path):
        raise RuntimeError(f"yt-dlp failed:\n{result.stderr}")
    if os.path.getsize(raw_path) < 1024 * 100:
        raise RuntimeError("Downloaded file is too small or empty.")
    cmd = [
        "ffmpeg", "-y", "-i", raw_path,
        "-c:v", "copy",  # ⚡ don't re-encode video
        "-c:a", "aac",  # ✅ re-encode audio for compatibility
        "-movflags", "+faststart",  # ✅ good for streaming
        final_path
    ]
    print("test1")
    result = subprocess.run(cmd, capture_output=True, text=True)

    os.remove(raw_path)
    return final_path


def main():
    filepath = download_video("https://www.youtube.com/watch?v=o8YBp9APnIw")
    transcript = generate_transcript(filepath)
    segments = break_segments(transcript, 30)
    # delete_frames("frames")
    extract_images("audio&video/paradox_fixed.mp4", "frames", 30)
    captions = process_frames("frames", 30)
    merged = []
    common_keys = sorted(set(captions.keys()) & set(segments.keys()))
    for ts in common_keys:
        merged.append(f"Caption: {captions[ts]}\nTranscript: {segments[ts]}")
    return chat_with_gpt(merged)


if __name__ == "__main__":
    main()

