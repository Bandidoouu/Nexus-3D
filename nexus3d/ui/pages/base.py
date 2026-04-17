from nexus3d.ui.widgets import create_shadow_card


class BasePage:
    def __init__(self, app, scroll_frame):
        self.app = app
        self.db = app.db
        self.colors = app.colors
        self.frame = scroll_frame.scrollable_frame

    def card(self, parent, title=""):
        return create_shadow_card(parent, self.colors, title)

    def refresh(self):
        pass
