"""Utility functions to support DOSData and DOSCollection objects"""
from typing import Optional

# This import is for the benefit of type-checking / mypy
if False:
    import matplotlib.axes
    import matplotlib.figure


class SimplePlottingAxes:
    def __init__(self,
                 ax: 'matplotlib.axes.Axes' = None,
                 show: bool = False,
                 filename: str = None) -> None:
        self.ax = ax
        self.show = show
        self.filename = filename
        self.figure = None  # type: Optional[matplotlib.figure.Figure]
        
    def __enter__(self) -> 'matplotlib.axes.Axes':
        if self.ax is None:
            import matplotlib.pyplot as plt
            self.figure, self.ax = plt.subplots()
        else:
            self.figure = self.ax.get_figure()

        return self.ax
            
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.figure is None:
            raise Exception("Did not initialize matplotlib figure properly")
        if self.show:
            self.figure.show()
        if self.filename is not None:
            self.figure.savefig(self.filename)
