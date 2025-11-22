# Pyculator

A modern Python calculator with GUI for executing scripts, plotting graphs, and data analysis.

## Features

- **Two-panel interface**: Python code editor on the left, output area on the right
- **Graph support**: automatic display of matplotlib graphs
- **Markdown support**: output results in Markdown format
- **Save and load**: file manager for working with Python scripts
- **Modern UI**: beautiful interface based on CustomTkinter
- **Code autocompletion**: intelligent suggestions using Jedi

## Installation

### Requirements
- Python 3.8 or higher
- pip for installing dependencies

### Installing dependencies

```bash
pip install -r requirements.txt
```

### Required packages
- `customtkinter>=5.2.0` - modern GUI framework
- `matplotlib>=3.7.0` - plotting graphs
- `numpy>=1.24.0` - numerical computing
- `jedi>=0.19.0` - code autocompletion
- `markdown>=3.4.0` - Markdown support
- `tkhtmlview>=0.3.0` - HTML display in Tkinter
- `beautifulsoup4>=4.11.0` - HTML parsing

## Running

### From source code
```bash
python src/main.py
```

### Running compiled application
The application is already compiled and located in the `src/dist/` folder:
```
src/dist/PyCalculator.exe
```

## Project structure

```
src/
├── main.py                 # Application entry point
├── app.py                  # Main application
├── components/             # UI components
│   ├── python_editor.py    # Python code editor
│   ├── output.py           # Output area
│   ├── file_panel.py       # File management panel
│   └── toolbar.py          # Toolbar
├── utils/                  # Utilities
│   ├── code_executor.py    # Code execution
│   └── data_manager.py     # Data management
├── data/                   # Example data and scripts
├── tests/                  # Tests
├── build/                  # PyInstaller build files
└── dist/                   # Compiled application
```

## Usage

1. **Code editing**: Enter or load Python code in the left panel
2. **Execution**: Press the "Run" button or use keyboard shortcuts
3. **Viewing results**: Execution results are displayed in the right panel
4. **Graphs**: Matplotlib graphs are automatically displayed in the interface
5. **Saving**: Use save buttons for file operations

## Building the application

To create an executable file, use the build script:

```bash
./src/build_exe.ps1
```