"""Command line interface for Drive Organizer."""

import os
import sys
import asyncio
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
import typer
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
from rich.console import Console
from loguru import logger
from ..organizer import DriveOrganizer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = typer.Typer(
    name="drive-organizer",
    help="Organize your Google Drive images using AI-powered image recognition",
    add_completion=False
)

console = Console()


def load_config(config_path: Optional[str]) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    
    Args:
        config_path: Path to the configuration file
    
    Returns:
        Configuration dictionary
    """
    if not config_path:
        return {}
    
    config_path = os.path.expanduser(config_path)
    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        return {}
    
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config or {}
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return {}


@app.command()
def organize(
    source: str = typer.Option(..., "--source", "-s", help="Source folder path in Google Drive"),
    destination: str = typer.Option(..., "--destination", "-d", help="Destination folder path in Google Drive"),
    recognition: str = typer.Option("gemini", "--recognition", "-r", help="Recognition provider (aws or gemini)"),
    batch_size: int = typer.Option(10, "--batch-size", "-b", help="Number of images to process in a batch"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file")
):
    """Organize images from a source folder to a destination folder."""
    config_dict = load_config(config)
    
    async def run_organizer():
        organizer = DriveOrganizer(
            recognition_provider=recognition,
            config=config_dict,
            batch_size=batch_size
        )
        
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            refresh_per_second=10
        ) as progress:
            task = progress.add_task("[green]Organizing images...", total=1.0)
            
            def update_progress(current, total):
                progress.update(task, completed=current / total if total > 0 else 1.0)
            
            success, failure = await organizer.organize_folder(source, destination, update_progress)
            
        console.print(f"\nOrganization complete!")
        console.print(f"[green]{success} files successfully organized")
        
        if failure > 0:
            console.print(f"[red]{failure} files failed to organize")
            
        await organizer.close()
    
    asyncio.run(run_organizer())


@app.command()
def analyze(
    source: str = typer.Option(..., "--source", "-s", help="Source folder path in Google Drive"),
    recognition: str = typer.Option("gemini", "--recognition", "-r", help="Recognition provider (aws or gemini)"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum number of images to analyze"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file")
):
    """Analyze images in a folder without organizing them."""
    config_dict = load_config(config)
    
    async def run_analyzer():
        organizer = DriveOrganizer(
            recognition_provider=recognition,
            config=config_dict
        )
        
        if not await organizer.authenticate():
            console.print("[red]Authentication failed")
            return
        
        console.print(f"[blue]Listing images in {source}...")
        image_files = await organizer.get_image_files(source)
        
        if not image_files:
            console.print("[yellow]No image files found in the source folder")
            return
        
        files_to_analyze = image_files[:limit]
        console.print(f"[blue]Analyzing {len(files_to_analyze)} images...")
        
        for i, file in enumerate(files_to_analyze):
            file_id = file['id']
            file_name = file['name']
            
            console.print(f"\n[bold]{i+1}/{len(files_to_analyze)}[/bold] Analyzing [cyan]{file_name}[/cyan]...")
            
            # Download the file
            temp_path = os.path.join(organizer.temp_dir, file_name)
            await organizer.storage.download_file(file_id, temp_path)
            
            # Analyze the file
            category, labels = await organizer.recognizer.analyze_image(temp_path)
            
            # Display results
            console.print(f"  Category: [green]{category}[/green]")
            console.print(f"  Labels: [yellow]{', '.join(labels[:10])}[/yellow]")
            
            # Clean up
            os.remove(temp_path)
        
        await organizer.close()
    
    asyncio.run(run_analyzer())


@app.command()
def web(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind the web server to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind the web server to"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file")
):
    """Start the web interface."""
    try:
        import uvicorn
        from ..web import create_app
    except ImportError:
        console.print("[red]Web interface dependencies not installed. Run pip install 'drive-organizer[web]'")
        return
    
    config_dict = load_config(config)
    app_instance = create_app(config_dict)
    
    console.print(f"[green]Starting web interface at http://{host}:{port}")
    uvicorn.run(app_instance, host=host, port=port)


@app.command()
def init():
    """Initialize the configuration files and authentication."""
    config_dir = os.path.expanduser("~/.drive-organizer")
    os.makedirs(config_dir, exist_ok=True)
    
    config_path = os.path.join(config_dir, "config.yaml")
    
    if not os.path.exists(config_path):
        default_config = {
            "recognition": {
                "provider": "gemini",
            },
            "storage": {
                "provider": "google_drive",
            },
            "organization": {
                "include_year": True,
                "include_month": False,
                "use_original_filenames": False,
            },
            "categories": {
                "Landscapes": ["mountain", "ocean", "sunset", "beach", "forest", "river"],
                "People": ["person", "face", "group", "crowd", "portrait"],
                "Food": ["meal", "dish", "restaurant", "cooking", "dinner", "lunch"],
                "Animals": ["dog", "cat", "bird", "pet", "wildlife", "zoo", "farm", "animal"],
                "Buildings": ["building", "architecture", "house", "skyscraper", "monument"],
                "Transportation": ["car", "vehicle", "bicycle", "motorcycle", "bus", "train"],
                "Events": ["wedding", "party", "concert", "festival", "ceremony", "celebration"],
                "Documents": ["document", "text", "paper", "receipt", "certificate", "letter"],
                "Screenshots": ["screenshot", "screen", "display", "monitor", "computer"],
                "Other": []
            }
        }
        
        with open(config_path, 'w') as file:
            yaml.dump(default_config, file, default_flow_style=False)
        
        console.print(f"[green]Created default configuration at {config_path}")
    else:
        console.print(f"[yellow]Configuration already exists at {config_path}")
    
    # Test authentication
    async def test_auth():
        organizer = DriveOrganizer()
        
        console.print("[blue]Testing authentication...")
        if await organizer.authenticate():
            console.print("[green]Authentication successful!")
        else:
            console.print("[red]Authentication failed")
        
        await organizer.close()
    
    asyncio.run(test_auth())


if __name__ == "__main__":
    app()
