from cache.store import get_cache, save_cache
from fetchers.man import fetch_man_page
from parsers.command_builder import build_commands
from parsers.command_extractor import extract_commands
from parsers.man_page_parser import parse_man_page
from ai.summarizer import summarize_commands
from core.formatter import format_output


def run_query(query: str, update: bool = False, offline: bool = False, limit: int = 20):

    # check cache
    if not update:
        cached = get_cache(query)
        if cached:
            output = format_output(cached, from_cache=True)
            if output:
                print(output)
            return

    if offline:
        print("No cached result found (offline mode enabled)")
        return

    print(f"[+] Fetching man page for: {query}")

    text = fetch_man_page(query)

    if not text:
        print("No man page found")
        return

    man_page = parse_man_page(text, query=query)
    man_page_data = man_page.to_dict()

    commands = build_commands(man_page_data)
    if not commands:
        commands = extract_commands(text)

    summary = summarize_commands(
        query,
        commands,
        man_page=man_page_data,
        limit=limit,
    )

    save_cache(query, summary)

    output = format_output(summary)
    if output:
        print(output)
