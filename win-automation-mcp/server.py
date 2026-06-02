"""
Windows Automation MCP Server
Provides tools for controlling Windows applications via MCP protocol.
"""

import ctypes
import ctypes.wintypes
import json
import os
import subprocess
import sys
import time
import threading
from typing import Any, Optional

# Set DPI awareness before any GUI operations
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

import pyautogui
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.fastmcp.utilities.types import Image

# Disable pyautogui failsafe
pyautogui.FAILSAFE = False

# Create server
server = FastMCP(
    name="win-automation",
    instructions="Windows desktop automation tools for controlling applications, capturing screenshots, and simulating user input."
)

# Global element index storage
_element_indices: dict[int, dict[int, Any]] = {}
_element_index_lock = threading.Lock()

# Windows API constants
GWL_STYLE = -16
GWL_EXSTYLE = -20
WS_VISIBLE = 0x10000000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000
SW_RESTORE = 9
SW_SHOW = 5
SW_SHOWNORMAL = 1
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
MAX_PATH = 265
PW_RENDERFULLCONTENT = 0x00000002

# Windows API functions
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
shell32 = ctypes.windll.shell32

# Function prototypes
user32.EnumWindows.argtypes = [ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p), ctypes.c_void_p]
user32.EnumWindows.restype = ctypes.c_bool
user32.IsWindowVisible.argtypes = [ctypes.c_void_p]
user32.IsWindowVisible.restype = ctypes.c_bool
user32.GetWindowTextW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.GetWindowThreadProcessId.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
user32.GetWindowThreadProcessId.restype = ctypes.c_ulong
user32.ShowWindow.argtypes = [ctypes.c_void_p, ctypes.c_int]
user32.ShowWindow.restype = ctypes.c_bool
user32.SetForegroundWindow.argtypes = [ctypes.c_void_p]
user32.SetForegroundWindow.restype = ctypes.c_bool
user32.GetWindowRect.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.wintypes.RECT)]
user32.GetWindowRect.restype = ctypes.c_bool
user32.GetClientRect.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.wintypes.RECT)]
user32.GetClientRect.restype = ctypes.c_bool
user32.ClientToScreen.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.wintypes.POINT)]
user32.ClientToScreen.restype = ctypes.c_bool
user32.GetWindowLongW.argtypes = [ctypes.c_void_p, ctypes.c_int]
user32.GetWindowLongW.restype = ctypes.c_long
user32.PrintWindow.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint]
user32.PrintWindow.restype = ctypes.c_bool
user32.GetDC.argtypes = [ctypes.c_void_p]
user32.GetDC.restype = ctypes.c_void_p
user32.ReleaseDC.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
user32.ReleaseDC.restype = ctypes.c_int

kernel32.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_bool, ctypes.c_ulong]
kernel32.OpenProcess.restype = ctypes.c_void_p
kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
kernel32.CloseHandle.restype = ctypes.c_bool
kernel32.QueryFullProcessImageNameW.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_ulong)]
kernel32.QueryFullProcessImageNameW.restype = ctypes.c_bool

gdi32 = ctypes.windll.gdi32
gdi32.CreateCompatibleDC.argtypes = [ctypes.c_void_p]
gdi32.CreateCompatibleDC.restype = ctypes.c_void_p
gdi32.CreateCompatibleBitmap.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
gdi32.CreateCompatibleBitmap.restype = ctypes.c_void_p
gdi32.SelectObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
gdi32.SelectObject.restype = ctypes.c_void_p
gdi32.DeleteObject.argtypes = [ctypes.c_void_p]
gdi32.DeleteObject.restype = ctypes.c_bool
gdi32.DeleteDC.argtypes = [ctypes.c_void_p]
gdi32.DeleteDC.restype = ctypes.c_bool
gdi32.GetDIBits.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint]
gdi32.GetDIBits.restype = ctypes.c_int


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", ctypes.c_uint32),
        ("biWidth", ctypes.c_int32),
        ("biHeight", ctypes.c_int32),
        ("biPlanes", ctypes.c_uint16),
        ("biBitCount", ctypes.c_uint16),
        ("biCompression", ctypes.c_uint32),
        ("biSizeImage", ctypes.c_uint32),
        ("biXPelsPerMeter", ctypes.c_int32),
        ("biYPelsPerMeter", ctypes.c_int32),
        ("biClrUsed", ctypes.c_uint32),
        ("biClrImportant", ctypes.c_uint32),
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ("bmiHeader", BITMAPINFOHEADER),
        ("bmiColors", ctypes.c_uint32 * 3),
    ]


