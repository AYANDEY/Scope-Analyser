

import matplotlib
import os
import sys
from matplotlib import backend_tools, cbook
from matplotlib._pylab_helpers import Gcf
from matplotlib.backend_bases import (
    _Backend, FigureCanvasBase, FigureManagerBase, NavigationToolbar2,
    TimerBase, cursors, ToolContainerBase, StatusbarBase, MouseButton)
import matplotlib.backends.qt_editor.figureoptions as figureoptions
from matplotlib.backends.qt_editor.formsubplottool import UiSubplotTool
from matplotlib.backend_managers import ToolManager
from matplotlib.backends.qt_compat import(
    QtCore, QtGui, QtWidgets, _isdeleted, _getSaveFileName,
    is_pyqt5, __version__, QT_API)

backend_version = __version__
from matplotlib.backends.backend_qt5 import SubplotToolQt

cursord = {
    cursors.MOVE: QtCore.Qt.SizeAllCursor,
    cursors.HAND: QtCore.Qt.PointingHandCursor,
    cursors.POINTER: QtCore.Qt.ArrowCursor,
    cursors.SELECT_REGION: QtCore.Qt.CrossCursor,
    cursors.WAIT: QtCore.Qt.WaitCursor,
    }

# make place holder
qApp = None

class NavigationToolbar_(NavigationToolbar2, QtWidgets.QToolBar):
    message = QtCore.Signal(str)

    def __init__(self, canvas, parent, coordinates=True):
        """coordinates: should we show the coordinates on the right?"""
        self.canvas = canvas
        self.parent = parent
        self.coordinates = coordinates
        self._actions = {}
        """A mapping of toolitem method names to their QActions"""

        QtWidgets.QToolBar.__init__(self, parent)
        NavigationToolbar2.__init__(self, canvas)

    def _icon(self, name, color=None):
        if is_pyqt5():
            name = name.replace('.png', '_large.png')
        pm = QtGui.QPixmap(os.path.join(self.basedir, name))
        if hasattr(pm, 'setDevicePixelRatio'):
            pm.setDevicePixelRatio(self.canvas._dpi_ratio)
        if color is not None:
            mask = pm.createMaskFromColor(QtGui.QColor('black'),
                                          QtCore.Qt.MaskOutColor)
            pm.fill(color)
            pm.setMask(mask)
        return QtGui.QIcon(pm)

    def _init_toolbar(self):
        self.basedir = str(cbook._get_data_path('images'))

        background_color = self.palette().color(self.backgroundRole())
        foreground_color = self.palette().color(self.foregroundRole())
        icon_color = (foreground_color
                      if background_color.value() < 128 else None)

        for text, tooltip_text, image_file, callback in self.toolitems:
            if callback not in ['zoom', 'pan' , 'back' , 'forward','home','configure_subplots']:
                if text is None:
                    #self.addSeparator()
                    pass
                else:
                    a = self.addAction(QIcon('res\\save_icon.ico'),
                                    text, getattr(self, callback))
                    self._actions[callback] = a
                    
                    if tooltip_text is not None:
                        a.setToolTip(tooltip_text)
                    if text == 'Subplots':
                        a = self.addAction(self._icon("qt4_editor_options.png",
                                                    icon_color),
                                        'Customize', self.edit_parameters)
                        a.setToolTip('Edit axis, curve and image parameters')
        
        # Add the (x, y) location widget at the right side of the toolbar
        # The stretch factor is 1 which means any resizing of the toolbar
        # will resize this label instead of the buttons.
        
        self.Progressbar = QtWidgets.QProgressBar(self)
        self.Progressbar.setAlignment(
                    QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.Progressbar.setSizePolicy(
                QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                      QtWidgets.QSizePolicy.Maximum))
        self.Progressbar_handler=self.addWidget(self.Progressbar)
        self.Progressbar_handler.setVisible(False)
        
        self.statusLabel = QtWidgets.QLabel("", self)
        self.statusLabel.setAlignment(
                QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.statusLabel.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                    QtWidgets.QSizePolicy.Ignored))
        
        self.statusLabel.setStyleSheet("QLabel { color : black; }")
        self.labelAction1 = self.addWidget(self.statusLabel)
        font1 = QtGui.QFont("Times", 12)
        self.labelAction1.setVisible(False)
        self.statusLabel.setFont(font1)
        
        if self.coordinates:
            self.locLabel = QtWidgets.QLabel("", self)
            self.locLabel.setAlignment(
                    QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.locLabel.setSizePolicy(
                QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                      QtWidgets.QSizePolicy.Ignored))
            self.labelAction = self.addWidget(self.locLabel)
            newfont = QtGui.QFont("Times", 10) 
            self.labelAction.setVisible(True)
            self.locLabel.setFont(newfont)

    @cbook.deprecated("3.1")
    @property
    def buttons(self):
        return {}

    @cbook.deprecated("3.1")
    @property
    def adj_window(self):
        return None

    def edit_parameters(self):
        axes = self.canvas.figure.get_axes()
        if not axes:
            QtWidgets.QMessageBox.warning(
                self.parent, "Error", "There are no axes to edit.")
            return
        elif len(axes) == 1:
            ax, = axes
        else:
            titles = [
                ax.get_label() or
                ax.get_title() or
                " - ".join(filter(None, [ax.get_xlabel(), ax.get_ylabel()])) or
                f"<anonymous {type(ax).__name__}>"
                for ax in axes]
            duplicate_titles = [
                title for title in titles if titles.count(title) > 1]
            for i, ax in enumerate(axes):
                if titles[i] in duplicate_titles:
                    titles[i] += f" (id: {id(ax):#x})"  # Deduplicate titles.
            item, ok = QtWidgets.QInputDialog.getItem(
                self.parent, 'Customize', 'Select axes:', titles, 0, False)
            if not ok:
                return
            ax = axes[titles.index(item)]
        figureoptions.figure_edit(ax, self)

    def _update_buttons_checked(self):
        # sync button checkstates to match active mode
        if 'pan' in self._actions:
            self._actions['pan'].setChecked(self._active == 'PAN')
        if 'zoom' in self._actions:
            self._actions['zoom'].setChecked(self._active == 'ZOOM')

    def pan(self, *args):
        super().pan(*args)
        self._update_buttons_checked()

    def zoom(self, *args):
        super().zoom(*args)
        self._update_buttons_checked()

    def set_message(self, s):
        self.message.emit(s)
        if self.coordinates:
            '''try:
                st=s.split('y')
                self.main.printf_(st)
                st[0]=st[0].rstrip(' ')
                s1=st[0].replace('x=','freq=')+ ' Hz '
                st[1]="y"+st[1].rstrip(" ")

                if self.parent.disp_type_indx==0:
                    s2=st[1].replace('y=', 'amp=')+' mv'
                    
                else:
                    s2=st[1].replace('y=', 'L=')+ ' db'
                s=s1+s2
            except Exception:
                pass'''
            #self.locLabel.setText(s)
            pass

    def set_cursor(self, cursor):
        self.canvas.setCursor(cursord[cursor])

    def draw_rubberband(self, event, x0, y0, x1, y1):
        height = self.canvas.figure.bbox.height
        y1 = height - y1
        y0 = height - y0
        rect = [int(val) for val in (x0, y0, x1 - x0, y1 - y0)]
        self.canvas.drawRectangle(rect)

    def remove_rubberband(self):
        self.canvas.drawRectangle(None)

    def configure_subplots(self):
        image = str(cbook._get_data_path('images/matplotlib.png'))
        dia = SubplotToolQt(self.canvas.figure, self.canvas.parent())
        dia.setWindowIcon(QtGui.QIcon(image))
        dia.exec_()

    def save_figure(self, *args):
        filetypes = self.canvas.get_supported_filetypes_grouped()
        sorted_filetypes = sorted(filetypes.items())
        default_filetype = self.canvas.get_default_filetype()

        startpath = os.path.expanduser(
            matplotlib.rcParams['savefig.directory'])
        start = os.path.join(startpath, self.canvas.get_default_filename())
        filters = []
        selectedFilter = None
        for name, exts in sorted_filetypes:
            exts_list = " ".join(['*.%s' % ext for ext in exts])
            filter = '%s (%s)' % (name, exts_list)
            if default_filetype in exts:
                selectedFilter = filter
            filters.append(filter)
        filters = ';;'.join(filters)

        fname, filter = _getSaveFileName(self.canvas.parent(),
                                         "Choose a filename to save to",
                                         start, filters, selectedFilter)
        if fname:
            # Save dir for next time, unless empty str (i.e., use cwd).
            if startpath != "":
                matplotlib.rcParams['savefig.directory'] = (
                    os.path.dirname(fname))
            try:
                self.canvas.figure.savefig(fname)
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Error saving file", str(e),
                    QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.NoButton)

    def set_history_buttons(self):
        can_backward = self._nav_stack._pos > 0
        can_forward = self._nav_stack._pos < len(self._nav_stack._elements) - 1
        if 'back' in self._actions:
            self._actions['back'].setEnabled(can_backward)
        if 'forward' in self._actions:
            self._actions['forward'].setEnabled(can_forward)

from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from PyQt5.QtGui import QIcon
NavigationToolbar2QT=NavigationToolbar_
