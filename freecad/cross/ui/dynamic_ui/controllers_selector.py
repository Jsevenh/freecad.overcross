# import statements
from PySide import QtGui, QtCore, QtWidgets
import FreeCADGui as fcgui
import FreeCAD as fc

from ...controller_proxy import get_controllers_data
from ...wb_utils import get_workbench_param, git_change_submodule_branch, is_robot_selected, set_workbench_param
from ...wb_utils import is_controller_selected
from ...wb_utils import is_broadcaster_selected
from ...controller_proxy import make_controller
from ...controller_proxy import make_broadcaster
from ...freecad_utils import message
from ...freecadgui_utils import getSelectedPropertiesAndObjectsInTreeView
from ... import wb_constants


class ControllersSelectorModalClass(QtGui.QDialog):
    """ Display modal with controllers and broadcaster adder to project """

    def __init__(self):
        super(ControllersSelectorModalClass, self).__init__()
        self.initUI()


    def initUI(self):
        self.resize(400, 350)
        self.setWindowTitle("Select controller")

        # get controller and brodcasters data and make dropdowns
        self.controllers = get_controllers_data()
        self.controllers_dropdown = QtGui.QComboBox(self)
        self.broadcasters_dropdown = QtGui.QComboBox(self)
        for controller_name, controller in self.controllers['controllers'].items():
            self.controllers_dropdown.addItem(controller_name, controller['description'])
        for broadcaster_name, broadcaster in self.controllers['broadcasters'].items():
            self.broadcasters_dropdown.addItem(broadcaster_name, broadcaster['description'])

        # attach triggers of changing descriptions
        self.controllers_dropdown.currentTextChanged.connect(self.update_controller_description)
        self.broadcasters_dropdown.currentTextChanged.connect(self.update_broadcaster_description)


        ### change controllers ros version
        # get ros_versions
        current_ros_version = get_workbench_param(wb_constants.ROS2_CONTROLLERS_CURRENT_ROS_VERSION_PARAM_NAME, 'jazzy')
        self.ros_versions = wb_constants.ROS2_CONTROLLERS_ROS_VERSIONS
        # fill ros_versions dropdown
        self.ros_versions_dropdown = QtGui.QComboBox(self)
        for ros_version in self.ros_versions:
            self.ros_versions_dropdown.addItem(ros_version['ros_version'], ros_version['ros_version'])
        self.ros_versions_dropdown.setCurrentText(current_ros_version)
        # create ros_versions box
        formGroupBoxRosVersions = QtWidgets.QGroupBox("ROS versions")
        form_layout = QtWidgets.QFormLayout(self)
        self.ros_version_desctiption = QtWidgets.QLabel()
        form_layout.addRow(QtWidgets.QLabel("Select ROS version:"), self.ros_versions_dropdown)
        form_layout.addRow(
            QtWidgets.QLabel(''),
            QtWidgets.QLabel(
                'Tip: choosen ROS version will be used to checkout ros2_controllers repository\n'
                'and forming related controllers forms.\n'
                'Use ROS version you plan to code generation for. It will update only new controllers.\n'
                'Controllers added earlier will retain their own version. Delete them and create new ones if required.',
            ),
        )
        # update ros controllers to choosen ros version
        updateControllersToROSversionBotton = QtGui.QPushButton('Update ros controllers to choosen ros version', self)
        updateControllersToROSversionBotton.clicked.connect(self.updateControllersToROSversionBotton)
        updateControllersToROSversionBotton.setAutoDefault(False)
        form_layout.addRow(QtWidgets.QLabel(""), updateControllersToROSversionBotton)
        # add form to ros_versions box
        formGroupBoxRosVersions.setLayout(form_layout)


        # attach triggers of changing descriptions
        self.controllers_dropdown.currentTextChanged.connect(self.update_controller_description)

        # add controllers adding button
        addControllerButton = QtGui.QPushButton('Add controller to project', self)
        addControllerButton.clicked.connect(self.onAddControllerButton)
        addControllerButton.setAutoDefault(False)

        # add broadcasters adding button
        addBroadcasterButton = QtGui.QPushButton('Add broadcaster to project', self)
        addBroadcasterButton.clicked.connect(self.onAddBroadcasterButton)
        addBroadcasterButton.setAutoDefault(False)

        # controllers block
        formGroupBox = QtWidgets.QGroupBox("Controllers")
        form_layout = QtWidgets.QFormLayout(self)
        self.controller_desctiption = QtWidgets.QLabel()
        form_layout.addRow(QtWidgets.QLabel("Select controller:"), self.controllers_dropdown)
        form_layout.addRow(QtWidgets.QLabel("Description:"), self.controller_desctiption)
        form_layout.addRow(QtWidgets.QLabel(""), addControllerButton)
        form_layout.addRow(
            QtWidgets.QLabel(''),
            QtWidgets.QLabel(
                'Tip: controllers chaining is posible by adding target controller to property (with other linked objects).\n'
                'Only some controllers and properties can be chained, RobotCAD does not check correctness of chaining.\n'
                'See docs to know where chain is applicable.',
            ),
        )
        formGroupBox.setLayout(form_layout)

        # brodcasters block
        formGroupBox1 = QtWidgets.QGroupBox("Broadcasters")
        form_layout = QtWidgets.QFormLayout(self)
        self.broadcaster_desctiption = QtWidgets.QLabel()
        form_layout.addRow(QtWidgets.QLabel("Select broadcaster:"), self.broadcasters_dropdown)
        form_layout.addRow(QtWidgets.QLabel("Description:"), self.broadcaster_desctiption)
        form_layout.addRow(QtWidgets.QLabel(""), addBroadcasterButton)
        formGroupBox1.setLayout(form_layout)

        # link to docks
        weblink = QtWidgets.QLabel()
        weblink.setText("<a href='https://control.ros.org/rolling/doc/ros2_controllers/doc/controllers_index.html'>ros2_controllers docs</a>")
        weblink.setTextFormat(QtCore.Qt.RichText)
        weblink.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        weblink.setOpenExternalLinks(True)


        # interfaces property setter
        formGroupBox2 = QtWidgets.QGroupBox("Interfaces property setter")
        form_layout = QtWidgets.QFormLayout(self)
        formGroupBox2.setLayout(form_layout)
        self.listControllersInterfaces = QtGui.QListWidget()
        self.listControllersInterfaces.setSelectionMode(QtGui.QAbstractItemView.MultiSelection) # 3 - MultipleSelection
        for interface in wb_constants.ROS2_CONTROLLERS_INTERFACES:
            self.listControllersInterfaces.addItem(QtGui.QListWidgetItem(interface))
        form_layout.addRow(QtWidgets.QLabel("Select interfaces:"), self.listControllersInterfaces)
        form_layout.addRow(
            QtWidgets.QLabel('Description:'),
            QtWidgets.QLabel(
                'Select required interfaces for selected interface property of controller or broadcaster.\n'
                'Seleted interface property means current selected in Comboview (Model) Data tab of added controller or broadcaster.\n'
                'It is just a helper for setting interfaces for interface properties of controllers and broadcasters.\n'
                '\n'
                'Interfaces used to communicate with hardware or simulation. \n'
                'Controller <-> interface <-> hardware/simulation. See ros2_control documentaion.',
            ),
        )
        setInterfacesButton = QtGui.QPushButton('Add interfaces to selected property', self)
        setInterfacesButton.clicked.connect(self.onSetInterfacesToPropertyButton)
        setInterfacesButton.setAutoDefault(False)
        form_layout.addRow(QtWidgets.QLabel(""), setInterfacesButton)
        formGroupBox2.setLayout(form_layout)
        # add interfaces adding button


        # adding widgets to main layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(formGroupBox)
        main_layout.addWidget(formGroupBox1)
        main_layout.addWidget(formGroupBox2)
        main_layout.addWidget(formGroupBoxRosVersions)
        main_layout.addWidget(weblink)
        self.setLayout(main_layout)


        # init current state of controllers and brodcaster desctiptions
        self.update_controller_description(self.controllers_dropdown.currentText())
        self.update_broadcaster_description(self.broadcasters_dropdown.currentText())


        self.show()


    def update_controller_description(self, text):
        index = self.controllers_dropdown.findText(text)
        description = self.controllers_dropdown.itemData(index)
        self.controller_desctiption.setText(description)


    def update_broadcaster_description(self, text):
        index = self.broadcasters_dropdown.findText(text)
        description = self.broadcasters_dropdown.itemData(index)
        self.broadcaster_desctiption.setText(description)


    def onSetInterfacesToPropertyButton(self):
        if is_controller_selected() or is_broadcaster_selected():
            doc = fc.activeDocument()
            doc.openTransaction('Set Interfaces to property')

            selected_interfaces = [item.text() for item in self.listControllersInterfaces.selectedItems()]
            props, objects = getSelectedPropertiesAndObjectsInTreeView()

            if not props:
                message('Select property of controller or broadcaster', gui = True)

            # set selected interface to all selected properties of all selected objects
            for object in objects:
                for prop in props:
                    if hasattr(object['object'], prop['full_name']):
                        try:
                            setattr(object['object'], prop['full_name'], selected_interfaces)
                        except TypeError:
                            if len(selected_interfaces):
                                setattr(object['object'], prop['full_name'], selected_interfaces[0])
                            else:
                                setattr(object['object'], prop['full_name'], '')

            doc.commitTransaction()
            doc.recompute()
        else:
            message('Select property of controller or broadcaster', gui = True)


    def onAddControllerButton(self):
        if is_robot_selected():
            doc = fc.activeDocument()
            doc.openTransaction('Add Controller')

            name = str(self.controllers_dropdown.currentText())
            controller = make_controller(self.controllers['controllers'][name])
            robot = fcgui.Selection.getSelection()[0]
            robot.addObject(controller)

            doc.commitTransaction()
            doc.recompute()
        else:
            message('Select robot container first', gui = True)


    def updateControllersToROSversionBotton(self):
        # close window
        self.close()
        # update controllers submodule
        ros_version = next((el for el in self.ros_versions if el['ros_version'] == self.ros_versions_dropdown.currentText()), None)
        git_change_submodule_branch(
            module_path = 'modules/ros2_controllers',
            branch = ros_version['controllers_branch'],
        )
        # save choosen ros version
        set_workbench_param(wb_constants.ROS2_CONTROLLERS_CURRENT_ROS_VERSION_PARAM_NAME, ros_version['ros_version'])
        # open new window
        form = ControllersSelectorModalClass()
        form.exec_()


    def onAddBroadcasterButton(self):
        if is_robot_selected():
            doc = fc.activeDocument()
            doc.openTransaction('Add Broadcaster')

            name = str(self.broadcasters_dropdown.currentText())
            broadcaster = make_broadcaster(self.controllers['broadcasters'][name])
            robot = fcgui.Selection.getSelection()[0]
            robot.addObject(broadcaster)

            doc.commitTransaction()
            doc.recompute()
        else:
            message('Select robot container first', gui = True)
