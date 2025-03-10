# AI Lecture Notation Assistant

An intelligent tool that helps students convert lecture audio recordings into structured text and generate comprehensive summaries using Large Language Models (LLM).

## Overview

This project aims to enhance the learning experience by:
- Converting lecture MP3 recordings into text
- Utilizing LLM to generate concise summaries
- Creating structured knowledge representations
- Helping students better understand and retain lecture content

## Features

- Audio to text conversion
- Intelligent lecture summarization
- Knowledge structure generation
- Study aid generation

## Prerequisites

- Python 3.x
- Required Python packages (see requirements.txt)
- OpenAI API key (for LLM functionality)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AI-Assitant-at-lecture-notation.git
cd AI-Assitant-at-lecture-notation
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Usage

1. Place your lecture MP3 files in the designated input directory
2. Run the conversion process:
```bash
python main.py --input path/to/lecture.mp3
```
3. Access the generated summaries and structured notes in the output directory

## Project Structure

```
AI-Assitant-at-lecture-notation/
├── input/              # Directory for lecture audio files
├── output/             # Generated text and summaries
├── src/                # Source code
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the LLM capabilities
- Contributors and maintainers