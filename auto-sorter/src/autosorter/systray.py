from infi.systray import SysTrayIcon

class SysTray:
    def __init__(self, icon_path, title, menu_options, on_quit):
        self.icon_path = icon_path
        self.title = title
        self.menu_options = menu_options
        self.on_quit = on_quit
        self.systray = None

    def start(self):
        self.systray = SysTrayIcon(self.icon_path, self.title, self.menu_options, on_quit=self.on_quit)
        self.systray.start()

    def update(self, menu_options):
        if self.systray:
            self.systray.update(menu_options=menu_options)