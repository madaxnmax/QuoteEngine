import os
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.Interface import Interface_Static
from OCC.Core.TDocStd import TDocStd_Document
from OCC.Core.XCAFDoc import XCAFDoc_DocumentTool
from OCC.Core.STEPCAFControl import STEPCAFControl_Reader
from OCC.Core.RWGltf import RWGltf_CafWriter
from OCC.Core.TCollection import TCollection_ExtendedString
from OCC.Core.TDataStd import TDataStd_Name
from OCC.Core.TDF import TDF_LabelSequence

def convert_step_to_glb(step_file_path, output_dir):
    """
    Converts a STEP file to GLB format.
    """
    filename = os.path.basename(step_file_path)
    name_without_ext = os.path.splitext(filename)[0]
    glb_file_path = os.path.join(output_dir, f"{name_without_ext}.glb")
    
    # Create a document
    doc = TDocStd_Document(TCollection_ExtendedString("pythonocc-doc"))
    shape_tool = XCAFDoc_DocumentTool.ShapeTool(doc.Main())
    
    # Read STEP file with colors and names
    reader = STEPCAFControl_Reader()
    reader.SetNameMode(True)
    reader.SetColorMode(True)
    reader.ReadFile(step_file_path)
    reader.Transfer(doc)
    
    # Iterate over shapes to assign names if missing (Face_0, Face_1, etc.)
    # This is critical for matching with the inference graph.
    # Note: The order of faces here MUST match the order in step_to_graph.py
    
    labels = TDF_LabelSequence()
    shape_tool.GetFreeShapes(labels)
    
    # This part is tricky. XCAF structure is complex.
    # For a simple STEP file, we might just have one root shape.
    # We need to traverse the topological faces and assign names to them in the XCAF doc.
    
    # For now, we rely on the writer to export the mesh.
    # To ensure face matching, we might need to perform the meshing manually or 
    # use a specific traversal order that is deterministic.
    
    writer = RWGltf_CafWriter(glb_file_path, True) # True for binary GLB
    writer.Perform(doc, TDataStd_Name(TCollection_ExtendedString("test")))
    
    return glb_file_path
