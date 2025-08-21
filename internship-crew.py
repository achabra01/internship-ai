from crewai import Agent, Crew, Task, Process
from crewai_tools import MCPServerAdapter
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from mcp import StdioServerParameters
from dotenv import load_dotenv
import os

load_dotenv()

specialist_knowledge = StringKnowledgeSource(
    content="""
The text can be highlighted in a few different ways:
* no highlighting - means that the internship application isn't open or there is no info currently about this internship application
* yellow - means that the internship application is open and it is either in-progress or hasn't been started yet
* green - means that the internship application has been submitted
* red - means that the internship rejected the application

ONLY THE USER IS ALLOWED TO HIGHLIGHT IN GREEN OR RED, YOU CAN ONLY USE YELLOW!

Here's a simple example of the structure you should aim for when working in the google doc:
Banks:
    1. company1 : url_for_company1_application
Quant Trading/Asset Managers/Hedge Funds:
    2. company2
        * role1_at_company2 : url_for_role1_at_company2_application
        * role2_at_company2 : url_for_role2_at_company2_application
Other Firms:
"""
)

google_server_params = StdioServerParameters(
            command="node",
            args=[os.getenv('PATH_TO_SERVER')],
            env={"NODE_ENV": "production"}
        )

github_server_params = {
    "url": os.getenv('SMITHERY_URL'),
    "transport": "streamable-http"
}

# List of MCP tools from the Google MCP server: readGoogleDoc, appendToGoogleDoc,
# insertText, deleteRange, applyTextStyle, applyParagraphStyle, insertTable, editTableCell,
# insertPageBreak, fixListFormatting, addComment, findElement, formatMatchingText,
# listGoogleDocs, searchGoogleDocs, getRecentGoogleDocs, getDocumentInfo, createFolder,
# listFolderContents, getFolderInfo, moveFile, copyFile, renameFile, deleteFile,
# createDocument, createFromTemplate
try:
    with MCPServerAdapter(github_server_params) as github_tools:
        with MCPServerAdapter(google_server_params) as google_tools:
            print(f"Available tools from Streamable HTTP MCP server: {[tool.name for tool in github_tools]}")
            print(f"Available tools from Local MCP server: {[tool.name for tool in google_tools]}")

            github_agent = Agent(
                role="Expert Git User",
                goal="""You are an expert git and github user. You are great at reading
                        README files and understanding them.""",
                backstory="""With over 10 years of experience in git and github
                            you excel at reading README files.""",
                tools=github_tools,
                llm=os.getenv("OPENAI_MODEL_NAME"),
                verbose=True,
                allow_delegation=False
            )

            github_task = Task(
                description="""Go to the Summer2026-Internships repository hosted
                               by vanshb03 and read the README""",
                expected_output="""A list of all the companies offering internships
                                   with the open roles for each company and the
                                   links to every application""",
                agent=github_agent
            )

            google_agent = Agent(
                role="Expert Google User",
                goal="""You are an expert google docs and google drive user.
                        You are great at creating, editing, and reading google docs.""",
                backstory="""With over 10 years of experience in google docs
                            and google drive, you excel at making google docs in google drive.""",
                knowledge_sources=[specialist_knowledge],
                tools=google_tools,
                llm=os.getenv("OPENAI_MODEL_NAME"),
                verbose=True,
                allow_delegation=False
            )

            google_task = Task(
                description="""MAIN OBJECTIVE: Update the 'Summer 2026 Internship List' Google Doc by comparing it with the GitHub README internship list.

                   SPECIFIC ACTIONS TO TAKE IN THE GOOGLE DOC:
                   
                   1. An internship opportunity is on the Github but not in the google doc:
                      - Determine which category it falls under: Banks, Quant Trading/Asset Managers/Hedge Funds, or Other Firms
                      - Add the company name for the opportunity at the end of the numbered list for that category
                      - Highlight the company name in yellow which means the internship is open but the application hasn't been started or hasn't been finished
                      - Add the link to that application next to the company name if the link is available
                   2. An internship opportunity is on the Github and in the google doc but the company name in the google doc isn't highlighted:
                      - highlight the company name in yellow which means the internship application is open but the application hasn't been started or hasn't been finished
                      - add the link to that application next to the company name if the link is available
                   3. An internship opportunity is not in the Github but it is in the google doc:
                      - Don't change anything for that company name in the google doc, just leave it as is
                   4. An internship opportunity is already highlighted yellow, green, or red in the google doc:
                      - Don't modify that internship opportunity in the google doc unless there's a link for that opportunity in the Github that hasn't been added to the google doc. In that case, just add the link to that opportunity in the google doc.
                   5. A special case where a company in the Github has more than one role open:
                      - Follow the appropriate scenario from 1 - 4 but with a slight change
                      - Under that company name in the google doc add all of the new roles for that company and the corresponding application links for each role.
                   
                   After making all necessary updates to the Google Doc, provide a summary report of your actions.""",
                expected_output="""A summary report containing:
                       • List of companies/roles added to the Google Doc
                       • List of companies/roles that were highlighted in yellow
                       • List of application links that were added
                       • Any uncertainties or issues encountered during the update process""",
                output_file="changes_to_internship_doc.md",
                agent=google_agent
            )

            crew = Crew(
                agents=[github_agent, google_agent],
                tasks=[github_task, google_task],
                verbose=True,
                process=Process.sequential
            )
            
            crew.kickoff()

except Exception as e:
    print(f"Error connecting to or using one of the MCP servers: {e}")
    print("Ensure the MCP servers are running and accessible.")