# ProxySeller API Manager

A Python-based command-line tool for managing proxy lists through the ProxySeller API. This tool provides a user-friendly interface to create, download, rename, and delete proxy lists with various configuration options.

## Features

- 📋 View existing proxy lists
- ⬇️ Download proxies in multiple formats
- ➕ Create new proxy lists with country presets
- ✏️ Rename existing lists
- 🗑️ Delete multiple lists at once
- 🌍 Support for worldwide proxy locations
- 🔒 Secure API key storage
- 📊 Multiple export formats (TXT, CSV, JSON)
- 🔄 Multiple proxy formats support
- 📝 Batch operations support

## Prerequisites

- Python 3.x
- ProxySeller API key
- `requests` library

## Installation

1. Clone this repository or download the source code
2. Install the required dependencies:
```bash
pip install requests
```

## Usage

1. Run the script:
```bash
python main.py
```

2. Enter your ProxySeller API key when prompted (it will be saved for future use)

3. Use the menu interface to:
   - Get existing IP lists
   - Download proxies from existing lists
   - Create new lists
   - Rename lists
   - Delete lists

## Proxy Formats

The tool supports the following proxy formats:
- `login:password@host:port` (default)
- `login:password:host:port`
- `host:port:login:password`
- `host:port@login:password`

## Export Formats

Proxies can be exported in:
- TXT (default)
- CSV
- JSON

## Country Presets

The tool includes predefined country presets for:
- Worldwide
- Europe
- Asia
- South America
- North America
- Africa

## Configuration

### API Key Storage
- The API key is stored in `api_key.txt` for future use
- You can manually edit this file or let the program create it

### Previous Countries
- Used countries are stored in `previous_countries.json`
- This helps in tracking and reusing country configurations

## Error Handling

The tool includes comprehensive error handling for:
- API connection issues
- Invalid inputs
- File operations
- API response errors

## Security

- API keys are stored locally
- Supports IP whitelisting for proxy access
- Secure API communication

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the documentation
2. Review existing issues
3. Create a new issue if needed

## Disclaimer

This tool is not affiliated with ProxySeller. It is an independent tool for managing ProxySeller services.