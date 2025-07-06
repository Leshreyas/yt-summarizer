import os
from typing import Union
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import whisper_project as wsp
import uvicorn
import shutil
import subprocess


app = FastAPI()
total_connections = 0


class Item(BaseModel):
    name: str
    # price: float
    # is_offer: Union[bool, None] = None # type can either be bool or None, default is None


# .get is HTTP method
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/summarize/file")
def summarize_video(file: UploadFile):
    print("hello")
    if file:
        folder = "audio&video"
        os.makedirs(folder, exist_ok=True)
        filename = "audio" + str(len(os.listdir(folder))) + ".mp4"
        filepath = os.path.join(folder, filename)
        print("test")
        with open(filepath, "wb") as buffer:      # wb -> write, binary mode (necessary for .mp4 files)
            buffer.write(file.file.read())     # file.file is the file-object from FastAPI
        if filepath:
            transcript = wsp.generate_transcript(filepath)
            segments = wsp.break_segments(transcript, 30)
            wsp.extract_images(filepath, "frames", 30)
            captions = wsp.process_frames("frames", 30)
            merged = []
            common_keys = sorted(set(captions.keys()) & set(segments.keys()))
            for ts in common_keys:
                merged.append(f"Caption: {captions[ts]}\nTranscript: {segments[ts]}")
            chat = wsp.chat_with_gpt(merged)
            wsp.delete_resources()
            return {"chat": chat}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_price": item.price, "item_id": item_id}


async def handle_lifespan(scope, receive, send):
    assert scope["type"] == "lifespan"
    while True:
        message = await receive()
        print(f"Got message: {message}")

        if message["type"] == "lifespan.startup":
            await send({"type": "lifespan.startup.complete"})
            break
        elif message["type"] == "lifespan.startup":
            await send({"type": "lifespan.startup.complete"})
            break


async def handle_http(scope, receive, send):
    assert scope["type"] == "http"
    while True:
        print("Waiting for message.....")
        message = await receive()
        print(f"Got message: {message}")

        if message["type"] == "http.disconnect":  # if user disconnects dont receive
            return
        if not message["more_body"]:
            break
    # start message
    response_message = {
        "type": "http.response.start",
        "status": 200,
        "headers": [(b"content-type", b"text/plain")],
    }
    print(f"Sending response start: {response_message}")
    await send(response_message)
    # body of the message
    response_message = {
        "type": "http.response.body",
        "body": b"k",
        "more-body": False,
    }
    print(f"Sending response body: {response_message}")
    await send(response_message)


# async def app(scope, receive, send):
#     global total_connections
#     total_connections += 1
#     current_connections = total_connections
#     print(f"Beginning connection {current_connections}. Scop {scope}")
#     if scope["type"] == "lifespan":
#         await handle_lifespan(scope, receive, send)
#     elif scope["type"] == "http":
#         await handle_http(scope, receive, send)
#     print(f"Ending connection {current_connections}")


def main():
    port = int(os.getenv("PORT"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()