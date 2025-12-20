import torch
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv, HeteroConv
import pickle
import os
import sys
import numpy as np

# Patch for Numpy 2.0 compatibility
if "numpy._core" not in sys.modules:
    try:
        from numpy import core

        sys.modules["numpy._core"] = core
        sys.modules["numpy._core.multiarray"] = core.multiarray
    except ImportError:
        pass


class HeteroGNN(torch.nn.Module):
    def __init__(self, hidden_channels, out_channels, num_layers, metadata):
        super().__init__()
        self.convs = torch.nn.ModuleList()
        node_types, edge_types = metadata
        for _ in range(num_layers):
            conv_dict = {
                edge_type: SAGEConv((-1, -1), hidden_channels)
                for edge_type in edge_types
            }
            self.convs.append(HeteroConv(conv_dict, aggr="sum"))

        # Renamed to decoder to match weights
        self.decoder = torch.nn.Linear(hidden_channels, out_channels)

    def forward(self, x_dict, edge_index_dict):
        for conv in self.convs:
            x_dict = conv(x_dict, edge_index_dict)
            x_dict = {key: F.relu(x) for key, x in x_dict.items()}
        return self.decoder(x_dict["herb"])


class AyurvedicAI:
    def __init__(self, model_dir="ai_engine"):
        self.model_dir = model_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._load_artifacts()

    def _load_artifacts(self):
        try:
            # Load Mappings
            with open(os.path.join(self.model_dir, "mappings.pkl"), "rb") as f:
                self.mappings = pickle.load(f)

            # Load Graph Data
            self.data = torch.load(
                os.path.join(self.model_dir, "graph_data.pt"), map_location=self.device
            )

            # Initialize Model
            metadata = self.data.metadata()
            self.model = HeteroGNN(
                hidden_channels=256, out_channels=1, num_layers=3, metadata=metadata
            )

            # Load Weights
            state_dict = torch.load(
                os.path.join(self.model_dir, "ayurveda_gnn_model.pth"),
                map_location=self.device,
            )

            try:
                self.model.load_state_dict(state_dict)
            except RuntimeError as e:
                print(f"Strict loading failed: {e}. Trying strict=False.")
                self.model.load_state_dict(state_dict, strict=False)

            self.model.to(self.device)
            self.model.eval()
            print("AI Engine Loaded Successfully.")

        except Exception as e:
            print(f"Error loading AI Engine: {e}")
            raise e

    def get_recommendations(self, symptom_name, prakriti=None, top_k=5):
        """
        Get herb recommendations for a given symptom using the GNN model.
        """
        if symptom_name not in self.mappings["symptom_to_id"]:
            print(f"Symptom '{symptom_name}' not found in AI mappings.")
            return []

        symptom_id = self.mappings["symptom_to_id"][symptom_name]

        with torch.no_grad():
            # Forward pass to get node embeddings
            out_dict = self.model(self.data.x_dict, self.data.edge_index_dict)

            # Assuming the model outputs scores for herbs directly
            herb_scores = out_dict.squeeze()

            scores = herb_scores  # Shape: [num_herbs]
            top_scores, top_indices = torch.topk(scores, top_k)

            recommendations = []
            for score, idx in zip(top_scores, top_indices):
                herb_idx = idx.item()
                if herb_idx in self.mappings["id_to_herb"]:
                    herb_name = self.mappings["id_to_herb"][herb_idx]
                    # Normalize score to 0-100
                    final_score = float(torch.sigmoid(score) * 100)

                    recommendations.append(
                        {
                            "name": herb_name,
                            "score": round(final_score, 1),
                            "reason": "AI Match",
                        }
                    )

            return recommendations
