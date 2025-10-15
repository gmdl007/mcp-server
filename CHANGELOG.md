# Changelog

All notable changes to the NSO Multi-Agent Standalone Application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-06

### Added
- **Quart-based async web application** - Modern async Flask alternative
- **nest_asyncio integration** - Proper async handling for Jupyter compatibility
- **Direct NSO query execution** - Fallback when LLM is not available
- **Comprehensive error handling** - Better error messages and fallbacks
- **Production deployment scripts** - Automated deployment with systemd
- **Health check endpoint** - `/health` for monitoring
- **Enhanced logging** - Structured logging with file and console output
- **Environment variable support** - Secure credential management
- **Git repository structure** - Version control and change tracking

### Fixed
- **LLM authentication** - Fixed invalid CLIENT_SECRET issue
- **Async event loop conflicts** - Resolved "no running event loop" errors
- **NSO environment setup** - Proper Python path configuration
- **Agent reset functionality** - Fixed NameError in reset endpoint
- **Port configuration** - Consistent port 5606 usage

### Changed
- **Web framework** - Migrated from Flask to Quart for async support
- **Agent creation** - Updated to use direct constructor instead of deprecated `from_tools`
- **Configuration management** - Environment variables with fallback to hardcoded values
- **Error handling** - More robust error handling and user feedback

### Removed
- **Jupyter notebook dependencies** - Fully standalone application
- **Deprecated methods** - Removed `ReActAgent.from_tools()` usage
- **Synchronous Flask limitations** - Replaced with async Quart

## [1.0.0] - 2025-01-05

### Added
- **Initial Flask-based implementation**
- **NSO integration** - Basic device management and automation
- **LlamaIndex ReActAgent** - AI-powered network automation
- **Cisco Azure OpenAI integration** - LLM capabilities
- **Basic web interface** - Simple query interface
- **NSO function tools** - Device discovery, command execution, monitoring

### Known Issues
- **Async conflicts** - Event loop issues in Flask
- **LLM authentication** - Invalid credentials
- **Limited error handling** - Basic error messages
- **No production deployment** - Development-only setup

---

## Migration Guide

### From v1.0 to v2.0

1. **Update dependencies**:
   ```bash
   pip install quart nest-asyncio
   ```

2. **Update configuration**:
   - Use environment variables for credentials
   - Update NSO_DIR path if needed

3. **Deploy using new scripts**:
   ```bash
   ./deploy.sh
   ```

4. **Access new endpoints**:
   - Health check: `http://localhost:5606/health`
   - Main interface: `http://localhost:5606/`

### Breaking Changes
- **Web framework change** - Flask → Quart (async)
- **Configuration format** - Environment variables preferred
- **Deployment method** - New systemd service setup
