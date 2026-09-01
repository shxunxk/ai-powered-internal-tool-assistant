class HumanInTheLoop:

    # def __init__(self, tool):
    #     self.tool = tool

    def tool_permission(self, tool) -> bool:
        """
        Simulates getting user feedback for the tool's output.
        In a real-world scenario, this would involve user interaction.
        """

        permission = input(f"Do you want to provide permission to use the {tool} tool? (strictlyyes/no): ").strip().lower()

        if permission == "yes":
            return True
        else:
            return False

