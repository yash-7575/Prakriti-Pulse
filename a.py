# COMPLETE RUNNABLE GCN MODEL
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from sklearn.model_selection import train_test_split

# 1. DATA PREPARATION
def create_sample_data():
    """Create sample graph data"""
    np.random.seed(42)
    node_features = np.random.randn(200, 64).astype(np.float32)
    adj_matrix = np.random.rand(200, 200).astype(np.float32)
    adj_matrix = (adj_matrix + adj_matrix.T) / 2  # Make symmetric
    labels = np.random.randint(0, 3, 200)
    return node_features, adj_matrix, labels

# 2. DATASET CLASS
class GraphDataset(Dataset):
    def __init__(self, node_features, adj_matrix, labels, node_indices):
        self.node_features = torch.FloatTensor(node_features)
        self.adj_matrix = torch.FloatTensor(adj_matrix)
        self.labels = torch.LongTensor(labels)
        self.node_indices = torch.LongTensor(node_indices)
    
    def __len__(self):
        return len(self.node_indices)
    
    def __getitem__(self, idx):
        node_idx = self.node_indices[idx]
        return {
            'features': self.node_features,
            'adj_matrix': self.adj_matrix,
            'label': self.labels[node_idx],
            'node_idx': torch.tensor(node_idx, dtype=torch.long)
        }

# 3. GCN LAYER
class GCNLayer(nn.Module):
    def __init__(self, in_features, out_features, bias=True):
        super(GCNLayer, self).__init__()
        self.weight = nn.Parameter(torch.FloatTensor(in_features, out_features))
        if bias:
            self.bias = nn.Parameter(torch.FloatTensor(out_features))
        else:
            self.register_parameter('bias', None)
        self.reset_parameters()
    
    def reset_parameters(self):
        nn.init.xavier_uniform_(self.weight)
        if self.bias is not None:
            nn.init.zeros_(self.bias)
    
    def forward(self, input_features, adj_matrix):
        support = torch.mm(input_features, self.weight)
        output = torch.mm(adj_matrix, support)
        if self.bias is not None:
            output = output + self.bias
        return output

# 4. COMPLETE GCN MODEL
class GCNModel(nn.Module):
    def __init__(self, input_dim, hidden_dims, output_dim, dropout=0.2):
        super(GCNModel, self).__init__()
        self.layers = nn.ModuleList()
        dims = [input_dim] + hidden_dims
        
        for i in range(len(dims) - 1):
            self.layers.append(GCNLayer(dims[i], dims[i + 1]))
        
        self.output_layer = GCNLayer(hidden_dims[-1], output_dim)
        self.dropout_layer = nn.Dropout(dropout)
    
    def normalize_adjacency(self, adj_matrix):
        identity = torch.eye(adj_matrix.size(0), device=adj_matrix.device)
        adj_tilde = adj_matrix + identity
        degree = torch.sum(adj_tilde, dim=1)
        degree_inv_sqrt = torch.diag(torch.pow(degree + 1e-6, -0.5))
        adj_norm = torch.mm(torch.mm(degree_inv_sqrt, adj_tilde), degree_inv_sqrt)
        return adj_norm
    
    def forward(self, node_features, adj_matrix):
        adj_norm = self.normalize_adjacency(adj_matrix)
        x = node_features
        
        for layer in self.layers:
            x = layer(x, adj_norm)
            x = F.relu(x)
            x = self.dropout_layer(x)
        
        x = self.output_layer(x, adj_norm)
        return F.log_softmax(x, dim=1)

# 5. TRAINING FUNCTION
def train_model(model, train_loader, val_loader, num_epochs=30, lr=0.01):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    criterion = nn.NLLLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=5e-4)
    
    print(f"Training on device: {device}")
    
    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for batch in train_loader:
            features = batch['features'].to(device)
            adj_matrix = batch['adj_matrix'].to(device)
            labels = batch['label'].to(device)
            node_indices = batch['node_idx'].to(device)
            
            optimizer.zero_grad()
            outputs = model(features, adj_matrix)
            node_outputs = outputs[node_indices]
            
            loss = criterion(node_outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = torch.max(node_outputs.data, 1)
            train_total += labels.size(0)
            train_correct += (predicted == labels).sum().item()
        
        if (epoch + 1) % 10 == 0:
            train_acc = 100 * train_correct / train_total
            print(f'Epoch [{epoch+1}/{num_epochs}] - Loss: {train_loss/len(train_loader):.4f}, Acc: {train_acc:.2f}%')
    
    return model

# 6. MAIN EXECUTION
def main():
    print("🚀 Starting GCN Model Training")
    
    # Create data
    node_features, adj_matrix, labels = create_sample_data()
    print(f"✅ Created graph with {len(labels)} nodes")
    
    # Split data
    num_nodes = len(labels)
    node_indices = np.arange(num_nodes)
    train_indices, temp_indices = train_test_split(node_indices, test_size=0.4, random_state=42)
    val_indices, test_indices = train_test_split(temp_indices, test_size=0.5, random_state=42)
    
    # Create datasets and loaders
    train_dataset = GraphDataset(node_features, adj_matrix, labels, train_indices)
    val_dataset = GraphDataset(node_features, adj_matrix, labels, val_indices)
    
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
    
    # Create and train model
    model = GCNModel(input_dim=64, hidden_dims=[128, 64], output_dim=3, dropout=0.2)
    trained_model = train_model(model, train_loader, val_loader, num_epochs=30)
    
    return trained_model

# RUN THE MODEL
if __name__ == "__main__":
    model = main()