from ode.helpers.ScrollableNotebook import ScrollableNotebook


class MyScrollableNotebook(ScrollableNotebook):
    """Custom table class inherits from Table. You can then override required methods"""
    def __init__(self, parent=None, **kwargs):
        ScrollableNotebook.__init__(self, parent, **kwargs)
        return

    def _rightSlide(self, event):
        try:
            self.notebookTab.select((self.notebookTab.index(self.notebookTab.select())) + 1)
        except Exception:
            pass
        if self.notebookTab.winfo_width() > self.notebookContent.winfo_width()-self.menuSpace:
            if (self.notebookContent.winfo_width()-(self.notebookTab.winfo_width()+self.notebookTab.winfo_x())) <= self.menuSpace+5:
                self.xLocation -= 20
                self.notebookTab.place(x=self.xLocation, y=0)

    def _leftSlide(self, event):
        try:
            self.notebookTab.select((self.notebookTab.index(self.notebookTab.select())) - 1)
        except Exception:
            pass
        if not self.notebookTab.winfo_x() == 0:
            self.xLocation += 20
            self.notebookTab.place(x=self.xLocation, y=0)
