from pydub import AudioSegment
import os
import requests
import json
from src.config import Config
from datetime import datetime

def convert_m4a_to_mp3(input_file, output_file):
    """
    Convert M4A file to MP3 format
    :param input_file: Path to input M4A file
    :param output_file: Path to output MP3 file
    """
    try:
        audio = AudioSegment.from_file(input_file, format="m4a")
        audio.export(output_file, format="mp3")
        print(f"Successfully converted {input_file} to {output_file}")
        return True
    except Exception as e:
        print(f"Error converting file: {str(e)}")
        return False

def split_mp3(file_path, output_dir, segment_length_sec=600):
    """
    Split MP3 file into segments of specified length
    :param file_path: Path to input MP3 file
    :param output_dir: Directory to save the segments
    :param segment_length_sec: Length of each segment in seconds (default: 600 seconds = 10 minutes)
    :return: List of created segment files
    """
    try:
        audio = AudioSegment.from_mp3(file_path)
        total_length_sec = len(audio) / 1000  # Convert milliseconds to seconds

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Get base filename
        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        
        segment_files = []
        start = 0
        part_num = 1

        while start < total_length_sec:
            end = start + segment_length_sec
            # Slice audio (convert seconds to milliseconds)
            segment_audio = audio[start*1000:end*1000]
            
            # Create output filename
            output_filename = f"{base_filename}_part{part_num}.mp3"
            output_path = os.path.join(output_dir, output_filename)
            
            # Export segment
            segment_audio.export(output_path, format="mp3")
            print(f"Exported segment: {output_path}")
            segment_files.append(output_path)
            
            part_num += 1
            start = end

        print("Splitting completed successfully!")
        return segment_files
    except Exception as e:
        print(f"Error splitting file: {str(e)}")
        return []

def transcribe_audio(file_path, output_dir="output/transcriptions"):
    """
    Transcribe audio file using Silicon Flow API and save results
    :param file_path: Path to audio file
    :param output_dir: Directory to save transcription results
    :return: Path to the saved transcription file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get the base filename without extension
        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        
        # Define output file paths
        txt_output = os.path.join(output_dir, f"{base_filename}_transcription.txt")
        json_output = os.path.join(output_dir, f"{base_filename}_transcription.json")

        url = "https://api.siliconflow.cn/v1/audio/transcriptions"
        
        # Open file in binary mode
        with open(file_path, "rb") as audio_file:
            # Build multipart/form-data request
            files = {
                "file": (os.path.basename(file_path), audio_file, "audio/mpeg"),
                "model": (None, "FunAudioLLM/SenseVoiceSmall")
            }
            
            headers = {
                "Authorization": f"Bearer {Config.SILICON_FLOW_API_KEY}"
            }

            response = requests.post(url, files=files, headers=headers)
            
        if response.status_code == 200:
            # Save raw JSON response
            with open(json_output, 'w', encoding='utf-8') as f:
                json.dump(response.json(), f, ensure_ascii=False, indent=2)
            
            # Extract and save text content
            try:
                transcription_text = response.json().get('text', '')
                with open(txt_output, 'w', encoding='utf-8') as f:
                    f.write(transcription_text)
                print(f"Transcription saved to {txt_output}")
                print(f"Full response saved to {json_output}")
                return txt_output
            except Exception as e:
                print(f"Error saving transcription: {str(e)}")
                return None
        else:
            print(f"Transcription failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return None

def create_lecture_summary(transcription_files, output_dir):
    """
    Create a combined and formatted lecture summary
    :param transcription_files: List of transcription file paths
    :param output_dir: Directory to save the summary
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    combined_output = os.path.join(output_dir, f"lecture_summary_{timestamp}.txt")
    
    with open(combined_output, 'w', encoding='utf-8') as outfile:
        # Write header
        outfile.write("=== Lecture Summary ===\n")
        outfile.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Write content from each part
        for i, file_path in enumerate(transcription_files, 1):
            outfile.write(f"\n=== Part {i} ===\n")
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read().strip()
                    outfile.write(content)
                    outfile.write("\n")
            except Exception as e:
                outfile.write(f"[Error reading part {i}: {str(e)}]\n")
        
        # Write footer
        outfile.write("\n=== End of Summary ===\n")
    
    print(f"\nLecture summary saved to {combined_output}")
    return combined_output