def _get_process_name(pid: int) -> str:
    """Get process executable path from PID."""
    try:
        h = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h:
            return ""
        buf = ctypes.create_unicode_buffer(MAX_PATH)
        size = ctypes.c_ulong(MAX_PATH)
        if kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
            kernel32.CloseHandle(h)
            return buf.value
        kernel32.CloseHandle(h)
    except Exception:
        pass
    return ""


def _enum_windows() -> list[dict[str, Any]]:
    """Enumerate all visible windows."""
    results = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def callback(hwnd, _):
        try:
            if not user32.IsWindowVisible(hwnd):
                return True

            style = user32.GetWindowLongW(hwnd, GWL_STYLE)
            ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)

            # Skip tool windows unless they have app window style
            if (ex_style & WS_EX_TOOLWINDOW) and not (ex_style & WS_EX_APPWINDOW):
                return True

            # Get title
            buf = ctypes.create_unicode_buffer(512)
            user32.GetWindowTextW(hwnd, buf, 512)
            title = buf.value.strip()

            if not title:
                return True

            # Get PID
            pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

            # Get process path
            proc_path = _get_process_name(pid.value)

            results.append({
                "hwnd": hwnd,
                "title": title,
                "pid": pid.value,
                "process_path": proc_path,
                "process_name": os.path.basename(proc_path) if proc_path else "",
            })
        except Exception:
            pass
        return True

    user32.EnumWindows(callback, None)
    return results


def _capture_window_screenshot(hwnd: int, max_width: int = 1280) -> bytes:
    """Capture window screenshot using PrintWindow. Returns PNG bytes."""
    from PIL import Image as PILImage
    import io

    # Get window rect
    rect = ctypes.wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        raise OSError(f"GetWindowRect failed for hwnd {hwnd}")

    width = rect.right - rect.left
    height = rect.bottom - rect.top

    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid window dimensions: {width}x{height}")

    # Create device context and bitmap
    hdc = user32.GetDC(hwnd)
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbitmap = gdi32.CreateCompatibleBitmap(hdc, width, height)
    old_bmp = gdi32.SelectObject(hdc_mem, hbitmap)

    # Capture window
    result = user32.PrintWindow(hwnd, hdc_mem, PW_RENDERFULLCONTENT)

    if not result:
        # Fallback: try without PW_RENDERFULLCONTENT
        result = user32.PrintWindow(hwnd, hdc_mem, 0)

    if not result:
        gdi32.SelectObject(hdc_mem, old_bmp)
        gdi32.DeleteObject(hbitmap)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(hwnd, hdc)
        raise OSError(f"PrintWindow failed for hwnd {hwnd}")

    # Prepare bitmap info
    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = width
    bmi.bmiHeader.biHeight = -height  # Top-down
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    bmi.bmiHeader.biCompression = 0  # BI_RGB

    # Get pixel data
    buf_size = width * height * 4
    buf = ctypes.create_string_buffer(buf_size)
    gdi32.GetDIBits(hdc_mem, hbitmap, 0, height, buf, ctypes.byref(bmi), 0)

    # Convert to PIL Image
    img = PILImage.frombuffer("RGBA", (width, height), buf, "raw", "BGRA", 0, 1)
    img = img.convert("RGB")

    # Scale down if needed
    if width > max_width:
        ratio = max_width / width
        new_height = int(height * ratio)
        img = img.resize((max_width, new_height), PILImage.LANCZOS)

    # Convert to PNG bytes
    output = io.BytesIO()
    img.save(output, format="PNG", optimize=True)
    png_data = output.getvalue()

    # Cleanup
    gdi32.SelectObject(hdc_mem, old_bmp)
    gdi32.DeleteObject(hbitmap)
    gdi32.DeleteDC(hdc_mem)
    user32.ReleaseDC(hwnd, hdc)

    return png_data


