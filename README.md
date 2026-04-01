# SmartLease — AI Lease & Agreement Generator

> Generate legally structured lease and agreement documents in seconds, powered by the Anthropic Claude API.

**[Live Demo]https://web-production-1f5ab.up.railway.app/** · **[GitHub](https://github.com/shivamhire025/smartlease)**

**Welcome Screen with Claude Connector Button**
<img width="1470" height="721" alt="Screenshot 2026-03-25 at 2 41 29 PM" src="https://github.com/user-attachments/assets/311e3931-6e0c-4cac-9ac6-120bd60edff4" />

**Document Generated After Conversation**
<img width="1419" height="700" alt="Screenshot 2026-03-25 at 2 44 24 PM" src="https://github.com/user-attachments/assets/c3ee4c75-6668-4801-ba69-7802ee9af739" />

---

## What it does

SmartLease takes structured inputs from users and generates context-aware, professionally formatted legal documents using Claude as the generation engine. No templates, no copy-paste — describe the parties and terms, and get a complete document back instantly.

**Supported agreement types:**
- Residential Lease Agreement
- Service Agreement
- NDA (Non-Disclosure Agreement)

---

## Features

- **AI-powered document generation** — Claude API generates each document from scratch based on user inputs, not fixed templates
- **Structured input forms** — field validation and conditional logic adapts the form to the selected agreement type
- **MCP server support** — connect SmartLease to any Claude agent via a configuration script and invoke document generation directly inside Claude
- **Clean document output** — formatted, legally structured output ready to review and use
- **E-signature and cloud storage** — in development, scoped with a defined third-party API contract

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| AI | Anthropic Claude API |
| Protocol | MCP (Model Context Protocol) |
| Deployment | Railway |
| Dev tooling | Cursor |

---

## MCP Integration

SmartLease exposes an MCP server, meaning you can connect it directly to your Claude agent and invoke document generation capabilities inside Claude without opening the web app.

To connect, add the following to your Claude MCP configuration:

```json
{
  "mcpServers": {
    "smartlease": {
      "url": "https://web-production-3cb6e.up.railway.app/mcp"
    }
  }
}
```

Once connected, you can prompt Claude directly:

> "Generate a residential lease agreement between John Smith and Acme Properties for 123 Main St, starting June 1st at $2,200/month."

---

## Running Locally

```bash
# Clone the repo
git clone https://github.com/shivamhire025/smartlease
cd smartlease

# Install dependencies
pip install -r requirements.txt

# Set up your environment variables
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# Start the server
uvicorn main:app --reload
```

---

## Why I built this

Legal document generation is a high-friction, high-cost process for individuals and small businesses. This project explores how LLM APIs can replace rigid template systems with flexible, context-aware generation — and demonstrates MCP as a composable integration layer for making AI tools usable across agents and workflows.

---

## Roadmap

- [ ] E-signature integration (third-party API contract already scoped)
- [ ] Cloud storage for generated documents
- [ ] Additional agreement types (Employment, Contractor, Rental)
- [ ] Document history and version tracking

---

Built by [Shivam Hire](https://github.com/shivamhire025) · Toronto, ON
