
try:
    from PyQt6.QtGui import QTextCursor
    print(f"End: {QTextCursor.MoveOperation.End}")
except AttributeError:
    print("MoveOperation.End not found")
except ImportError:
    print("PyQt6 not installed")
except Exception as e:
    print(f"Error: {e}")
