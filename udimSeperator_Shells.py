""" 
Script Name: udimSeperator.py
Author: Ram Yogeshwaran
Company: The Mill
Contact: Ram.Yogeshwaran@themill.com
Description: This script is used to seperate a geo based on all the UDIMS present inside it
"""
import maya.cmds as cmds
import maya.mel as mel
from PySide2 import QtCore,QtGui,QtWidgets
import maya.OpenMaya as om 
import pprint
import logging
import time 

#create custom Exception
class UVShellError(Exception):
    pass

# Set up the logger
logger = logging.getLogger("UDIM Seperator")

# Manually check if there are handlers, and remove them if necessary
if len(logger.handlers) > 0:
    del logger.handlers[:]  # Clear the handlers list by deleting all its elements

# Create a StreamHandler to output logs to Maya's Script Editor
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)

# Create a formatter and set it for the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(stream_handler)

class UDIM_SEPERATOR(QtWidgets.QWidget):
    """
    This is a UDIM_SEPERATOR class that lets us create the UI for this tool 
    
    Methods:
        __init__: This is the Constructor function to initialize all the necessary variables ,and call the build_UI method
        build_UI: This method builds the UI for the tool and makes respective connections 
        main : This is the main function that contains the main functionality to call other methods
        get_udim_shells : This is the function that returns a dictionary of all the shells in the passed geometry based on the UDIM
        split_mesh_into_udims: This function splits a mesh into multiple meshes based on UDIMs defined in the tiles_faces_dict.
    """
    def __init__(self):
        """ 
        This is the Constructor function to initialize all the necessary variables ,and call the build_UI method
            
        Args:
            None
        Returns:
            None
        """
        super(UDIM_SEPERATOR,self).__init__() #call the parent init class for the QWidget class
        self.build_UI()

    def build_UI(self):
        """ 
        This method builds the UI for the tool and makes respective connections.

        Args:
            None
        Returns:
            None
        """
        #set size 
        self.setMinimumSize(600,120)

        #set the window title
        self.setWindowTitle("UDIM Seperator")

        #set always on top
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)

        #bold font
        bold_font = QtGui.QFont()
        bold_font.setBold(True)

        #progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setFont(bold_font)
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_bar.setStyleSheet("QProgressBar {border: 0px;} QProgressBar::chunk {background-color: rgb(0, 150, 200);};")
        self.progress_bar.setValue(0) #reset progress

        #status label
        self.status_label = QtWidgets.QLabel("Please select a mesh or multiple meshes to seperate") 

        #create layout
        self.main_layout = QtWidgets.QGridLayout()

        #add button
        seperate_btn = QtWidgets.QPushButton("Seperate selected object(s)")

        #set  and add to layout
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(seperate_btn,0,0)
        self.main_layout.addWidget(self.progress_bar,1,0)
        self.main_layout.addWidget(self.status_label,2,0)

        #connections
        seperate_btn.clicked.connect(self.main)

    def main(self):
        """
        This is the main function that contains the main functionality to call other methods.
        
        Args:
            None
        Returns:
            None
        """
        start_time = time.time()  # Record the start time

        #progress bar settings
        self.progress_bar.setValue(0) #reset progress
        self.progress_bar.setStyleSheet("QProgressBar {border: 0px;} QProgressBar::chunk {backgrouand-color: rgb(0, 150, 200);};")

        #status label addition
        message = ""
        self.status_label.setText(message)



        #check for selection
        if cmds.ls(sl=True):
            
            selected_items = cmds.ls(sl=True) #store selection

            logger.debug(selected_items)

            # Flatten the list of all meshes in the selection, including those within groups
            all_selected_meshes = []

            for item in selected_items:
                
                # Find all mesh objects in the hierarchy (including groups)
                all_meshes = cmds.listRelatives(item, allDescendents=True, type="mesh", fullPath=True) or []

                # Remove any intermediate objects (if they exist)
                all_meshes = [mesh for mesh in all_meshes if not cmds.getAttr("{0}.intermediateObject".format(mesh))]

                logger.debug("Removed Intermediates: "+ str(all_meshes))

                all_meshes = [cmds.listRelatives(mesh, parent=True, fullPath=True)[0] for mesh in all_meshes]  # get parent transform nodes

                if not all_meshes:
                    logger.info("Skipping {} as it contains no meshes.".format(item))
                    skipped_objects += 1
                    continue

                all_selected_meshes.extend(all_meshes)
                

            logger.debug("Selected Meshes: "+ str(all_selected_meshes))

            total_steps = len(all_selected_meshes) #total steps for progress

            i=0 #tracker for iterations
            udim_meshes = [] #tracker for number of objects with udims
            seperated_meshes=0 #tracker for seperated objects
            skipped_objects = 0 #tracker for skipped meshes
            

            #iterate through all the meshes
            for mesh in all_selected_meshes:
                
                #start label
                shells_message = "Initializing Shells Check..."
                if i == 0:
                    self.status_label.setText(shells_message)
                    self.progress_bar.setValue(1) #start progress
                else:
                    self.status_label.setText(self.status_message+"\n"+shells_message) #go to next line

                i=i+1 #add the step counter
                                    #update label
                self.status_message = "Status : {0}/{1} | Current Object : {2} | Seperated Objects : {3} | Skipped Objects: {4}".format(str(i),str(total_steps),mesh.split('|')[-1], str(seperated_meshes),str(skipped_objects))
                self.status_label.setText(self.status_message)

                shape_node = cmds.listRelatives(mesh, shapes=True) #go inside the transform node

                if not shape_node:
                    #error out in the UI
                    message = "Found an Invalid Selection "
                    self.status_label.setText(message)

                    om.MGlobal.displayWarning("Found an Invalid Selection ")
                    return

                try:
                    node_type = cmds.nodeType(shape_node[0]) #node type of shape
                    logging.debug(node_type)
                    if node_type == "mesh":
                        tiles_shells_dict = self.get_udim_shells(mesh)

                        if len(tiles_shells_dict.keys())==1:
                            logger.info("Skipping {0} since there is only one single UDIM".format(mesh))
                            #update tracker  
                            skipped_objects+=1

                        else:
                            
                            #set the message in UI
                            mesh_message = "Initializing Mesh Split..."
                            if i ==0:
                                self.status_label.setText(mesh_message)
                            else:
                                self.status_label.setText(self.status_message+"\n"+mesh_message) #go to next line


                            QtWidgets.QApplication.processEvents() #force the GUI updates

                            self.split_mesh_into_udims(mesh,tiles_shells_dict) #split the mesh
                            #update tracker
                            seperated_meshes+=1
                            udim_meshes.append(mesh)
                    
                    else:
                        logger.info("Skipping since {0} is not a mesh".format(mesh.split('|')[-1]))
                        skipped_objects+=1

                except UVShellError:
                    #update progressbar
                    self.progress_bar.setValue(100)
                    self.progress_bar.setStyleSheet("QProgressBar {border: 0px;} QProgressBar::chunk {background-color: rgb(200, 0, 0);};")

                    #update label
                    error_message = "UV Error: There is a shell that is spanning across UDIMS in {0} (Check log)".format(mesh.split('|')[-1])
                    self.status_label.setText(error_message)

                    return
                except RuntimeError:
                    logger.error("There was a RunTime error while Trying to Split".format(mesh.split('|')[-1]))
                except:
                    logger.error("There seems to be an error in the mesh/UV".format(mesh.split('|')[-1]))
                    skipped_objects+=1


                #update label
                self.status_message = "Status : {0}/{1} | Current Object : {2} | Seperated Objects : {3} | Skipped Objects: {4}".format(str(i),str(total_steps),mesh.split('|')[-1], str(seperated_meshes),str(skipped_objects))
                self.status_label.setText(self.status_message)

                #update progress bar
                progress_value = int((float(i) / total_steps) * 100)
                self.progress_bar.setValue(progress_value)#set the value


            #set final label   
            self.status_message = "Status : {0}/{1} | Last Selected Object : {2} | Seperated Objects : {3} | Skipped Objects: {4}".format(str(i),str(total_steps),mesh.split('|')[-1], str(seperated_meshes),str(skipped_objects))
            add_message = "\nTotal UDIM objects found : "+str(len(udim_meshes))
            
            self.status_label.setText(self.status_message+add_message)
            


        else:
            #error out in the UI
            message = "Nothing is selected"
            self.status_label.setText(message)

            om.MGlobal.displayError("Please select a mesh to seperate")
            raise RuntimeError("Please select a mesh to seperate")

        #LOG the FINAL OUTPUT
        end_time = time.time()  # Record the end time
        elapsed_time = (end_time - start_time) / 60  # Calculate the time taken
        logger.info("Function completed in {0:.2f} minutes".format(elapsed_time))  # Log the time taken

    def get_udim_shells(self,geometry):
        """
        This is the function that returns a dictionary of all the shells in the passed geometry based on the UDIM
        
        Args:
            geometry: mesh to determine the UDIMS
        Returns:
            udim_shells_dict : a dictionary containing the UDIM and shells data of the passed geometry
        """
        # Ensure the input geometry is valid
        if not cmds.objExists(geometry):
            raise ValueError("{0} Geometry does not exist.".format(geometry))

        # Get the total number of UV shells
        shell_count = cmds.polyEvaluate(geometry, uvShell=True)
        
        #update the UI


        # Initialize a dict to store UV shells
        uv_shells = {} 
        
        # Iterate over each shell ID to retrieve its UVs 
        for shell_id in range(shell_count):
            # Query the UVs in the current shell
            uv_shell = cmds.polyEvaluate(geometry, uvsInShell=shell_id)
            uv_shells[shell_id]=uv_shell #format {0:'obj.map[1:20],'obj..'...'}
        
        
        # Dictionary to store UDIM tile number and UV Shells
        udim_shells_dict = {} 

        # Iterate over each shells
        for shell_id,shell_uvs in uv_shells.items():

            message = "Analyzing UV Shells: ({0}/{1})".format(shell_id+1,shell_count)

            self.status_label.setText(self.status_message+"\n"+message)
            QtWidgets.QApplication.processEvents() #force the GUI updates
            
            #calculate the bouding box
            bbox = cmds.polyEvaluate(shell_uvs,bc2=True) #return (umin,umax)(vmin,vmax)
            logger.debug("Calculating Bounding box of shell: {} ".format(shell_uvs))
            
            # Tracker to see if all UVs belong to the same UDIM tile
            uv_udim = None
            shell_in_single_udim = True
            
            #store the correct coordinates from the bounding box return value
            minimum_coord = (bbox[0][0],bbox[1][0]) #save only the minimum coordinate (u,v)
            maximum_coord = (bbox[0][1],bbox[1][1])
            
            #make a list out of it
            coord_to_check = [minimum_coord,maximum_coord]

            logger.debug("Checking if the above shells exist in single UDIM")

            # Loop over the above list to check UDIM tiles
            for uv_coord in coord_to_check:
                
                u_coord, v_coord = uv_coord[0], uv_coord[1]

                # Determining UDIM tile
                
                #integer conversion to get the whole number
                u_tile = int(u_coord) 
                v_tile = int(v_coord)

                current_udim = 1001 + u_tile+ (v_tile * 10) #UDIM Tile number formula 1001+(10×V_tile)+(U_tile)

                # On first UV, initialize the UDIM
                if uv_udim is None:
                    uv_udim = current_udim
                # If UVs don't match the first UV's UDIM, this shell crosses UDIMs
                elif current_udim != uv_udim:
                    shell_in_single_udim = False
                    break

            # If all UVs are in the same UDIM, append this shell to the dictionary
            if shell_in_single_udim:
                if uv_udim not in udim_shells_dict:
                    udim_shells_dict[uv_udim] = []
                udim_shells_dict[uv_udim].extend(shell_uvs)
                logging.debug("Added shell to {0} in the dictionary".format(str(uv_udim)))
            else:
                #select the incorrect shell
                cmds.select(cl=True)
                cmds.select(shell_uvs)

                #error it out
                om.MGlobal.displayError("There is a shell that is spanning across UDIMS (check {0})".format(current_udim))
                raise UVShellError("There is a shell that is spanning across UDIMS (check {0})".format(current_udim))
                return None

        return udim_shells_dict

    def split_mesh_into_udims(self,mesh,tiles_shells_dict):
        """
        This function splits a mesh into multiple meshes based on UDIMs defined in the tiles_shells_dict.

        Args:
            mesh (str): The name of the original mesh to split.
            tiles_faces_dict (dict): Dictionary with UDIMs as keys and lists of face strings as values.
        Returns:
            None
        """
        logger.info("Splitting "+mesh.split('|')[-1])

        # Create a list to hold the new mesh names
        new_meshes = [] 

        mesh_name = mesh.split('|')[-1] #get only the last name
        
        #trackers for GUI Updates
        total_count = len(tiles_shells_dict.keys())
        i = 1 
        # Iterate through the udim dictionary
        for udim, uv_shells in tiles_shells_dict.items():
            message = "Splitting Mesh: ({0}/{1})".format(i,total_count)
            self.status_label.setText(self.status_message+"\n"+message)
            QtWidgets.QApplication.processEvents() #force the GUI updates
            
            #set suffix for duplicates
            if "_render_GEO" in mesh: #if there is already a suffix
                new_mesh_name = "{0}_{1}_render_GEO".format(mesh_name.split("_render")[0], udim)
                
            else:
                suffix = "_render_GEO"
                new_mesh_name = "{0}_{1}".format(mesh_name, udim)+suffix

            #get only the map[1],map[2]... list
            only_uvs_list = []
            for original_uv_shell in uv_shells:
                only_uvs_list.append(original_uv_shell.split('.')[-1])
            

            # Duplicate the original mesh
            new_mesh = cmds.duplicate(mesh,name = new_mesh_name)[0]  # Get the new mesh name

            shells_to_be_kept = []

            #build the new shells list
            for uv_shell in only_uvs_list:
                shells_to_be_kept.append(new_mesh_name+"."+uv_shell)

            #convert the uvs to faces
            faces_to_be_kept = cmds.polyListComponentConversion(shells_to_be_kept, toFace=True)

            #clear selection
            cmds.select(cl=True)

            #selec the appropriate faces
            cmds.select(faces_to_be_kept)  
            cmds.select(new_mesh_name+".f[*]", tgl=True) #invert selection
            cmds.delete() 

            # Add the new mesh to the list
            new_meshes.append(new_mesh_name)

            logger.info("Created mesh: {0} with shells: {1}".format(new_mesh_name, str(uv_shells))) 

            #update Tracker
            i+=1
        # Create a new group for the split meshes
        group_name = "{}_GRP".format(mesh_name.split("_render")[0])
        cmds.group(new_meshes, name=group_name)

        # Delete the original mesh
        cmds.delete(mesh)
        logger.info("Deleted original mesh: {0}".format(mesh.split('|')[-1]))

#make instance of the main class and show it
UV_window = UDIM_SEPERATOR()
UV_window.show()
