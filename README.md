# Content Strategy Crew by KSRX

A powerful AI-powered content strategy system built with [crewAI](https://crewai.com) that orchestrates multiple specialized AI agents to analyze data, research trends, and develop comprehensive content strategies.

## Overview

The Content Strategy Crew automates the entire content planning process through a collaborative workflow where data flows from specialized agents to a central strategist:

```mermaid
graph TD
    subgraph "Content Strategy Crew"
        A[Crew Initialization]
        
        subgraph "Data Collection & Analysis"
            B[Historical Data Analyst]
            C[Company Background Analyst]
            D[Data Provider Agent]
        end
        
        subgraph "Strategy Development"
            E[Content Strategist]
        end
        
        A --> B
        A --> C
        A --> D
        
        B -->|Executes| F[Social Media Analysis Task]
        C -->|Executes| G[Company Data Scraping Task]
        D -->|Executes| H[Web Search & Scraping Tasks]
        
        F -->|Outputs| I[analysis_report.md]
        G -->|Outputs| J[company_data_scraping_report.md]
        H -->|Outputs| K[websearch_report.md]
        
        I -->|Context Input| L[Content Strategy Planning Task]
        J -->|Context Input| L
        K -->|Context Input| L
        
        E -->|Executes| L
        L -->|Outputs| M[content_strategy_plan.md]
    end
    
    classDef agent fill:#f9d5e5,stroke:#333,stroke-width:1px;
    classDef task fill:#eeeeee,stroke:#333,stroke-width:1px;
    classDef output fill:#d5f9e5,stroke:#333,stroke-width:1px;
    
    class B,C,D,E agent;
    class F,G,H,L task;
    class I,J,K,M output;
```


## How It Works

The system follows a sequential process where:

1. The Historical Data Analyst examines past social media performance
2. The Company Background Analyst researches your company's profile
3. The Data Provider Agent gathers current industry trends
4. The Content Strategist synthesizes all this information to create a comprehensive strategy

All data from the first three agents flows into the Content Strategist, who then creates a unified content strategy plan based on this collective intelligence.

## Installation

Ensure you have Python >=3.10 <3.13 installed on your system.

```bash
# Install dependencies
pip install -r requirements.txt

# Or using UV
pip install uv
crewai install
```


## Configuration

1. Add your API keys to the `.env` file:

```
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key
AGENTOPS_API_KEY=your_agentops_api_key
```

2. Prepare your data:
    - Place your social media analytics CSV file at `data1.csv`
3. Customize agent and task configurations in the YAML files:
    - `config/agents.yaml`: Define agent roles and goals
    - `config/tasks.yaml`: Customize task descriptions and outputs

## Usage

Run the Content Strategy Crew with:

```bash
python main.py
# Or
crewai run
```

The system will generate output files in the `./output/` directory:

- `analysis_report.md`: Social media performance analysis
- `company_data_scraping_report.md`: Company background research
- `websearch_report.md`: Industry trends and competitor analysis
- `content_strategy_plan.md`: Final comprehensive content strategy


## Key Implementation Note

To ensure the Content Strategist receives all data from previous tasks, make sure to configure the context properly:

```python
@task
def content_strategy_planning(self) -> Task:
    return Task(
        config=self.tasks_config['content_strategy_planning'],
        context=[
            self.social_media_analysis(),
            self.company_data_scraping(),
            self.website_scraping()
        ],
        output_file='./output/content_strategy_plan.md'
    )
```

This ensures that all the outputs from previous tasks flow into the Content Strategist, allowing for a truly integrated strategy.

## Process Flow

```mermaid
sequenceDiagram
    participant Crew as Content Strategy Crew
    participant HDA as Historical Data Analyst
    participant CBA as Company Background Analyst
    participant DPA as Data Provider Agent
    participant CS as Content Strategist
    
    Crew->>HDA: Analyze social media data
    HDA->>Crew: Return performance analysis
    Crew->>CBA: Research company background
    CBA->>Crew: Return company insights
    Crew->>DPA: Search & scrape industry trends
    DPA->>Crew: Return research findings
    Crew->>CS: Synthesize all data
    Note right of CS: Receives context from all previous tasks
    CS->>Crew: Deliver comprehensive strategy
```


## Creator

This project was created by Kaviru Hapuarachchi.

- Website: [kaviru.cc](https://kaviru.cc)
- Email: [hello@kaviru.cc](mailto:hello@kaviru.cc)
- GitHub: [@Kavirubc](https://github.com/Kavirubc)

If you have any questions or need assistance with this project, please don't hesitate to reach out!
