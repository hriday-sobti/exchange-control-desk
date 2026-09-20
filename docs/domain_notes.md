# Domain Notes: Exchange Architecture & Transaction Operations

This document outlines the core domain concepts, exchange mechanisms, and operational flows governing Virtual Digital Asset (VDA) platforms like CoinDCX.

---

## 1. Core VDA Exchange Concepts

1. **Virtual Digital Asset (VDA):** Any code or number or token generated through cryptographic means providing a digital representation of value that can be traded digitally.
2. **Centralized Exchange (CEX):** A centralized platform acting as an intermediary, custodian, and match-maker between buyers and sellers, holding order books in an internal matching engine off-chain for speed and low latency.
3. **Custody & Wallets:**
   - **Hot Wallet:** Connected to the internet, holds a small working balance (typically 5–10% of total reserves) to facilitate automated, near-instant user withdrawal requests.
   - **Cold Storage / Multi-Sig Vaults:** Air-gapped offline storage holding the vast majority (>90%) of exchange assets protected by multi-party computation (MPC) or multi-signature keys.
4. **Order Book & Matching Engine:**
   - Matches buy orders (bids) and sell orders (asks).
   - **Maker:** Provides liquidity to the order book (limit order not immediately filled); pays lower fees.
   - **Taker:** Consumes existing liquidity from the order book (market order filled immediately); pays standard fees.
5. **Fiat On-Ramp / Off-Ramp:**
   - **On-Ramp:** Depositing sovereign fiat currency (INR via IMPS/NEFT/UPI or bank transfer) into exchange fiat ledger balance.
   - **Off-Ramp:** Withdrawing fiat balance back to the user's verified bank account.

---

## 2. Transaction Lifecycle on a VDA Platform

Every interaction on the platform represents a state machine with a specific lifecycle:

```
+-----------------------------------------------------------------------------------+
|                            TRANSACTION LIFECYCLES                                 |
+-----------------------------------------------------------------------------------+
| 1. DEPOSIT (Fiat or Crypto):                                                      |
|    INITIATED -> GATEWAY/CHAIN_PENDING -> CONFIRMED -> CREDITED (or REJECTED)      |
|                                                                                   |
| 2. SPOT TRADE:                                                                    |
|    ORDER_PLACED -> MATCHED -> SETTLED -> BALANCE_UPDATED (or CANCELLED/EXPIRED)    |
|                                                                                   |
| 3. WITHDRAWAL (Fiat or Crypto):                                                   |
|    REQUESTED -> RISK_SCREENING -> 2FA_VERIFIED -> BROADCAST -> COMPLETED/FAILED   |
+-----------------------------------------------------------------------------------+
```

### Key Analytical Fields
- **Gross Value:** Nominal value of transaction before fee deduction (`Quantity * Execution Price`).
- **Fee:** Platform exchange fee deducted in base or target asset.
- **Net Value:** Effective economic value credited or debited to the account balance (`Gross Value - Fee` for sales/withdrawals; `Gross Value + Fee` for purchases).
- **Status:** Final state (`COMPLETED`, `FAILED`, `CANCELLED`, `PENDING`).

---

## 3. Operational Failure Modes & Risks

1. **Payment Gateway Timeouts:** Fiat deposit drops due to banking partner network failures, causing reconciliation discrepancies between banking statements and platform ledger.
2. **Blockchain Network Congestion:** Spikes in gas fees causing delayed on-chain transaction confirmations.
3. **Liquidity Shocks & Slippage:** Thin order book depth during high-volatility events leading to large price slippage and potential user complaints.
4. **Flash Layering / Rapid Drain:** Compromised user credentials where fiat is rapidly deposited, swapped to an unhosted crypto asset, and withdrawn within minutes to bypass manual reviews.
5. **Data Pipeline Inconsistencies:** Dropped websocket events, delayed batch ETL jobs, or missing tick records creating blind spots in operational monitoring.
