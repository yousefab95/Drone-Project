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

        self.toolbar = self.iface.addToolBar(u'Mission Planner')
        self.toolbar.setObjectName(u'Mission Planner')
        # store layer id
        self.layerid = ''

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

    def clickHandler(self, event):
        self.counter = self.counter + 1     #increment the coutner of points
        if not QgsMapLayerRegistry.instance().mapLayer(self.layerid) :
            layerName = "Mission"
            # Specify the geometry type
            self.layer = QgsVectorLayer('Point?crs=epsg:3857', layerName , 'memory')
            self.provider = self.layer.dataProvider()

            # add fields
            self.provider.addAttributes( [QgsField("count", QVariant.Double)] )
            self.layer.updateFields()
            self.provider.addAttributes( [QgsField("mission", QVariant.String)] )
            self.layer.updateFields()
            self.provider.addAttributes( [QgsField("Lat", QVariant.Double)] )
            self.layer.updateFields()
            self.provider.addAttributes( [QgsField("Lon", QVariant.Double)] )
            self.layer.updateFields()         

            # Labels on
            label = self.layer.label()
            label.setLabelField(QgsLabel.Text, 0) 
            self.layer.enableLabels(True)
            
            self.layer.updateFields()
            # Add the layer to the Layers panel
            QgsMapLayerRegistry.instance().addMapLayer(self.layer)
            # store layer id
            self.layerid = QgsMapLayerRegistry.instance().mapLayers().keys()[-1]
     
        # Add a new feature and assign the geometry
        feat = QgsFeature()
        self.feat = feat
        x = event.x()
        y = event.y()
        point = QgsPoint(x,y)
        feat.setGeometry(QgsGeometry.fromPoint(point))

        #Convert point coordinates to latlon
        canvasCRS = self.canvas.mapSettings().destinationCrs()
        if canvasCRS == self.epsg4326:
            pt4326 = point
        else:
            transform = QgsCoordinateTransform(canvasCRS, self.epsg4326)
            pt4326 = transform.transform(point.x(), point.y())      

        #Set attributes for the point feature
        feat.initAttributes(4)
        feat[0] = self.counter  #Order of points
        feat[1] = "mission"     #Label of points
        feat[2] = pt4326.y()    #Latitude of point
        feat[3] = pt4326.x()    #Longitude of point

        self.provider.addFeatures( [ feat ] )  #adds feature to the layer
        
        # Update extent of the layer
        self.layer.updateExtents()
                
        self.layer.triggerRepaint()
        self.dlg.comBtn.clicked.connect(lambda : self.completeMission()) #Complete creation of mission

    def clickToolActivator(self, counter):
        self.clickTool = QgsMapToolEmitPoint(self.canvas) #clicktool instance generated in here.
        self.clickTool.canvasClicked.connect(self.clickHandler)
        self.canvas.setMapTool(self.clickTool) #clickTool is activated

    def completeMission(self):
        self.canvas.unsetMapTool(self.clickTool) #Close click tool
        self.points = self.provider.getFeatures()
        point1 = self.points.nextFeature(self.feat)
        point2 = self.points.nextFeature(self.feat)
        self.verticies = [point1, point2]
        layerName = "Paths"
        # Specify the geometry type
        lay = QgsVectorLayer('Point?crs=epsg:3857', layerName , 'memory')
        prov = self.layer.dataProvider()
        lay.updateFields()
        # Add the layer to the Layers panel
        QgsMapLayerRegistry.instance().addMapLayer(lay)
        fet = QgsFeature()
        #for loop to connect points with lines
        #self.verticies = [QgsPoint(start[1], start[2]), QgsPoint(end[1], end[2])]
        fet.setGeometry(QgsGeometry.fromPolyline(self.verticies))
        prov.addFeatures( [ fet ] )
        lay.updateExtents()
        lay.triggerRepaint()

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
        self.epsg4326 = QgsCoordinateReferenceSystem('EPSG:4326')
        # Set project coordinate reference system to WGS84: 3857
        self.iface.mapCanvas().mapRenderer().setProjectionsEnabled(True) # Enable on the fly reprojections
        self.iface.mapCanvas().mapRenderer().setDestinationCrs(QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.PostgisCrsId))

        #initialize counter and GUI
        self.counter = 0    #counts the number of points
        self.canvas = self.iface.mapCanvas()
        self.dlg = MissionPlannerDialog()
        self.dlg.setFixedSize(self.dlg.size())
        marker = 'http://bit.ly/aUwrKs'
        self.dlg.runBtn.clicked.connect(lambda : self.clickToolActivator(self.counter))

        self.dlg.show()
        self.canvas.refresh()
