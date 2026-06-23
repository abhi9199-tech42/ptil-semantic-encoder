"""
PTIL + CrewAI Integration

Compress agent memory 80%. Search without decompressing.
"""

from crewai import Agent, Task, Crew, Tool


# ─────────────────────────────────────────────
# PTIL Tools for CrewAI
# ─────────────────────────────────────────────

@Tool("compress_text")
def compress_text(text: str) -> str:
    """Compress text to 20% of original size. Use to save memory when storing long outputs."""
    from ptil import PTILEncoder
    from ptil.ultra_compact_serializer import UltraCompactCSCSerializer

    encoder = PTILEncoder()
    serializer = UltraCompactCSCSerializer()
    cscs = encoder.encode(text)
    return serializer.serialize_multiple(cscs)


@Tool("search_memory")
def search_memory(query: str) -> str:
    """Search previously stored information. Use this to recall past context."""
    from ptil.rag import PTILRAG

    rag = PTILRAG()
    try:
        rag.import_index("crew_memory.json")
    except FileNotFoundError:
        return "No memory stored yet."

    results = rag.search(query, top_k=3)
    if not results:
        return "No results found."

    return "\n".join(f"[{r['score']:.2f}] {r['text']}" for r in results)


@Tool("store_memory")
def store_memory(text: str) -> str:
    """Store information in compressed memory. Use after important findings or decisions."""
    from ptil.rag import PTILRAG

    rag = PTILRAG()
    try:
        rag.import_index("crew_memory.json")
    except FileNotFoundError:
        pass

    rag.add_document(text)
    rag.export_index("crew_memory.json")
    stats = rag.get_stats()
    return f"Stored. {stats['total_documents']} docs, {stats['reduction_pct']:.1f}% compression."


# ─────────────────────────────────────────────
# Example Crew with PTIL Memory
# ─────────────────────────────────────────────

def create_research_crew():
    researcher = Agent(
        role="Research Analyst",
        goal="Find and store important information",
        backstory="You are a meticulous researcher who stores key findings in memory.",
        tools=[compress_text, store_memory, search_memory],
        verbose=True,
    )

    analyst = Agent(
        role="Data Analyst",
        goal="Analyze stored data and find patterns",
        backstory="You analyze previously stored research findings.",
        tools=[search_memory, store_memory],
        verbose=True,
    )

    research_task = Task(
        description="Research the latest trends in AI agent memory management. "
                    "Store key findings in memory using store_memory.",
        agent=researcher,
        expected_output="Summary of key trends with findings stored in memory.",
    )

    analysis_task = Task(
        description="Search memory for all stored research findings. "
                    "Compile a report from the stored data.",
        agent=analyst,
        expected_output="Report based on stored research findings.",
    )

    crew = Crew(
        agents=[researcher, analyst],
        tasks=[research_task, analysis_task],
        verbose=True,
    )

    return crew


if __name__ == "__main__":
    crew = create_research_crew()
    result = crew.kickoff()
    print(result)
