""" 
Script Name: uv3dDistribute.py
Author: Ram Yogeshwaran
Company: The Mill
Contact: Ram.Yogeshwaran@themill.com
Description: This script is used to layout already unwrapped meshes based on a specific 3D Axis (X or Z)
"""

import maya.cmds as cmds
from collections import OrderedDict
import pprint
import maya.mel as mel
from PySide2 import QtCore,QtGui,QtWidgets


class UV_Distribute(QtWidgets.QWidget):
    """
    This is a UV_Distribute class that lets us create the UI for this tool 
    
    Methods:
        __init__: This is the Constructor function to initialize all the necessary variables ,and call the build_UI method
        build_UI: This is the function that builds the basic window and connects the UI with their respective functions.
        clear_help: This function clears the help_label from the ui
        main: This is the main function that contains the main functionality to call other distribution methods.
        get_positions: This function gets all the object centers of all selected meshes and returns it
        sort_positions: This function sorts the positions dict, based on the direction of the axis 
        distribute_uvs: This function stacks all the selected meshes and distributes them in the UV viewport based on the distribution value 
        get_uv_shells: This function returns the list of UV shells for the given geometry 
        get_uv_shell_bbox: This function returns the list of UV shell's bounding box for the given geometry.
        move_uv_shell: This function moves the given UV shell by u_offset and v_offset left or right)

    """
    def __init__(self):
        """
            This is the Constructor function to initialize all the necessary variables ,and call the build_UI method
            
            Args:
                None
            Returns:
                None
        """
        super(UV_Distribute,self).__init__()
        self.build_UI()

    def build_UI(self):
        """
            This is the function that builds the basic window and connects the UI with their respective functions.

            Args:
                None
            Returns:
                None
        """
        #set title
        self.setWindowTitle("3D UV Distribute ")

        #set always on top
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)

        #main layout
        self.main_layout = QtWidgets.QGridLayout()
        
        #add labels
        axis_label = QtWidgets.QLabel("3D Axis :")
        shell_padding_label = QtWidgets.QLabel("Shell Padding :")

        #add dropdown box
        self.dropdown = QtWidgets.QComboBox()
        self.dropdown.addItem("X axis")
        self.dropdown.addItem("-X axis")
        self.dropdown.addItem("Z axis")
        self.dropdown.addItem("-Z axis")

        #add line edit
        self.distribute_value = QtWidgets.QLineEdit()
        self.distribute_value.setText("0.00") #default value

        validator = self.distribute_value.setValidator(QtGui.QDoubleValidator(decimals=3))
        #print(validator.decimals())
        #add button
        distribute_btn = QtWidgets.QPushButton("Distribute")

        #add to layouts
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(axis_label,0,0)
        self.main_layout.addWidget(self.dropdown,0,1)
        self.main_layout.addWidget(shell_padding_label,0,2)
        self.main_layout.addWidget(self.distribute_value,0,3)
        self.main_layout.addWidget(distribute_btn,0,4)

        #connections
        distribute_btn.clicked.connect(self.main)
        self.distribute_value.textChanged.connect(self.clear_help)

    def clear_help(self):
        """
            This function clears the help_label from the ui 

            Args:
                None
            Returns:
                None
        """
        try:
            self.help_label.destroy()
            self.help_label.deleteLater()
        except:
            pass

    def main(self):
        """
            This is the main function that contains the main functionality to call other distribution methods.
            
            Args:
                None
            Returns:
                None
        """
        #check for selection
        if cmds.ls(sl=True):
            
            selected_meshes = cmds.ls(sl=True) #store selection

            #get values
            selected_axis = self.dropdown.currentText()

            if '-' in self.dropdown.currentText():
                selected_direction = 0 
            else:
                selected_direction = 1

            selected_value = float(self.distribute_value.text())

            positions_dict = self.get_positions(selected_meshes,selected_axis) #call positions func and store it

            sorted_dict = self.sort_positions(positions_dict,selected_direction)

            #call the distribute func
            self.distribute_uvs(sorted_dict,value=selected_value)

            self.help_label = QtWidgets.QLabel("Successfully Laid out UVs")
            self.main_layout.addWidget(self.help_label,1,0,1,4)

        else:
            print("Nothing is selected")

            raise RuntimeError("Nothing selected")
        
    def get_positions(self,selection,axis):
        """
            This function gets all the object centers of all selected meshes and returns it
            
            Args:
                selection: a list of selected meshes
                axis : axis to determine the order of list
            Returns:
                mesh_positions : a dict containing the mesh names and their object centers.
        """
        mesh_positions ={} #empty dict to store the mesh and positions data

        for mesh in selection: #iterate through selection
            full_coordinates = cmds.objectCenter(mesh,gl=True)

            if 'Z' in axis:
                pos = full_coordinates[2] #get only z coordinate
            elif 'X' in axis:
                pos = full_coordinates[0] #get only x coordinate
            
            mesh_positions[mesh]= pos #append to dictionary

        return mesh_positions

    def sort_positions(self,positions_dict,direction):
        """
            This function sorts the positions dict, based on the direction of the axis 
            
            Args:
                positions_dict : input dictionary
                direction : 3d direction to sort the dictionary in . 
            Returns:
                sorted_positions : sorted version of positions dictionary based
        """
        # Sort in ascending order (left to right, or closer to farther along the X or Z axis)
        sorted_items = sorted(positions_dict.items(), key = lambda item: item[1], reverse=(direction == 0))

        # Convert the sorted list of tuples back to a dictionary
        sorted_positions = OrderedDict(sorted_items) #ordered dict, because dictionary by default is unordered

        return sorted_positions

    def distribute_uvs(self,sorted_dict,value):
        """
            This function stacks all the selected meshes and distributes them in the UV viewport based on the distribution value 

            Args:
                sorted_dict : input dictionary with proper order 
                value : value for shell padding
            Returns:
                None
        """
        #first stack all the shells
        mel.eval('texStackShells {};')

        #padding in tiles
        tile_padding = 0.005

        #Then Distribute it
        tile_size = [1.0-tile_padding,1.0-tile_padding]
        current_position = [tile_padding,tile_padding]  # Start distributing from U = 0 , v= 0
        max_row_height = 0

        #Iterate through each geometry in the provided order
        for geo in sorted_dict.keys():

            shells = self.get_uv_shells(geo)  # Get UV shells for the current geometry

            #error out and continue
            if not shells:
                print("Skipping " + geo+" since there are no UVs")
                continue

            for shell in shells:
                bbox_min_u, bbox_max_u , bbox_min_v , bbox_max_v = self.get_uv_shell_bbox(shell)  # Get u_coordinates of bounding box for the shell

                shell_width = bbox_max_u - bbox_min_u  # Calculate shell width

                # Update max_row_height based on the shell's bounding box
                shell_height = bbox_max_v - bbox_min_v 
                
                # Check if the current position exceeds the tile width
                if current_position[0]+shell_width > tile_size[0]:
                    # Move to the next row
                    current_position[0] =   (tile_size[0]-1+tile_padding)+tile_padding  # Reset U position
                    current_position[1] += max_row_height + value  # set V position by the height of the row
                    max_row_height = 0  # Reset max row height for the next row

                # Check if the current position exceeds the tile height
                if current_position[1]+shell_height>tile_size[1]:
                    tile_size = [tile_size[0]+1,tile_size[1]]
                    #move to next tile
                    current_position[0]+= 1
                    current_position[1] = tile_padding

                u_offset = current_position[0] - bbox_min_u  # Calculate how much to move the shell
                v_offset = current_position[1] - bbox_min_v  # set V position

                self.move_uv_shell(shell, u_offset,v_offset)  # Move the shell to its new position
                    
                current_position[0] += shell_width + value  # Update the current U position for the next shell

                
                max_row_height = max(max_row_height, shell_height)

            #print(current_position) #for development

        #select all the geos again
        cmds.select(cl=True) #clear selection
        for geo in sorted_dict.keys():
            cmds.select(geo,add= True)

    def get_uv_shells(self,geometry):
        """
            This function returns the list of UV shells for the given geometry.

            Args:
                geometry : geometry containing all the UV shells
            Returns:
                list of all the UV shells
        """
        cmds.select("{0}.map[*]".format(geometry))  # Select all UVs
        shell_ids = cmds.polyEvaluate(uvShell=True)  # Get the number of UV shells

        return ["{0}.map[*]".format(geometry) for i in range(shell_ids)]

    def get_uv_shell_bbox(self,shell):
        """
            This function returns the list of UV shell's bounding box for the given geometry.

            Args:
                shell : shell to calculate bbox for
            Returns:
                min_u: minimum value of U coordinate of bouding box
                max_u: maximum value of U coordinate of bouding box
                min_v: minimum value of V coordinate of bouding box
                max_v: maximum value of V coordinate of bouding box
        """

        cmds.select(shell)
        uvs = cmds.polyEvaluate(shell, boundingBox2d=True)  # Get the bounding box of the UVs
        min_u = uvs[0][0]  # minU coordinate
        max_u = uvs[0][1]  # maxU coordinate
        min_v = uvs[1][0] #minV coordinate
        max_v = uvs[1][1] #maxV coordinate

        return min_u, max_u , min_v , max_v

    def move_uv_shell(self,shell, u_offset,v_offset):
        """
            This function moves the given UV shell by u_offset and v_offset left or right)

            Args:
                shell : shell to perform move operatoin
                u_offset: offset value in U direction
                v_offset : offset value in V direction
            Returns:
                None
        """

        cmds.select(shell)
        cmds.polyEditUV(relative=True, u=u_offset,v=v_offset) #set the u to  calculated pos

#make instance of the main class and show it
UV_window = UV_Distribute()
UV_window.show()
