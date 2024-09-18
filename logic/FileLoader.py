class FileLoader:

    @staticmethod
    def load(file_path: str):
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            raise IOError(f"Error loading file from path {file_path}: {e}")
