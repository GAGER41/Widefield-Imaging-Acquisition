import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import random
import numpy as np
import importlib.util       
 

spec = importlib.util.spec_from_file_location(
  "signal_generator", "/Users/maxence/chul/Widefield-Imaging-Acquisition/src/signal_generator.py")   
signal_generator = importlib.util.module_from_spec(spec)       
spec.loader.exec_module(signal_generator)

class PlotWindow(QDialog):
    def __init__(self, parent=None):
        super(PlotWindow, self).__init__(parent)

        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent

        # Just some button connected to `plot` method

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def get_data(self, time_values, pulses, jitter, width=0.2):
        y_values = signal_generator.random_square(time_values, pulses, width, jitter)
        return y_values

    def plot(self, x, y):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(x, y)
        self.canvas.draw()

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Widefield Imaging Aquisition'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.plot_x_values = []
        self.plot_y_values = []
        self.elapsed_time = 0
        
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.grid_layout.setAlignment(Qt.AlignTop)

        self.experiment_settings_label = QLabel('Experiment Settings')
        self.experiment_settings_label.setFont(QFont("IBM Plex Sans", 17))
        self.grid_layout.addWidget(self.experiment_settings_label, 0,0)

        self.experiment_settings_main_window = QVBoxLayout()
        self.experiment_name_window = QHBoxLayout()
        self.experiment_name = QLabel('Experiment Name')
        self.experiment_name_window.addWidget(self.experiment_name)
        self.experiment_name_cell = QLineEdit()
        self.experiment_name_window.addWidget(self.experiment_name_cell)
        self.experiment_settings_main_window.addLayout(self.experiment_name_window)

        self.mouse_id_window = QHBoxLayout()
        self.mouse_id_label = QLabel('Mouse ID')
        self.mouse_id_window.addWidget(self.mouse_id_label)
        self.mouse_id_cell = QLineEdit()
        self.mouse_id_window.addWidget(self.mouse_id_cell)
        self.experiment_settings_main_window.addLayout(self.mouse_id_window)

        self.directory_window = QHBoxLayout()
        self.directory_save_files_checkbox = QCheckBox()
        self.directory_save_files_checkbox.setText("Save")
        self.directory_save_files_checkbox.stateChanged.connect(self.enable_directory)
        self.directory_window.addWidget(self.directory_save_files_checkbox)
        self.directory_choose_button = QPushButton("Select Directory")
        self.directory_choose_button.setIcon(QIcon("gui/icons/folder-plus.png"))
        self.directory_choose_button.setDisabled(True)
        self.directory_choose_button.clicked.connect(self.choose_directory)
        self.directory_window.addWidget(self.directory_choose_button)
        self.directory_cell = QLineEdit("")
        self.directory_cell.setReadOnly(True)
        self.directory_window.addWidget(self.directory_cell)
        self.experiment_settings_main_window.addLayout(self.directory_window)

        self.grid_layout.addLayout(self.experiment_settings_main_window, 1, 0)

        self.image_settings_label = QLabel('Image Settings')
        self.image_settings_label.setFont(QFont("IBM Plex Sans", 17))
        self.grid_layout.addWidget(self.image_settings_label, 0,1)

        self.image_settings_main_window = QVBoxLayout()

        self.framerate_window = QHBoxLayout()
        self.framerate_label = QLabel('Framerate')
        self.framerate_window.addWidget(self.framerate_label)
        self.framerate_cell = QLineEdit('30')
        self.framerate_window.addWidget(self.framerate_cell)
        self.image_settings_main_window.addLayout(self.framerate_window)

        self.exposure_window = QHBoxLayout()
        self.exposure_label = QLabel('Exposure')
        self.exposure_window.addWidget(self.exposure_label)
        self.exposure_cell = QLineEdit('10')
        self.exposure_window.addWidget(self.exposure_cell)
        self.image_settings_main_window.addLayout(self.exposure_window)

        self.image_settings_second_window = QHBoxLayout()
        self.speckle_button = QCheckBox('Infrared')
        self.image_settings_second_window.addWidget(self.speckle_button)
        self.red_button = QCheckBox('Red')
        self.image_settings_second_window.addWidget(self.red_button)
        self.green_button = QCheckBox('Green')
        self.image_settings_second_window.addWidget(self.green_button)
        self.fluorescence_button = QCheckBox('Blue')
        self.image_settings_second_window.addWidget(self.fluorescence_button)
        self.image_settings_main_window.addLayout(self.image_settings_second_window)
        
        self.grid_layout.addLayout(self.image_settings_main_window, 1, 1)

        self.live_preview_label = QLabel('Live Preview')
        self.live_preview_label.setFont(QFont("IBM Plex Sans", 17))
        self.grid_layout.addWidget(self.live_preview_label, 0, 2)

        self.live_preview_pixmap = QPixmap('mouse.jpg')
        self.live_preview_image = QLabel(self)
        self.live_preview_image.setPixmap(self.live_preview_pixmap)
        self.live_preview_image.resize(self.live_preview_pixmap.width(),
                          self.live_preview_pixmap.height())
        self.grid_layout.addWidget(self.live_preview_image, 1, 2)

        self.stimulation_tree_label = QLabel('Stimulation Tree')
        self.stimulation_tree_label.setFont(QFont("IBM Plex Sans", 17))
        self.grid_layout.addWidget(self.stimulation_tree_label, 2, 0)

        self.stimulation_tree_window = QVBoxLayout()
        self.stimulation_tree = QTreeWidget()
        self.stimulation_tree.setHeaderLabels(["Name", "Iterations", "Delay", "Type", "Pulses", "Duration", "Jitter", "Width", "Frequency", "Duty", "Canal 1", "Canal 2"])
        for i in range(9):
            #self.stimulation_tree.header().hideSection(i+1)
            pass
        self.stimulation_tree.currentItemChanged.connect(self.actualize_tree)
        self.stimulation_tree_window.addWidget(self.stimulation_tree)


        self.stimulation_tree_switch_window = QStackedLayout()
        self.stimulation_tree_second_window = QHBoxLayout()
        self.stim_buttons_container = QWidget()
        self.delete_branch_button = QPushButton('Delete')
        self.delete_branch_button.setIcon(QIcon("gui/icons/trash.png"))
        self.delete_branch_button.clicked.connect(self.delete_branch)
        self.stimulation_tree_second_window.addWidget(self.delete_branch_button)
        self.add_brother_branch_button = QPushButton('Add Sibling')
        self.add_brother_branch_button.clicked.connect(self.add_brother)
        self.add_brother_branch_button.setIcon(QIcon("gui/icons/arrow-bar-down.png"))
        self.stimulation_tree_second_window.addWidget(self.add_brother_branch_button)
        self.add_child_branch_button = QPushButton('Add Child')
        self.add_child_branch_button.clicked.connect(self.add_child)
        self.add_child_branch_button.setIcon(QIcon("gui/icons/arrow-bar-right.png"))
        self.stimulation_tree_second_window.addWidget(self.add_child_branch_button)
        self.stim_buttons_container.setLayout(self.stimulation_tree_second_window)
        self.stimulation_tree_switch_window.addWidget(self.stim_buttons_container)
        
        self.new_branch_button = QPushButton("New Stimulation")
        self.new_branch_button.setIcon(QIcon("gui/icons/square-plus.png"))
        self.stimulation_tree_third_window = QHBoxLayout()
        self.stimulation_tree_third_window.addWidget(self.new_branch_button)
        self.stim_buttons_container2 = QWidget()
        self.stim_buttons_container2.setLayout(self.stimulation_tree_third_window)
        self.stimulation_tree_switch_window.addWidget(self.stim_buttons_container2)
        self.new_branch_button.clicked.connect(self.first_stimulation)
        self.grid_layout.addLayout(self.stimulation_tree_switch_window, 4, 0)
        
        #self.stimulation_tree_window.addLayout(self.stimulation_tree_switch_window)
        self.stimulation_tree_switch_window.setCurrentIndex(1)
        self.grid_layout.addLayout(self.stimulation_tree_window, 3, 0)

        self.signal_adjust_label = QLabel('Signal Adjust')
        self.signal_adjust_label.setFont(QFont("IBM Plex Sans", 17))
        self.grid_layout.addWidget(self.signal_adjust_label, 2, 1)


        self.signal_adjust_superposed = QStackedLayout()
        self.stimulation_edit_layout = QVBoxLayout()
        self.stimulation_edit_layout.setContentsMargins(0, 0, 0, 0)

        self.stimulation_name_label = QLabel("Stimulation Name")
        self.stimulation_name_cell = QLineEdit()
        self.stimulation_name_cell.textEdited.connect(self.name_to_tree)
        self.stimulation_name_window = QHBoxLayout()
        self.stimulation_name_window.addWidget(self.stimulation_name_label)
        self.stimulation_name_window.addWidget(self.stimulation_name_cell)
        self.stimulation_edit_layout.addLayout(self.stimulation_name_window)

        self.stimulation_type_label = QLabel("Stimulation Type")
        self.stimulation_type_cell = QComboBox()
        self.stimulation_type_cell.addItem("random-square")
        self.stimulation_type_cell.addItem("square")
        self.stimulation_type_cell.addItem("Third")
        self.stimulation_type_cell.currentIndexChanged.connect(self.type_to_tree)
        self.stimulation_type_window = QHBoxLayout()
        self.stimulation_type_window.addWidget(self.stimulation_type_label)
        self.stimulation_type_window.addWidget(self.stimulation_type_cell)
        self.stimulation_edit_layout.addLayout(self.stimulation_type_window)
        self.different_signals_window = QStackedLayout()

        

        self.first_signal_duration_window = QHBoxLayout()
        self.first_signal_type_duration_label = QLabel("Duration (s)")
        self.first_signal_duration_window.addWidget(self.first_signal_type_duration_label)
        self.first_signal_type_duration_cell = QLineEdit()
        self.first_signal_type_duration_cell.textEdited.connect(self.signal_to_tree)
        self.first_signal_duration_window.addWidget(self.first_signal_type_duration_cell)

        self.first_signal_type_window = QVBoxLayout()
        self.first_signal_type_window.setAlignment(Qt.AlignLeft)
        self.first_signal_type_window.setAlignment(Qt.AlignTop)
        self.first_signal_type_window.setContentsMargins(0, 0, 0, 0)
        self.first_signal_type_container = QWidget()
        self.first_signal_type_container.setLayout(self.first_signal_type_window)
        self.stimulation_edit_layout.addLayout(self.first_signal_duration_window)
        self.stimulation_edit_layout.addLayout(self.different_signals_window)


        

        self.first_signal_pulses_window = QHBoxLayout()
        self.first_signal_type_pulses_label = QLabel("Pulses")
        self.first_signal_pulses_window.addWidget(self.first_signal_type_pulses_label)
        self.first_signal_type_pulses_cell = QLineEdit()
        self.first_signal_type_pulses_cell.textEdited.connect(self.signal_to_tree)
        self.first_signal_pulses_window.addWidget(self.first_signal_type_pulses_cell)


        self.first_signal_frequency_window = QHBoxLayout()
        self.first_signal_type_frequency_label = QLabel("Frequency (Hz)")
        self.first_signal_frequency_window.addWidget(self.first_signal_type_frequency_label)
        self.first_signal_type_frequency_cell = QLineEdit()
        self.first_signal_type_frequency_cell.setDisabled(True)
        self.first_signal_frequency_window.addWidget(self.first_signal_type_frequency_cell)
        

        self.first_signal_jitter_window = QHBoxLayout()
        self.first_signal_type_jitter_label = QLabel("Jitter (s)")
        self.first_signal_jitter_window.addWidget(self.first_signal_type_jitter_label)
        self.first_signal_type_jitter_cell = QLineEdit()
        self.first_signal_type_jitter_cell.setText("0")
        self.first_signal_type_jitter_cell.textEdited.connect(self.signal_to_tree)
        self.first_signal_jitter_window.addWidget(self.first_signal_type_jitter_cell)

        self.first_signal_width_window = QHBoxLayout()
        self.first_signal_type_width_label = QLabel("Width (s)")
        self.first_signal_width_window.addWidget(self.first_signal_type_width_label)
        self.first_signal_type_width_cell = QLineEdit()
        self.first_signal_type_width_cell.setText("0")
        self.first_signal_type_width_cell.textEdited.connect(self.signal_to_tree)
        self.first_signal_width_window.addWidget(self.first_signal_type_width_cell)

        self.first_signal_type_window.addLayout(self.first_signal_duration_window)
        self.first_signal_type_window.addLayout(self.first_signal_pulses_window)
        self.first_signal_type_window.addLayout(self.first_signal_width_window)
        self.first_signal_type_window.addLayout(self.first_signal_jitter_window)
        self.first_signal_type_window.addLayout(self.first_signal_frequency_window)
