import sys
import os
from   pathlib import Path
import time
from   typing import Callable, Sequence

import numpy as np
import torch
import torch.nn as nn
from   torch.utils.data import DataLoader, Dataset, Sampler, random_split


from torchvision import datasets
from torchvision.transforms import v2
import matplotlib.pyplot as plt




from mldashboard.plotter import DashPlotter
from mldashboard.containers.setupconfig import Config, GraphConfig, TraceConfig

from mldashboard.utils.training_metrics import calc_net_weightnorm
from mldashboard.utils.training_metrics import calc_net_gradnorm


# def criterion(sample: dict, pred: torch.Tensor):
#     return torch.abs(pred - sample["label"][:, None])

# def do_loss(criterion: Callable, sample: dict, pred: torch.Tensor):
#     loss        = criterion(sample, pred)
#     loss_avg    = torch.mean(loss)
#     loss_std_hi = torch.std(loss[loss > loss_avg], unbiased=False)
#     loss_std_lo = torch.std(loss[loss < loss_avg], unbiased=False)
    
#     return loss_avg, loss_std_hi, loss_std_lo

# def do_validation(criterion: Callable, network: nn.Module, validation_dataloader: DataLoader, device: str):
#     with torch.no_grad():
#         loss = None
#         for sample in validation_dataloader:
#             sample = {key: value.to(device) for key, value in sample.items()}
#             pred   = network(sample)
            
#             if loss is None:
#                 loss = criterion(sample, pred)
#             else:
#                 loss = torch.cat([loss, criterion(sample, pred)])
                
#         loss_avg    = torch.mean(loss)
#         loss_std_hi = torch.std(loss[loss > loss_avg], unbiased=False)
#         loss_std_lo = torch.std(loss[loss < loss_avg], unbiased=False)
        
#     return  loss_avg, loss_std_hi, loss_std_lo

# def do_gradnorm(grad_norm_collection: list):
#     grad_norm_collection = np.array(grad_norm_collection)
    
#     if len(grad_norm_collection) == 0:
#         gn_avg    = 0
#         gn_std_hi = 0
#         gn_std_lo = 0
#         return gn_avg, gn_std_hi, gn_std_lo
    
#     gn_avg = np.mean(grad_norm_collection)
    
#     if len(grad_norm_collection[grad_norm_collection > gn_avg]) > 0:
#         gn_std_hi = np.std(grad_norm_collection[grad_norm_collection > gn_avg])
#     else:
#         gn_std_hi = 0  
#     if len(grad_norm_collection[grad_norm_collection < gn_avg]) > 0:
#         gn_std_lo = np.std(grad_norm_collection[grad_norm_collection < gn_avg])
#     else: 
#         gn_std_lo = 0
    
#     return gn_avg, gn_std_hi, gn_std_lo


class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(28*28, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, 10),
        )

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits





