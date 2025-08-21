# internship-ai
A CrewAI application for assisting with internship applications using MCP tools

# How it works
When the crew of agents is run, the github_agent will use the github MCP server to
go to https://github.com/vanshb03/Summer2026-Internships and fetch the list of
internships from there. Then the google_agent takes over and goes to my google doc
where I like to keep track of open internships with my own organizational system. It compares
the list from github to the list in my google doc and adds any new internships from the
github repo to my google doc while adhering to the organizational and color coding system
I use in the google doc. Finally, the crew produces a markdown file that summarizes
the changes it made to my google doc.

# MCP servers
Github: https://smithery.ai/server/@smithery-ai/github

Google: https://github.com/a-bonus/google-docs-mcp (this mcp server is added as a submodule to my project)
