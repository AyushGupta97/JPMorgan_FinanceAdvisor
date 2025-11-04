# JPMorgan Finance Advisor

## Overview
JPMorgan Finance Advisor is a multi-agent financial advisory system built using the LangChain framework. The system consists of three primary agents that work together to provide tailored financial advice to clients. The agents leverage tools such as internet search and a knowledge store to achieve their goals.

## Features
- **Client Agent**: Simulates a client profile with attributes such as age, risk aversion, assets, and investments. It can generate dummy profiles using an LLM.
- **Advisor Agent**: Acts as the intermediary between the client and the analyst. It defines tasks for the analyst based on the client's profile and goals.
- **Analyst Agent**: Fetches information from the internet and a knowledge store to assist the advisor in tailoring responses to the client.
- **Knowledge Store**: Stores and retrieves relevant data for financial analysis.
- **Internet Search**: Uses DuckDuckGo to fetch real-time information.

## Project Structure
```
JPMorgan_FinanceAdvisor/
├── src/
│   ├── agents/
│   │   ├── client_agent.py
│   │   ├── advisor_agent.py
│   │   ├── analyst_agent.py
│   ├── tools/
│   │   ├── knowledge_store.py
│   │   ├── internet_search.py
├── main.py
├── requirements.txt
├── README.md
```

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/AyushGupta97/JPMorgan_FinanceAdvisor.git
   cd JPMorgan_FinanceAdvisor
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install Ollama https://ollama.com/download

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the main script:
   ```bash
   python3 -m src.main
   ```

2. Follow the prompts to interact with the agents.


## Areas of Improvement
1. Using a larger LLM with larger context window
2. Experimenting with a LLM fine tuned on financial data
3. Integrate different web api for data sources, such as yahoo finance for stock or news API
4. Restructure the knowledge store on different attributes other than just name
5. Define rule based prompting, example: if user is interested in stocks investment then define prompt accordingly or based on client risk aversion level