def _activate_window(hwnd: int) -> bool:
    """Bring window to foreground."""
    try:
        # Restore if minimized
        user32.ShowWindow(hwnd, SW_RESTORE)
        time.sleep(0.1)
        return user32.SetForegroundWindow(hwnd)
    except Exception:
        return False


def _get_client_offset(hwnd: int) -> tuple[int, int]:
    """Get client area offset from window rect."""
    window_rect = ctypes.wintypes.RECT()
    client_rect = ctypes.wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(window_rect))
    user32.GetClientRect(hwnd, ctypes.byref(client_rect))
    point = ctypes.wintypes.POINT(0, 0)
    user32.ClientToScreen(hwnd, ctypes.byref(point))
    return (point.x - window_rect.left, point.y - window_rect.top)


def _build_accessibility_tree(hwnd: int, max_depth: int = 10, max_elements: int = 500) -> tuple[str, dict[int, Any]]:
    """Build accessibility tree using UI Automation. Returns (tree_text, index_map)."""
    try:
        import comtypes
        import comtypes.client
        import comtypes.gen.UIAutomationClient as UIAClient

        # Create UI Automation instance
        uia = comtypes.client.CreateObject(
            '{ff48dba4-60ef-4201-aa87-54103eef594e}',
            interface=UIAClient.IUIAutomation
        )

        # Get element from handle
        element = uia.ElementFromHandle(hwnd)
        if not element:
            return "No accessible content", {}

        index_map = {}
        lines = []
        current_index = [0]  # Mutable counter

        def walk(elem, depth, parent_info=""):
            if depth > max_depth or current_index[0] >= max_elements:
                return

            idx = current_index[0]
            current_index[0] += 1
            index_map[idx] = elem

            try:
                name = elem.CurrentName or ""
                control_type = elem.CurrentLocalizedControlType or ""
                class_name = elem.CurrentClassName or ""

                # Get patterns
                patterns = []
                try:
                    # Check for Value pattern
                    vp = elem.GetCurrentPattern(10002)  # UIA_ValuePatternId
                    if vp:
                        patterns.append("Value")
                except Exception:
                    pass

                try:
                    # Check for Invoke pattern
                    ip = elem.GetCurrentPattern(10000)  # UIA_InvokePatternId
                    if ip:
                        patterns.append("Invoke")
                except Exception:
                    pass

                try:
                    # Check for Toggle pattern
                    tp = elem.GetCurrentPattern(10001)  # UIA_TogglePatternId
                    if tp:
                        patterns.append("Toggle")
                except Exception:
                    pass

                try:
                    # Check for SelectionItem pattern
                    sp = elem.GetCurrentPattern(10010)  # UIA_SelectionItemPatternId
                    if sp:
                        patterns.append("SelectionItem")
                except Exception:
                    pass

                # Build line
                indent = "  " * depth
                pattern_str = f" [{', '.join(patterns)}]" if patterns else ""
                value_str = ""
                if "Value" in patterns:
                    try:
                        vp = elem.GetCurrentPattern(10002)
                        value_str = f' value="{vp.CurrentValue}"'
                    except Exception:
                        pass

                name_display = f'"{name}"' if name else '""'
                line = f"{indent}[{idx}] {name_display} ({control_type}){pattern_str}{value_str}"
                lines.append(line)

                # Walk children
                walker = uia.CreateTreeWalker(uia.RawViewCondition)
                try:
                    child = walker.GetFirstChildElement(elem)
                    while child:
                        walk(child, depth + 1)
                        next_child = walker.GetNextSiblingElement(child)
                        child = next_child
                except Exception:
                    pass

            except Exception:
                pass

        walk(element, 0)
        tree_text = "\n".join(lines) if lines else "No accessible elements found"

        return tree_text, index_map

    except ImportError:
        return "comtypes not installed - accessibility tree unavailable", {}
    except Exception as e:
        return f"Error building accessibility tree: {e}", {}


def _get_element_by_index(hwnd: int, index: int) -> Any:
    """Get element from index map."""
    with _element_index_lock:
        hwnd_map = _element_indices.get(hwnd, {})
        return hwnd_map.get(index)


