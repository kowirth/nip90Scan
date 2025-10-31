# NIP-90 Data Vending Machine Scanner

A Python security research tool for discovering and analyzing NIP-90 Data Vending Machines (DVMs) on the Nostr network.

## What is NIP-90?

NIP-90 is a Nostr protocol specification for Data Vending Machines - decentralized service providers that offer computational services (AI, data processing, translation, etc.) in exchange for payment over the Nostr network.

## Purpose

This scanner helps security researchers:
- Discover active DVM vendors on Nostr relays
- Identify what services DVMs are offering
- Track DVM activity and service announcements
- Build a comprehensive database of the DVM marketplace
- Monitor trends in decentralized service offerings

## Features

- 🔑 **Automatic Key Generation**: Creates Nostr keypair for relay connections
- 🔍 **Multi-Relay Scanning**: Connects to 10+ popular Nostr relays
- 📊 **Comprehensive Data Collection**: Captures DVM announcements, results, and requests
- 💾 **Persistent Storage**: Saves all discovered vendors to JSON
- 📝 **Verbose Logging**: Master log tracks every operation and discovery
- 🔄 **Incremental Scanning**: Preserves previous data across multiple scans

## How It Works

The scanner:
1. Generates a temporary Nostr identity (or uses existing keys)
2. Connects to multiple popular Nostr relays
3. Queries for NIP-90 events:
   - **Kind 31990**: DVM service announcements
   - **Kinds 5000-5999**: DVM job requests
   - **Kinds 6000-6999**: DVM job results
   - **Kind 7000**: DVM feedback events
4. Extracts vendor public keys, services offered, and activity data
5. Saves everything to `dvm_vendors.json` and logs to `dvm_scan_master.log`

## Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Quick Start

```bash
# Run the automated setup and scanner
./run.sh
```

### Manual Setup

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Run the scanner
python scanner.py
```

## Output Files

### `dvm_vendors.json`
Complete structured data about all discovered DVMs:
```json
{
  "pubkey_hex": {
    "pubkey": "hex_public_key",
    "npub": "npub_bech32_format",
    "first_seen": "2025-10-31T03:00:00",
    "last_seen": "2025-10-31T03:15:00",
    "announcements": [...],
    "services": [...],
    "results": [...],
    "request_count": 42
  }
}
```

### `dvm_scan_master.log`
Verbose log of all operations:
- Timestamp for every action
- Relay connection status
- Event discoveries
- Error messages
- Summary statistics

## Understanding the Data

### Vendor Fields
- **pubkey**: Vendor's public key (hex format)
- **npub**: Human-readable public key (bech32 format)
- **first_seen**: When vendor was first discovered
- **last_seen**: Most recent activity timestamp
- **announcements**: List of DVM service announcements
- **services**: Array of offered services
- **results**: Recent job results published
- **request_count**: Number of requests targeting this vendor

### NIP-90 Event Kinds
- **5000-5999**: Job requests from users to DVMs
- **6000-6999**: Job results from DVMs to users
- **7000**: Feedback about job quality
- **31990**: DVM service announcement (advertises capabilities)

## Security Research Applications

This tool is useful for:
- Market analysis of decentralized services
- Identifying popular DVM use cases
- Tracking vendor reliability and activity
- Discovering new service categories
- Analyzing pricing trends
- Monitoring network health

## Monitored Relays

The scanner connects to these public Nostr relays:
- wss://relay.damus.io
- wss://relay.nostr.band
- wss://nos.lol
- wss://relay.snort.social
- wss://nostr.wine
- wss://relay.primal.net
- wss://nostr-pub.wellorder.net
- wss://relay.nostr.bg
- wss://nostr.mom
- wss://relay.current.fyi

## Customization

### Add More Relays
Edit `scanner.py` and add relay URLs to the `DEFAULT_RELAYS` list.

### Adjust Event Limits
Modify the `.limit()` values in the filter creation section to fetch more/fewer events.

### Scan Specific Event Kinds
Change the range in `result_filters` and `request_filters` to focus on specific NIP-90 kinds.

## Privacy Notes

- The scanner generates a new Nostr keypair each run (logged in master log)
- Your IP address is visible to relay operators
- All NIP-90 events are public information
- No private DMs or encrypted content is accessed

## Troubleshooting

### Connection Issues
If relays fail to connect:
- Check your internet connection
- Some relays may be temporarily down
- Firewall might block WebSocket connections

### No DVMs Found
- DVMs are still emerging technology
- Try running during peak hours
- Some relays may not have NIP-90 traffic

### Python Version Errors
Ensure you're using Python 3.8+:
```bash
python --version
```

## Dependencies

- **nostr-sdk**: Official Nostr SDK for Python (Rust-based, high performance)

## Contributing

This is a research tool. Feel free to:
- Add more relay sources
- Improve event parsing
- Add analytics features
- Enhance logging detail

## Disclaimer

This tool is for security research and educational purposes. Respect the Nostr network and relay operators. Do not abuse relays with excessive requests.

## Resources

- [NIP-90 Specification](https://github.com/nostr-protocol/nips/blob/master/90.md)
- [Nostr Protocol](https://nostr.com)
- [Nostr SDK Documentation](https://rust-nostr.org/)

## License

MIT License - Use freely for research purposes

---

**Happy DVM Hunting! 🔍⚡**
