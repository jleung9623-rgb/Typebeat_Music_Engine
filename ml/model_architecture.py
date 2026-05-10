import torch
import torch.nn as nn

class TypebeatLSTMEncoder(nn.Module):
    def __init__(self, input_features=4, hidden_dim=128, output_dim=256, num_layers=2):
        super(TypebeatLSTMEncoder, self).__init__()

        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        # Initializes the recurrent engine with specified dimensions and dropout for regularization
        # batch_first=True ensures tensors of shape are selected (Batch, Seq_Len, Features)
        self.lstm = nn.LSTM(
            input_size = input_features,
            hidden_size = hidden_dim,
            num_layers = num_layers,
            batch_first = True,
            dropout = 0.1 if num_layers > 1 else 0.0
        )

        # Projects the LSTM's hidden state into Qdrant's strict 256-Dimension requirement
        self.projection = nn.Sequential(
            nn.Linear(hidden_dim, output_dim),
            nn.LayerNorm(output_dim) # Stabilizes the spatial distribution for Cosine Similarity
        )
    
    def forward(self, x):
        """
        Expects x shape: (Batch, Seq_Len, 4)
        """
        # Output Shape: (Batch, Sequence_Length, 4)
        # Hidden State (h_n) Shape: (Num_Layers, Batch, Hidden_Dim)
        lstm_out, (h_n, c_n) = self.lstm(x)

        # Collapses the variable-length sequence into a single static sumamry vector by extracting only the last hidden state of the top LSTM layer
        final_hidden_state = h_n[-1, :, :] # Shape: (Batch, Hidden_Dim)

        # Projects to 256-Dimension Space
        qdrant_vector = self.projection(final_hidden_state) # Shape: (Batch, 256)

        return qdrant_vector
    
if __name__ == "__main__":
    # Instantiates the untrained architecture
    model = TypebeatLSTMEncoder()
    model.eval()
    print("--- Typebeat Encoder Activated ---")

    # Simulates the two extreme motif note lengths to verify that the architecture can handle both ends of the spectrum without dimensional collapse or errors
    dummy_short_motif = torch.rand(1, 14, 4)    # 14-Note Limit
    dummy_long_motif = torch.rand(1, 45, 4)     # 45-Note Limit

    output_short = model(dummy_short_motif)
    output_long = model(dummy_long_motif)

    print(f"Short Motif Output Shape: {output_short.shape}") # Expected: [1, 256]
    print(f"Long Motif Output Shape: {output_long.shape}")   # Expected: [1, 256]

    assert output_short.shape == (1, 256) and output_long.shape == (1, 256), "ERROR: Dimensional collapse failed."
    print("--- Mathematical Verification Passed ---")

    scripted_model = torch.jit.script(model)
    scripted_model.save("ml/typebeat_embedding_model.pt")

    print("SUCCESS: 'typebeat_embedding_model.pt' has been generated. Uploader pipeline is now unblocked.")