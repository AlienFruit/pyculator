"""Module for managing application data saving and loading."""
import json
import os
from typing import Dict, Optional, Tuple


def get_data_directory() -> str:
    """
    Get path to directory for storing Python files.

    Returns:
        Path to data directory
    """
    # Get directory where script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go to project root directory
    project_root = os.path.dirname(script_dir)
    # Create path to data folder
    data_dir = os.path.join(project_root, "data")
    # Create folder if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir


def get_app_state_file() -> str:
    """
    Get path to application state file.

    Returns:
        Path to app_state.json file in project root
    """
    # Get directory where script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go to project root directory
    project_root = os.path.dirname(script_dir)
    # Return path to app_state.json file in project root
    return os.path.join(project_root, "app_state.json")


class DataManager:
    """Class for managing application data in Python files."""

    def __init__(self, data_file: Optional[str] = None, directory: Optional[str] = None):
        """
        Initialize data manager.

        Args:
            data_file: Path to data file (if None, calculator_data.py in directory is used)
            directory: Directory for working with files (if None, data folder is used)
        """
        if directory is None:
            directory = get_data_directory()

        self.directory = directory

        if data_file is None:
            data_file = os.path.join(directory, "calculator_data.py")

        self.data_file = data_file
        self._default_code = (
            "# Enter your Python code here\n"
            "# For example:\n"
            "print('Hello, world!')\n"
            "result = 2 + 2\n"
            "print(f'Result: {result}')"
        )
    
    def load_data(self) -> Dict:
        """
        Load data from Python file.

        Returns:
            Dictionary with application data (code only)
        """
        if not os.path.exists(self.data_file):
            return {"code": ""}

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                code = f.read()
                return {"code": code}
        except Exception as e:
            print(f"Error loading data: {e}")
            return {"code": ""}
    
    def save_data(self, code: str) -> bool:
        """
        Save data to Python file.

        Args:
            code: Code to save

        Returns:
            True if save successful, False otherwise
        """
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                f.write(code)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def get_code(self) -> str:
        """
        Get saved code.

        Returns:
            Saved code or default code
        """
        data = self.load_data()
        code = data.get("code", "")
        return code if code else self._default_code
    
    def load_data_from_file(self, file_path: str) -> Dict:
        """
        Load data from specified Python file.

        Args:
            file_path: Path to Python file

        Returns:
            Dictionary with application data (code only)
        """
        if not os.path.exists(file_path):
            return {"code": ""}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
                return {"code": code}
        except Exception as e:
            print(f"Error loading data from {file_path}: {e}")
            return {"code": ""}
    
    def save_data_to_file(self, file_path: str, code: str) -> bool:
        """
        Save data to specified Python file.

        Args:
            file_path: Path to Python file
            code: Code to save

        Returns:
            True if save successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            file_dir = os.path.dirname(file_path)
            if file_dir and not os.path.exists(file_dir):
                os.makedirs(file_dir)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            return True
        except Exception as e:
            print(f"Error saving data to {file_path}: {e}")
            return False
    
    def set_directory(self, directory: str):
        """
        Set working directory.

        Args:
            directory: Path to directory
        """
        if os.path.isdir(directory):
            self.directory = directory
            # Update path to default data file
            self.data_file = os.path.join(directory, "calculator_data.py")
    
    def get_data_directory(self) -> str:
        """
        Get path to directory for storing Python files.

        Returns:
            Path to data directory
        """
        return get_data_directory()
    
    def get_window_size(self) -> Tuple[int, int]:
        """
        Get saved window size from app_state.json.

        Returns:
            Tuple (width, height)
        """
        state = self.load_app_state()
        window_size = state.get("window_size", {})
        return (
            window_size.get("width", 1400),
            window_size.get("height", 700)
        )

    def get_splitter_position(self) -> float:
        """
        Get saved splitter position.

        Returns:
            Splitter position (0.0 to 1.0, where 0.5 is center)
        """
        state = self.load_app_state()
        return state.get("splitter_position", 0.5)

    def save_splitter_position(self, position: float) -> bool:
        """
        Save splitter position.

        Args:
            position: Splitter position (0.0 to 1.0)

        Returns:
            True if save successful, False otherwise
        """
        try:
            state_file = get_app_state_file()

            # Load current state
            current_state = self.load_app_state()

            # Update splitter position
            current_state["splitter_position"] = max(0.0, min(1.0, position))

            # Save state
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(current_state, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving splitter position: {e}")
            return False
    
    def load_app_state(self) -> Dict:
        """
        Load application state from app_state.json file.

        Returns:
            Dictionary with application state
        """
        state_file = get_app_state_file()
        if not os.path.exists(state_file):
            return {
                "current_directory": get_data_directory(),
                "last_file": None,
                "window_size": {"width": 1400, "height": 700},
                "splitter_position": 0.5,
                "hotkeys": {}
            }
        
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
                # Check that directory exists
                if "current_directory" in state:
                    if not os.path.isdir(state["current_directory"]):
                        state["current_directory"] = get_data_directory()
                else:
                    state["current_directory"] = get_data_directory()

                # Make sure window_size is in state
                if "window_size" not in state:
                    state["window_size"] = {"width": 1400, "height": 700}
                
                # Make sure hotkeys is in state
                if "hotkeys" not in state:
                    state["hotkeys"] = {}
                
                return state
        except Exception as e:
            print(f"Error loading application state: {e}")
            return {
                "current_directory": get_data_directory(),
                "last_file": None,
                "window_size": {"width": 1400, "height": 700},
                "splitter_position": 0.5,
                "hotkeys": {}
            }
    
    def save_app_state(self, current_directory: Optional[str] = None, last_file: Optional[str] = None, window_size: Optional[Tuple[int, int]] = None) -> bool:
        """
        Save application state to app_state.json file.

        Args:
            current_directory: Currently selected directory
            last_file: Last opened file
            window_size: Window size (width, height)

        Returns:
            True if save successful, False otherwise
        """
        try:
            state_file = get_app_state_file()
            
            # Load current state to save other parameters
            current_state = self.load_app_state()

            # Update only passed parameters
            if current_directory is not None:
                current_state["current_directory"] = current_directory
            if last_file is not None:
                current_state["last_file"] = last_file
            if window_size is not None:
                current_state["window_size"] = {
                    "width": window_size[0],
                    "height": window_size[1]
                }

            # Save state
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(current_state, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving application state: {e}")
            return False
    
    def get_current_directory(self) -> str:
        """
        Get saved current directory from application state.

        Returns:
            Path to current directory or default data folder
        """
        state = self.load_app_state()
        directory = state.get("current_directory", get_data_directory())
        # Check that directory exists
        if os.path.isdir(directory):
            return directory
        return get_data_directory()
    
    def get_last_file(self) -> Optional[str]:
        """
        Get last opened file from application state.

        Returns:
            Path to last file or None
        """
        state = self.load_app_state()
        last_file = state.get("last_file")
        # Check that file exists
        if last_file and os.path.exists(last_file):
            return last_file
        return None
    
    def clean_data_files(self, directory: Optional[str] = None) -> int:
        """
        Convert old JSON files to Python files.

        Args:
            directory: Directory for conversion (if None, data folder is used)

        Returns:
            Number of converted files
        """
        if directory is None:
            directory = get_data_directory()

        if not os.path.isdir(directory):
            print(f"Directory {directory} does not exist")
            return 0

        converted_count = 0

        # Go through all JSON files in directory
        for filename in os.listdir(directory):
            if not filename.endswith('.json'):
                continue

            file_path = os.path.join(directory, filename)
            if not os.path.isfile(file_path):
                continue

            try:
                # Load data from JSON file
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Get code
                code = data.get("code", "")

                # Create new filename with .py extension
                new_filename = filename.replace('.json', '.py')
                new_file_path = os.path.join(directory, new_filename)

                # Save code to new .py file
                with open(new_file_path, "w", encoding="utf-8") as f:
                    f.write(code)

                # Remove old JSON file
                os.remove(file_path)

                converted_count += 1
                print(f"Converted file: {filename} -> {new_filename}")
            except Exception as e:
                print(f"Error converting file {filename}: {e}")

        return converted_count
    
    def save_hotkeys_config(self, hotkeys: Dict[str, str]) -> bool:
        """
        Сохранить конфигурацию горячих клавиш.
        
        Args:
            hotkeys: Словарь с настройками горячих клавиш (например, {"run_code": "F5"})
        
        Returns:
            True если сохранение успешно, False иначе
        """
        try:
            state_file = get_app_state_file()
            current_state = self.load_app_state()
            current_state["hotkeys"] = hotkeys
            
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(current_state, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения конфигурации горячих клавиш: {e}")
            return False
    
    def load_hotkeys_config(self) -> Dict[str, str]:
        """
        Загрузить конфигурацию горячих клавиш.
        
        Returns:
            Словарь с настройками горячих клавиш
        """
        state = self.load_app_state()
        return state.get("hotkeys", {})

