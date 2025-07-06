import streamlit as st
import requests
import whisper_project as wsp


def main():
    st.title("Youtube Video Summarizer")
    st.write("Get YouTube transcript and use AI to summarize YouTube videos in one click for free.")
    # link = st.text_input(label="Enter the video link:")
    file = st.file_uploader("Upload an mp4 file", type="mp4", accept_multiple_files=False, key=None, help=None, on_change=None, args=None,
                            kwargs=None, disabled=False, label_visibility="visible")
    if file:
        with st.spinner("Processing in backend", show_time=True):
            try:
                files = {"file": (file.name, file.getvalue(), file.type)}
                res = requests.post("https://fffc-35-230-62-98.ngrok-free.app/summarize/file", files=files)
                if res.status_code == 200:
                    st.success("Request sent successfully!")
                    st.write(res.json().get("chat"))
                else:
                    st.error(f"Failed: {res.status_code}")
                # st.write(res.json()["chat"])
            except Exception as e:
                st.error(f"Error: {e}")
        # with st.spinner("Downloading Video", show_time=True):
        #     filepath = wsp.download_video(link)
        # st.write(f"✅ Downloaded Video")
        # print("done",filepath)
        # if filepath:
        #     print("test")
        #     with st.spinner("Generating Transcript", show_time=True):
        #         transcript = wsp.generate_transcript(filepath)
        #     st.write(f"✅ Generated Transcript")
        #     with st.spinner("Breaking Segments", show_time=True):
        #         segments = wsp.break_segments(transcript, 30)
        #     st.write(f"✅ Broken Transcript")
        #     with st.spinner("Extracting Images", show_time=True):
        #         wsp.extract_images(filepath, "frames", 30)
        #     st.write(f"✅ Extracted Images")
        #     with st.spinner("Generating Captions", show_time=True):
        #         captions = wsp.process_frames("frames", 30)
        #     st.write(f"✅ Generated Captions")
        #     merged = []
        #     common_keys = sorted(set(captions.keys()) & set(segments.keys()))
        #     for ts in common_keys:
        #         merged.append(f"Caption: {captions[ts]}\nTranscript: {segments[ts]}")
        #     st.write(wsp.chat_with_gpt(merged))
            wsp.delete_resources()


if __name__ == "__main__":
    main()
