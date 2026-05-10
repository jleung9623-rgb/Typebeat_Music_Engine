import torch
import torch.nn as nn
import torch.optim as optim
import random
from model_architecture import TypebeatLSTMEncoder

class SyntheticTripletDataset:
    """
    Mocks the SQL data extraction phase.
    In production, this class will query the MySQL database to build triplets based on MotifClass and ChordID.
    """

    def __init__(self, num_samples=100):
        self.num_samples = num_samples
    
    def __len__(self):
        return self.num_samples
    
    def __getitem__(self, idx):
        # Simulates variable-length sequences between 10 and 50 notes
        anchor_len = random.randint(10, 50)
        positive_len = random.randint(10, 50)
        negative_len = random.randint(10, 50)

        # Feature Shape: (Seq_Len, 4) -> [pitch, duration, beat, micro_offset]
        anchor = torch.rand(1, anchor_len, 4)
        positive = torch.rand(1, positive_len, 4)
        negative = torch.rand(1, negative_len, 4)

        return anchor, positive, negative
    

def execute_contrastive_training():
    # Boots Hardware & Model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"--- Booting Training Environment on {device.type.upper()} ---")

    model = TypebeatLSTMEncoder().to(device)
    model.train() # Enables Dropout and Gradient Tracking

    # Margin = 1.0 means the Negative vector must be at least 1.0 spatial unit further away than the Positive Vector
    criterion = nn.TripletMarginLoss(margin=1.0, p=2)

    # Adam Optimizer: Handles the weight updates. Learning rate set clinically low to prevent spatial collapse
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Data Inflow
    dataset = SyntheticTripletDataset(num_samples=500)

    epochs = 5
    print("--- Commencing Triplet Optimization ---")

    for epoch in range(epochs):
        epoch_loss = 0.0

        for i in range(len(dataset)):
            anchor_seq, positive_seq, negative_seq = dataset[i]

            # Hardware routing
            anchor_seq = anchor_seq.to(device)
            positive_seq = positive_seq.to(device)
            negative_seq = negative_seq.to(device)

            # Compresses the variable-length sequences into 256-D vectors
            anchor_vec = model(anchor_seq)
            positive_vec = model(positive_seq)
            negative_vec = model(negative_seq)

            # Loss Calculation
            loss = criterion(anchor_vec, positive_vec, negative_vec)

            # Weighting Update
            optimizer.zero_grad()   # Flushes old gradients
            loss.backward()         # Calculates the mathematical trajectory for correction
            optimizer.step()        # Physically updates the LSTM weights

            epoch_loss += loss.item()

        avg_loss = epoch_loss / len(dataset)
        print(f"Epoch {epoch + 1}/{epochs} | Average Triplet Loss: {avg_loss:.4f}")

    print("--- Training Complete. Exporting Verified Weights ---")
    model.eval() # Locks the weights
    scripted_model = torch.jit.script(model)
    scripted_model.save("ml/typebeat_embedding_model.pt")
    print("SUCCESS: 'ml/typebeat_embedding_model.pt' overwritten with trained parameters.")


if __name__ == "__main__":
    execute_contrastive_training()