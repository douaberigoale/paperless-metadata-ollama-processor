class FileLoader:
    def load(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found at path: {file_path}")
        except Exception as e:
            raise IOError(f"Error reading prompt file: {e}")
