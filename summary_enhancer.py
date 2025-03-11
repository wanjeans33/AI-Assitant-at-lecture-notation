import os
from openai import OpenAI
from datetime import datetime
from src.config import Config

def enhance_lecture_summary(input_file, output_dir="output/enhanced_summaries"):
    """
    Enhance lecture summary using DeepSeek API and output as Markdown
    :param input_file: Path to input lecture summary file
    :param output_dir: Directory to save the enhanced summary
    :return: Path to the enhanced summary file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Read the original summary
        with open(input_file, 'r', encoding='utf-8') as f:
            original_summary = f.read()
        
        # Initialize DeepSeek client
        client = OpenAI(
            api_key=Config.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        
        # Construct the prompt for enhancement with Markdown formatting
        system_prompt = """You are an expert at analyzing and improving lecture summaries. Your task is to enhance the lecture summary and provide it in well-structured Markdown format. Please:

1. Remove any irrelevant content or transcription artifacts
2. Fix any transcription errors or unclear sentences
3. Organize the content using proper Markdown headings (##, ###, etc.)
4. Maintain the key points and main ideas from the lecture
5. Use proper academic language
6. Add clear transitions between sections
7. Remove any filler words or redundant information
8. Ensure the summary flows logically

Format requirements:
- Use # for the main title
- Use ## for major sections
- Use ### for subsections
- Use bullet points (- or *) for lists
- Use **bold** for emphasis on key terms
- Use > for important quotes or key takeaways
- Add a table of contents at the beginning
- Include a metadata section at the top with date and source
- Use proper Markdown formatting for any code blocks, if present
- Add horizontal rules (---) between major sections

Please ensure the output is in perfect Markdown format."""

        user_prompt = f"""Please enhance this lecture summary and convert it into a well-structured Markdown document:

{original_summary}"""

        # Get enhanced summary from DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=False
        )
        
        enhanced_summary = response.choices[0].message.content
        
        # Save the enhanced summary as Markdown
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"enhanced_summary_{timestamp}.md")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Add YAML frontmatter
            f.write("---\n")
            f.write(f"title: Enhanced Lecture Summary\n")
            f.write(f"date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"source_file: {os.path.basename(input_file)}\n")
            f.write(f"generated_by: DeepSeek AI\n")
            f.write("---\n\n")
            # Write the enhanced summary
            f.write(enhanced_summary)
        
        print(f"\nEnhanced summary saved to {output_file}")
        return output_file
        
    except Exception as e:
        print(f"Error enhancing summary: {str(e)}")
        return None

def main():
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    transcriptions_dir = os.path.join(base_dir, "output", "transcriptions")
    
    # Find the most recent lecture summary file
    summary_files = [f for f in os.listdir(transcriptions_dir) if f.startswith("lecture_summary_") and f.endswith(".txt")]
    if not summary_files:
        print("No lecture summary files found. Please run the transcription process first.")
        return
    
    # Sort by timestamp in filename and get the most recent
    latest_summary = sorted(summary_files)[-1]
    input_file = os.path.join(transcriptions_dir, latest_summary)
    
    print(f"\n=== Starting Summary Enhancement ===")
    print(f"Processing file: {latest_summary}")
    
    # Enhance the summary
    enhanced_file = enhance_lecture_summary(input_file)
    if enhanced_file:
        print("\n=== Summary Enhancement Complete ===")
        print("The summary has been saved in Markdown format with proper formatting and structure.")
    else:
        print("\nFailed to enhance summary. Please check the errors above.")

if __name__ == "__main__":
    main() 