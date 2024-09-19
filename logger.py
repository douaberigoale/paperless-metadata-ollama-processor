import traceback


class Logger:
    def __init__(self, file):
        self.file = file

    def log(self, message):
        with open(self.file, "a") as file:
            file.write(message + "\n")

    def log_error(self, error_msg, arguments=None):
        with open(self.file, "a") as file:
            file.write(f"Error: {error_msg}\n")
            if arguments:
                file.write(f"Arguments: {arguments}\n")
            file.write(traceback.format_exc() + "\n")