def _set_clipboard_text(text: str) -> None:
    """Set clipboard text using Windows API."""
    CF_UNICODETEXT = 13

    user32.OpenClipboard(0)
    user32.EmptyClipboard()

    # Allocate memory for text
    text_bytes = text.encode("utf-16-le") + b"\x00\x00"
    h_mem = kernel32.GlobalAlloc(0x0042, len(text_bytes))  # GMEM_MOVEABLE | GMEM_ZEROINIT
    p_mem = kernel32.GlobalLock(h_mem)
    ctypes.memmove(p_mem, text_bytes, len(text_bytes))
    kernel32.GlobalUnlock(h_mem)

    user32.SetClipboardData(CF_UNICODETEXT, h_mem)
    user32.CloseClipboard()


def _paste_text(text: str) -> None:
    """Paste text via clipboard."""
    _set_clipboard_text(text)
    time.sleep(0.05)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.05)


def _parse_key_string(key_str: str) -> list[str]:
    """Parse key string like 'Control_L+c' into pyautogui key list."""
    # Map X11 keysym names to pyautogui names
    KEY_MAP = {
        "Control_L": "ctrl",
        "Control_R": "ctrl",
        "Shift_L": "shift",
        "Shift_R": "shift",
        "Alt_L": "alt",
        "Alt_R": "alt",
        "Return": "enter",
        "KP_Enter": "enter",
        "Escape": "escape",
        "Tab": "tab",
        "BackSpace": "backspace",
        "Delete": "delete",
        "space": "space",
        "Up": "up",
        "Down": "down",
        "Left": "left",
        "Right": "right",
        "Home": "home",
        "End": "end",
        "Page_Up": "pageup",
        "Page_Down": "pagedown",
        "F1": "f1",
        "F2": "f2",
        "F3": "f3",
        "F4": "f4",
        "F5": "f5",
        "F6": "f6",
        "F7": "f7",
        "F8": "f8",
        "F9": "f9",
        "F10": "f10",
        "F11": "f11",
        "F12": "f12",
        "period": ".",
        "greater": ">",
        "less": "<",
        "comma": ",",
        "slash": "/",
        "question": "?",
    }

    parts = key_str.replace(" ", "").split("+")
    result = []
    for part in parts:
        result.append(KEY_MAP.get(part, part.lower()))
    return result


# ========== MCP Tools ==========

@server.tool()
async def list_apps() -> str:
    """List running applications with their visible windows.

    Returns a formatted list showing each application's windows with HWND, title, and PID.
    Use the HWND values for other tools like get_window_state, click, etc.
    """
    try:
        windows = _enum_windows()

        # Group by process
        by_process: dict[str, list[dict]] = {}
        for w in windows:
            key = w.get("process_name") or "(unknown)"
            by_process.setdefault(key, []).append(w)

        lines = []
        for proc_name, wins in sorted(by_process.items()):
            lines.append(f"\nApplication: {proc_name}")
            for w in wins:
                lines.append(f"  [{w['hwnd']}] {w['title']} (PID={w['pid']})")

        return "\n".join(lines) if lines else "No visible windows found"

    except Exception as e:
        return f"Error listing apps: {e}"


@server.tool()
async def list_windows() -> str:
    """List all open visible windows.

    Returns a flat list of all visible windows with HWND, title, and process info.
    """
    try:
        windows = _enum_windows()

        lines = []
        for w in windows:
            lines.append(f"[{w['hwnd']}] {w['title']} - {w.get('process_name', 'unknown')} (PID={w['pid']})")

        return "\n".join(lines) if lines else "No visible windows found"

    except Exception as e:
        return f"Error listing windows: {e}"


@server.tool()
async def get_window(hwnd: int) -> str:
    """Get information about a specific window by HWND.

    Args:
        hwnd: Window handle from list_apps or list_windows

    Returns window title, position, size, and state.
    """
    try:
        if not user32.IsWindow(hwnd):
            return f"Window {hwnd} no longer exists"

        # Get title
        buf = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, buf, 512)
        title = buf.value

        # Get rect
        rect = ctypes.wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))

        # Get PID
        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

        proc_path = _get_process_name(pid.value)

        return json.dumps({
            "hwnd": hwnd,
            "title": title,
            "pid": pid.value,
            "process_path": proc_path,
            "rect": {
                "left": rect.left,
                "top": rect.top,
                "right": rect.right,
                "bottom": rect.bottom,
                "width": rect.right - rect.left,
                "height": rect.bottom - rect.top,
            }
        }, indent=2, ensure_ascii=False)

    except Exception as e:
        return f"Error getting window: {e}"


