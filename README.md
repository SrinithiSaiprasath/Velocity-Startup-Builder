# Startup Builder OS 🚀

Startup Builder OS is an automated, multi-agent AI framework designed to take a startup idea from initial research to a pitch-ready launch. It utilizes specialized AI personas, **LangGraph** for state management, and the **Model Context Protocol (MCP)** to integrate with essential tools like Figma, Google Drive, Google Sheets, and Tavily.

## 🏗️ Project Structure

- **`main.py`**: The entry point for the full automated LangGraph workflow.
- **`agent_bridge.py`**: The "Communication Hub" and interactive terminal interface. It routes user requests to specific agents or triggers the full workflow.
- **`registry.py`**: Manages connections to MCP servers (Tavily, Reddit, Figma, Google Drive/Sheets).
- **`state.py`**: Defines the global state shared across all agents.
- **`agents/`**: Contains specialized personas:
  - **Archeologist**: Market trends and pain point research.
  - **Architect**: Vision, mission, and core audience profiling.
  - **Business Analyst**: Market sizing (TAM/SAM/SOM) and business modeling.
  - **Investor**: Financial modeling and valuation (Google Sheets).
  - **Product Owner**: Feature mapping and technical flowcharts (Mermaid).
  - **Designer**: UI/UX wireframes and Figma integration.
  - **Marketer**: Social media growth strategies and asset storage.
- **`figma-console-mcp/`**: A specialized MCP server for deep Figma integration.
- **`reports/`**: Output folder for generated strategies and blueprints.

## ⚙️ Setup

### 1. Prerequisites
- Python 3.10+
- Node.js (for MCP servers)
- [Tavily API Key](https://tavily.com/)
- [OpenAI](https://platform.openai.com/) or [Anthropic](https://console.anthropic.com/) API Key

### 2. Installation
1. Clone the repository.
2. Activate the virtual environment:
   ```powershell
   & .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

### 3. Environment Variables
Create a `.env` file in the root directory (refer to `.env.template` if available) and add your keys:
```env
TAVILY_API_KEY=your_tavily_key
OPENAI_API_KEY=your_openai_key
FIGMA_PERSONAL_ACCESS_TOKEN=your_figma_token
FIGMA_FILE_KEY=your_figma_file_id
# If using Google Drive/Sheets
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/client_secret.json
```

---

## 🚀 Running the Project

### Option 1: The Interactive Terminal / Chat Interface
The **Agent Bridge** provides an interactive "Chat-like" interface in your terminal. This is the best way to interact with specific agents or trigger the full orchestrator.

**To start the interactive interface:**
```powershell
python agent_bridge.py
```
Once started, you can type natural language commands like:
- `"Research rural fintech trends"` (Routes to BA/Archeologist)
- `"Build a figma template for a landing page"` (Routes to Designer)
- `"Generate a financial model for an AI SaaS"` (Routes to Investor/BA)

To exit the interactive session, type `exit`.

### Option 2: Running via Agent Bridge (Direct Command)
You can pass a command directly to the Agent Bridge without entering the interactive loop:
```powershell
python agent_bridge.py "build a design for a mobile app"
```

### Option 3: Full Automated Workflow
To run the complete linear startup building process (from research to marketing) for a specific prompt:
1. Open `main.py`.
2. Update the `user_prompt` in the `initial_state` block.
3. Run the script:
   ```powershell
   python main.py
   ```

---

## 🛠️ MCP Tools Integration
This project uses the Model Context Protocol to bridge AI agents with real-world tools. Ensure your MCP servers are configured in `registry.py` if you wish to extend them. The system currently supports:
- **Tavily**: Web search and research.
- **Reddit**: Community sentiment analysis.
- **Figma**: UI/UX design automation.
- **Google Drive/Sheets**: Document storage and financial modeling.
