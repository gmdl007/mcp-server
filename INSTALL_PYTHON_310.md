# Install Python 3.10+ Without Homebrew

Since Homebrew requires sudo/admin access, here are alternative methods to install Python 3.10+:

## Option 1: Download Python 3.12 from python.org (Easiest)

1. **Download Python 3.12 installer:**
   ```bash
   cd ~/Downloads
   curl -O https://www.python.org/ftp/python/3.12.0/python-3.12.0-macos11.pkg
   ```
   
   Or download manually from: https://www.python.org/downloads/

2. **Install the package:**
   ```bash
   sudo installer -pkg ~/Downloads/python-3.12.0-macos11.pkg -target /
   ```

3. **After installation, create virtual environment:**
   ```bash
   cd /Users/gudeng/MCP_Server
   rm -rf mcp_venv
   python3.12 -m venv mcp_venv
   source mcp_venv/bin/activate
   pip install --upgrade pip
   pip install requests python-dotenv fastmcp
   ```

## Option 2: Install Homebrew Manually (Requires Admin)

Run this command and enter your password when prompted:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then add to your PATH (for Apple Silicon Mac):
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
```

Then install Python 3.12:
```bash
brew install python@3.12
```

## Option 3: Use pyenv (No Admin Required)

Install pyenv:
```bash
curl https://pyenv.run | bash
```

Add to your shell config:
```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc
```

Install Python 3.12:
```bash
pyenv install 3.12.0
pyenv local 3.12.0
```

Then create venv:
```bash
cd /Users/gudeng/MCP_Server
rm -rf mcp_venv
python -m venv mcp_venv
source mcp_venv/bin/activate
pip install --upgrade pip
pip install requests python-dotenv fastmcp
```

## Option 4: Use Existing Python (If Available)

Check if you have Python 3.10+ installed:
```bash
python3.10 --version
python3.11 --version
python3.12 --version
python3.13 --version
```

If any of these work, use it to create the venv.

## Recommended: Option 1 (Python.org Installer)

This is the simplest and doesn't require Homebrew. Just download and install the .pkg file, then use `python3.12` to create your venv.

