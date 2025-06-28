
# GitHub Copilot CLI

A powerful automation tool that integrates with GitHub Copilot to automatically perform Git operations and code modifications through automated UI interactions with VS Code.

## Features

- **Automated GitHub Copilot Chat**: Interacts with GitHub Copilot in VS Code through automated UI controls
- **Git Repository Management**: Clone, checkout branches, and push changes automatically
- **Specification-based Automation**: Define complex workflows using YAML specification files
- **Cross-platform Support**: Currently supports macOS with Windows support planned
- **Flexible Configuration**: Configure timing, logging, and behavior through YAML config files

## Installation

### Prerequisites

- Python 3.12 or higher
- GitHub CLI (`gh`) installed and authenticated
- VS Code with GitHub Copilot extension installed
- Required Python packages (installed automatically)

### Using pip

```bash
pip install -r requirements.txt
```

### Using Poetry

```bash
poetry install
```

## Usage

### Basic Usage

Execute a single Copilot chat session:

```bash
python github_copilot_cli.py \
  --file "./src/main.py" \
  --working_directory "/path/to/project" \
  --chat_message "Add error handling to this function"
```

### Specification-based Automation

Create a YAML specification file to define complex workflows:

```yaml
global:
  chat_message: "Improve code documentation"
  wait_response_time: 60
  repository: "your-org/your-repo"
  working_directory: "./workspace"

spec:
  - action: clone
    source_branch: main
    
  - action: checkout
    new_branch: feature/improve-docs
    
  - action: chat
    file: "./src/main.py"
    
  - action: chat
    file: "./src/utils.py"
    
  - action: push
    commit_message: "Improve code documentation"
```

Then run:

```bash
python github_copilot_cli.py --spec_file spec.yml
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--file` | Target file for Copilot chat | None |
| `--working_directory` | Working directory for operations | None |
| `--chat_message` | Message to send to Copilot | None |
| `--spec_file` | Path to YAML specification file | None |
| `--wait_response_time` | Seconds to wait for Copilot response | 60 |
| `--log_level` | Logging level (CRITICAL, ERROR, WARNING, INFO, DEBUG) | INFO |
| `--log_file` | Path to log file | None |
| `--only_logs` | Print only logs without console output | False |

## Specification File Format

### Global Configuration

```yaml
global:
  chat_message: "Default message for all chat actions"
  wait_response_time: 60
  repository: "owner/repo-name"
  working_directory: "./workspace"
```

### Supported Actions

#### Clone Repository
```yaml
- action: clone
  repository: "owner/repo-name"  # Optional if set in global
  source_branch: "main"
  working_directory: "./workspace"  # Optional if set in global
```

#### Checkout Branch
```yaml
- action: checkout
  new_branch: "feature/new-feature"
  working_directory: "./workspace"  # Optional if set in global
```

#### Copilot Chat
```yaml
- action: chat
  file: "./src/main.py"
  chat_message: "Specific message for this file"  # Optional
  wait_response_time: 30  # Optional
```

#### Push Changes
```yaml
- action: push
  commit_message: "Custom commit message"
  working_directory: "./workspace"  # Optional if set in global
```

## Configuration

The tool uses a configuration file at `github_copilot_cli/config/config.yml` to control timing and behavior:

```yaml
sleep_seconds:
  after_open_vscode: 2
  after_open_chat: 1
  before_write_message: 0.5
  wait_second_enter: 0.1
  after_copilot_chat_response: 2
  after_save: 1
  after_close_vscode: 5
  wait_close_retry: 5
```

## How It Works

1. **Repository Management**: Uses GitHub CLI to clone repositories and manage branches
2. **VS Code Automation**: Opens VS Code with specific files using system commands
3. **UI Interaction**: Uses PyAutoGUI to interact with VS Code's GitHub Copilot chat interface
4. **OCR Detection**: Uses Tesseract OCR to detect when Copilot responses are complete
5. **Git Operations**: Automatically commits and pushes changes using Git commands

## Dependencies

- `PyAutoGUI`: For automated UI interactions
- `PyYAML`: For parsing YAML configuration and specification files
- `Pillow`: For image processing and screenshots
- `pytesseract`: For OCR text detection
- `pygetwindow`: For window management

## Platform Support

- ✅ **macOS**: Fully supported
- ⚠️ **Windows**: Partial implementation (commented out)
- ❌ **Linux**: Not yet implemented

## Limitations

- Requires VS Code with GitHub Copilot extension
- Currently macOS only (Windows/Linux support in development)
- Depends on UI automation which may be affected by VS Code updates
- Requires stable internet connection for Copilot functionality

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Kanji Shinohara** - kanji@cont-aid.com

## Troubleshooting

### Common Issues

1. **VS Code not opening**: Ensure VS Code is installed in `/Applications/Visual Studio Code.app` on macOS
2. **GitHub CLI authentication**: Run `gh auth login` to authenticate with GitHub
3. **OCR not working**: Install Tesseract OCR using `brew install tesseract` on macOS
4. **Permission errors**: Ensure the script has accessibility permissions on macOS

### Debug Mode

Enable debug logging to troubleshoot issues:

```bash
python github_copilot_cli.py --log_level DEBUG --spec_file spec.yml
```
