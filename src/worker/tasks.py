from worker.celery_app import celery_app
import zipfile
import os

@celery_app.task(bind=True)
def zip_folder(self, folder_path: str, output_dir: str):
    if not os.path.isdir(folder_path):
        raise ValueError(f"The folder path {folder_path} is not a valid directory.")
    
    folder_path = os.path.abspath(folder_path)
    folder_name = os.path.basename(folder_path.rstrip(os.sep))
    zip_path = os.path.join(output_dir, f"{folder_name}.zip")
    os.makedirs(output_dir, exist_ok=True)

    all_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            all_files.append(os.path.join(root, file))

    total_files = len(all_files)
    if total_files == 0:
        return {
            "status": "empty",
            "zip": zip_path
        }

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for index, full_path in enumerate(all_files, start=1):
            relative_path = os.path.relpath(full_path, start=folder_path)
            zipf.write(full_path, arcname=relative_path)
            self.update_state(
                state='PROGRESS', 
                meta={
                    'current': index,
                    'total': total_files,
                    'percent': int((index + 1) / total_files * 100),
                    'file': relative_path
                }
            )


    return {
        "status": "Completed",
        "current": total_files,
        "total": total_files,
        "percent": 100,
        "folder": folder_path,
        "zip": zip_path,
    }