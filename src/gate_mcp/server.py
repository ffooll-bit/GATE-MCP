"""GATE-MCP stdio server skeleton.

GATE = Guided Agent Through Enforcement. The full expansion is
"Guided Agent Through Enforcement MCP" (MCP stays unexpanded).

ponytail: workflow gate tools are added in the later vertical-slice
session; this file is the minimal runnable stdio MCP server skeleton.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("gate-mcp")


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
