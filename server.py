import pandas as pd
import os
import uuid
from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse

from classify import classify_logs

app = FastAPI()

def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)

@app.post("/classify/")
def classify(file: UploadFile, background_tasks: BackgroundTasks):
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="The input has to be a .csv file")
    
    try:
        df = pd.read_csv(file.file)
        if 'source' not in df.columns or 'log_message' not in df.columns:
            raise HTTPException(status_code=400, detail="The input CSV file must contain 'source' and 'log_message' columns.")

        df['label'] = classify_logs(list(zip(df['source'], df['log_message'])))

        os.makedirs("resources", exist_ok=True)

        # Unique path per request prevents collisions and premature deletion
        output_file = f"resources/classified_logs_{uuid.uuid4().hex}.csv"

        df.to_csv(output_file, index=False)
        print("Logs successfully classified.")

        # Delete the unique temp file after FileResponse finishes streaming
        background_tasks.add_task(remove_file, output_file)

        return FileResponse(
            output_file,
            media_type='text/csv',
            filename="classified_logs.csv"
        )
        # FileResponse is designed strictly to stream an existing file from server's filesystem

    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))