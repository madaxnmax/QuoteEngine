import torch
import os
import sys

# Add BrepMFR to python path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../BrepMFR"))

from models.brepseg_model import BrepSeg
# from models.modules.utils.macro import * # Import macro if needed for label mapping

class InferenceEngine:
    def __init__(self, checkpoint_path):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.load_model(checkpoint_path)
        
    def load_model(self, checkpoint_path):
        if not os.path.exists(checkpoint_path):
            print(f"Warning: Checkpoint not found at {checkpoint_path}. Using random weights.")
            # Create a dummy args object if needed by BrepSeg.__init__
            class Args:
                num_classes = 25
                n_layers_encode = 4
                dim_node = 256
                d_model = 512
                n_heads = 8
                dropout = 0.1
                attention_dropout = 0.1
                act_dropout = 0.1
            
            model = BrepSeg(Args())
        else:
            model = BrepSeg.load_from_checkpoint(checkpoint_path)
            
        model.to(self.device)
        model.eval()
        return model

    def predict(self, graph):
        """
        Runs inference on a DGL graph.
        Returns a list of labels for each node (face).
        """
        # Prepare batch (single graph)
        # BrepMFR expects a specific batch structure. 
        # We might need to wrap the graph in a collator or manually create the batch dict.
        
        # Simplified prediction for now
        with torch.no_grad():
            # This part needs to match BrepMFR's input expectation exactly.
            # For now, we'll return dummy predictions if the graph structure isn't fully aligned yet.
            pass
            
        # Placeholder: Return random labels for testing
        num_nodes = graph.num_nodes()
        import random
        labels = ["Hole", "Slot", "Plane", "Cylinder", "Chamfer"]
        predictions = {f"Face_{i}": random.choice(labels) for i in range(num_nodes)}
        
        return predictions

# Singleton instance
# engine = InferenceEngine("checkpoints/best.ckpt")
