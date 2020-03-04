import plotly.graph_objects as go
from plotly.offline import iplot, init_notebook_mode

def hv_line(direction, offset):
    assert(direction in ('v','h'))
    if direction == 'h':
        return [dict(
            type = "line", 
            x0 = 0, x1 = 1, 
            y0 = offset, y1 = offset,
            xref = "paper"
        )]
    else:
        return [dict(
            type = "line", 
            x0 = offset, x1 = offset, 
            y0 = 0, y1 = 1,
            yref = "paper"
        )]