from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table

from worker.celery_app import celery_app
from worker.tasks import zip_folder

app = typer.Typer(help=" Batch folder zipping service using Celery and Redis.")
console = Console()

@app.command()
def zip(
    folder: str = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        help="Path to the folder containing subfolders to be zipped."
    ), 
    output_dir: str = typer.Option(
        Path("zipped_output"),
        "--output-dir",
        "-o",
        help="Directory where the zipped files will be saved."
        ),
    ):
    """
    Submit a folder path which contains subfolders for zipping task to the Celery worker.

    Args:
        folder_path (str): The path of the folder that containes folders to be zipped.
        output_dir (str): The directory where the zip file will be saved.
    """ 

    folder_path = Path(folder).resolve()
    
    subfolders = [f for f in folder_path.iterdir() if f.is_dir()]
    if not subfolders:
        console.print(f"[red]No subfolders found in {folder_path} to zip.[/red]")
        raise typer.Exit(code=1)
    console.print(
        f"""[bold cyan ]Queuing zipping tasks for {len(subfolders)} 
        subfolders in [yellow]{folder_path}[/yellow]...[/bold cyan ]"""
    )
    table = Table(title="Zipping Tasks Status")
    table.add_column("Subfolder", style="cyan")
    table.add_column("Task ID", style="magenta")
    table.add_column("Status", style="green")

    for subfolder in subfolders:
        task = celery_app.send_task(
            'tasks.zip_folder', 
            args=[str(subfolder), str(output_dir)]
        )    
        table.add_row(str(subfolder.name), task.id, "Queued")
    
    console.print(table)
    console.print(
        f"""[bold green]All tasks have been queued. 
        Zipped files will be saved in [yellow]{output_dir}[/yellow].[/bold green]"""
        )
    
if __name__ == "__main__":
    app()