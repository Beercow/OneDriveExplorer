# OneDriveExplorer
# Copyright (C) 2022
#
# This file is part of OneDriveExplorer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

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
