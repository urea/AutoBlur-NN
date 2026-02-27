import sys
import os

# Add App directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'App'))

from gui import AutoMosaicGUI

if __name__ == "__main__":
    app = AutoMosaicGUI()
    app.mainloop()
