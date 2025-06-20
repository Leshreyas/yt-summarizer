import streamlit as st
import whisper_project as wsp


def main():
    st.title("Youtube Video Summarizer")
    st.write("Get YouTube transcript and use AI to summarize YouTube videos in one click for free.")
    link = st.text_input(label="Enter the video link:")
    if link:
        with st.spinner("Downloading Video", show_time=True):
            filepath = wsp.download_video(link)
        st.write(f"✅ Downloaded Video")
        print("done",filepath)
        if filepath:
            print("test")
            with st.spinner("Generating Transcript", show_time=True):
                transcript = wsp.generate_transcript(filepath)
            st.write(f"✅ Generated Transcript")
            with st.spinner("Breaking Segments", show_time=True):
                segments = wsp.break_segments(transcript, 30)
            st.write(f"✅ Broken Transcript")
            with st.spinner("Extracting Images", show_time=True):
                wsp.extract_images(filepath, "frames", 30)
            st.write(f"✅ Extracted Images")
            with st.spinner("Generating Captions", show_time=True):
                captions = wsp.process_frames("frames", 30)
            st.write(f"✅ Generated Captions")
            merged = []
            common_keys = sorted(set(captions.keys()) & set(segments.keys()))
            for ts in common_keys:
                merged.append(f"Caption: {captions[ts]}\nTranscript: {segments[ts]}")
            st.write(wsp.chat_with_gpt(merged))
            wsp.delete_resources("frames")



if __name__ == "__main__":
    main()
