"""CLI interface for J-Quants documentation MCP server."""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    """Entry point for j-quants-doc-mcp CLI.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success)
    """
    if argv is None:
        argv = sys.argv[1:]

    if "--help" in argv or "-h" in argv:
        print("J-Quants Documentation MCP Server")
        print()
        print("Usage: j-quants-doc-mcp [options]")
        print()
        print("Options:")
        print("  -h, --help     Show this help message and exit")
        print("  --version      Show version information")
        return 0

    if "--version" in argv:
        print("j-quants-doc-mcp version 0.1.0")
        return 0

    # Start the MCP server
    from j_quants_doc_mcp.server import run_server

    try:
        run_server()
        return 0
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        return 0
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
