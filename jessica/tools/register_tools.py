from jessica.tools.tool_manager import register_tool
from jessica.tools.data.file_tools import create_directory, write_file


def register_all_tools():

    register_tool("create_directory", create_directory)
    register_tool("write_file", write_file)
