plot_cb = PlotterCallback(PLOTTER)

trainer = Trainer(
    epochs=n_epochs,
    model=model,
    optimizer=optim,
    device=DEVICE,
    train_loader=loader_train,
    valid_loader=loader_valid,
    callbacks=[plot_cb],
)

trainer.fit()



class PlotterCallback:
    def __init__(self, plotter):
        self.p = plotter
        self.sample_counter = 0
        self.grad_norm = []

    def on_train_batch_start(self, batch):
        self.p.batchtimer("start")

    def on_train_batch_end(self, batch, outputs, loss_stats):
        BS = batch["input"].shape[0]
        self.sample_counter += BS

        loss_avg, loss_std_lo, loss_std_hi = loss_stats

        self.p.add_data(1, 0, self.sample_counter, loss_avg, loss_std_lo, loss_std_hi)
        self.p.add_data(2, 1, self.sample_counter, BS)

        self.p.batchtimer("stop", batch_size=BS)
        self.p.add_data(2, 0, self.sample_counter, self.p.batchtimer("read"))

    def on_after_backward(self, model):
        self.grad_norm.append(calc_net_gradnorm(model))

    def on_validation_end(self, val_loss, model):
        self.p.add_data(1, 1, self.sample_counter, val_loss)
        self.p.add_data(3, 1, self.sample_counter, calc_net_weightnorm(model))

        gn_avg, gn_std_hi, gn_std_lo = do_gradnorm(self.grad_norm)
        self.p.add_data(3, 0, self.sample_counter, gn_avg, gn_std_lo, gn_std_hi)

        self.grad_norm = []
 
 
        
class Trainer:
    def __init__(self, model, optimizer, device, train_loader, valid_loader, epochs, callbacks=[]):
        self.model        = model
        self.optimizer    = optimizer
        self.device       = device
        self.train_loader = train_loader
        self.valid_loader = valid_loader
        self.epochs       = epochs
        self.callbacks    = callbacks

    def _call(self, hook, *args):
        for cb in self.callbacks:
            fn = getattr(cb, hook, None)
            if fn:
                fn(*args)

    def fit(self):
        for E in range(self.epochs):
            self.model.train()
            for batch in self.train_loader:
                batch = {k: v.to(self.device) for k, v in batch.items()}
                self._call("on_train_batch_start", batch)

                pred = self.model(batch)
                loss_avg, loss_std_hi, loss_std_lo = do_loss(criterion, batch, pred)

                loss_avg.backward()
                self._call("on_after_backward", self.model)

                self.optimizer.step()
                self.optimizer.zero_grad()

                self._call("on_train_batch_end", batch,
                           pred, (loss_avg, loss_std_lo, loss_std_hi))

            val_avg, _, _ = do_validation(criterion, self.model, self.valid_loader, self.device)
            self._call("on_validation_end", val_avg, self.model)
            
 
  
            
            
plot_cb = PlotterCallback(PLOTTER)

trainer = Trainer(
    epochs=n_epochs,
    model=model,
    optimizer=optim,
    device=DEVICE,
    train_loader=loader_train,
    valid_loader=loader_valid,
    callbacks=[plot_cb],
)

trainer.fit()
PLOTTER.run_script_spin()