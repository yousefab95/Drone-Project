# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MissionPlanner
                                 A QGIS plugin
 Plan missions for automated drone control
                              -------------------
        begin                : 2018-02-11
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Alex Cone'
        email                : alexcone@live.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.gui import *
from qgis.core import *
from mission_planner_dialog import *
import os,urllib2

class MissionPlanner:
    pointCount = 0
    def __init__(self, iface):
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Mission Planner')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Mission Planner')
        self.toolbar.setObjectName(u'Mission Planner')

    def tr(self, message):
        return QCoreApplication.translate('Mission Planner', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
   

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        icon_path = self.plugin_dir + os.sep + 'icon.png'

        self.add_action(
            icon_path,
            text=self.tr(u'Mission Planner'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def toolActivator(self, QLineEdit):
        # self.dlg.showMinimized()
        global whichTextBox
        whichTextBox = QLineEdit #I find this way to control it
        self.clickTool.canvasClicked.connect(self.clickHandler)
        self.canvas.setMapTool(self.clickTool) #clickTool is activated

    def clickHandler(self, event):
        layerName = "point"
        # Specify the geometry type
        layer = QgsVectorLayer('Point?crs=epsg:4326', layerName , 'memory')
         
        # Set the provider to accept the data source
        prov = layer.dataProvider()
           
        # Add a new feature and assign the geometry
        feat = QgsFeature()

        x = event.x()
        y = event.y()
        point = QgsPoint(x,y)
        #point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        

        feat.setGeometry(QgsGeometry.fromPoint(point))
        prov.addFeatures([feat])
         
        # Update extent of the layer
        layer.updateExtents()
         
        # Add the layer to the Layers panel
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        self.dlg.showNormal()
        self.canvas.show()
        self.canvas.unsetMapTool(self.clickTool) #Close click tool

    def clickToolActivator(self, pointCount):
        self.clickTool = QgsMapToolEmitPoint(self.canvas) #clicktool instance generated in here.
        self.clickTool.canvasClicked.connect(self.clickHandler)
        self.canvas.setMapTool(self.clickTool) #clickTool is activated

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Mission Planner'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def run(self):
        pointCount = 0
        # self.routeEngine = RouteProvider()
        self.canvas = self.iface.mapCanvas()
        self.dlg = MissionPlannerDialog()
        self.dlg.setFixedSize(self.dlg.size())
        marker = 'http://bit.ly/aUwrKs'
        # self.routeMaker(str(QgsPoint.x()) + ',' + str(QgsPoint.y()))
        # self.dlg.startBtn.clicked.connect(lambda : self.toolActivator(self.dlg.startTxt))
        # self.dlg.stopBtn.clicked.connect(lambda : self.toolActivator(self.dlg.stopTxt))
        self.dlg.runBtn.clicked.connect(lambda : self.clickToolActivator(pointCount))

        self.dlg.show()
