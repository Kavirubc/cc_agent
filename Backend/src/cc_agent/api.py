from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
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

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Mount static files directory
app.mount("/static", StaticFiles(directory="src/cc_agent/www"), name="static")

# MongoDB setup
mongo_uri = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/cc_agent_db")
client = None
db = None
output_collection = None

def connect_to_mongodb():
    global client, db, output_collection
    if mongo_uri:
        try:
            # Set a timeout for server selection to avoid hanging
            client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            # Force a connection to verify it works
            client.server_info()
            db = client["cc_agent_db"]  # Database name
            output_collection = db["crew_outputs"]  # Collection name
            logging.info("Connected to MongoDB successfully")
            return True
        except pymongo.errors.ServerSelectionTimeoutError as e:
            logging.error(f"MongoDB connection timed out: {e}")
            client = None
            return False
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}\n{traceback.format_exc()}")
            client = None
            return False
    else:
        logging.warning("MONGODB_URI not set or invalid. MongoDB integration disabled.")
        return False

# Initial connection attempt
connect_to_mongodb()

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

    # Simulate actual agent and task execution logging
    agent_task_logs = [
        {"agent": "Historical Data Analyst", "task": "Social Media Analysis"},
        {"agent": "Company Background Analyst", "task": "Company Data Scraping"},
        {"agent": "Data Provider Agent", "task": "Web Search & Scraping"},
        {"agent": "Content Strategist", "task": "Content Strategy Planning"}
    ]

    for item in agent_task_logs:
        agent = item["agent"]
        task = item["task"]
        log_message = f"Agent: {agent} - Task: {task}\n"
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
        
        # Convert inputs to dictionary explicitly
        inputs_dict = inputs.model_dump()
        
        # Execute the crew and get the output
        crew_output = crew_instance.kickoff(inputs=inputs_dict)
        
        # Extract the raw output string if it's a CrewOutput object
        if hasattr(crew_output, 'raw'):
            output = crew_output.raw
        else:
            output = str(crew_output)
        
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
    """Saves the output to MongoDB with reconnection logic."""
    global client, db, output_collection
    
    # Try to reconnect if client is None
    if client is None:
        connect_to_mongodb()
    
    if client:
        try:
            # Test the connection with a ping before attempting to save
            client.admin.command('ping')
            
            document = {
                "session_id": session_id,
                "date": datetime.datetime.now(),
                "inputs": inputs,
                "output": output,
                "logs": logs
            }
            
            # Try to save to MongoDB
            result = output_collection.insert_one(document)
            logging.info(f"Output saved to MongoDB with session ID: {session_id}, document ID: {result.inserted_id}")
            return True
        except pymongo.errors.AutoReconnect:
            # Handle reconnection
            logging.warning("MongoDB connection lost. Attempting to reconnect...")
            if connect_to_mongodb():
                # Try again after reconnection
                try:
                    document = {
                        "session_id": session_id,
                        "date": datetime.datetime.now(),
                        "inputs": inputs,
                        "output": output,
                        "logs": logs
                    }
                    result = output_collection.insert_one(document)
                    logging.info(f"Output saved to MongoDB after reconnection with session ID: {session_id}")
                    return True
                except Exception as e:
                    error_msg = f"Failed to save to MongoDB after reconnection: {str(e)}\n{traceback.format_exc()}"
                    logging.error(error_msg)
                    return False
            return False
        except Exception as e:
            error_msg = f"Failed to save to MongoDB: {str(e)}\n{traceback.format_exc()}"
            logging.error(error_msg)
            
            # Try a simple document to see if it's a data format issue
            try:
                test_doc = {"test": "simple_test", "date": datetime.datetime.now()}
                test_result = output_collection.insert_one(test_doc)
                logging.info(f"Test document saved successfully, ID: {test_result.inserted_id}")
                logging.error("Original document was too large or had invalid format")
                
                # Try saving a simplified version of the original document
                simplified_doc = {
                    "session_id": session_id,
                    "date": datetime.datetime.now(),
                    "inputs": inputs,
                    "output_summary": output[:1000] + "..." if len(output) > 1000 else output,
                    "logs_summary": logs[:1000] + "..." if len(logs) > 1000 else logs
                }
                result = output_collection.insert_one(simplified_doc)
                logging.info(f"Simplified output saved to MongoDB with session ID: {session_id}")
                return True
            except Exception as inner_e:
                logging.error(f"Even simplified document failed: {str(inner_e)}")
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
        
        # Try saving to MongoDB
        mongodb_save_result = await save_to_mongodb(session_id, inputs.model_dump(), output, full_logs)
        
        if mongodb_save_result:
            save_message = f"\nExecution details saved to MongoDB with session ID: {session_id}\n"
        else:
            # Try one more time with a direct connection attempt
            logging.info("Attempting one more MongoDB connection...")
            if connect_to_mongodb():
                mongodb_save_result = await save_to_mongodb(session_id, inputs.model_dump(), output, full_logs)
                if mongodb_save_result:
                    save_message = f"\nExecution details saved to MongoDB with session ID: {session_id} (after retry)\n"
                else:
                    save_message = f"\nFailed to save execution details to MongoDB even after reconnection attempt\n"
            else:
                save_message = f"\nFailed to save execution details to MongoDB\n"
        
        log_collector.add_log(save_message)
        yield save_message.encode()

    return StreamingResponse(generate_stream(), media_type="text/plain")

@app.get("/health")
async def health_check():
    """Health check endpoint with MongoDB write test."""
    global client, db
    
    if client is None:
        connect_to_mongodb()
        
    if client:
        try:
            # Ping MongoDB to check connection
            client.admin.command('ping')
            
            # Test write operation
            test_collection = db["health_checks"]
            test_doc = {"test": "write_test", "timestamp": datetime.datetime.now()}
            test_result = test_collection.insert_one(test_doc)
            test_collection.delete_one({"_id": test_result.inserted_id})
            
            return {
                "status": "healthy", 
                "mongodb": "connected and writable",
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            error_details = str(e)
            # Try to reconnect
            if connect_to_mongodb():
                return {
                    "status": "recovered",
                    "mongodb": "reconnected after error",
                    "previous_error": error_details,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy", 
                    "mongodb": f"error: {error_details}",
                    "timestamp": datetime.datetime.now().isoformat()
                }
    else:
        return {
            "status": "unhealthy", 
            "mongodb": "not configured or connection failed",
            "timestamp": datetime.datetime.now().isoformat()
        }
    
@app.get("/")
async def read_root():
    """Serve the main HTML file."""
    return HTMLResponse(open("src/cc_agent/www/index.html").read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)