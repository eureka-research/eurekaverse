import torch
import torch.nn as nn
import sys
import torchvision

class RecurrentDepthBackbone(nn.Module):
    def __init__(self, base_backbone, env_cfg, output_yaw=True) -> None:
        super().__init__()
        activation = nn.ELU()
        last_activation = nn.Tanh()
        self.base_backbone = base_backbone
        self.combination_mlp = nn.Sequential(
            nn.Linear(32 + env_cfg.env.n_proprio, 128),
            activation,
            nn.Linear(128, 32)
        )
        self.recurrent_size = 512
        # self.recurrent_size = 256  # 2x smaller
        self.rnn = nn.GRU(input_size=32, hidden_size=self.recurrent_size, batch_first=True)
        output_size = 32 + 2 if output_yaw else 32
        self.output_mlp = nn.Sequential(
            nn.Linear(self.recurrent_size, output_size),
            last_activation
        )
        # self.hidden_states = None
        self.hidden_states = torch.zeros(1, 0, self.recurrent_size)
        self.rnn.flatten_parameters()

    def forward(self, depth_image, proprioception):
        if self.hidden_states.shape[1] == 0:
            # On the first forward pass, initialize hidden states to proper batch size
            self.hidden_states = torch.zeros(1, depth_image.shape[0], self.recurrent_size).to(depth_image.device)

        depth_image = self.base_backbone(depth_image)
        depth_latent = self.combination_mlp(torch.cat((depth_image, proprioception), dim=-1))
        # depth_latent = self.base_backbone(depth_image)
        depth_latent, self.hidden_states = self.rnn(depth_latent[:, None, :], self.hidden_states)
        depth_latent = self.output_mlp(depth_latent.squeeze(1))
        
        return depth_latent

    def detach_hidden_states(self):
        self.hidden_states = self.hidden_states.detach().clone()
    
class DepthOnlyFCBackbone58x87(nn.Module):
    def __init__(self, prop_dim, scandots_output_dim, hidden_state_dim, output_activation=None, num_frames=1):
        super().__init__()

        self.num_frames = num_frames
        activation = nn.ELU()
        self.image_compression = nn.Sequential(
            # [1, 58, 87] [1, 60, 90] [1, 56, 90]
            nn.Conv2d(in_channels=self.num_frames, out_channels=32, kernel_size=5),
            # [32, 54, 83] [32, 56, 86] [32, 52, 86]
            nn.MaxPool2d(kernel_size=2, stride=2),
            # [32, 27, 41] [32, 28, 43] [32, 26, 43]
            activation,
            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3),
            activation,
            nn.Flatten(),
            # [64, 25, 39] [64, 26, 41] [64, 24, 41]
            # nn.Linear(64 * 25 * 39, 128),
            nn.Linear(64 * 26 * 41, 128),
            # nn.Linear(64 * 24 * 41, 128),
            activation,
            nn.Linear(128, scandots_output_dim)
        )

        # 2x larger
        # self.image_compression = nn.Sequential(
        #     nn.Conv2d(in_channels=self.num_frames, out_channels=64, kernel_size=5),
        #     nn.MaxPool2d(kernel_size=2, stride=2),
        #     activation,
        #     nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3),
        #     activation,
        #     nn.Flatten(),
        #     nn.Linear(128 * 26 * 41, 256),
        #     activation,
        #     nn.Linear(256, scandots_output_dim)
        # )

        # 8x smaller
        # self.image_compression = nn.Sequential(
        #     nn.Conv2d(in_channels=self.num_frames, out_channels=4, kernel_size=5),
        #     nn.MaxPool2d(kernel_size=2, stride=2),
        #     activation,
        #     nn.Conv2d(in_channels=4, out_channels=8, kernel_size=3),
        #     activation,
        #     nn.Flatten(),
        #     nn.Linear(8 * 26 * 41, 16),
        #     activation,
        #     nn.Linear(16, scandots_output_dim)
        # )

        # 16x smaller
        # self.image_compression = nn.Sequential(
        #     nn.Conv2d(in_channels=self.num_frames, out_channels=2, kernel_size=5),
        #     nn.MaxPool2d(kernel_size=2, stride=2),
        #     activation,
        #     nn.Conv2d(in_channels=2, out_channels=4, kernel_size=3),
        #     activation,
        #     nn.Flatten(),
        #     nn.Linear(4 * 26 * 41, 8),
        #     activation,
        #     nn.Linear(8, scandots_output_dim)
        # )

        if output_activation == "tanh":
            self.output_activation = nn.Tanh()
        else:
            self.output_activation = activation

    def forward(self, images: torch.Tensor):
        images_compressed = self.image_compression(images.unsqueeze(1))
        latent = self.output_activation(images_compressed)

        return latent