import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from crewai_tools import CSVSearchTool, SerperDevTool, ScrapeWebsiteTool
import agentops
import typing

load_dotenv()

csv_search_tool = CSVSearchTool(csv='data.csv')

@CrewBase

class ContentStrategyCrew():
    """Content strategy crew"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self):
        # Initialize with dynamic CSV paths
        self.csv_tool_1 = CSVSearchTool(csv='data1.csv')
        # self.csv_tool_2 = CSVSearchTool(csv='data2.csv')
        self.serper_dev_tool = SerperDevTool()
        self.scrape_website_tool = ScrapeWebsiteTool()

    # Agents Section
    @agent
    def historical_data_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['historical_data_analyst'],
            verbose=True,
            tools=[self.csv_tool_1]  # Use the appropriate CSV tool
        )
    
    @agent
    def company_background_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['company_background_analyst'],
            verbose=True,
            tools=[self.serper_dev_tool, self.scrape_website_tool]
        )
    
    @agent
    def data_provider_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['data_provider_agent'],
            verbose=True,
            tools=[self.serper_dev_tool, self.scrape_website_tool]
        )
    
    @agent
    def content_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['content_strategist'],
            verbose=True,
        )

    # Tasks Section
    @task
    def social_media_analysis(self) -> Task:
        return Task(
            config=self.tasks_config['social_media_analysis'],
            context=[],  # Add any required context
            tools=[self.csv_tool_1],  # Explicitly attach tool
            output_file='./output/analysis_report.md'
        )
    
    @task
    def web_background_analysis(self) -> Task:
        return Task(
            config=self.tasks_config['web_background_analysis'],
            context=[],
            tools=[self.serper_dev_tool],
        )
    
    @task
    def company_data_scraping(self) -> Task:
        return Task(
            config=self.tasks_config['company_data_scraping'],
            context=[],
            tools=[self.scrape_website_tool],
            output_file='./output/company_data_scraping_report.md'
        )
    
    @task
    def web_search(self) -> Task:
        return Task(
            config=self.tasks_config['web_search'],
            context=[],
            tools=[self.serper_dev_tool]
        )

    @task
    def website_scraping(self) -> Task:
        return Task(
            config=self.tasks_config['website_scraping'],
            context=[],
            tools=[self.scrape_website_tool],
            output_file='./output/websearch_report.md'
        )
    
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


    agentops.init(api_key=os.getenv("AGENTOPS_API_KEY"))
    @crew
    def crew(self) -> Crew:
        """Creates the Content Strategy crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            # manager_llm="gpt-4o-mini",  # Update with your preferred manager LLM
            verbose=True,
            memory=True,
            full_output=True
        )