@server.tool()
async def launch_app(path_or_name: str) -> str:
    """Launch an application by name or path.

    Args:
        path_or_name: Application name (e.g. "notepad") or full path (e.g. "C:\\Windows\\notepad.exe")

    Returns the HWND of the launched application's main window, or error message.
    """
    try:
        # Get current windows before launch
        before = {w["hwnd"] for w in _enum_windows()}

        # Launch via ShellExecute
        result = shell32.ShellExecuteW(None, "open", path_or_name, None, None, SW_SHOWNORMAL)

        if result <= 32:
            return f"Failed to launch '{path_or_name}' (error code: {result})"

        # Wait for window to appear
        time.sleep(1.0)

        # Find new windows
        after = _enum_windows()
        new_windows = [w for w in after if w["hwnd"] not in before]

        if new_windows:
            w = new_windows[0]
            return f"Launched '{path_or_name}' -> [{w['hwnd']}] {w['title']}"
        else:
            return f"Launched '{path_or_name}' but no new window detected. Check list_windows."

    except Exception as e:
        return f"Error launching app: {e}"


@server.tool()
async def get_window_state(hwnd: int, include_screenshot: bool = True, include_accessibility: bool = False, max_screenshot_width: int = 1280) -> list:
    """Capture the current state of a window.

    Args:
        hwnd: Window handle from list_apps or list_windows
        include_screenshot: Whether to capture a screenshot (default True)
        include_accessibility: Whether to build accessibility tree with element indexes (default False)
        max_screenshot_width: Maximum screenshot width in pixels (default 1280)

    Returns screenshot image and/or accessibility tree with element indexes.
    Element indexes are ephemeral - they're only valid until the next get_window_state call.
    """
    try:
        if not user32.IsWindow(hwnd):
            return [f"Window {hwnd} no longer exists"]

        result = []

        # Screenshot
        if include_screenshot:
            try:
                png_data = _capture_window_screenshot(hwnd, max_screenshot_width)
                img = Image(data=png_data, format="png")
                result.append(img)
            except Exception as e:
                result.append(f"Screenshot error: {e}")

        # Accessibility tree
        if include_accessibility:
            try:
                tree_text, index_map = _build_accessibility_tree(hwnd)

                # Store index map
                with _element_index_lock:
                    _element_indices[hwnd] = index_map

                result.append(f"Accessibility Tree (indexes refreshed, {len(index_map)} elements):\n{tree_text}")
            except Exception as e:
                result.append(f"Accessibility tree error: {e}")

        if not result:
            return ["No data captured. Set include_screenshot or include_accessibility to True."]

        return result

    except Exception as e:
        return [f"Error capturing window state: {e}"]


@server.tool()
async def click(hwnd: int, x: Optional[int] = None, y: Optional[int] = None, index: Optional[int] = None, button: str = "left", clicks: int = 1) -> str:
    """Click in a window at coordinates or on an element by index.

    Args:
        hwnd: Window handle
        x: X coordinate in window (client area). Required if index not provided.
        y: Y coordinate in window (client area). Required if index not provided.
        index: Element index from get_window_state accessibility tree. Takes priority over x/y.
        button: Mouse button - "left", "right", or "middle" (default "left")
        clicks: Number of clicks (default 1)

    Coordinates are relative to the window's client area.
    Element indexes are ephemeral - refresh with get_window_state if stale.
    """
    try:
        if not user32.IsWindow(hwnd):
            return f"Window {hwnd} no longer exists"

        _activate_window(hwnd)
        time.sleep(0.1)

        if index is not None:
            # Click by element index
            elem = _get_element_by_index(hwnd, index)
            if not elem:
                return f"Element index {index} not found. Call get_window_state to refresh indexes."

            try:
                rect = elem.CurrentBoundingRectangle
                cx = (rect.left + rect.right) // 2
                cy = (rect.top + rect.bottom) // 2

                # Convert screen coords to window-relative
                window_rect = ctypes.wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(window_rect))
                rel_x = cx - window_rect.left
                rel_y = cy - window_rect.top

                # Use screen coords for pyautogui
                pyautogui.click(cx, cy, button=button, clicks=clicks)
                return f"Clicked element [{index}] at screen ({cx}, {cy})"
            except Exception as e:
                return f"Error clicking element [{index}]: {e}"

        elif x is not None and y is not None:
            # Click by coordinates - convert window-relative to screen coords
            window_rect = ctypes.wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(window_rect))
            screen_x = window_rect.left + x
            screen_y = window_rect.top + y

            pyautogui.click(screen_x, screen_y, button=button, clicks=clicks)
            return f"Clicked at window ({x}, {y}) -> screen ({screen_x}, {screen_y})"
        else:
            return "Must provide either (x, y) coordinates or element index"

    except Exception as e:
        return f"Error clicking: {e}"


