from __future__ import annotations

import FreeCAD as fc

import FreeCADGui as fcgui

from ..gui_utils import tr
from ..wb_utils import rotate_origin, rotate_placement, set_placement_fast


# Stubs and type hints.
from ..joint import Joint
from ..link import Link
DO = fc.DocumentObject
CrossLink = Link
CrossJoint = Joint
LCS = DO  # Local coordinate systen, TypeId == "PartDesign::CoordinateSystem"


class _SetCROSSPlacementFastSensorCommand:
    """Command to set "Set placement - fast", and after use axis orietation correction for sensor (front of sensor is positive x-oriented).
    """

    def GetResources(self):
        return {
            'Pixmap': 'set_cross_placement_fast_sensor.svg',
            'MenuText': tr('Set placement - sensor'),
            'Accel': 'P, S',
            'ToolTip': tr(
                'Set the Origin of a joint and Mounted Placement of link.\n'
                '\n'
                'Select (with Ctlr): \n'
                '    1) subelement (face, edge, vertex, LCS) of body (of Real) of robot link (first reference)\n'
                '    2) subelement (face, edge, vertex, LCS) of body (of Real) of robot link (second reference)\n'
                '\n'
                'Works same way as "Set placement - fast", and after uses parent joint orietation correction for sensor link.\n'
                'Front of sensor is positive x-oriented (red arrow) of parent joint.\n'
                '\n'
                'It may be necessary to ajust MountedPlacement after.\n'
                'Use "Rotate joint/link" tool (select some face of sensor) or "Set placement - by orienteer" tool after that tool.\n',
            ),
        }

    def IsActive(self):
        return bool(fcgui.Selection.getSelection())

    def Activated(self):
        doc = fc.activeDocument()

        try:
            joint, child_link, parent_link = set_placement_fast()
            doc.recompute()
        except TypeError:
            return

        doc.openTransaction(tr("Rotate joint origin"))
        x = None
        y = 270
        z = None
        joint.Origin = rotate_placement(joint.Origin, x, y, z)
        doc.recompute()
        x = 270
        y = None
        z = None
        joint.Origin = rotate_placement(joint.Origin, x, y, z)
        doc.commitTransaction()
        doc.recompute()

        doc.openTransaction(tr("Rotate link MountedPlacement"))
        x = None
        y = None
        z = 90
        rotate_origin(x, y, z)
        doc.commitTransaction()
        doc.recompute()


fcgui.addCommand('SetCROSSPlacementFastSensor', _SetCROSSPlacementFastSensorCommand())
