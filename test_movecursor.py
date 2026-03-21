
import sys
from PyQt6.QtWidgets import QApplication, QTextEdit
from PyQt6.QtGui import QTextCursor

app = QApplication(sys.argv)
te = QTextEdit()
te.setText("Hello World")
try:
    te.moveCursor(QTextCursor.MoveOperation.End)
    print("Success: moveCursor(QTextCursor.MoveOperation.End)")
except Exception as e:
    print(f"Error: {e}")

try:
    # This should fail with TypeError if it's the bug
    te.moveCursor(True)
    print("Success: moveCursor(True)")
except TypeError as te_err:
    print(f"Expected TypeError: {te_err}")
except Exception as e:
    print(f"Other Error: {e}")

sys.exit(0)