#-------------------

        self.second_signal_type_window = QVBoxLayout()
        self.second_signal_type_container = QWidget()
        self.second_signal_type_window.setAlignment(Qt.AlignLeft)
        self.second_signal_type_window.setAlignment(Qt.AlignTop)
        self.second_signal_type_window.setContentsMargins(0, 0, 0, 0)
        self.second_signal_type_container.setLayout(self.second_signal_type_window)
        self.stimulation_edit_layout.addLayout(self.different_signals_window)

        self.second_signal_frequency_window = QHBoxLayout()
        self.second_signal_type_frequency_label = QLabel("Frequency")
        self.second_signal_frequency_window.addWidget(self.second_signal_type_frequency_label)
        self.second_signal_type_frequency_cell = QLineEdit()
        self.second_signal_type_frequency_cell.textEdited.connect(self.signal_to_tree)
        self.second_signal_frequency_window.addWidget(self.second_signal_type_frequency_cell)

        self.second_signal_duty_window = QHBoxLayout()
        self.second_signal_type_duty_label = QLabel("Duty")
        self.second_signal_duty_window.addWidget(self.second_signal_type_duty_label)
        self.second_signal_type_duty_cell = QLineEdit()
        self.second_signal_type_duty_cell.textEdited.connect(self.signal_to_tree)
        self.second_signal_duty_window.addWidget(self.second_signal_type_duty_cell)

        self.second_signal_type_window.addLayout(self.second_signal_frequency_window)
        self.second_signal_type_window.addLayout(self.second_signal_duty_window)

