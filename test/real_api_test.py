#!/usr/bin/env python
"""
Real API integration test for KMB Bus MCP Server

This script performs a simple integration test with the real KMB API
to verify that our functions can connect to the API and parse the responses correctly.
"""

from pathlib import Path
from pprint import pprint

import asyncio
import json
import sys

# Import the MCP server module - assuming it's saved as kmb_mcp.py
import sys
sys.path.append(Path("__file__").parent.parent.as_posix())
import kmb_mcp

async def run_integration_test():
    """Run a series of tests against the real KMB API"""
    print("🔍 Running integration tests against real KMB API...\n")
    
    # Reset any cache
    kmb_mcp.cache = {
        "route_list": None,
        "stop_list": None, 
        "route_stop_list": None,
        "last_update": None
    }
    
    # Test 1: Get route list
    print("📋 Testing get_route_list()...")
    routes = await kmb_mcp.get_route_list()
    if isinstance(routes, list) and len(routes) > 0:
        print(f"✅ Success! Retrieved {len(routes)} routes")
        print(f"📄 Sample route: {routes[0]['route']} from {routes[0].get('orig_en', 'Unknown')} to {routes[0].get('dest_en', 'Unknown')}")
    else:
        print("❌ Failed to retrieve routes")
        return False
    
    # Pick a test route - using route 1A if available, otherwise the first route
    test_route = next((r["route"] for r in routes if r["route"] == "1A"), routes[0]["route"])
    
    # Test 2: Get stop list
    print("\n📋 Testing get_stop_list()...")
    stops = await kmb_mcp.get_stop_list()
    if isinstance(stops, list) and len(stops) > 0:
        print(f"✅ Success! Retrieved {len(stops)} stops")
        print(f"📄 Sample stop: {stops[0]['name_en']} (ID: {stops[0]['stop']})")
    else:
        print("❌ Failed to retrieve stops")
        return False
    
    # Test 3: Get route details
    print(f"\n🚌 Testing get_route_details() for route {test_route}...")
    route_details = await kmb_mcp.get_route_details(test_route)
    if isinstance(route_details, list) and len(route_details) > 0:
        print(f"✅ Success! Retrieved details for route {test_route}")
        for details in route_details:
            print(f"📄 {details.get('bound', '?')} bound: {details.get('orig_en', 'Unknown')} to {details.get('dest_en', 'Unknown')}")
    else:
        print(f"❌ Failed to retrieve details for route {test_route}")
        return False
    
    # Test 4: Check for a stop with a known name (e.g., "Central")
    print("\n🔍 Testing find_stops_by_name() for 'Central'...")
    central_stops = await kmb_mcp.find_stops_by_name("Central")
    if isinstance(central_stops, list):
        if len(central_stops) > 0:
            print(f"✅ Success! Found {len(central_stops)} stops matching 'Central'")
            for stop in central_stops[:3]:  # Show first 3 at most
                print(f"📄 {stop['name_en']} (ID: {stop['stop']})")
        else:
            print("⚠️ No stops found matching 'Central'")
    else:
        print("❌ Failed to search for stops")
        return False
    
    # Test 5: Try to get ETA for a specific stop
    test_stop = stops[0]["stop"]
    print(f"\n⏱️ Testing get_eta() for stop {test_stop}...")
    eta_data = await kmb_mcp.get_eta(test_stop)
    if isinstance(eta_data, list):
        if len(eta_data) > 0:
            print(f"✅ Success! Retrieved {len(eta_data)} ETAs")
            for eta in eta_data[:3]:  # Show first 3 at most
                print(f"📄 ETA: {eta.get('eta', 'Unknown')} to {eta.get('dest_en', 'Unknown')}")
        else:
            print("⚠️ No ETAs available (this may be normal depending on time of day)")
    else:
        print("❌ Failed to retrieve ETAs")
        return False
    
    # Test 6: Test one of the MCP tools directly
    print("\n🔧 Testing get_next_bus() MCP tool for '1A' at 'Central'...")
    try:
        next_bus_result = await kmb_mcp.get_next_bus("1A", "Central")
        print("✅ Success! Tool executed without errors")
        print(f"\nResult:\n{next_bus_result}")
    except Exception as e:
        print(f"❌ Tool execution failed: {e}")
        return False
    
    print("\n🎉 All integration tests completed successfully!")
    return True

if __name__ == "__main__":
    result = asyncio.run(run_integration_test())
    sys.exit(0 if result else 1)