@server.tool()
async def type_text(hwnd: int, text: str) -> str:
    """Type text into a window.

    Args:
        hwnd: Window handle
        text: Text to type (supports Unicode/Chinese characters)

    Activates the window first, then pastes text via clipboard.
    """
    try:
        if not user32.IsWindow(hwnd):
            return f"Window {hwnd} no longer exists"

        _activate_window(hwnd)
        time.sleep(0.1)

        _paste_text(text)
        return f"Typed {len(text)} characters"

    except Exception as e:
        return f"Error typing text: {e}"


@server.tool()
async def press_key(hwnd: int, keys: str) -> str:
    """Press a key or keyboard shortcut.

    Args:
        hwnd: Window handle
        keys: Key specification using X11 keysym names, e.g.:
            - Single key: "Return", "Escape", "Tab", "space"
            - Shortcut: "Control_L+c", "Control_L+Shift_L+s"
            - Arrows: "Up", "Down", "Left", "Right"
            - Function keys: "F1" through "F12"

    Whitespace around '+' is ignored.
    """
    try:
        if not user32.IsWindow(hwnd):
            return f"Window {hwnd} no longer exists"

        _activate_window(hwnd)
        time.sleep(0.1)

        key_list = _parse_key_string(keys)

        if len(key_list) == 1:
            pyautogui.press(key_list[0])
        else:
            pyautogui.hotkey(*key_list)

        return f"Pressed: {keys}"

    except Exception as e:
        return f"Error pressing key: {e}"


@server.tool()
async def scroll(hwnd: int, x: int, y: int, scroll_y: int, scroll_x: int = 0) -> str:
    """Scroll in a window at the specified coordinates.

    Args:
        hwnd: Window handle
        x: X coordinate in window (client area)
        y: Y coordinate in window (client area)
        scroll_y: Vertical scroll amount. Positive = scroll down, negative = scroll up.
        scroll_x: Horizontal scroll amount. Positive = scroll right, negative = scroll left.

    Coordinates are relative to the window's client area.
    """
    try:
        if not user32.IsWindow(hwnd):
            return f"Window {hwnd} no longer exists"

        _activate_window(hwnd)
        time.sleep(0.1)

        # Convert to screen coords
        window_rect = ctypes.wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(window_rect))
        screen_x = window_rect.left + x
        screen_y = window_rect.top + y

        # PyAutoGUI scroll: positive = up, negative = down (opposite of our convention)
        if scroll_y != 0:
            pyautogui.scroll(-scroll_y, x=screen_x, y=screen_y)

        if scroll_x != 0:
            pyautogui.hscroll(scroll_x, x=screen_x, y=screen_y)

        return f"Scrolled at ({x}, {y}): dx={scroll_x}, dy={scroll_y}"

    except Exception as e:
        return f"Error scrolling: {e}"


@server.tool()
async def drag(hwnd: int, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5, button: str = "left") -> str:
    """Drag from one position to another in a window.

    Args:
        hwnd: Window handle
        start_x: Starting X coordinate in window (client area)
        start_y: Starting Y coordinate in window (client area)
        end_x: Ending X coordinate in window (client area)
        end_y: Ending Y coordinate in window (client area)
        duration: Drag duration in seconds (default 0.5)
        button: Mouse button to use (default "left")

    Coordinates are relative to the window's client area.
    """
    try:
        if not user32.IsWindow(hwnd):
            return f"Window {hwnd} no longer exists"

        _activate_window(hwnd)
        time.sleep(0.1)

        # Convert to screen coords
        window_rect = ctypes.wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(window_rect))

        sx = window_rect.left + start_x
        sy = window_rect.top + start_y
        ex = window_rect.left + end_x
        ey = window_rect.top + end_y

        pyautogui.moveTo(sx, sy)
        pyautogui.drag(ex - sx, ey - sy, duration=duration, button=button)

        return f"Dragged from ({start_x},{start_y}) to ({end_x},{end_y})"

    except Exception as e:
        return f"Error dragging: {e}"


