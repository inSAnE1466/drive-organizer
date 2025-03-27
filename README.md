# Drive Organizer

A Python application to automatically organize your cloud storage images using AI-powered image recognition. Built with a React Vite frontend and a redis DB for data visualization + ease of use.

This started as a CRUD app with llm API calls and manual tool calls, but that is only because the original setup existed before LLMs had tool calls built into their libraries. I am going to build out an agentic flow with the api calls so as to build context for the image recognition as ensure that tool calls are as efficient as possible.

Orchestrator-worker flows work well for a task like this, as we are performing tasks asynchronously.



## Tech Stack

- Redis implementation to tag images and organize/visualize data (hashing for metadata)
- Gemini/PydanticAI for LLM and tool calls
- React Vite + ShadCN for frontend 
- Python FastAPI for backend 

## Features

- Connect to Google Drive to access and organize your images
- Analyze images using advanced image recognition (AWS Rekognition or Google Gemini API)
- Organize images into folders based on AI-detected content
- User-configurable categories for custom organization
- Parallel processing for improved performance
- Simple command-line and web interfaces

## Why This Project?

Managing the ever-growing collection of digital images has become increasingly challenging. This tool leverages the power of AI to automatically categorize and organize images based on their content, making it easier to find and manage your photo collection.


## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/drive-organizer.git
   cd drive-organizer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys and configuration
   ```

## Usage

### Command Line Interface

```bash
# Basic usage
python -m drive_organizer organize --source "Google Photos" --destination "Organized Photos"

# With custom configuration
python -m drive_organizer organize --config my_config.yaml

# Analyze without organizing
python -m drive_organizer analyze --source "My Images"

# Run web interface
python -m drive_organizer web
```

### Web Interface

1. Start the web server:
   ```bash
   python -m drive_organizer web
   ```

2. Open your browser and navigate to `http://localhost:8000`

## Configuration

Create a `config.yaml` file to customize your organization preferences:

```yaml
# Example configuration
recognition:
  provider: "gemini"  # or "aws"
  
categories:
  - name: "Landscapes"
    keywords: ["mountain", "ocean", "sunset", "beach", "forest", "river"]
  - name: "People"
    keywords: ["person", "face", "group", "crowd", "portrait"]
  - name: "Food"
    keywords: ["meal", "dish", "restaurant", "cooking", "dinner", "lunch"]
    
organization:
  include_year: true
  include_month: false
  use_original_filenames: false
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
