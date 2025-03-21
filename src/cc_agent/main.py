import sys
import os
import warnings
from datetime import datetime
from crew import ContentStrategyCrew
from dotenv import load_dotenv
load_dotenv()



warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def execute_crew():
    """Run the content strategy crew with actual inputs"""
    inputs = {
        'csv_file': 'data.csv',
        'company_name': 'convogrid.ai',
        'industry': 'Conversation Design and Marketing and Content Creation',
        'brand_guidelines': 'modern, youthful, eco-conscious',
        'brand_voice': 'casual yet authoritative',
        'current_date': '2025 March 20'
    }
    # agentops.init(
    # api_key=os.getenv("AGENTOPS_API_KEY"),
    # tags=['cc-agent']
    # )
    
    try:
        ContentStrategyCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        print(f"Execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    execute_crew()  # Single entry point without recursion
