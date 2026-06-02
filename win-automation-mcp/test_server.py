"""Test script for Windows Automation MCP Server."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from server import _enum_windows, _capture_window_screenshot, _build_accessibility_tree

def test_enum_windows():
    """Test window enumeration."""
    print("Testing window enumeration...")
    windows = _enum_windows()
    print(f"Found {len(windows)} windows")

    # Show first 5
    for w in windows[:5]:
        print(f"  [{w['hwnd']}] {w['title'][:50]}... - {w.get('process_name', 'unknown')}")

    return windows

def test_screenshot(hwnd):
    """Test screenshot capture."""
    print(f"\nTesting screenshot capture for hwnd {hwnd}...")
    try:
        png_data = _capture_window_screenshot(hwnd, max_width=800)
        print(f"Captured screenshot: {len(png_data)} bytes")

        # Save to file for inspection
        test_file = os.path.join(os.path.dirname(__file__), "test_screenshot.png")
        with open(test_file, "wb") as f:
            f.write(png_data)
        print(f"Saved to: {test_file}")
        return True
    except Exception as e:
        print(f"Screenshot failed: {e}")
        return False

def test_accessibility(hwnd):
    """Test accessibility tree."""
    print(f"\nTesting accessibility tree for hwnd {hwnd}...")
    try:
        tree_text, index_map = _build_accessibility_tree(hwnd, max_depth=5, max_elements=100)
        print(f"Found {len(index_map)} elements")
        print("Tree preview (first 500 chars):")
        print(tree_text[:500])
        return True
    except Exception as e:
        print(f"Accessibility tree failed: {e}")
        return False

if __name__ == "__main__":
    print("Windows Automation MCP Server - Test")
    print("=" * 50)

    # Test 1: Window enumeration
    windows = test_enum_windows()

    if not windows:
        print("\nNo windows found. Exiting.")
        sys.exit(1)

    # Use first window for testing
    test_hwnd = windows[0]["hwnd"]
    print(f"\nUsing window for tests: [{test_hwnd}] {windows[0]['title'][:50]}...")

    # Test 2: Screenshot
    test_screenshot(test_hwnd)

    # Test 3: Accessibility tree
    test_accessibility(test_hwnd)

    print("\n" + "=" * 50)
    print("Tests complete!")