#-------------------

        self.third_signal_type_window = QVBoxLayout()
        self.third_signal_type_container = QWidget()
        self.third_signal_type_container.setLayout(self.third_signal_type_window)
        self.stimulation_edit_layout.addLayout(self.different_signals_window)

        self.third_signal_type_name = QLabel("signal3")
        self.third_signal_type_window.addWidget(self.third_signal_type_name)

        self.different_signals_window.addWidget(self.first_signal_type_container)
        self.different_signals_window.addWidget(self.second_signal_type_container)
        self.different_signals_window.addWidget(self.third_signal_type_container)



        self.stimulation_edit_container = QWidget()
        self.stimulation_edit_container.setLayout(self.stimulation_edit_layout)
        self.block_edit_layout = QVBoxLayout()
        self.block_edit_layout.setContentsMargins(0, 0, 0, 0)
        self.block_edit_layout.setAlignment(Qt.AlignLeft)
        self.block_edit_layout.setAlignment(Qt.AlignTop)

        self.canal_window = QHBoxLayout()
        self.first_signal_first_canal_check = QCheckBox()
        self.first_signal_first_canal_check.stateChanged.connect(self.canals_to_tree)
        self.first_signal_first_canal_check.setText("Canal 1")
        self.canal_window.addWidget(self.first_signal_first_canal_check)
        self.first_signal_second_canal_check = QCheckBox()
        self.first_signal_second_canal_check.stateChanged.connect(self.canals_to_tree)
        self.first_signal_second_canal_check.setText("Canal 2")
        self.canal_window.addWidget(self.first_signal_second_canal_check)
        self.first_signal_type_window.addLayout(self.canal_window)

        self.block_name_label = QLabel("Block Name")
        self.block_name_cell = QLineEdit()
        self.block_name_cell.textEdited.connect(self.name_to_tree)
        self.block_name_window = QHBoxLayout()
        self.block_name_window.addWidget(self.block_name_label)
        self.block_name_window.addWidget(self.block_name_cell)
        self.block_edit_layout.addLayout(self.block_name_window)

        self.block_iterations_window = QHBoxLayout()
        self.block_iterations_label = QLabel("Iterations")
        self.block_iterations_cell = QLineEdit()
        self.block_iterations_cell.textEdited.connect(self.block_to_tree)
        self.block_iterations_window.addWidget(self.block_iterations_label)
        self.block_iterations_window.addWidget(self.block_iterations_cell)
        self.block_edit_layout.addLayout(self.block_iterations_window)

        self.block_delay_window = QHBoxLayout()
        self.block_delay_label = QLabel("Delay")
        self.block_delay_cell = QLineEdit()
        self.block_delay_cell.textEdited.connect(self.block_to_tree)
        self.block_delay_window = QHBoxLayout()
        self.block_delay_window.addWidget(self.block_delay_label)
        self.block_delay_window.addWidget(self.block_delay_cell)
        self.block_edit_layout.addLayout(self.block_delay_window)

    



        self.block_edit_container = QWidget()
        self.block_edit_container.setLayout(self.block_edit_layout)
        self.signal_adjust_superposed.addWidget(self.stimulation_edit_container)
        self.signal_adjust_superposed.addWidget(self.block_edit_container)
        self.signal_adjust_superposed.addWidget(QLabel())
        self.signal_adjust_superposed.setCurrentIndex(2)
        self.grid_layout.addLayout(self.signal_adjust_superposed, 3, 1)

        

        self.signal_preview_label = QLabel('Signal Preview')
        self.signal_preview_label.setFont(QFont("IBM Plex Sans", 17))
        self.grid_layout.addWidget(self.signal_preview_label, 2, 2)

        self.buttons_main_window = QHBoxLayout()
        self.stop_button = QPushButton('Stop')
        self.stop_button.setIcon(QIcon("gui/icons/player-stop.png"))
        self.stop_button.clicked.connect(self.stop)
        self.buttons_main_window.addWidget(self.stop_button)
        self.run_button = QPushButton('Run')
        self.run_button.setIcon(QIcon("gui/icons/player-play.png"))
        self.run_button.clicked.connect(self.run)
        self.buttons_main_window.addWidget(self.run_button)
        self.plot_window = PlotWindow()
        self.grid_layout.addWidget(self.plot_window, 3,2)
        self.grid_layout.addLayout(self.buttons_main_window, 4, 2)

        self.show()

    def run(self):
        lights = []
        if self.speckle_button.isChecked():
            lights.append('ir')
        if self.red_button.isChecked():
            lights.append('red')
        if self.green_button.isChecked():
            lights.append('green')
        if self.fluorescence_button.isChecked():
            lights.append('blue')
        print('\n'.join(lights))

    def stop(self):
        pass

    def choose_directory(self):
        folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.directory_cell.setText(folder)

    def enable_directory(self):
        if self.directory_save_files_checkbox.isChecked():
            self.directory_choose_button.setDisabled(False)
            self.directory_cell.setDisabled(False)
        else:
            self.directory_choose_button.setDisabled(True)
            self.directory_cell.setDisabled(True)

    def delete_branch(self):
        try:
            root = self.stimulation_tree.invisibleRootItem()
            parent = self.stimulation_tree.currentItem().parent()
            if parent.childCount() == 1:
                parent.setIcon(0, QIcon("gui/icons/wave-square.png"))
            (parent or root).removeChild(self.stimulation_tree.currentItem())
        except Exception:
            root.removeChild(self.stimulation_tree.currentItem())
        
    
    def add_brother(self):
        if self.stimulation_tree.currentItem():
            stimulation_tree_item = QTreeWidgetItem()
            stimulation_tree_item.setText(0, "No Name")
            stimulation_tree_item.setForeground(0, QBrush(QColor(211,211,211)))
            stimulation_tree_item.setIcon(0, QIcon("gui/icons/wave-square.png"))
            parent = self.stimulation_tree.selectedItems()[0].parent()
            if parent:
                index = parent.indexOfChild(self.stimulation_tree.selectedItems()[0])
                parent.insertChild(index+1, stimulation_tree_item)
            else:
                self.stimulation_tree.addTopLevelItem(stimulation_tree_item)
            self.stimulation_tree.setCurrentItem(stimulation_tree_item)
            self.type_to_tree(first = True)
            self.canals_to_tree(first=True)
        else:
            pass

    def add_child(self):
        if self.stimulation_tree.currentItem():
            self.stimulation_tree.currentItem().setIcon(0, QIcon("gui/icons/package.png"))
            self.stimulation_tree.currentItem().setText(1, "1")
            stimulation_tree_item = QTreeWidgetItem()
            stimulation_tree_item.setIcon(0, QIcon("gui/icons/wave-square.png"))
            stimulation_tree_item.setText(0,"No Name")
            stimulation_tree_item.setForeground(0, QBrush(QColor(211,211,211)))
            self.stimulation_tree.selectedItems()[0].addChild(stimulation_tree_item)
            self.stimulation_tree.selectedItems()[0].setExpanded(True)
            self.stimulation_tree.setCurrentItem(stimulation_tree_item)
            self.type_to_tree(first = True)
            self.canals_to_tree(first=True)
        else:
            pass

    def first_stimulation(self):
        stimulation_tree_item = QTreeWidgetItem()
        stimulation_tree_item.setForeground(0, QBrush(QColor(211,211,211)))
        stimulation_tree_item.setIcon(0, QIcon("gui/icons/wave-square.png"))
        stimulation_tree_item.setText(0, "No Name")
        self.stimulation_tree.addTopLevelItem(stimulation_tree_item)
        self.stimulation_tree_switch_window.setCurrentIndex(0)
        self.stimulation_tree.setCurrentItem(stimulation_tree_item)
        self.canals_to_tree(first=True)
        self.type_to_tree(first = True)

    def change_frequency(self):
        try:
            self.first_signal_type_frequency_cell.setText(str(round(int(self.first_signal_type_pulses_cell.text())/int(self.first_signal_type_duration_cell.text()), 3)))
        except Exception:
            self.first_signal_type_frequency_cell.setText("")

    def actualize_tree(self):
        if self.stimulation_tree.currentItem():
            self.stimulation_tree_switch_window.setCurrentIndex(0)
        else:
            self.stimulation_tree_switch_window.setCurrentIndex(1)
        try:
            if self.stimulation_tree.currentItem().childCount() > 0:
                self.signal_adjust_superposed.setCurrentIndex(1)
            else:
                self.signal_adjust_superposed.setCurrentIndex(0)
        except AttributeError:
            self.signal_adjust_superposed.setCurrentIndex(2)
        self.tree_to_name()
        self.tree_to_block()
        self.tree_to_type()
        self.tree_to_signal()
        self.tree_to_canal()
        self.plot()
        self.draw()

    def name_to_tree(self):
        branch = self.stimulation_tree.currentItem()
        branch.setForeground(0, QBrush(QColor(0, 0, 0)))
        if branch.childCount() > 0:
            branch.setText(0, self.block_name_cell.text())
        else:
            branch.setText(0, self.stimulation_name_cell.text())

    def tree_to_name(self):
        try:
            if self.stimulation_tree.currentItem().childCount() > 0:
                if self.stimulation_tree.currentItem().text(0) != "No Name":
                    self.block_name_cell.setText(self.stimulation_tree.currentItem().text(0))
                else:
                    self.block_name_cell.setText("")
            else:
                if self.stimulation_tree.currentItem().text(0) != "No Name":
                    self.stimulation_name_cell.setText(self.stimulation_tree.currentItem().text(0))
                else:
                    self.stimulation_name_cell.setText("")
        except AttributeError:
            pass
    
    def type_to_tree(self, first=False):
        if first is True:
            self.stimulation_type_cell.setCurrentIndex(0)
        try:
            self.different_signals_window.setCurrentIndex(self.stimulation_type_cell.currentIndex())
            self.stimulation_tree.currentItem().setText(3, str(self.stimulation_type_cell.currentText()))
            self.plot()
            self.draw()
        except Exception:
            pass

    def tree_to_type(self):
        try:
            self.stimulation_type_cell.setCurrentIndex(int(self.stimulation_tree.currentItem().text(3)))
        except Exception:
            self.stimulation_type_cell.setCurrentIndex(0)

    def signal_to_tree(self):
        self.change_frequency()
        self.stimulation_tree.currentItem().setText(4, self.first_signal_type_pulses_cell.text())
        self.stimulation_tree.currentItem().setText(5, self.first_signal_type_duration_cell.text())
        self.stimulation_tree.currentItem().setText(6, self.first_signal_type_jitter_cell.text())
        self.stimulation_tree.currentItem().setText(7, self.first_signal_type_width_cell.text())
        self.stimulation_tree.currentItem().setText(8, self.second_signal_type_frequency_cell.text())
        self.stimulation_tree.currentItem().setText(9, self.second_signal_type_duty_cell.text())
        self.plot()
        self.draw()

    def tree_to_signal(self):
        try:
            self.first_signal_type_pulses_cell.setText(self.stimulation_tree.currentItem().text(4))
            self.first_signal_type_duration_cell.setText(self.stimulation_tree.currentItem().text(5))
            self.first_signal_type_jitter_cell.setText(self.stimulation_tree.currentItem().text(6))
            self.first_signal_type_width_cell.setText(self.stimulation_tree.currentItem().text(7))
        except Exception:
            pass

    def tree_to_block(self):
        try:
            self.block_iterations_cell.setText(self.stimulation_tree.currentItem().text(1))
            self.block_delay_cell.setText(self.stimulation_tree.currentItem().text(2))
        except Exception:
            pass

    def block_to_tree(self):
        self.stimulation_tree.currentItem().setText(1, self.block_iterations_cell.text())
        self.stimulation_tree.currentItem().setText(2, self.block_delay_cell.text())
        self.plot()
        self.draw()

    def tree_to_canal(self):
        self.canal_running = True
        try:
            self.first_signal_first_canal_check.setChecked(self.boolean(self.stimulation_tree.currentItem().text(10)))
            self.first_signal_second_canal_check.setChecked(self.boolean(self.stimulation_tree.currentItem().text(11)))
        except Exception:
            pass
        self.canal_running = False

    def canals_to_tree(self, first=False):
        if self.canal_running is not True:
            if first is True:
                self.stimulation_tree.currentItem().setText(10, "False")
                self.stimulation_tree.currentItem().setText(11, "False")
            else:
                self.stimulation_tree.currentItem().setText(10, str(self.first_signal_first_canal_check.isChecked()))
                self.stimulation_tree.currentItem().setText(11, str(self.first_signal_second_canal_check.isChecked()))
            self.actualize_tree()

    def boolean(self, string):
        if string == "True":
            return True
        return False



    def plot(self, item = None):
        try: 
            if not item:
                item = self.stimulation_tree.currentItem()
            if item.childCount() > 0:
                for iteration in range(int(item.text(1))):
                    for index in range(item.childCount()):
                        child = item.child(index)
                        self.plot(child)
            else:
                sign_type = item.text(3)
                duration = int(item.text(5))
                try:
                    pulses = int(item.text(4))
                    jitter = int(item.text(6))
                    width = int(item.text(7))
                except Exception:
                    pulses = 0
                    jitter = 0
                    width = 0
                try:
                    frequency = int(item.text(8))
                    duty = float(item.text(9))
                except Exception:
                    frequency = 0
                    duty = 0
                time_values = np.linspace(0, duration, duration*300)
                data  = signal_generator.make_signal(time_values, sign_type, width, pulses, jitter, frequency, duty)
                if sign_type == "square":
                    data *= 5
                time_values += self.elapsed_time
                self.plot_x_values = np.concatenate((self.plot_x_values, time_values))
                self.plot_y_values = np.concatenate((self.plot_y_values, data))
                self.elapsed_time += duration
        except Exception as err:
            self.plot_x_values = []
            self.plot_y_values = []
            self.elapsed_time = 0
            print(err)

    def draw(self):
        new_x_values = []
        new_y_values = []
        try:
            sampling_indexes = np.linspace(0, len(self.plot_x_values)-1, 3000, dtype=int)
            new_x_values = np.take(self.plot_x_values, sampling_indexes, 0)
            new_y_values = np.take(self.plot_y_values, sampling_indexes, 0)
        except Exception as err:
            pass
            print(err)
        self.plot_window.plot(new_x_values, new_y_values)
        self.plot_x_values = []
        self.plot_y_values = []
        self.elapsed_time = 0



if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont()
    font.setFamily("IBM Plex Sans")
    app.setFont(font)
    ex = App()
    sys.exit(app.exec_())