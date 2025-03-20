import os
from pydub import AudioSegment
import requests
import json
from openai import OpenAI
from datetime import datetime
from src.config import Config

class LecturePipeline:
    def __init__(self, input_file):
        """
        Initialize the lecture processing pipeline
        :param input_file: Path to input audio file (M4A or MP3)
        """
        self.input_file = input_file
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(self.base_dir, "output")
        self.temp_dir = os.path.join(self.output_dir, "temp")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize API clients
        self.deepseek_client = OpenAI(
            api_key=Config.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )

    def convert_to_mp3(self, input_file):
        """Convert M4A to MP3 if needed"""
        try:
            if input_file.lower().endswith('.m4a'):
                output_file = os.path.join(self.temp_dir, "converted.mp3")
                audio = AudioSegment.from_file(input_file, format="m4a")
                audio.export(output_file, format="mp3")
                print(f"Converted {input_file} to MP3")
                return output_file
            return input_file
        except Exception as e:
            print(f"Error converting file: {str(e)}")
            return None

    def split_audio(self, file_path, segment_length_sec=600):
        """Split audio into segments"""
        try:
            audio = AudioSegment.from_mp3(file_path)
            total_length_sec = len(audio) / 1000
            segments = []
            
            for i in range(0, int(total_length_sec), segment_length_sec):
                end = min(i + segment_length_sec, total_length_sec)
                segment = audio[i*1000:int(end*1000)]
                segment_path = os.path.join(self.temp_dir, f"segment_{i//segment_length_sec + 1}.mp3")
                segment.export(segment_path, format="mp3")
                segments.append(segment_path)
            
            print(f"Split audio into {len(segments)} segments")
            return segments
        except Exception as e:
            print(f"Error splitting audio: {str(e)}")
            return []

    def transcribe_segment(self, segment_path):
        """Transcribe a single audio segment"""
        try:
            url = "https://api.siliconflow.cn/v1/audio/transcriptions"
            
            with open(segment_path, "rb") as audio_file:
                files = {
                    "file": (os.path.basename(segment_path), audio_file, "audio/mpeg"),
                    "model": (None, "FunAudioLLM/SenseVoiceSmall")
                }
                headers = {"Authorization": f"Bearer {Config.SILICON_FLOW_API_KEY}"}
                response = requests.post(url, files=files, headers=headers)
            
            if response.status_code == 200:
                return response.json().get('text', '')
            else:
                print(f"Transcription failed for segment {segment_path}")
                return None
        except Exception as e:
            print(f"Error transcribing segment: {str(e)}")
            return None

    def enhance_summary(self, text):
        """Enhance the summary using DeepSeek API with two different approaches"""
        try:
            # First prompt for concept summarization
            concept_prompt = """You are an expert at analyzing and summarizing academic lectures. Your task is to create a comprehensive concept summary in Markdown format. Please:

1. Extract and organize the main concepts and key ideas
2. Identify the relationships between different concepts
3. Highlight important definitions and terminology
4. Create a clear hierarchy of ideas
5. Include examples and applications where relevant
6. Add cross-references between related concepts
7. Identify the main learning objectives
8. Note any practical applications or real-world connections

Format requirements:
- Use # for the main title
- Use ## for major concept categories
- Use ### for sub-concepts
- Use bullet points (- or *) for key points
- Use **bold** for important terms and definitions
- Use > for key concepts and definitions
- Use `code` for technical terms
- Add a concept map or outline at the beginning
- Include a glossary of key terms at the end
- Use horizontal rules (---) between major concept sections

Please ensure the output is in perfect Markdown format with clear concept organization."""

            # Second prompt for transcription correction
            correction_prompt = """You are an expert at correcting and improving lecture transcriptions. Your task is to fix and enhance the transcription while maintaining its original meaning. Please:

1. Fix any transcription errors and unclear sentences
2. Correct grammar and punctuation
3. Improve sentence structure and flow
4. Remove filler words and redundant phrases
5. Fix technical term misspellings
6. Add proper paragraph breaks
7. Maintain the original lecture's tone and style
8. Preserve important pauses and emphasis

Format requirements:
- Use # for the main title
- Use ## for major sections
- Use ### for subsections
- Use proper paragraph spacing
- Use **bold** for emphasis on corrected terms
- Use > for important quotes
- Add timestamps or section markers
- Include a note about major corrections
- Use horizontal rules (---) between major sections

Please ensure the output is in perfect Markdown format with clear corrections and improvements."""

            # Get both types of summaries
            concept_response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": concept_prompt},
                    {"role": "user", "content": f"Please create a concept summary of this lecture:\n\n{text}"},
                ],
                stream=False
            )
            
            correction_response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": correction_prompt},
                    {"role": "user", "content": f"Please correct and improve this lecture transcription:\n\n{text}"},
                ],
                stream=False
            )
            
            # Combine both summaries with clear separation
            combined_summary = f"""# Lecture Analysis Report

## Table of Contents
- [Concept Summary](#concept-summary)
- [Corrected Transcription](#corrected-transcription)

---

## Concept Summary

{concept_response.choices[0].message.content}

---

## Corrected Transcription

{correction_response.choices[0].message.content}

---

*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            return combined_summary
        except Exception as e:
            print(f"Error enhancing summary: {str(e)}")
            return None

    def process(self):
        """Run the complete pipeline"""
        try:
            print("\n=== Starting Lecture Processing Pipeline ===")
            
            # Step 1: Convert to MP3 if needed
            mp3_file = self.convert_to_mp3(self.input_file)
            if not mp3_file:
                return
            
            # Step 2: Split audio into segments
            segments = self.split_audio(mp3_file)
            if not segments:
                return
            
            # Step 3: Transcribe all segments
            print("\nTranscribing segments...")
            transcriptions = []
            for i, segment in enumerate(segments, 1):
                print(f"Transcribing segment {i} of {len(segments)}...")
                text = self.transcribe_segment(segment)
                if text:
                    transcriptions.append(text)
            
            if not transcriptions:
                print("No transcriptions were generated.")
                return
            
            # Step 4: Combine transcriptions
            combined_text = "\n\n".join(transcriptions)
            
            # Step 5: Enhance the summary
            print("\nEnhancing summary...")
            enhanced_summary = self.enhance_summary(combined_text)
            
            if enhanced_summary:
                # Save the final enhanced summary
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = os.path.join(self.output_dir, f"lecture_analysis_{timestamp}.md")
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    # Add YAML frontmatter
                    f.write("---\n")
                    f.write(f"title: Lecture Analysis Report\n")
                    f.write(f"date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"source_file: {os.path.basename(self.input_file)}\n")
                    f.write(f"generated_by: AI Lecture Assistant\n")
                    f.write("---\n\n")
                    # Write the enhanced summary
                    f.write(enhanced_summary)
                
                print(f"\n=== Pipeline Complete ===")
                print(f"Lecture analysis saved to: {output_file}")
                
                # Clean up temporary files
                for file in os.listdir(self.temp_dir):
                    os.remove(os.path.join(self.temp_dir, file))
                os.rmdir(self.temp_dir)
            else:
                print("Failed to enhance the summary.")
        
        except Exception as e:
            print(f"Error in pipeline: {str(e)}")
        finally:
            # Clean up temporary files in case of error
            if os.path.exists(self.temp_dir):
                for file in os.listdir(self.temp_dir):
                    os.remove(os.path.join(self.temp_dir, file))
                os.rmdir(self.temp_dir)

def main():
    # Define input file path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(base_dir, "data", "Frankfurt School of Finance & Management 3.m4a")
    
    # Create and run pipeline
    pipeline = LecturePipeline(input_file)
    pipeline.process()

if __name__ == "__main__":
    main() 