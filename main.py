from server import mcp
from tools import *
from config import HOST, PORT


if __name__ == "__main__":
    mcp.run(transport="http", host=HOST, port=PORT)
