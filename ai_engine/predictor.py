import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import HeteroConv, SAGEConv
from torch_geometric.data import HeteroData
import pandas as pd
import pickle
from fuzzywuzzy import process
import os

# ---------------------------------------------------------
# 1. MODEL ARCHITECTURE (Exact copy from your Colab)
# ---------------------------------------------------------

class HeteroGNN(torch.nn.Module):
    def __init__(self, data, hidden_channels, num_layers, dropout_rate):
        super().__init__()
        self.num_layers = num_layers
        self.dropout_rate = dropout_rate

        # Linear layers to project initial node features to hidden_channels
        self.lin_dict = torch.nn.ModuleDict()
        for node_type in data.node_types:
            # The .x attribute is guaranteed to have the correct feature dimension
            self.lin_dict[node_type] = nn.Linear(data[node_type].x.shape[1], hidden_channels)

        # Multiple HeteroConv layers
        self.convs = torch.nn.ModuleList()
        for _ in range(num_layers):
            conv = HeteroConv({
                (src, rel, dst): SAGEConv((hidden_channels, hidden_channels), hidden_channels)
                for src, rel, dst in data.edge_types
            }, aggr='sum')
            self.convs.append(conv)

        # Define a linear layer as the decoder for the recommendation task
        self.decoder = nn.Linear(2 * hidden_channels, 1)

    def forward(self, x_dict, edge_index_dict, cond_herb_edge_label_index, dosha_herb_edge_label_index):
        # 1. Project initial features to hidden_channels and apply ReLU
        # Create a copy to modify features in place across layers
        h_dict = {node_type: F.relu(self.lin_dict[node_type](x)) for node_type, x in x_dict.items()}

        # 2. Pass through heterogeneous convolution layers
        for i, conv in enumerate(self.convs):
            # Pass the current node features h_dict through the convolution layer
            # conv(h_dict, edge_index_dict) returns a dictionary containing updated features
            # for destination node types only.
            h_dict_updated_by_conv = conv(h_dict, edge_index_dict)

            # Create the next h_dict by merging outputs from the conv with original h_dict
            # to ensure all node types are carried forward.
            next_h_dict = {}
            for node_type in h_dict.keys(): # Iterate over all node types that should exist
                if node_type in h_dict_updated_by_conv:
                    # If this node type was a destination in the current conv layer, use its new features.
                    features = h_dict_updated_by_conv[node_type]
                else:
                    # Otherwise, carry over its features from the previous layer.
                    features = h_dict[node_type]

                # Apply ReLU
                features = F.relu(features)

                # Apply Dropout, unless it's the last GNN layer
                if i < self.num_layers - 1:
                    features = F.dropout(features, p=self.dropout_rate, training=self.training)
                next_h_dict[node_type] = features
            h_dict = next_h_dict # Update h_dict for the next iteration

        x_dict_processed = h_dict # Final processed features for all node types

        # Condition -> Herb recommendation decoding
        cond_herb_pred = torch.empty(0, device=list(x_dict_processed.values())[0].device if x_dict_processed else 'cpu')
        
        # Check if we have edges to predict for Condition->Herb
        if cond_herb_edge_label_index.numel() > 0 and 'condition' in x_dict_processed and 'herb' in x_dict_processed:
            cond_src = cond_herb_edge_label_index[0]
            herb_tgt = cond_herb_edge_label_index[1]

            # Ensure indices are valid
            valid_cond_src_mask = cond_src < x_dict_processed['condition'].shape[0]
            valid_herb_tgt_mask = herb_tgt < x_dict_processed['herb'].shape[0]
            combined_mask = valid_cond_src_mask & valid_herb_tgt_mask

            cond_src_filtered = cond_src[combined_mask]
            herb_tgt_filtered = herb_tgt[combined_mask]

            if cond_src_filtered.numel() > 0 and herb_tgt_filtered.numel() > 0:
                h_cond = x_dict_processed['condition'][cond_src_filtered]
                h_herb = x_dict_processed['herb'][herb_tgt_filtered]
                cond_herb_pred = self.decoder(torch.cat([h_cond, h_herb], dim=-1)).squeeze()

        # Dosha -> Herb recommendation decoding
        dosha_herb_pred = torch.empty(0, device=list(x_dict_processed.values())[0].device if x_dict_processed else 'cpu')
        
        # Check if we have edges to predict for Dosha->Herb
        if dosha_herb_edge_label_index.numel() > 0 and 'dosha' in x_dict_processed and 'herb' in x_dict_processed:
            dosha_src = dosha_herb_edge_label_index[0]
            herb_tgt_dosha = dosha_herb_edge_label_index[1]

            valid_dosha_src_mask = dosha_src < x_dict_processed['dosha'].shape[0]
            valid_herb_tgt_dosha_mask = herb_tgt_dosha < x_dict_processed['herb'].shape[0]
            combined_mask_dosha = valid_dosha_src_mask & valid_herb_tgt_dosha_mask

            dosha_src_filtered = dosha_src[combined_mask_dosha]
            herb_tgt_dosha_filtered = herb_tgt_dosha[combined_mask_dosha]

            if dosha_src_filtered.numel() > 0 and herb_tgt_dosha_filtered.numel() > 0:
                h_dosha = x_dict_processed['dosha'][dosha_src_filtered]
                h_herb_dosha = x_dict_processed['herb'][herb_tgt_dosha_filtered]
                dosha_herb_pred = self.decoder(torch.cat([h_dosha, h_herb_dosha], dim=-1)).squeeze()

        return cond_herb_pred, dosha_herb_pred

