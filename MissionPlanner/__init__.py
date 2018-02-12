# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MissionPlanner
                                 A QGIS plugin
 Plan missions for automated drone control
                             -------------------
        begin                : 2018-02-11
        copyright            : (C) 2018 by Alex Cone'
        email                : alexcone@live.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load MissionPlanner class from file MissionPlanner.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .mission_planner import MissionPlanner
    return MissionPlanner(iface)