@server.tool()
async def set_value(hwnd: int, index: int, value: str) -> str:
    """Set the value of an editable element by index.

    Args:
        hwnd: Window handle
        index: Element index from get_window_state accessibility tree
        value: New value to set

    Element indexes are ephemeral - refresh with get_window_state if stale.
    """
    try:
        if not user32.IsWindow(hwnd):
            return f"Window {hwnd} no longer exists"

        elem = _get_element_by_index(hwnd, index)
        if not elem:
            return f"Element index {index} not found. Call get_window_state to refresh indexes."

        try:
            # Try ValuePattern
            vp = elem.GetCurrentPattern(10002)  # UIA_ValuePatternId
            if vp:
                vp.SetValue(value)
                return f"Set value of element [{index}] to: {value}"
            else:
                return f"Element [{index}] does not support Value pattern"
        except Exception as e:
            return f"Error setting value on element [{index}]: {e}"

    except Exception as e:
        return f"Error: {e}"


@server.tool()
async def perform_secondary_action(hwnd: int, index: int, action: str) -> str:
    """Perform a secondary action on an element by index.

    Args:
        hwnd: Window handle
        index: Element index from get_window_state accessibility tree
        action: Action to perform. Common actions:
            - "Invoke" - click/activate the element
            - "Toggle" - toggle checkbox/switch
            - "Expand" / "Collapse" - expand/collapse tree nodes
            - "Select" - select the element

    Element indexes are ephemeral - refresh with get_window_state if stale.
    """
    try:
        if not user32.IsWindow(hwnd):
            return f"Window {hwnd} no longer exists"

        elem = _get_element_by_index(hwnd, index)
        if not elem:
            return f"Element index {index} not found. Call get_window_state to refresh indexes."

        action_lower = action.lower()

        try:
            if action_lower == "invoke":
                ip = elem.GetCurrentPattern(10000)  # UIA_InvokePatternId
                if ip:
                    ip.Invoke()
                    return f"Invoked element [{index}]"
                else:
                    return f"Element [{index}] does not support Invoke pattern"

            elif action_lower == "toggle":
                tp = elem.GetCurrentPattern(10001)  # UIA_TogglePatternId
                if tp:
                    tp.Toggle()
                    return f"Toggled element [{index}]"
                else:
                    return f"Element [{index}] does not support Toggle pattern"

            elif action_lower in ("expand", "collapse"):
                ep = elem.GetCurrentPattern(10005)  # UIA_ExpandCollapsePatternId
                if ep:
                    if action_lower == "expand":
                        ep.Expand()
                    else:
                        ep.Collapse()
                    return f"{action.capitalize()}ed element [{index}]"
                else:
                    return f"Element [{index}] does not support ExpandCollapse pattern"

            elif action_lower == "select":
                sp = elem.GetCurrentPattern(10010)  # UIA_SelectionItemPatternId
                if sp:
                    sp.Select()
                    return f"Selected element [{index}]"
                else:
                    return f"Element [{index}] does not support SelectionItem pattern"

            else:
                return f"Unknown action: {action}. Supported: Invoke, Toggle, Expand, Collapse, Select"

        except Exception as e:
            return f"Error performing {action} on element [{index}]: {e}"

    except Exception as e:
        return f"Error: {e}"


@server.tool()
async def activate_window(hwnd: int) -> str:
    """Bring a window to the foreground.

    Args:
        hwnd: Window handle

    Restores the window if minimized and brings it to front.
    """
    try:
        if not user32.IsWindow(hwnd):
            return f"Window {hwnd} no longer exists"

        buf = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, buf, 512)

        if _activate_window(hwnd):
            return f"Activated window [{hwnd}]: {buf.value}"
        else:
            return f"Failed to activate window [{hwnd}]: {buf.value}"

    except Exception as e:
        return f"Error activating window: {e}"


def main():
    """Entry point for the MCP server."""
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
