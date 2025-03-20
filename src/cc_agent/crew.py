import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from crewai_tools import CSVSearchTool, SerperDevTool, ScrapeWebsiteTool
import agentops


load_dotenv()
agentops.init(api_key=os.getenv("AGENTOPS_API_KEY"))


csv_search_tool = CSVSearchTool(csv='data.csv')

@CrewBase

class ContentStrategyCrew():
    """Content strategy crew"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self):
        # Initialize with dynamic CSV path
        self.csv_tool = CSVSearchTool(csv='data.csv')

    # Agents Section
    @agent
    def data_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['data_analyst'],
            
            verbose=True,
            tools=[self.csv_tool]
        )
    
    @agent
    def retrieve_news(self) -> Agent:
        return Agent(
			config=self.agents_config['retrieve_news'],
			tools=[SerperDevTool()],
			verbose=True,
		)
	

    @agent
    def website_scraper(self) -> Agent:
        return Agent(
			config=self.agents_config['website_scraper'],
			tools=[ScrapeWebsiteTool()],
			verbose=True,
			# llm=self.ollama_llm
		)

    @agent
    def trend_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['trend_researcher'],
            verbose=True
        )

    @agent
    def content_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['content_strategist'],
            verbose=True
        )

    @agent
    def content_creator(self) -> Agent:
        return Agent(
            config=self.agents_config['content_creator'],
            verbose=True
        )

    @agent
    def quality_controller(self) -> Agent:
        return Agent(
            config=self.agents_config['quality_controller'],
            verbose=True
        )

    # Tasks Section
    @task
    def data_analysis(self) -> Task:
        return Task(
            config=self.tasks_config['data_analysis'],
            context=[],  # Add any required context
            tools=[self.csv_tool],  # Explicitly attach tool
            output_file='./output/analysis_report.md'
    )

    @task
    def retrieve_news_task(self) -> Task:
        return Task(
			config=self.tasks_config['retrieve_news_task'],
		)


    @task
    def website_scrape_task(self) -> Task:
        return Task(
			config=self.tasks_config['website_scrape_task'],
		)

    @task
    def trend_research(self) -> Task:
        return Task(
            config=self.tasks_config['trend_research'],
            output_file='./output/trend_report.md'
        )

    @task
    def strategy_development(self) -> Task:
        return Task(
            config=self.tasks_config['strategy_development'],
            output_file='./output/content_calendar.md'
        )

    @task
    def content_creation(self) -> Task:
        return Task(
            config=self.tasks_config['content_creation'],
            output_file='./output/content_assets.md'
        )

    @task
    def quality_assurance(self) -> Task:
        return Task(
            config=self.tasks_config['quality_assurance'],
            output_file='./output/final_package.md'
        )


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
