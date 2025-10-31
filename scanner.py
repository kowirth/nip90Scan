#!/usr/bin/env python3
"""
NIP-90 Data Vending Machine Scanner
Discovers and logs all NIP-90 DVM vendors on Nostr relays
"""

import json
import time
import os
from datetime import datetime, timedelta
from nostr_sdk import Keys, Client, Filter, Kind, EventBuilder, NostrSigner, Timestamp, RelayUrl

# Configure logging
LOG_FILE = "dvm_scan_master.log"
DATA_FILE = "dvm_vendors.json"

# Default relay list - popular Nostr relays
DEFAULT_RELAYS = [
    "wss://relay.damus.io",
    "wss://relay.nostr.band",
    "wss://nos.lol",
    "wss://relay.snort.social",
    "wss://nostr.wine",
    "wss://relay.primal.net",
    "wss://nostr-pub.wellorder.net",
    "wss://relay.nostr.bg",
    "wss://nostr.mom",
    "wss://relay.current.fyi"
]

# NIP-90 kinds (5000-5999 for DVM job requests, 6000-6999 for results, 7000 for feedback)
NIP90_REQUEST_KINDS = list(range(5000, 6000))
NIP90_RESULT_KINDS = list(range(6000, 7000))
NIP90_FEEDBACK_KIND = 7000

def log_message(message, level="INFO"):
    """Log message to both console and master log file"""
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')

def save_vendor_data(vendors):
    """Save discovered vendor data to JSON file"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(vendors, f, indent=2, ensure_ascii=False)
    log_message(f"Saved {len(vendors)} vendors to {DATA_FILE}")

def load_existing_data():
    """Load existing vendor data if available"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log_message(f"Error loading existing data: {e}", "WARNING")
    return {}

