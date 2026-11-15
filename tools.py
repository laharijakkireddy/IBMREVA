"""
tools.py  -  The agent's "pencil box".

Each tool is a plain Python function. The agent (Gemini) never sees the code.
It only reads: the function NAME, its ARGUMENTS and its DOCSTRING.
So the docstring is really a prompt that tells the AI WHEN to use the tool.
"""

import json
from pathlib import Path

from ddgs import DDGS

RESOURCES_FILE = Path(__file__).parent / "learning_resources.json"

# Different words students use -> the key used in our JSON "diary".
ALIASES = {
    "py": "python",
    "database": "sql", "databases": "sql", "mysql": "sql", "postgres": "sql",
    "spreadsheet": "excel", "spreadsheets": "excel",
    "visualization": "visualisation", "data visualization": "visualisation",
    "data visualisation": "visualisation", "tableau": "visualisation",
    "power bi": "visualisation", "powerbi": "visualisation", "charts": "visualisation",
    "stats": "statistics", "probability": "statistics",
    "interview": "communication", "soft skills": "communication", "english": "communication",
}


def search_local_bookmarks(skill_name: str) -> dict:
    """Look up a skill in the senior's trusted bookmarks (a local JSON file).

    Use this FIRST for common skills: python, sql, excel, visualisation,
    statistics, communication. Returns a YouTube link, documentation link and
    a practice link. If the skill is not in the bookmarks, it says so and you
    should call web_search instead.

    Args:
        skill_name: Name of the skill, for example "sql" or "statistics".
    """
    data = json.loads(RESOURCES_FILE.read_text(encoding="utf-8"))
    key = skill_name.lower().strip()
    key = ALIASES.get(key, key)
    if key in data:
        return {"found": True, "skill": key, **data[key]}
    return {"found": False, "skill": skill_name,
            "message": "Not in bookmarks. Use web_search for this skill."}


def web_search(query: str) -> dict:
    """Search the live internet (DuckDuckGo) for free learning material.

    Use this ONLY when search_local_bookmarks says the skill was not found,
    for example for newer or niche skills such as FastAPI, Docker or React.

    Args:
        query: What to search for, for example "FastAPI tutorial for beginners".
    """
    try:
        results = DDGS(timeout=8).text(f"{query} free tutorial", max_results=4)
        links = [{"title": r.get("title", ""), "url": r.get("href", "")} for r in results]
        if links:
            return {"found": True, "query": query, "results": links}
    except Exception:
        pass  # Wi-Fi blocked or search engine busy -> use the safe fallback below
    q = query.replace(" ", "+")
    return {
        "found": True,
        "query": query,
        "note": "Live search unavailable, so here are direct search links.",
        "results": [
            {"title": f"YouTube: {query}", "url": f"https://www.youtube.com/results?search_query={q}+tutorial"},
            {"title": f"Google: {query} docs", "url": f"https://www.google.com/search?q={q}+official+documentation"},
        ],
    }


def get_study_calendar_template() -> dict:
    """Get the blank 2-week study calendar layout.

    Call this when you are ready to build the final timetable. Fill every day
    of the template with concrete tasks, and keep the total hours within the
    student's weekly availability.
    """
    return {
        "Week 1": {
            "Day 1-2": "Learn core concepts and set up tools",
            "Day 3-4": "Guided practice exercises",
            "Day 5-6": "Mini project",
            "Day 7": "Revision and rest",
        },
        "Week 2": {
            "Day 8-9": "Intermediate topics",
            "Day 10-11": "Bigger practice project",
            "Day 12-13": "Mock interview questions",
            "Day 14": "Final review and plan next steps",
        },
    }


# The list we hand to the agent. Adding a new tool = write a function + add it here.
ALL_TOOLS = [search_local_bookmarks, web_search, get_study_calendar_template]
