import sys
from modern_delivery import ModernDelivery

if __name__ == "__main__":
    app = ModernDelivery(sys.argv)

    # app.showWindow()

    sys.exit(app.exec())