# ---------------------------------------------------------
# 2. PREDICTION ENGINE (Handles loading and inference)
# ---------------------------------------------------------

class AyurvedaPredictor:
    def __init__(self, model_path, data_path, artifacts_path):
        self.device = torch.device('cpu') # Run on CPU for the web app
        
        print(f"Loading AI Engine...")
        # 1. Load Graph Data
        self.data = torch.load(data_path, map_location=self.device)
        
        # 2. Load Artifacts (Mappings and Thresholds)
        with open(artifacts_path, 'rb') as f:
            self.artifacts = pickle.load(f)
            
        self.herb2id = self.artifacts['herb2id']
        self.cond2id = self.artifacts['cond2id']
        self.dosha2id = self.artifacts['dosha2id']
        self.herbs_df = self.artifacts['herbs_df']
        
        # Extract thresholds or set defaults if missing
        self.thresholds = self.artifacts.get('optimal_thresholds', {'cond': 0.7, 'dosha': 0.6})

        # 3. Initialize Model
        # IMPORTANT: hyperparams must match training exactly
        hidden_channels = 256
        num_layers = 3
        dropout = 0.4
        
        self.model = HeteroGNN(self.data, hidden_channels, num_layers, dropout)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        print("AI Model Loaded Successfully!")

    def get_id_fuzzy(self, name, map_dict, choices_df):
        """Find best matching ID for a text input using fuzzy matching"""
        if not name: return None
        
        # Get list of possible names from the DataFrame or Dict keys
        choices = choices_df['name'].tolist() if isinstance(choices_df, pd.DataFrame) else list(choices_df.keys())
        
        # Fuzzy match
        best_match, score = process.extractOne(name, choices)
        
        if score < 75: 
            # Confidence too low, assume no match
            return None
        
        # Retrieve the ID for the best match
        if isinstance(choices_df, pd.DataFrame):
            original_id = choices_df[choices_df['name'] == best_match]['nodeid'].values[0]
        else:
            # If passed a dict of names directly (like for Doshas sometimes)
            # This handles cases where choices_df might just be the keys
            original_id = best_match 

        # Map the CSV ID to the Graph Index ID
        return map_dict.get(original_id)

    def predict(self, condition_name, dosha_name):
        recommendations = []
        
        with torch.no_grad():
            # 1. Resolve IDs from User Input
            cond_id = self.get_id_fuzzy(condition_name, self.cond2id, self.artifacts['conditions_df'])
            
            # For Dosha, we might need a simple dataframe if one wasn't saved
            dosha_keys = list(self.dosha2id.keys()) # e.g., [1, 2, 3] or names
            # Assuming artifacts has a dosha dataframe, if not we mock one for the fuzzy search
            dosha_df = pd.DataFrame({'name': ['Vata', 'Pitta', 'Kapha'], 'nodeid': [1, 2, 3]})
            dosha_id = self.get_id_fuzzy(dosha_name, self.dosha2id, dosha_df)
            
            # List of all herb indices in the graph to score against
            all_herb_indices = torch.tensor(list(self.herb2id.values()), dtype=torch.long)
            
            # -------------------------------------------------
            # Prediction A: Condition -> Herb
            # -------------------------------------------------
            if cond_id is not None:
                # Create pairs: [Target_Condition, Every_Herb]
                src = torch.tensor([cond_id] * len(all_herb_indices), dtype=torch.long)
                edge_label_index = torch.stack([src, all_herb_indices], dim=0)
                
                # Run Model (pass empty for dosha edges)
                logits, _ = self.model(
                    self.data.x_dict, 
                    self.data.edge_index_dict, 
                    edge_label_index, 
                    torch.empty(2, 0, dtype=torch.long)
                )
                scores = torch.sigmoid(logits)
                
                # Filter using Optimal Threshold
                mask = scores > self.thresholds['cond']
                valid_indices = all_herb_indices[mask]
                valid_scores = scores[mask]
                
                for idx, score in zip(valid_indices, valid_scores):
                    # Convert Graph Index back to Real Name
                    # Find original ID where value == idx
                    original_node_id = [k for k, v in self.herb2id.items() if v == idx.item()][0]
                    herb_info = self.herbs_df[self.herbs_df['nodeid'] == original_node_id].iloc[0]
                    
                    recommendations.append({
                        'name': herb_info['name'],
                        'score': float(score),
                        'reason': f"AI matched for {condition_name}",
                        'type': 'condition',
                        'form': herb_info['medicine_form']
                    })

            # -------------------------------------------------
            # Prediction B: Dosha -> Herb
            # -------------------------------------------------
            if dosha_id is not None:
                src = torch.tensor([dosha_id] * len(all_herb_indices), dtype=torch.long)
                edge_label_index = torch.stack([src, all_herb_indices], dim=0)
                
                # Run Model (pass empty for condition edges)
                _, logits = self.model(
                    self.data.x_dict, 
                    self.data.edge_index_dict, 
                    torch.empty(2, 0, dtype=torch.long),
                    edge_label_index
                )
                scores = torch.sigmoid(logits)
                
                # Filter
                mask = scores > self.thresholds['dosha']
                valid_indices = all_herb_indices[mask]
                valid_scores = scores[mask]
                
                for idx, score in zip(valid_indices, valid_scores):
                    original_node_id = [k for k, v in self.herb2id.items() if v == idx.item()][0]
                    herb_info = self.herbs_df[self.herbs_df['nodeid'] == original_node_id].iloc[0]
                    
                    # Check if already recommended to avoid duplicates
                    existing = next((item for item in recommendations if item['name'] == herb_info['name']), None)
                    if existing:
                        # Boost score if it matches both condition AND dosha
                        existing['score'] = max(existing['score'], float(score))
                        existing['reason'] += f" & Balances {dosha_name}"
                    else:
                        recommendations.append({
                            'name': herb_info['name'],
                            'score': float(score),
                            'reason': f"Balances {dosha_name} Dosha",
                            'type': 'dosha',
                            'form': herb_info['medicine_form']
                        })

        # Sort by confidence score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top 5 results
        return recommendations[:5]