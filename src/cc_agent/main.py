import sys
import warnings
from datetime import datetime
from crew import ContentStrategyCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def execute_crew():
    """Run the content strategy crew with actual inputs"""
    inputs = {
        'csv_file': 'data.csv',
        'company': 'convogrid.ai',
        'industry': 'Conversation Design \ Marketing and Content Creation',
        'brand_guidelines': 'modern, youthful, eco-conscious',
        'brand_voice': 'casual yet authoritative'
    }
    
    try:
        ContentStrategyCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        print(f"Execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    execute_crew()  # Single entry point without recursion
