from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn
from pydantic import BaseModel
import asyncio
import datetime
import uuid
import os
import traceback
import json
import io
import logging
import sys
import glob
from typing import Dict, Any, Optional, List, Tuple
import pymongo
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MongoDB setup
mongo_uri = os.getenv("MONGODB_URI")
if mongo_uri:
    try:
        client = pymongo.MongoClient(mongo_uri)
        db = client["cc_agent_db"]  # Database name
        output_collection = db["crew_outputs"]  # Collection name
        logging.info("Connected to MongoDB")
    except pymongo.errors.ConnectionFailure as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        client = None
else:
    logging.warning("MONGODB_URI not set in .env file. MongoDB integration disabled.")
    client = None

class CrewInput(BaseModel):
    csv_file: str
    company_name: str
    industry: str
    brand_guidelines: str
    brand_voice: str
    current_date: str

class LogCollector:
    def __init__(self):
        self.logs = []
    
    def add_log(self, message):
        self.logs.append(message)
    
    def get_full_logs(self):
        return "".join(self.logs)

async def log_execution_details(inputs: Dict[str, str], log_collector: LogCollector):
    """Simulate streaming execution details and collect logs."""
    for key, value in inputs.items():
        await asyncio.sleep(0.5)
        log_message = f"Input - {key}: {value}\n"
        log_collector.add_log(log_message)
        yield log_message.encode()
    
    await asyncio.sleep(1)
    log_message = "Executing crew...\n"
    log_collector.add_log(log_message)
    yield log_message.encode()
    await asyncio.sleep(1)

    # Placeholder for actual agent and task execution logging
    agent_task_logs = [
        "Agent: Historical Data Analyst - Task: Social Media Analysis\n",
        "Agent: Company Background Analyst - Task: Company Data Scraping\n",
        "Agent: Data Provider Agent - Task: Web Search & Scraping\n",
        "Agent: Content Strategist - Task: Content Strategy Planning\n"
    ]

    for log_message in agent_task_logs:
        await asyncio.sleep(2)
        log_collector.add_log(log_message)
        yield log_message.encode()

    await asyncio.sleep(1)

async def run_crew_process(inputs: CrewInput, log_collector: LogCollector):
    """Runs the crew and captures the output."""
    from crew import ContentStrategyCrew  # Import here to avoid circular dependencies
    try:
        log_message = "Initializing ContentStrategyCrew...\n"
        log_collector.add_log(log_message)
        
        crew_instance = ContentStrategyCrew().crew()
        
        log_message = "Starting crew execution...\n"
        log_collector.add_log(log_message)
        
        output = crew_instance.kickoff(inputs=inputs.model_dump())
        
        log_message = "Crew execution completed successfully.\n"
        log_collector.add_log(log_message)
        
        return output
    except Exception as e:
        error_traceback = traceback.format_exc()
        log_message = f"Crew execution failed: {error_traceback}\n"
        log_collector.add_log(log_message)
        logging.error(log_message)
        return str(e)

async def save_to_mongodb(session_id: str, inputs: Dict[str, str], output: str, logs: str):
    """Saves the output to MongoDB."""
    if client:
        try:
            document = {
                "session_id": session_id,
                "date": datetime.datetime.now(),
                "inputs": inputs,
                "output": output,
                "logs": logs
            }
            result = output_collection.insert_one(document)
            logging.info(f"Output saved to MongoDB with session ID: {session_id}, document ID: {result.inserted_id}")
            return True
        except Exception as e:
            error_msg = f"Failed to save to MongoDB: {str(e)}"
            logging.error(error_msg)
            return False
    else:
        logging.warning("MongoDB client not initialized. Skipping save to MongoDB.")
        return False

@app.post("/execute_crew")
async def execute_crew_endpoint(inputs: CrewInput):
    """API endpoint to execute the crew and stream the output."""
    session_id = str(uuid.uuid4())
    log_collector = LogCollector()
    
    async def generate_stream():
        # Stream and collect logs
        async for log_message in log_execution_details(inputs.model_dump(), log_collector):
            yield log_message

        # Run the crew process and collect output
        output = await run_crew_process(inputs, log_collector)
        
        # Add completion message to logs
        completion_message = f"\nCrew execution completed. Session ID: {session_id}\n"
        log_collector.add_log(completion_message)
        yield completion_message.encode()
        
        output_message = f"\nOutput: {output}\n"
        log_collector.add_log(output_message)
        yield output_message.encode()
        
        # Save to MongoDB
        full_logs = log_collector.get_full_logs()
        mongodb_save_result = await save_to_mongodb(session_id, inputs.model_dump(), output, full_logs)
        
        if mongodb_save_result:
            save_message = f"\nExecution details saved to MongoDB with session ID: {session_id}\n"
        else:
            save_message = f"\nFailed to save execution details to MongoDB\n"
        
        log_collector.add_log(save_message)
        yield save_message.encode()

    return StreamingResponse(generate_stream(), media_type="text/plain")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if client:
        try:
            # Ping MongoDB to check connection
            client.admin.command('ping')
            return {"status": "healthy", "mongodb": "connected"}
        except Exception as e:
            return {"status": "unhealthy", "mongodb": f"error: {str(e)}"}
    else:
        return {"status": "healthy", "mongodb": "not configured"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