if __name__ == "__main__":
    print("\033[2J\033[3J\033[H", end="", flush=True) # start with an empty terminal
    print(f"\033[1m\033[38;2;51;153;102mrunning script {__file__}... \033[0m")
    
    # Device setup 
    DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"⯈ using {DEVICE} as device")
    
    print("⯈ loading dataset ...")
    training_data = datasets.FashionMNIST(
        root="./data",
        train=True,
        download=True,
        transform=v2.Compose([v2.ToImage(), v2.ToDtype(torch.float32, scale=True)])
    )
    test_data = datasets.FashionMNIST(
        root="data",
        train=False,
        download=False,
        transform=v2.Compose([v2.ToImage(), v2.ToDtype(torch.float32, scale=True)])
    )
    train_dataloader = DataLoader(training_data, batch_size=256, shuffle=True, pin_memory=True)
    test_dataloader = DataLoader(test_data, batch_size=256, shuffle=True, pin_memory=True)
    
    loss_fn = nn.CrossEntropyLoss(reduction="none")
    
    model = NeuralNetwork().to(DEVICE)
    optim = torch.optim.Adam(model.parameters(), lr=10**-3, betas=(0.9, 0.999), weight_decay=0)

    n_epochs = 5
    n_samples = n_epochs * len(training_data)
    
    # plotter startup app and storage stuff
    cfg = Config(
        graph1=GraphConfig(
            title   = "Training Loss and Validation Loss",
            xlabel  = "number of samples processed total",
            ylabel1 = "loss",
            ylabel2 = False,
            showmax = False,
            showmin = "trace1",
            totalx  = n_samples,
            nxdown  = False,
            traces  = [  
                TraceConfig(name="loss_train", color="firebrick"),
                TraceConfig(name="loss_valid", color="seagreen"),
            ]
        ),
        graph2=GraphConfig(
            title   = "other",
            xlabel  = False,
            ylabel1 = "proc. speed",
            ylabel2 = "batch size",
            showmax = False,
            showmin = False,
            totalx  = n_samples,
            nxdown  = False,
            traces  = [  
                TraceConfig(name="proc. speed", color="gold"),
                TraceConfig(name="batch sz.",   color="darkorchid", yaxis="secondary"),
            ]
        ),
        graph3=GraphConfig(
            title   = "other",
            xlabel  = False,
            ylabel1 = "grad norm",
            ylabel2 = "weight norm",
            showmax = False,
            showmin = False,
            totalx  = n_samples,
            nxdown  = False,
            traces = [
                TraceConfig(name="grad norm",   color="steelblue"),
                TraceConfig(name="weight norm", color="plum", yaxis="secondary"),
            ]
        ),
    )
    PLOTTER = DashPlotter(cfg)
    PLOTTER.run_script()
    sample_counter = 0
    
    
    # initial evaluation
    model.eval()
    test_loss, correct = 0.0, 0  
    with torch.no_grad():
        for X, y in test_dataloader:
            X = X.to(DEVICE)
            y = y.to(DEVICE, non_blocking=True)

            pred = model(X)
            test_loss += loss_fn(pred, y).sum().item()
            correct += (pred.argmax(1) == y).sum().item()
    n = len(test_dataloader.dataset)
    PLOTTER.add_data(g_nr=1, t_nr=1, x=sample_counter, y=test_loss/n)
    
    # main training loop
    for E in range(n_epochs):
        
        # training per epoch ------
        model.train()
        
        for X, y in train_dataloader:
            
            PLOTTER.batchtimer("start")
            
            X = X.to(DEVICE, non_blocking=True)
            y = y.to(DEVICE, non_blocking=True)
            
            optim.zero_grad()
            pred = model(X)
            losses = loss_fn(pred, y)
            loss = losses.mean()
            loss.backward()
            optim.step()
            
            # plotting
            with torch.no_grad():
                q_lo, q_hi = torch.quantile(losses, torch.tensor([0.10, 0.90], device=losses.device))
            loss_value = loss.item()
            BS = X.shape[0]
            PLOTTER.batchtimer("stop", batch_size=BS) # only stop after .item since this syncs threads with gpu
            sample_counter += BS

            PLOTTER.add_data(g_nr=1, t_nr=0, x=sample_counter, y=loss_value)
        
        
        
        
        # eval -------
        model.eval()
        test_loss, correct = 0.0, 0
    
        with torch.no_grad():
            for X, y in test_dataloader:
                X = X.to(DEVICE)
                y = y.to(DEVICE, non_blocking=True)

                pred = model(X)
                test_loss += loss_fn(pred, y).sum().item()
                correct += (pred.argmax(1) == y).sum().item()
                
        n = len(test_dataloader.dataset)
        PLOTTER.add_data(g_nr=1, t_nr=1, x=sample_counter, y=test_loss/n)
        
    
    # keep plotter app alive -------------------------------------------------------------------------------------------
    PLOTTER.run_script_spin()
    
    
    