def merge_transcriptions(transcription_files, output_dir):
    """
    Merge all transcription files into a single, well-formatted document
    :param transcription_files: List of transcription file paths
    :param output_dir: Directory to save the merged document
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    merged_output = os.path.join(output_dir, f"complete_lecture_{timestamp}.txt")
    
    with open(merged_output, 'w', encoding='utf-8') as outfile:
        # Write document header
        outfile.write("=" * 80 + "\n")
        outfile.write("COMPLETE LECTURE TRANSCRIPTION\n")
        outfile.write("=" * 80 + "\n\n")
        outfile.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        outfile.write(f"Total Parts: {len(transcription_files)}\n")
        outfile.write("-" * 80 + "\n\n")
        
        # Write content from each part
        for i, file_path in enumerate(transcription_files, 1):
            # Write part header
            outfile.write(f"PART {i}\n")
            outfile.write("-" * 40 + "\n")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read().strip()
                    # Add proper paragraph spacing
                    paragraphs = content.split('\n\n')
                    for para in paragraphs:
                        if para.strip():
                            outfile.write(para.strip() + "\n\n")
            except Exception as e:
                outfile.write(f"[Error reading part {i}: {str(e)}]\n\n")
            
            # Add separator between parts
            outfile.write("-" * 80 + "\n\n")
        
        # Write document footer
        outfile.write("=" * 80 + "\n")
        outfile.write("END OF LECTURE TRANSCRIPTION\n")
        outfile.write("=" * 80 + "\n")
    
    print(f"\nComplete lecture document saved to {merged_output}")
    return merged_output

def main():
    # Define paths using os.path.join to handle spaces in paths correctly
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(base_dir, "data", "Frankfurt School of Finance & Management 2.m4a")
    mp3_dir = os.path.join(base_dir, "output", "mp3")
    transcriptions_dir = os.path.join(base_dir, "output", "transcriptions")
    
    # Ensure directories exist
    os.makedirs(mp3_dir, exist_ok=True)
    os.makedirs(transcriptions_dir, exist_ok=True)
    
    # Commented out for testing transcription only
    """
    print("=== Starting Lecture Processing ===")
    
    # Convert M4A to MP3
    output_file = os.path.join(mp3_dir, "converted_lecture.mp3")
    if not convert_m4a_to_mp3(input_file, output_file):
        print("Failed to convert audio file. Exiting.")
        return
    
    # Split the MP3 file into 10-minute segments
    segment_files = split_mp3(output_file, mp3_dir, segment_length_sec=600)
    if not segment_files:
        print("Failed to split audio file. Exiting.")
        return

    
    # For testing transcription with existing files
    segment_files = [os.path.join(mp3_dir, f) for f in os.listdir(mp3_dir) if f.endswith('.mp3')]
    
    # Create a list to store all transcription file paths
    transcription_files = []
    
    # Transcribe all segments
    print("\n=== Starting Transcription Process ===")
    for i, segment_file in enumerate(segment_files, 1):
        print(f"\nTranscribing segment {i} of {len(segment_files)}: {os.path.basename(segment_file)}...")
        result_file = transcribe_audio(segment_file, transcriptions_dir)
        if result_file:
            transcription_files.append(result_file)
        else:
            print(f"Warning: Failed to transcribe segment {i}")
    """
    # Create the final summary and complete document
    if transcription_files:
        print("\n=== Creating Documents ===")
        # Create the summary
        create_lecture_summary(transcription_files, transcriptions_dir)
        # Create the complete document
        merge_transcriptions(transcription_files, transcriptions_dir)
        print("\n=== Processing Complete ===")
    else:
        print("\nNo transcriptions were generated. Please check the errors above.")

if __name__ == "__main__":
    main()
    