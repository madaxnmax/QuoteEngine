import torch
import dgl
import numpy as np
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_EDGE
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface, BRepAdaptor_Curve
from OCC.Core.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder, GeomAbs_Cone, GeomAbs_Sphere, GeomAbs_Torus, GeomAbs_BezierSurface, GeomAbs_BSplineSurface
from OCC.Core.BRepGProp import brepgprop_SurfaceProperties, brepgprop_LinearProperties
from OCC.Core.GProp import GProp_GProps
from OCC.Core.BRep import BRep_Tool
from OCC.Core.GeomLProp import GeomLProp_SLProps
from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Dir

def step_to_graph(step_file_path):
    """
    Reads a STEP file and converts it into a DGL graph with features compatible with BrepMFR.
    """
    reader = STEPControl_Reader()
    status = reader.ReadFile(step_file_path)
    if status != 1:
        raise ValueError("Error reading STEP file")
    
    reader.TransferRoots()
    shape = reader.OneShape()
    
    # 1. Extract Faces (Nodes)
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    faces = []
    while explorer.More():
        faces.append(explorer.Current())
        explorer.Next()
        
    num_nodes = len(faces)
    
    # 2. Extract Edges (Edges) and build adjacency
    # This is a simplified adjacency extraction. 
    # In a real B-Rep graph, we need to find which faces share which edges.
    # We can use a map of Edge -> [Faces] to build the graph.
    
    from OCC.Core.TopTools import TopTools_IndexedDataMapOfShapeListOfShape
    from OCC.Core.TopExp import topexp_MapShapesAndAncestors
    
    edge_face_map = TopTools_IndexedDataMapOfShapeListOfShape()
    topexp_MapShapesAndAncestors(shape, TopAbs_EDGE, TopAbs_FACE, edge_face_map)
    
    src_nodes = []
    dst_nodes = []
    edge_features_list = []
    
    # Map face shape to index
    face_to_idx = {face: i for i, face in enumerate(faces)}
    
    for i in range(1, edge_face_map.Extent() + 1):
        edge = edge_face_map.FindKey(i)
        connected_faces = edge_face_map.FindFromIndex(i)
        
        if connected_faces.Extent() == 2:
            # Manifold edge shared by 2 faces
            it = connected_faces.Iterator()
            face1 = it.Value()
            it.Next()
            face2 = it.Value()
            
            idx1 = face_to_idx[face1]
            idx2 = face_to_idx[face2]
            
            # Add bidirectional edges
            src_nodes.extend([idx1, idx2])
            dst_nodes.extend([idx2, idx1])
            
            # Compute edge features (simplified for now)
            # We need 6 channels: x, y, z, tx, ty, tz sampled along the curve
            # For now, we'll use a placeholder or simplified sampling
            edge_feat = compute_edge_features(edge)
            edge_features_list.append(edge_feat)
            edge_features_list.append(edge_feat) # Same feature for reverse edge?
            
    # 3. Compute Node Features (Face UV Grids)
    node_features_list = []
    for face in faces:
        node_feat = compute_face_features(face)
        node_features_list.append(node_feat)
        
    # 4. Build DGL Graph
    g = dgl.graph((src_nodes, dst_nodes), num_nodes=num_nodes)
    
    # Stack features
    # Node features: [num_nodes, 64, 64, 7]
    node_features_tensor = torch.stack(node_features_list)
    g.ndata['x'] = node_features_tensor
    
    # Edge features: [num_edges, 64, 6] (Assuming 64 sample points for edges too?)
    # The model code expects edge features. Let's check dimensions in model code again if needed.
    # CurveEncoder in feature_encoders.py takes in_channels=6.
    if edge_features_list:
        edge_features_tensor = torch.stack(edge_features_list)
        g.edata['x'] = edge_features_tensor
    else:
        # Handle case with no edges (single face?)
        pass
        
    return g

def compute_face_features(face, grid_size=64):
    """
    Samples a 64x64 UV grid on the face.
    Returns tensor of shape [64, 64, 7]
    Channels: x, y, z, nx, ny, nz, mask
    """
    surf_adaptor = BRepAdaptor_Surface(face)
    u_min, u_max, v_min, v_max = surf_adaptor.FirstUParameter(), surf_adaptor.LastUParameter(), surf_adaptor.FirstVParameter(), surf_adaptor.LastVParameter()
    
    features = torch.zeros((grid_size, grid_size, 7))
    
    for i in range(grid_size):
        u = u_min + (u_max - u_min) * i / (grid_size - 1)
        for j in range(grid_size):
            v = v_min + (v_max - v_min) * j / (grid_size - 1)
            
            pnt = gp_Pnt()
            vec_u = gp_Vec()
            vec_v = gp_Vec()
            
            surf_adaptor.D1(u, v, pnt, vec_u, vec_v)
            
            # Normal
            normal = gp_Vec()
            try:
                # Cross product of tangents gives normal
                normal = vec_u.Crossed(vec_v)
                normal.Normalize()
            except:
                normal = gp_Vec(0, 0, 1) # Fallback
                
            # Check if point is inside face boundaries (trimming)
            # This requires a classifier. For now, assume simple surfaces are full.
            # Ideally use BRepClass_FaceClassifier
            mask = 1.0 
            
            features[i, j, 0] = pnt.X()
            features[i, j, 1] = pnt.Y()
            features[i, j, 2] = pnt.Z()
            features[i, j, 3] = normal.X()
            features[i, j, 4] = normal.Y()
            features[i, j, 5] = normal.Z()
            features[i, j, 6] = mask
            
    return features

def compute_edge_features(edge, num_samples=64):
    """
    Samples points along the edge.
    Returns tensor of shape [num_samples, 6]
    Channels: x, y, z, tx, ty, tz
    """
    curve_adaptor = BRepAdaptor_Curve(edge)
    u_min, u_max = curve_adaptor.FirstParameter(), curve_adaptor.LastParameter()
    
    features = torch.zeros((num_samples, 6))
    
    for i in range(num_samples):
        u = u_min + (u_max - u_min) * i / (num_samples - 1)
        
        pnt = gp_Pnt()
        tangent = gp_Vec()
        
        curve_adaptor.D1(u, pnt, tangent)
        try:
            tangent.Normalize()
        except:
            tangent = gp_Vec(1, 0, 0)
            
        features[i, 0] = pnt.X()
        features[i, 1] = pnt.Y()
        features[i, 2] = pnt.Z()
        features[i, 3] = tangent.X()
        features[i, 4] = tangent.Y()
        features[i, 5] = tangent.Z()
        
    return features
