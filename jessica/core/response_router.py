from datetime import datetime

from jessica.memory.memory_manager import recall, remember
from jessica.tools.load_generated_tools import load_generated_tools
from jessica.tools.register_tools import register_all_tools
from jessica.tools.system.system_monitor import get_system_status


class ResponseRouter:
    """Routes request layers that do not require model inference."""

    def __init__(self, core):
        self.core = core

    def route_identity_layer(self, lowered_input):
        if "who created you" in lowered_input:
            creator = self.core.identity.get_creator()
            architecture = self.core.identity.get_architecture()
            return f"I was originally created by {creator}, who designed my {architecture} architecture."

        if "what is your name" in lowered_input:
            name = self.core.identity.get_ai_name()
            architecture = self.core.identity.get_architecture()
            return f"My name is {name}. I am a local {architecture} assistant."

        if "who owns this system" in lowered_input:
            owner = self.core.identity.get_owner()
            return f"This installation of Jessica belongs to {owner}."

        if "who are you assisting" in lowered_input:
            owner = self.core.identity.get_owner()
            return f"I am assisting {owner} on this computer."

        return None

    def route_tool_approval_layer(self, lowered_input):
        if lowered_input not in ["yes", "generate tool", "create tool"]:
            return None

        tool = self.core.tool_advisor.approve_tool()

        if not tool:
            return "No tool suggestion is pending approval right now."

        from jessica.tools.generated.create_tool import create_tool

        generated_name = create_tool(
            tool["tool_name"],
            tool["description"],
        )

        register_all_tools()
        load_generated_tools()

        tool_intent = tool.get("intent")

        if tool_intent:
            self.core.skill_memory.record_skill(tool_intent, generated_name)

        return (
            f"Tool generated successfully: {generated_name}\n"
            f"Tool registered and loaded."
        )

    def route_internal_intent_layer(self, intent, user_input):
        if intent == "STATUS":
            return f"System status: {self.core.state_manager.get_state().value}"

        if intent == "SYSTEM_STATUS":
            status = get_system_status()
            return (
                f"System status:\n"
                f"CPU usage: {status['cpu']}%\n"
                f"Memory usage: {status['memory']}%\n"
                f"Disk usage: {status['disk']}%"
            )

        if intent == "HELP":
            return "Available commands: status, help, time, date, or ask a question."

        if intent == "TIME":
            now = datetime.now().strftime("%H:%M")
            return f"The current system time is {now}."

        if intent == "DATE":
            today = datetime.now().strftime("%Y-%m-%d")
            return f"Today's date is {today}."

        if intent == "SET_NAME":
            name = user_input.lower().split("my name is")[-1].strip().split()[0].title()
            remember("first_name", name)
            return f"Nice to meet you, {name}. I will remember your name."

        if intent == "SET_SURNAME":
            surname = user_input.lower().split("my surname is")[-1].strip().split()[0].title()
            remember("last_name", surname)
            return f"Thank you. I will remember your surname, {surname}."

        if intent == "GET_SURNAME":
            surname = recall("last_name")
            if surname:
                return f"Your surname is {surname}."
            return "I don't know your surname yet. You can tell me by saying 'My surname is ...'."

        if intent == "GET_NAME":
            first = recall("first_name")
            last = recall("last_name")

            if first and last:
                return f"Your name is {first} {last}."

            if first:
                return f"Your name is {first}."

            return "I don't know your name yet."

        return None
