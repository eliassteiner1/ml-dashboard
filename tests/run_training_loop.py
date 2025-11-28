import os
import sys
from   pathlib import Path
import copy
import math
import random
import time
from   typing import Callable, Sequence

import h5py
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import torch
import torch.nn as nn
from   torch.utils.data import DataLoader, Dataset, Sampler, random_split

sys.path.insert(0, os.path.normcase(Path(__file__).resolve().parents[1]))
from mldashboard.config.coreconfig import ROOT
from mldashboard.plotter import DashPlotter

from mldashboard.utils.training_metrics import calc_net_weightnorm
from mldashboard.utils.training_metrics import calc_net_gradnorm



class MyDataset(Dataset):
    """ Barebone dataset classm """
    
    def __init__(self, data: Sequence):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx: int):
        return self.data[idx] 

class ScheduledBatchSampler(Sampler):
    """
    batch_sampler with batch size scheduling based on a custom dict. Use as custom batch_sampler fn in Dataloader().
    batch schedule = {how many epochs : batch size, ... : ...}. the current epoch needs to be set in the training loop by using set_epoch(E). If more epochs are trained than specified in the schedule, the last batch size is returned
    """
    
    def __init__(self, data_source: Dataset, schedule: list[tuple], shuffle: bool=False, drop_last: bool=False):
        """
        Args:
            data_source: Dataset to sample from.
            schedule   : list of tuples with (BS, nr_epochs for that BS), e.g. [(32, 2), (64, 4), (128, 8)]
            shuffle    : whether to shuffle the dataset indices.
            drop_last  : whether to drop the last incomplete batch.
        """
        
        # set up instance variables
        self._data_source   = data_source                     # this is essentially the whole dataset
        self._num_samples   = len(data_source)                # length of the whole dataset
        self._indices       = list(range(self._num_samples))  # base indices. (shuffled) batches of these are returned
        self._schedule      = self._expand_schedule(schedule) # schedule list but now with each batch size repeated * n
        self._current_epoch = None                            # to keep track of the current epoch in training loop
        self._shuffle       = shuffle
        self._drop_last     = drop_last

    def __iter__(self):
        """
        this function is essentially responsible for returning a generator object. The yield statement is kind of like a return, but instead it just advances the loop further every time the next() method is called, or in a for loop. it kind of "remebers" the last time it was called.
        """
        
        if self._current_epoch is None:
            raise ValueError(f"no epoch set! always set current epoch of sampler in training loop with set_epoch!")
        
        # determine batch size
        batch_size = self._get_batch_size()
        
        # Shuffle before returning the generator object for the new epoch
        if self._shuffle:
            random.shuffle(self._indices) 

        # determines the start indices for each batch. range(start, stop, step). 
        # Note this is essentially only the index to find the indices in self.indices for one batch xD
        for start_idx in range(0, len(self._indices), batch_size):
            # grab all the indices (now those indices corresponding to samples) belonging to a batch
            batch = self._indices[start_idx:start_idx + batch_size]
            # skip yielding the last semi-full batch if self.drop_last is true
            if len(batch) < batch_size and self._drop_last:
                continue
            # basically returns one element when it"s called and then pauses the function execution until next()
            yield batch

    def __len__(self):
        """
        just returns the number of batches in the current epoch. changes by 1 depending on whether the last semi-full one is dropped or not.
        """
        
        if self._current_epoch is None:
            raise ValueError(f"no epoch set yet!")
        
        batch_size = self._get_batch_size()
        if self._drop_last:
            return math.floor(self._num_samples / batch_size)
        else:
            return math.ceil(self._num_samples / batch_size)

    def _expand_schedule(self, schedule: list[tuple]):
        """
        Expand the schedule to be a list of repeated batch size values. 
        e.g from [(64, 1), (128, 2), (256, 4)] -> [64, 128, 128, 256, 256, 256, 256]
        """
        
        expanded_schedule = []
        for batch_size, epochs in schedule:
            expanded_schedule.extend([batch_size] * epochs)
        return expanded_schedule

    def _get_batch_size(self):
        """
        just convenience for getting the currend batch size from the expanded schedule depending on current epoch. If the epoch is larger than what is specified in the schedule, it just returns the last value.
        """
        
        if self._current_epoch < len(self._schedule):
            return self._schedule[self._current_epoch]
        else:
            return self._schedule[-1]

    def get_total_epochs(self):
        """
        Returns the total number of epochs specified with the schedule
        """
        
        return len(self._schedule)
    
    def get_total_steps(self):
        """
        Returns the total number of batches that are returned by sampler. Takes drop_last into account.
        """
        
        total_steps = 0
        if self._drop_last is True:
            for bs in self._schedule:
                total_steps += math.floor(self._num_samples / bs)
        else:
            for bs in self._schedule:
                total_steps += math.ceil(self._num_samples / bs)
        return int(total_steps)
    
    def get_total_samples(self):
        """
        Returns the total number of samples that are returned by the sampler. Takes drop_last into account.
        """
        total_samples = 0
        
        if self._drop_last is True:
            for bs in self._schedule:
                total_samples += (self._num_samples // bs) * bs
        else:
            total_samples = len(self._schedule) * self._num_samples
        return int(total_samples)
    
    def set_epoch(self, epoch: int):
        """
        update the current epoch when called in the training loop
        note: could also be replaced with something like step() to just increment the epoch by one ...
        """
        
        self._current_epoch = epoch

class TestNet(nn.Module):
    def __init__(self, init_mode: str="none"):
        super().__init__()
        
        SZ = 25
        self.linear_1x1 = nn.Linear( 1, SZ)
        self.linear_1x2 = nn.Linear(SZ, SZ)
        self.linear_1x3 = nn.Linear(SZ, SZ)
        self.linear_1x4 = nn.Linear(SZ,  1)
        
        self.activation = nn.ReLU()
        
        
        self._initialize_weights(mode=init_mode)
        return
        
    def _initialize_weights(self, mode: str):
        if mode == "none":
            return
        if mode not in ["xavier", "kaiming", "orthogonal"]:
            raise ValueError(f"please choose a valid method from [xavier, kaiming, orthogonal]! (got {mode})")
        
        for m in self.modules():
            if isinstance(m, nn.Linear):
                if mode == "xavier":
                    nn.init.xavier_uniform_(m.weight)
                    nn.init.zeros_(m.bias)
                if mode == "kaiming":
                    nn.init.kaiming_uniform_(m.weight)
                    nn.init.zeros_(m.bias)
                if mode == "orthogonal":
                    nn.init.orthogonal_(m.weight)
                    nn.init.zeros_(m.bias)
        return
    
    def forward(self, sample: dict):
        
        x = sample["input"][:, None].float()
        
        x = self.activation(self.linear_1x1(x))
        x = self.activation(self.linear_1x2(x))
        x = self.activation(self.linear_1x3(x))
        x = self.linear_1x4(x)
        
        return x

def criterion(sample: dict, pred: torch.Tensor):
    return torch.abs(pred - sample["label"][:, None])

def do_loss(criterion: Callable, sample: dict, pred: torch.Tensor):
    loss        = criterion(sample, pred)
    loss_avg    = torch.mean(loss)
    loss_std_hi = torch.std(loss[loss > loss_avg], unbiased=False)
    loss_std_lo = torch.std(loss[loss < loss_avg], unbiased=False)
    
    return loss_avg, loss_std_hi, loss_std_lo

def do_validation(criterion: Callable, network: nn.Module, validation_dataloader: DataLoader, device: str):
    with torch.no_grad():
        loss = None
        for sample in validation_dataloader:
            sample = {key: value.to(device) for key, value in sample.items()}
            pred   = network(sample)
            
            if loss is None:
                loss = criterion(sample, pred)
            else:
                loss = torch.cat([loss, criterion(sample, pred)])
                
        loss_avg    = torch.mean(loss)
        loss_std_hi = torch.std(loss[loss > loss_avg], unbiased=False)
        loss_std_lo = torch.std(loss[loss < loss_avg], unbiased=False)
        
    return  loss_avg, loss_std_hi, loss_std_lo

def do_gradnorm(grad_norm_collection: list):
    grad_norm_collection = np.array(grad_norm_collection)
    
    if len(grad_norm_collection) == 0:
        gn_avg    = 0
        gn_std_hi = 0
        gn_std_lo = 0
        return gn_avg, gn_std_hi, gn_std_lo
    
    gn_avg = np.mean(grad_norm_collection)
    
    if len(grad_norm_collection[grad_norm_collection > gn_avg]) > 0:
        gn_std_hi = np.std(grad_norm_collection[grad_norm_collection > gn_avg])
    else:
        gn_std_hi = 0  
    if len(grad_norm_collection[grad_norm_collection < gn_avg]) > 0:
        gn_std_lo = np.std(grad_norm_collection[grad_norm_collection < gn_avg])
    else: 
        gn_std_lo = 0
    
    return gn_avg, gn_std_hi, gn_std_lo


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear") # start with an empty terminal
    print(f"\033[1m\033[38;2;51;153;102mrunning script {__file__}... \033[0m")
    
    # check if cuda is available
    print(f"cuda check: {torch.cuda.is_available()}")
    
    # load the data
    n_samples_to_load = 10_000
    with h5py.File(ROOT/"tests/data/example_dataset.h5", "r") as f:
        data = [{key: np.array(f[item][key]) for key in f[item]} for item in list(f.keys())[:n_samples_to_load]]
    print("data loaded!") 
    
    # setup ------------------------------------------------------------------------------------------------------------
    DEVICE             = "cuda:0"

    # load dataset and split
    ds_full            = MyDataset(data)
    ds_len             = len(ds_full)
    split              = 0.80
    ds_train, ds_valid = random_split(ds_full, [round(split * ds_len), ds_len - round(split * ds_len)])

    # setup dataloaders and batch schedule
    bs_schedule        = [(32, 2), (64, 4), (512, 8), (1028, 8), (2048, 8)]
    sampler_train      = ScheduledBatchSampler(ds_train, bs_schedule, shuffle=True, drop_last=True)
    loader_train       = DataLoader(ds_train, batch_sampler=sampler_train)
    loader_valid       = DataLoader(ds_valid, batch_size=1000)
    n_epochs           = sampler_train.get_total_epochs()
    n_samples          = sampler_train.get_total_samples()

    # initialize model, weights and optimizer
    model              = TestNet(init_mode="none").to(DEVICE)
    optim              = torch.optim.Adam(model.parameters(), lr=10**-3, betas=(0.9, 0.999), weight_decay=0)
        
    # plotter startup app and storage stuff
    setup_options      = dict(
        graph1 = dict(
            options = dict(
                title       = "Training Loss and Validation Loss",
                subplots    = ...,
                xlabel      = "number of samples processed total",
                ylabel1     = "loss",
                ylabel2     = False,
                showmax     = False,
                showmin     = "trace2",
                totalx      = n_samples,
                downsamplex = False,
            ), 
            traces  = dict(
                trace1 = dict(N="loss_train", C="firebrick", T="primary", E=True,  P=True, S="spline"),
                trace2 = dict(N="loss_valid", C="limegreen", T="primary", E=False, P=True, S="spline"),
            ),
        ),
        graph2 = dict(
            options = dict(
                title       = "Processing Metrics",
                subplots    = ...,
                xlabel      = False,
                ylabel1     = "proc. speed",
                ylabel2     = "batch size",
                showmax     = False,
                showmin     = False,
                totalx      = n_samples,
                downsamplex = False,
            ),
            traces  = dict(
                trace1 = dict(N="proc. speed", C="gold",       T="primary",   E=False, P=True, S="spline"),
                trace2 = dict(N="batch sz.",   C="darkorchid", T="secondary", E=False, P=True, S="spline"),
            ),  
        ),
        graph3 = dict(
            options = dict(
                title       = "Network Statistics: Gradient and Weight Norm",
                subplots    = ...,
                xlabel      = False,
                ylabel1     = "grad norm",
                ylabel2     = "weight norm",
                showmax     = False,
                showmin     = False,
                totalx      = n_samples,
                downsamplex = False, 
            ),
            traces  = dict(
                trace1 = dict(N="grad norm",   C="steelblue", T="primary",   E=True,  P=True, S="spline"),
                trace2 = dict(N="weight norm", C="plum",      T="secondary", E=False, P=True, S="spline"),  
            ),
        ),
    )
    sample_counter     = 0
    input_data         = [{"input": torch.tensor([1]).to(DEVICE)}] # example input data for model summary
    PLOTTER            = DashPlotter(setup_options, model = model, input_data = input_data)
    PLOTTER.run_script()
      
    # training loop ----------------------------------------------------------------------------------------------------
    val_avg, _, _ = do_validation(criterion, model, loader_valid, DEVICE)
    weight_norm   = calc_net_weightnorm(model)
    grad_norm     = [0]
    PLOTTER.add_data(graph_nr=1, trace_nr=2, x=sample_counter, y=val_avg)
    PLOTTER.add_data(graph_nr=3, trace_nr=2, x=sample_counter, y=weight_norm)
    PLOTTER.add_data(graph_nr=3, trace_nr=1, x=sample_counter, y=np.mean(grad_norm), yStdLo=0, yStdHi=0)

    for E in range(n_epochs):
        
        model.train()
        sampler_train.set_epoch(E)
        
        grad_norm = []
                
        for sample in loader_train:
            PLOTTER.batchtimer("start")
            
            sample = {key: value.to(DEVICE) for key, value in sample.items()}            
            optim.zero_grad()
            pred  = model(sample)
            loss_avg, loss_std_hi, loss_std_lo = do_loss(criterion, sample, pred)
            loss_avg.backward()
            optim.step()
            
            # plotting
            BS = sample["input"].shape[0]
            sample_counter += BS
            
            grad_norm.append(calc_net_gradnorm(model))
            PLOTTER.add_data(graph_nr=1, trace_nr=1, x=sample_counter, y=loss_avg, yStdLo=loss_std_lo, yStdHi=loss_std_hi) 
            PLOTTER.add_data(graph_nr=2, trace_nr=2, x=sample_counter, y=BS)

            time.sleep(0.01)
            
            PLOTTER.batchtimer("stop", batch_size = BS)
            PLOTTER.add_data(graph_nr=2, trace_nr=1, x=sample_counter, y=PLOTTER.batchtimer("read"))
        
        # validation (for plotting)    
        val_avg, _, _ = do_validation(criterion, model, loader_valid, DEVICE)
        PLOTTER.add_data(graph_nr=1, trace_nr=2, x=sample_counter, y=val_avg)
        # weight norm for plotting
        weight_norm = calc_net_weightnorm(model)
        PLOTTER.add_data(graph_nr=3, trace_nr=2, x=sample_counter, y=weight_norm)
        # grad norm
        gn_avg, gn_std_hi, gn_std_lo = do_gradnorm(grad_norm)
        PLOTTER.add_data(graph_nr=3, trace_nr=1, x=sample_counter, y=gn_avg, yStdLo=gn_std_lo, yStdHi=gn_std_hi)
    
    # keep plotter app alive -------------------------------------------------------------------------------------------
    PLOTTER.run_script_spin()
    
    
    