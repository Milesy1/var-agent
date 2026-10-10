# Monte Carlo Simulation in Energy Risk Management

Monte Carlo simulation is a computational technique that uses random sampling to model the probability of different outcomes in systems with inherent uncertainty.

## How It Works
1. Define statistical properties of risk factors (price, volatility, correlation)
2. Generate thousands of random scenarios using those properties
3. Calculate portfolio P&L for each scenario
4. Analyse the distribution of outcomes

## Applications in Energy Trading

### Price Risk
Simulate future price paths for crude oil, natural gas, power, and refined products. Capture mean reversion, seasonality, and volatility clustering.

### Options Pricing
Value complex energy derivatives where analytical solutions do not exist. Monte Carlo is the standard approach for path-dependent options like Asian options and swing contracts.

### VaR Calculation
Generate full P&L distribution from simulated price paths. Estimate VaR and CVaR (Expected Shortfall) without distributional assumptions.

### Portfolio Optimisation
Simulate correlated moves across a multi-commodity portfolio. Identify diversification benefits and concentration risks.

## Energy-Specific Considerations
- Mean reversion: Energy prices tend to revert to long-run marginal cost
- Jump diffusion: Model price spikes common in power and gas markets
- Seasonality: Heating oil and natural gas demand follows weather patterns
- Correlation structure: Crude oil, refined products, and shipping freight move together

## Computational Approach
- Geometric Brownian Motion (GBM) for oil and liquid commodities
- Ornstein-Uhlenbeck (mean-reverting) for power and gas
- Cholesky decomposition for correlated multi-asset simulation
- Variance reduction techniques: antithetic variates, control variates

## Validation
Monte Carlo models require backtesting against historical data. Model risk is significant in energy markets where regime changes occur.
