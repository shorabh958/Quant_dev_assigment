# Quant Development & Trading Engine

A modular Python quantitative trading-engine prototype covering strategy research,
risk management, execution, market-data abstraction, backtesting, reconciliation,
observability, and SDLC automation.

## Architecture

```text
Market Data
    │
    ├── Yahoo / CSV / Synthetic
    └── Broker WebSocket Adapter
             │
             ▼
     Contract / Rollover
             │
             ▼
      Technical Analysis
             │
             ▼
       Macro Regime Engine
             │
             ▼
     Grid / Stop-Reversal
             │
             ▼
       Risk Management
             │
             ▼
     Cost / Slippage Model
             │
        ┌────┴────┐
        ▼         ▼
    Backtest    Execution
        │         │
        └────┬────┘
             ▼
       Portfolio / P&L
             │
       ┌─────┼─────┐
       ▼     ▼     ▼
   Metrics  Logs  Alerts
             │
             ▼
      Reconciliation
             │
             ▼
        Dashboard