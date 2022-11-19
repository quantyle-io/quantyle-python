import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import skewnorm

class BacktestAnalysis():
    def __init__(self, performance_metrics):
        self.performance_metrics = performance_metrics
    
    def plot_trade_profit_distribution(self, bins=25, color='C0'):
        distribution = self.performance_metrics["trade_profit_distribution"]
        n_trades = distribution["n_trades"]
        mean = distribution["mean"]
        variance = distribution["variance"]
        skew = distribution["skew"]
        x = np.linspace(distribution["min_profit"], distribution["max_profit"], 100)
        SkewNormDistParams = skewnorm.fit(distribution["trade_profits"])
        p = skewnorm.pdf(x, *SkewNormDistParams)

        fig, ax = plt.subplots(figsize=(8, 6))
        stats = "num(trades): {n_trades}, mean: {mean:.2f} %,\n variance: {variance:.2f}, skew: {skew:.2f}".format(n_trades=n_trades, mean=mean, variance=variance, skew=skew)
        title = "Precent Profit Distribution\n" + stats
        ax.hist(distribution["trade_profits"], bins=bins, density=True, color=color)
        ax.plot(x, p, color='black', label='skewnorm fit')
        ax.set_xlabel("% profit")
        ax.set_ylabel("frequency")
        ax.set_title(title)
        ax.legend(loc='best')
    
    def plot_trade_length_distribution(self, bins=25, color='C1'):
        distribution = self.performance_metrics["trade_length_distribution"]
        n_trades = distribution["n_trades"]
        mean = distribution["mean"]
        variance = distribution["variance"]
        skew = distribution["skew"]
        x = np.linspace(distribution["min_length"], distribution["max_length"], 100)
        SkewNormDistParams = skewnorm.fit(distribution["trade_lengths"])
        p = skewnorm.pdf(x, *SkewNormDistParams)

        fig, ax = plt.subplots(figsize=(8, 6))
        stats = "num(trades): {n_trades}, mean: {mean:.2f} %,\n variance: {variance:.2f}, skew: {skew:.2f}".format(n_trades=n_trades, mean=mean, variance=variance, skew=skew)
        title = "Precent Profit Distribution\n" + stats
        ax.hist(distribution["trade_lengths"], bins=bins, density=True, color=color)
        ax.plot(x, p, color='black', label='skewnorm fit')
        ax.set_xlabel("trade length [min]")
        ax.set_ylabel("frequency")
        ax.set_title(title)
        ax.legend(loc='best')
    
    def plot_trade_length_vs_profit(self):
        lengths = self.performance_metrics["trade_length_distribution"]["trade_lengths"]
        profits = self.performance_metrics["trade_profit_distribution"]["trade_profits"]
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(lengths, profits)
        ax.set_xlabel("trade length [min]")
        ax.set_ylabel("% profit")



