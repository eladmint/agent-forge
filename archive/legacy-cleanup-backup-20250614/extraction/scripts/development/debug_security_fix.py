#!/usr/bin/env python3
"""Debug script to test the security fix by examining the actual DebugInfo model behavior."""

import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot_api.core.models import DebugInfo


def test_debug_info_model():
    """Test if DebugInfo model properly excludes user_id_processed."""

    print("Testing DebugInfo model security fix...")
    print("=" * 50)

    # Test 1: Try to create DebugInfo with user_id_processed
    try:
        debug_info = DebugInfo(
            model_name="test-model",
            request_id="test-123",
            user_id_processed="test-user",  # This should be rejected
        )
        print("❌ SECURITY ISSUE: DebugInfo accepted user_id_processed field!")
        print(f"Model data: {debug_info.model_dump()}")
    except Exception as e:
        print(f"✅ EXPECTED: DebugInfo rejected user_id_processed field: {e}")

    # Test 2: Create valid DebugInfo without user_id_processed
    try:
        debug_info = DebugInfo(
            model_name="test-model",
            request_id="test-123",
            final_response_text="Test response",
        )
        dumped_data = debug_info.model_dump(exclude_none=True)
        print("\n✅ Valid DebugInfo created successfully")
        print(f"Fields in model: {list(dumped_data.keys())}")

        if "user_id_processed" in dumped_data:
            print("❌ SECURITY ISSUE: user_id_processed found in model_dump output!")
        else:
            print("✅ SECURITY CONFIRMED: user_id_processed not in model_dump output")

    except Exception as e:
        print(f"❌ ERROR: Failed to create valid DebugInfo: {e}")

    # Test 3: Check model fields
    print(f"\nDebugInfo model fields: {list(DebugInfo.model_fields.keys())}")
    if "user_id_processed" in DebugInfo.model_fields:
        print("❌ SECURITY ISSUE: user_id_processed is still a model field!")
    else:
        print("✅ SECURITY CONFIRMED: user_id_processed is not a model field")


if __name__ == "__main__":
    test_debug_info_model()