async def scan_for_dvms():
    """Main scanning function to discover NIP-90 DVMs"""
    log_message("=" * 80)
    log_message("Starting NIP-90 DVM Scanner")
    log_message("=" * 80)
    
    # Generate or load keys
    keys = Keys.generate()
    log_message(f"Generated Nostr keys - Public key: {keys.public_key().to_bech32()}")
    log_message(f"Private key (nsec): {keys.secret_key().to_bech32()}")
    
    # Initialize client
    signer = NostrSigner.keys(keys)
    client = Client(signer)
    
    # Add relays
    log_message(f"Adding {len(DEFAULT_RELAYS)} relays...")
    for relay_url in DEFAULT_RELAYS:
        try:
            await client.add_relay(RelayUrl.parse(relay_url))
            log_message(f"Added relay: {relay_url}")
        except Exception as e:
            log_message(f"Failed to add relay {relay_url}: {e}", "ERROR")
    
    # Connect to relays
    log_message("Connecting to relays...")
    await client.connect()
    time.sleep(2)  # Give time to establish connections
    
    # Load existing vendor data
    vendors = load_existing_data()
    log_message(f"Loaded {len(vendors)} existing vendors from previous scans")
    
    # Create filters for NIP-90 events
    log_message("Creating filters for NIP-90 events...")
    
    # Search for DVM announcements (kind 31990 - DVM service announcement)
    announcement_filter = Filter().kind(Kind(31990)).limit(1000)
    
    # Search for recent DVM results (kinds 6000-6999)
    result_filters = [Filter().kind(Kind(k)).limit(100) for k in range(6000, 6010)]
    
    # Search for DVM requests (kinds 5000-5999) 
    request_filters = [Filter().kind(Kind(k)).limit(100) for k in range(5000, 5010)]
    
    log_message("Subscribing to NIP-90 DVM announcements (kind 31990)...")
    events = await client.fetch_events(announcement_filter, timedelta(seconds=10))
    log_message(f"Found {events.len()} DVM announcement events")
    
    for event in events.to_vec():
        try:
            pubkey = event.author().to_hex()
            
            if pubkey not in vendors:
                vendors[pubkey] = {
                    "pubkey": pubkey,
                    "npub": event.author().to_bech32(),
                    "first_seen": datetime.now().isoformat(),
                    "announcements": [],
                    "services": []
                }
            
            announcement_data = {
                "event_id": event.id().to_hex(),
                "created_at": event.created_at().as_secs(),
                "content": event.content(),
                "tags": [[str(t) for t in tag.as_vec()] for tag in event.tags()],
                "discovered_at": datetime.now().isoformat()
            }
            
            vendors[pubkey]["announcements"].append(announcement_data)
            vendors[pubkey]["last_seen"] = datetime.now().isoformat()
            
            # Extract service information from tags
            for tag in event.tags():
                tag_vec = tag.as_vec()
                if len(tag_vec) >= 2:
                    tag_name = str(tag_vec[0])
                    if tag_name == "d":
                        service_id = str(tag_vec[1])
                        if service_id not in [s.get("id") for s in vendors[pubkey]["services"]]:
                            vendors[pubkey]["services"].append({"id": service_id, "type": "unknown"})
                    elif tag_name == "k":
                        kind = str(tag_vec[1])
                        log_message(f"  DVM supports kind: {kind}")
            
            log_message(f"Discovered DVM: {pubkey[:16]}... | Services: {len(vendors[pubkey]['services'])}")
            
        except Exception as e:
            log_message(f"Error processing announcement event: {e}", "ERROR")
    
    # Scan for DVM results to find active DVMs
    log_message("Scanning for recent DVM result events (kinds 6000-6009)...")
    for result_filter in result_filters:
        try:
            events = await client.fetch_events(result_filter, timedelta(seconds=10))
            event_list = events.to_vec()
            log_message(f"Found {len(event_list)} events for filter")
            
            for event in event_list:
                pubkey = event.author().to_hex()
                
                if pubkey not in vendors:
                    vendors[pubkey] = {
                        "pubkey": pubkey,
                        "npub": event.author().to_bech32(),
                        "first_seen": datetime.now().isoformat(),
                        "announcements": [],
                        "services": [],
                        "results": []
                    }
                
                if "results" not in vendors[pubkey]:
                    vendors[pubkey]["results"] = []
                
                result_data = {
                    "event_id": event.id().to_hex(),
                    "kind": event.kind().as_u16(),
                    "created_at": event.created_at().as_secs(),
                    "content": event.content()[:500],  # Truncate content
                    "discovered_at": datetime.now().isoformat()
                }
                
                vendors[pubkey]["results"].append(result_data)
                vendors[pubkey]["last_seen"] = datetime.now().isoformat()
                
                log_message(f"Found DVM result from: {pubkey[:16]}... (kind {event.kind().as_u16()})")
                
        except Exception as e:
            log_message(f"Error scanning result events: {e}", "ERROR")
    
    # Scan for DVM requests to understand what services are being used
    log_message("Scanning for recent DVM request events (kinds 5000-5009)...")
    for request_filter in request_filters:
        try:
            events = await client.fetch_events(request_filter, timedelta(seconds=10))
            event_list = events.to_vec()
            log_message(f"Found {len(event_list)} request events for filter")
            
            for event in event_list:
                # Requests are made by users, but we can see which DVMs they're targeting
                for tag in event.tags():
                    tag_vec = tag.as_vec()
                    if len(tag_vec) >= 2 and str(tag_vec[0]) == "p":
                        target_pubkey = str(tag_vec[1])
                        if target_pubkey in vendors:
                            if "request_count" not in vendors[target_pubkey]:
                                vendors[target_pubkey]["request_count"] = 0
                            vendors[target_pubkey]["request_count"] += 1
                            
        except Exception as e:
            log_message(f"Error scanning request events: {e}", "ERROR")
    
    # Save all discovered data
    save_vendor_data(vendors)
    
    # Summary
    log_message("=" * 80)
    log_message(f"SCAN COMPLETE - Discovered {len(vendors)} unique DVM vendors")
    log_message("=" * 80)
    
    for pubkey, vendor in vendors.items():
        log_message(f"\nVendor: {pubkey[:16]}...")
        log_message(f"  NPub: {vendor['npub']}")
        log_message(f"  First Seen: {vendor['first_seen']}")
        log_message(f"  Last Seen: {vendor.get('last_seen', 'N/A')}")
        log_message(f"  Announcements: {len(vendor.get('announcements', []))}")
        log_message(f"  Services: {len(vendor.get('services', []))}")
        log_message(f"  Results Found: {len(vendor.get('results', []))}")
        log_message(f"  Request Count: {vendor.get('request_count', 0)}")
        
        if vendor.get('services'):
            for service in vendor['services'][:5]:  # Show first 5 services
                log_message(f"    - Service: {service.get('id', 'unknown')}")
    
    log_message("\n" + "=" * 80)
    log_message(f"All data saved to: {DATA_FILE}")
    log_message(f"Master log saved to: {LOG_FILE}")
    log_message("=" * 80)

if __name__ == "__main__":
    import asyncio
    asyncio.run(scan_for_dvms())
