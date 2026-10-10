# Value at Risk (VaR) in Energy Trading

Value at Risk (VaR) is a statistical measure that quantifies the potential loss in value of a portfolio over a defined period for a given confidence interval.

## Definition
VaR answers the question: "What is the maximum loss we would expect to incur over a given time horizon, with a given level of confidence?"

For example, a 1-day 95% VaR of $1 million means there is a 95% probability that the portfolio will not lose more than $1 million in a single trading day.

## Common VaR Methods

### Historical Simulation
Uses actual historical returns to simulate potential future losses. No distributional assumptions required. Captures fat tails and volatility clustering naturally.

### Parametric (Variance-Covariance)
Assumes returns are normally distributed. Fast to compute. Underestimates tail risk in energy markets due to price spikes.

### Monte Carlo Simulation
Generates thousands of random price scenarios based on statistical assumptions. Most flexible method. Captures non-linear risk from options and complex derivatives.

## VaR in Energy Markets
Energy commodities exhibit unique risk characteristics:
- Price spikes from supply/demand shocks
- Seasonal demand patterns (heating oil, natural gas)
- Geopolitical risk (oil supply disruptions)
- Weather-driven demand volatility

Standard VaR models often underestimate energy market risk due to heavy-tailed price distributions. Energy traders supplement VaR with Conditional VaR (CVaR), also known as Expected Shortfall.

## Limitations
- VaR does not capture losses beyond the confidence threshold (tail risk)
- Assumes liquid markets and normal trading conditions
- Historical VaR is backward-looking and may miss structural market changes
- Correlation assumptions break down in stress scenarios
