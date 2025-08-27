from mcp.server.fastmcp import FastMCP


def math_tools(mcp_instance: FastMCP):
    @mcp_instance.tool()
    def add(a: float, b: float) -> float:
        return a + b

    @mcp_instance.tool()
    def subtract(a: float, b: float) -> float:
        return a - b

    @mcp_instance.tool()
    def multiply(a: float, b: float) -> float:
        return a * b

    @mcp_instance.tool()
    def divide(a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Divisão por zero não é permitida")
        return a / b

    @mcp_instance.tool()
    def power(a: float, b: float) -> float:
        return a**b
