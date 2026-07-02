from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("notes-server")

# Simple in-memory storage for notes
notes: dict[str, str] = {}

# ============ TOOLS ============

@mcp.tool
def add_note(name: str, content: str) -> str:
    """Add a new note with the given name and content.
    
    Args:
        name: The name/title of the note
        content: The content of the note
    """
    try:
        if not name or not content:
            return "Error: Name and content are required."
        notes[name] = content
        return f"Note '{name}' added successfully."
    except Exception as e:
        return f"Error adding note: {str(e)}"

@mcp.tool
def get_note(name: str) -> str:
    """Retrieve a note by its name.
    
    Args:
        name: The name of the note to retrieve
    """
    if name in notes:
        return notes[name]
    return f"Note '{name}' not found."

@mcp.tool
def list_notes() -> str:
    """List all available notes."""
    if not notes:
        return "No notes saved yet."
    return "Saved notes: " + ", ".join(notes.keys())

@mcp.tool
def delete_note(name: str) -> str:
    """Delete a note by its name.
    
    Args:
        name: The name of the note to delete
    """
    if name in notes:
        del notes[name]
        return f"Note '{name}' deleted."
    return f"Note '{name}' not found."

# ============ RESOURCES ============

@mcp.resource("notes://all")
def all_notes_resource() -> str:
    """All saved notes as a formatted list."""
    if not notes:
        return "No notes available."
    return "\n".join([f"## {name}\n{content}" for name, content in notes.items()])

@mcp.resource("notes://count")
def notes_count_resource() -> str:
    """The current number of saved notes."""
    return f"{len(notes)} notes saved"

@mcp.resource("notes://{name}")
def specific_note_resource(name: str) -> str:
    """A specific note by name."""
    if name in notes:
        return notes[name]
    return f"Note '{name}' not found."

# ============ PROMPTS ============

@mcp.prompt
def note_taking_assistant(topic: str) -> str:
    """A prompt for helping organize notes on a specific topic.
    
    Args:
        topic: The topic to create notes about
    """
    return f"""You are a note-taking assistant helping organize information about {topic}.

When the user provides information:
1. Identify the key points
2. Suggest a note name  
3. Use the add_note tool to save it

When the user asks about existing notes:
1. Use list_notes to see what's available
2. Use get_note to retrieve specific notes
3. Summarize the relevant information

Be organized and concise."""

# ============ RUN SERVER ============

if __name__ == "__main__":
    mcp.run()

