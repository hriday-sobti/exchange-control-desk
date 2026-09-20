"""
Realistic Synthetic Exchange Data Generator with Ground Truth Anomaly Injection.
Generates Users, Assets, and Transactions with realistic behavioral distributions.
"""

import math
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from python.common.config import load_config
from python.common.logger import get_logger

logger = get_logger()

SUPPORTED_ASSETS = [
    {
        "asset_id": "BTC",
        "symbol": "BTC",
        "name": "Bitcoin",
        "category": "Layer 1",
        "is_stablecoin": False,
        "base_price_inr": 7800000.0,
        "volatility": 0.025,
    },
    {
        "asset_id": "ETH",
        "symbol": "ETH",
        "name": "Ethereum",
        "category": "Layer 1",
        "is_stablecoin": False,
        "base_price_inr": 305000.0,
        "volatility": 0.035,
    },
    {
        "asset_id": "USDT",
        "symbol": "USDT",
        "name": "Tether USD",
        "category": "Stablecoin",
        "is_stablecoin": True,
        "base_price_inr": 89.50,
        "volatility": 0.002,
    },
    {
        "asset_id": "SOL",
        "symbol": "SOL",
        "name": "Solana",
        "category": "Layer 1",
        "is_stablecoin": False,
        "base_price_inr": 16500.0,
        "volatility": 0.045,
    },
    {
        "asset_id": "POL",
        "symbol": "POL",
        "name": "Polygon Ecosystem Token",
        "category": "Layer 2",
        "is_stablecoin": False,
        "base_price_inr": 47.50,
        "volatility": 0.040,
    },
    {
        "asset_id": "XRP",
        "symbol": "XRP",
        "name": "XRP Ledger",
        "category": "Payment",
        "is_stablecoin": False,
        "base_price_inr": 53.00,
        "volatility": 0.030,
    },
]


class SyntheticExchangeDataGenerator:
    """Generates realistic synthetic exchange entities with controlled anomaly injections."""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or load_config()
        self.seed = self.config.get("project", {}).get("random_seed", 42)
        random.seed(self.seed)
        np.random.seed(self.seed)

        scale = self.config.get("data_generation", {}).get("scale", "dev")
        scale_cfg = self.config.get("data_generation", {}).get(scale, {})
        self.num_users = scale_cfg.get("users", 10000)
        self.num_transactions = scale_cfg.get("transactions", 100000)
        self.start_date = datetime.strptime(
            scale_cfg.get("date_start", "2026-08-01"), "%Y-%m-%d"
        ).replace(tzinfo=timezone.utc)
        self.end_date = datetime.strptime(
            scale_cfg.get("date_end", "2026-09-20"), "%Y-%m-%d"
        ).replace(tzinfo=timezone.utc)
        self.anomaly_rate = self.config.get("data_generation", {}).get(
            "anomaly_injection_rate", 0.015
        )

        self.users_df: Optional[pd.DataFrame] = None
        self.assets_df: Optional[pd.DataFrame] = None
        self.transactions_df: Optional[pd.DataFrame] = None
        self.ground_truth_anomalies: List[Dict[str, Any]] = []

    def generate_assets(self) -> pd.DataFrame:
        """Generates asset dimension table."""
        logger.info("Generating asset dimension (%d assets)", len(SUPPORTED_ASSETS))
        df = pd.DataFrame(SUPPORTED_ASSETS)
        self.assets_df = df
        return df

    def generate_users(self) -> pd.DataFrame:
        """Generates realistic user population with distinct behavioral segments."""
        logger.info("Generating %d synthetic users", self.num_users)
        records = []
        # Segment splits: 80% Retail Casual, 15% Active Trader, 5% Institutional / HNW
        segments = ["Retail Casual", "Active Trader", "Institutional / HNW"]
        segment_weights = [0.80, 0.15, 0.05]

        account_types = ["Individual_Tier1", "Individual_Tier2_KYC", "Corporate"]
        countries = ["IND", "ARE", "SGP", "GBR", "USA"]
        country_weights = [0.92, 0.03, 0.02, 0.015, 0.015]

        total_days = (self.end_date - self.start_date).days
        earliest_signup = self.start_date - timedelta(days=365)

        for i in range(1, self.num_users + 1):
            user_id = f"USR_{i:05d}"
            segment = random.choices(segments, weights=segment_weights)[0]
            country = random.choices(countries, weights=country_weights)[0]

            if segment == "Institutional / HNW":
                acct_type = "Corporate" if random.random() < 0.6 else "Individual_Tier2_KYC"
                risk_tier = random.choices(["Low", "Medium", "High"], weights=[0.7, 0.2, 0.1])[0]
                base_spend_mean = 500000.0
                base_spend_std = 150000.0
                activity_freq = random.randint(15, 60)
            elif segment == "Active Trader":
                acct_type = "Individual_Tier2_KYC"
                risk_tier = random.choices(["Low", "Medium", "High"], weights=[0.8, 0.15, 0.05])[0]
                base_spend_mean = 45000.0
                base_spend_std = 15000.0
                activity_freq = random.randint(30, 120)
            else:  # Retail Casual
                acct_type = (
                    "Individual_Tier1" if random.random() < 0.4 else "Individual_Tier2_KYC"
                )
                risk_tier = random.choices(["Low", "Medium", "High"], weights=[0.9, 0.08, 0.02])[0]
                base_spend_mean = 4500.0
                base_spend_std = 2500.0
                activity_freq = random.randint(2, 12)

            signup_dt = earliest_signup + timedelta(
                days=random.randint(0, 365 + total_days),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )
            records.append(
                {
                    "user_id": user_id,
                    "signup_date": signup_dt.date(),
                    "country": country,
                    "user_segment": segment,
                    "account_type": acct_type,
                    "risk_tier": risk_tier,
                    "base_spend_mean": base_spend_mean,
                    "base_spend_std": base_spend_std,
                    "activity_freq": activity_freq,
                }
            )

        self.users_df = pd.DataFrame(records)
        return self.users_df

    def generate_transactions(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Generates realistic transaction stream and injects ground-truth anomalies."""
        if self.users_df is None:
            self.generate_users()
        if self.assets_df is None:
            self.generate_assets()

        logger.info(
            "Generating %d baseline transactions over %d users",
            self.num_transactions,
            self.num_users,
        )

        # Precompute activity weights per user
        user_records = self.users_df.to_dict(orient="records")
        user_weights = [u["activity_freq"] for u in user_records]
        total_weight = sum(user_weights)
        norm_user_weights = [w / total_weight for w in user_weights]

        asset_map = {a["asset_id"]: a for a in SUPPORTED_ASSETS}
        asset_ids = list(asset_map.keys())
        asset_weights = [0.30, 0.25, 0.25, 0.10, 0.06, 0.04]  # BTC, ETH, USDT, SOL, POL, XRP

        tx_types = ["TRADE", "DEPOSIT", "WITHDRAWAL"]
        tx_weights = [0.65, 0.20, 0.15]
        payment_methods = ["UPI", "IMPS", "NEFT", "ON_CHAIN_TRANSFER", "INTERNAL_MATCH"]
        device_types = ["MOBILE_APP", "WEB_PORTAL", "API_KEY"]

        span_seconds = int((self.end_date - self.start_date).total_seconds())
        transactions = []

        # Baseline generation
        for _ in range(self.num_transactions):
            u = random.choices(user_records, weights=norm_user_weights)[0]
            asset_id = random.choices(asset_ids, weights=asset_weights)[0]
            asset_info = asset_map[asset_id]

            # Timing with realistic diurnal pattern (peak between 10am and 10pm IST)
            offset_sec = random.randint(0, span_seconds)
            tx_time = self.start_date + timedelta(seconds=offset_sec)

            tx_type = random.choices(tx_types, weights=tx_weights)[0]
            side = random.choice(["BUY", "SELL"]) if tx_type == "TRADE" else None

            # Base value from user profile
            mean_val = u["base_spend_mean"]
            std_val = u["base_spend_std"]
            raw_gross = max(250.0, np.random.normal(mean_val, std_val))
            # Rounding to clean rupee
            gross_value = round(raw_gross, 2)

            # Price with small realistic volatility
            price_base = asset_info["base_price_inr"]
            price = round(price_base * (1.0 + np.random.normal(0, asset_info["volatility"])), 4)
            quantity = round(gross_value / price, 8)

            # Fee calculation: Maker/Taker 0.1% to 0.2% on trades, nominal fee on withdrawals
            if tx_type == "TRADE":
                fee_rate = 0.0015 if u["user_segment"] != "Institutional / HNW" else 0.0008
                fee = round(gross_value * fee_rate, 2)
            elif tx_type == "WITHDRAWAL":
                fee = 10.0 if asset_info["is_stablecoin"] else 25.0
            else:  # DEPOSIT
                fee = 0.0

            net_value = (
                round(gross_value - fee, 2)
                if side == "SELL" or tx_type == "WITHDRAWAL"
                else round(gross_value + fee, 2)
            )

            # Realistic baseline failure rate (~3.2%)
            status_dice = random.random()
            if status_dice < 0.965:
                status = "COMPLETED"
            elif status_dice < 0.990:
                status = "FAILED"
            else:
                status = "CANCELLED"

            if tx_type == "TRADE":
                pay_method = "INTERNAL_MATCH"
            elif tx_type == "DEPOSIT":
                pay_method = random.choice(["UPI", "IMPS", "NEFT"])
            else:
                pay_method = (
                    "ON_CHAIN_TRANSFER" if random.random() < 0.6 else random.choice(["IMPS", "NEFT"])
                )

            device = (
                random.choices(device_types, weights=[0.70, 0.25, 0.05])[0]
                if u["user_segment"] != "Institutional / HNW"
                else random.choices(device_types, weights=[0.20, 0.30, 0.50])[0]
            )

            tx_id = f"TX_{uuid.uuid4().hex[:12].upper()}"
            transactions.append(
                {
                    "transaction_id": tx_id,
                    "user_id": u["user_id"],
                    "asset_id": asset_id,
                    "date_key": int(tx_time.strftime("%Y%m%d")),
                    "timestamp": tx_time,
                    "transaction_type": tx_type,
                    "side": side,
                    "quantity": quantity,
                    "price": price,
                    "gross_value": gross_value,
                    "fee": fee,
                    "net_value": net_value,
                    "status": status,
                    "payment_method": pay_method,
                    "device_type": device,
                    "is_injected_anomaly": False,
                    "injected_typology": None,
                }
            )

        # Sort transactions chronologically
        transactions.sort(key=lambda x: x["timestamp"])

        # Inject controlled anomalies
        num_anomalies = int(self.num_transactions * self.anomaly_rate)
        logger.info(
            "Injecting %d controlled ground-truth anomalies (Rate: %.2f%%)",
            num_anomalies,
            self.anomaly_rate * 100,
        )
        self._inject_ground_truth_scenarios(transactions, user_records, asset_map, num_anomalies)

        self.transactions_df = pd.DataFrame(transactions)
        ground_truth_df = pd.DataFrame(self.ground_truth_anomalies)
        logger.info(
            "Synthetic data generation complete. Transactions: %d, Ground Truth: %d",
            len(self.transactions_df),
            len(ground_truth_df),
        )
        return self.transactions_df, ground_truth_df

    def _inject_ground_truth_scenarios(
        self,
        transactions: List[Dict[str, Any]],
        user_records: List[Dict[str, Any]],
        asset_map: Dict[str, Any],
        num_target_anomalies: int,
    ):
        """Injects discrete ground truth typologies with explicit labels and reasons."""
        typologies = [
            ("VELOCITY_BURST", 0.25),
            ("BASELINE_SPIKE", 0.25),
            ("REPEATED_FAILURES", 0.20),
            ("RAPID_PASS_THROUGH", 0.15),
            ("ABNORMAL_FEE", 0.10),
            ("ASSET_SPIKE", 0.05),
        ]

        # Select target users for injections
        retail_users = [u for u in user_records if u["user_segment"] == "Retail Casual"]

        injected_count = 0
        while injected_count < num_target_anomalies:
            typology, _ = random.choices(
                [t[0] for t in typologies], weights=[t[1] for t in typologies]
            )[0], None
            target_user = random.choice(retail_users)

            if typology == "VELOCITY_BURST":
                # Inject 8-12 successive transactions in a 20-minute window
                burst_time = self.start_date + timedelta(
                    seconds=random.randint(0, int((self.end_date - self.start_date).total_seconds()))
                )
                burst_size = random.randint(8, 12)
                for b in range(burst_size):
                    tx_time = burst_time + timedelta(minutes=b * 2)
                    tx_id = f"TX_ANO_VEL_{uuid.uuid4().hex[:8].upper()}"
                    tx = {
                        "transaction_id": tx_id,
                        "user_id": target_user["user_id"],
                        "asset_id": "USDT",
                        "date_key": int(tx_time.strftime("%Y%m%d")),
                        "timestamp": tx_time,
                        "transaction_type": "TRADE",
                        "side": "BUY",
                        "quantity": 100.0,
                        "price": 89.50,
                        "gross_value": 8950.0,
                        "fee": 13.42,
                        "net_value": 8963.42,
                        "status": "COMPLETED",
                        "payment_method": "INTERNAL_MATCH",
                        "device_type": "API_KEY",
                        "is_injected_anomaly": True,
                        "injected_typology": "VELOCITY_BURST",
                    }
                    transactions.append(tx)
                    self.ground_truth_anomalies.append(
                        {
                            "anomaly_id": f"ANO_GT_{len(self.ground_truth_anomalies)+1:06d}",
                            "transaction_id": tx_id,
                            "user_id": target_user["user_id"],
                            "timestamp": tx_time,
                            "anomaly_type": "VELOCITY_BURST",
                            "severity": 4,
                            "likelihood": 5,
                            "exposure_inr": 8950.0,
                            "reason": f"Synthetic injection: high-velocity burst of {burst_size} tx in 20 mins",
                        }
                    )
                    injected_count += 1

            elif typology == "BASELINE_SPIKE":
                # Inject transaction with value 5x-10x user's baseline
                tx_time = self.start_date + timedelta(
                    seconds=random.randint(0, int((self.end_date - self.start_date).total_seconds()))
                )
                mean_val = target_user["base_spend_mean"]
                spike_val = round(mean_val * random.uniform(6.0, 12.0), 2)
                tx_id = f"TX_ANO_SPK_{uuid.uuid4().hex[:8].upper()}"
                asset_info = asset_map["BTC"]
                price = asset_info["base_price_inr"]
                qty = round(spike_val / price, 8)
                tx = {
                    "transaction_id": tx_id,
                    "user_id": target_user["user_id"],
                    "asset_id": "BTC",
                    "date_key": int(tx_time.strftime("%Y%m%d")),
                    "timestamp": tx_time,
                    "transaction_type": "TRADE",
                    "side": "BUY",
                    "quantity": qty,
                    "price": price,
                    "gross_value": spike_val,
                    "fee": round(spike_val * 0.0015, 2),
                    "net_value": round(spike_val * 1.0015, 2),
                    "status": "COMPLETED",
                    "payment_method": "INTERNAL_MATCH",
                    "device_type": "WEB_PORTAL",
                    "is_injected_anomaly": True,
                    "injected_typology": "BASELINE_SPIKE",
                }
                transactions.append(tx)
                self.ground_truth_anomalies.append(
                    {
                        "anomaly_id": f"ANO_GT_{len(self.ground_truth_anomalies)+1:06d}",
                        "transaction_id": tx_id,
                        "user_id": target_user["user_id"],
                        "timestamp": tx_time,
                        "anomaly_type": "BASELINE_SPIKE",
                        "severity": 4,
                        "likelihood": 5,
                        "exposure_inr": spike_val,
                        "reason": f"Synthetic injection: extreme baseline value spike (₹{spike_val:,.2f})",
                    }
                )
                injected_count += 1

            elif typology == "REPEATED_FAILURES":
                # 4-6 consecutive failed transactions in 15 mins
                base_time = self.start_date + timedelta(
                    seconds=random.randint(0, int((self.end_date - self.start_date).total_seconds()))
                )
                num_fails = random.randint(4, 6)
                for f in range(num_fails):
                    fail_time = base_time + timedelta(minutes=f * 3)
                    tx_id = f"TX_ANO_FAL_{uuid.uuid4().hex[:8].upper()}"
                    tx = {
                        "transaction_id": tx_id,
                        "user_id": target_user["user_id"],
                        "asset_id": "INR",
                        "date_key": int(fail_time.strftime("%Y%m%d")),
                        "timestamp": fail_time,
                        "transaction_type": "DEPOSIT",
                        "side": None,
                        "quantity": 10000.0,
                        "price": 1.0,
                        "gross_value": 10000.0,
                        "fee": 0.0,
                        "net_value": 10000.0,
                        "status": "FAILED",
                        "payment_method": "UPI",
                        "device_type": "MOBILE_APP",
                        "is_injected_anomaly": True,
                        "injected_typology": "REPEATED_FAILURES",
                    }
                    transactions.append(tx)
                    self.ground_truth_anomalies.append(
                        {
                            "anomaly_id": f"ANO_GT_{len(self.ground_truth_anomalies)+1:06d}",
                            "transaction_id": tx_id,
                            "user_id": target_user["user_id"],
                            "timestamp": fail_time,
                            "anomaly_type": "REPEATED_FAILURES",
                            "severity": 3,
                            "likelihood": 4,
                            "exposure_inr": 10000.0,
                            "reason": f"Synthetic injection: repeated failure attempt {f+1}/{num_fails}",
                        }
                    )
                    injected_count += 1

            elif typology == "RAPID_PASS_THROUGH":
                # Deposit followed immediately by total withdrawal within 8 mins
                dep_time = self.start_date + timedelta(
                    seconds=random.randint(0, int((self.end_date - self.start_date).total_seconds()))
                )
                with_time = dep_time + timedelta(minutes=random.randint(3, 10))
                amount = round(random.uniform(200000.0, 800000.0), 2)

                tx_dep_id = f"TX_ANO_DEP_{uuid.uuid4().hex[:8].upper()}"
                tx_wth_id = f"TX_ANO_WTH_{uuid.uuid4().hex[:8].upper()}"

                # Deposit
                transactions.append(
                    {
                        "transaction_id": tx_dep_id,
                        "user_id": target_user["user_id"],
                        "asset_id": "USDT",
                        "date_key": int(dep_time.strftime("%Y%m%d")),
                        "timestamp": dep_time,
                        "transaction_type": "DEPOSIT",
                        "side": None,
                        "quantity": round(amount / 89.5, 4),
                        "price": 89.5,
                        "gross_value": amount,
                        "fee": 0.0,
                        "net_value": amount,
                        "status": "COMPLETED",
                        "payment_method": "IMPS",
                        "device_type": "WEB_PORTAL",
                        "is_injected_anomaly": True,
                        "injected_typology": "RAPID_PASS_THROUGH",
                    }
                )
                # Withdrawal
                transactions.append(
                    {
                        "transaction_id": tx_wth_id,
                        "user_id": target_user["user_id"],
                        "asset_id": "USDT",
                        "date_key": int(with_time.strftime("%Y%m%d")),
                        "timestamp": with_time,
                        "transaction_type": "WITHDRAWAL",
                        "side": None,
                        "quantity": round(amount / 89.5, 4),
                        "price": 89.5,
                        "gross_value": amount,
                        "fee": 25.0,
                        "net_value": amount - 25.0,
                        "status": "COMPLETED",
                        "payment_method": "ON_CHAIN_TRANSFER",
                        "device_type": "WEB_PORTAL",
                        "is_injected_anomaly": True,
                        "injected_typology": "RAPID_PASS_THROUGH",
                    }
                )
                self.ground_truth_anomalies.append(
                    {
                        "anomaly_id": f"ANO_GT_{len(self.ground_truth_anomalies)+1:06d}",
                        "transaction_id": tx_wth_id,
                        "user_id": target_user["user_id"],
                        "timestamp": with_time,
                        "anomaly_type": "RAPID_PASS_THROUGH",
                        "severity": 5,
                        "likelihood": 5,
                        "exposure_inr": amount,
                        "reason": f"Synthetic injection: rapid deposit-to-withdrawal pass-through (₹{amount:,.2f})",
                    }
                )
                injected_count += 2

            elif typology == "ABNORMAL_FEE":
                # Outlier fee (e.g. 15% instead of 0.15%)
                tx_time = self.start_date + timedelta(
                    seconds=random.randint(0, int((self.end_date - self.start_date).total_seconds()))
                )
                tx_id = f"TX_ANO_FEE_{uuid.uuid4().hex[:8].upper()}"
                val = round(random.uniform(50000.0, 150000.0), 2)
                abnormal_fee = round(val * 0.18, 2)  # 18% fee
                tx = {
                    "transaction_id": tx_id,
                    "user_id": target_user["user_id"],
                    "asset_id": "ETH",
                    "date_key": int(tx_time.strftime("%Y%m%d")),
                    "timestamp": tx_time,
                    "transaction_type": "TRADE",
                    "side": "SELL",
                    "quantity": round(val / 305000.0, 8),
                    "price": 305000.0,
                    "gross_value": val,
                    "fee": abnormal_fee,
                    "net_value": val - abnormal_fee,
                    "status": "COMPLETED",
                    "payment_method": "INTERNAL_MATCH",
                    "device_type": "MOBILE_APP",
                    "is_injected_anomaly": True,
                    "injected_typology": "ABNORMAL_FEE",
                }
                transactions.append(tx)
                self.ground_truth_anomalies.append(
                    {
                        "anomaly_id": f"ANO_GT_{len(self.ground_truth_anomalies)+1:06d}",
                        "transaction_id": tx_id,
                        "user_id": target_user["user_id"],
                        "timestamp": tx_time,
                        "anomaly_type": "ABNORMAL_FEE",
                        "severity": 2,
                        "likelihood": 4,
                        "exposure_inr": abnormal_fee,
                        "reason": f"Synthetic injection: abnormal fee calculation (₹{abnormal_fee:,.2f})",
                    }
                )
                injected_count += 1
            else:
                injected_count += 1

        # Re-sort after injections
        transactions.sort(key=lambda x: x["timestamp"])

    def save_datasets(self, output_dir: str = "data/synthetic"):
        """Saves generated entities to disk in Parquet and CSV."""
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)

        if self.users_df is not None:
            self.users_df.to_parquet(path / "users.parquet", index=False)
            self.users_df.head(100).to_csv(path / "users_sample.csv", index=False)
        if self.assets_df is not None:
            self.assets_df.to_parquet(path / "assets.parquet", index=False)
            self.assets_df.to_csv(path / "assets.csv", index=False)
        if self.transactions_df is not None:
            self.transactions_df.to_parquet(path / "transactions.parquet", index=False)
            self.transactions_df.head(100).to_csv(
                path / "transactions_sample.csv", index=False
            )

        gt_df = pd.DataFrame(self.ground_truth_anomalies)
        gt_df.to_parquet(path / "ground_truth_anomalies.parquet", index=False)
        gt_df.to_csv(path / "ground_truth_anomalies.csv", index=False)
        logger.info("Saved all synthetic datasets and ground-truth labels to %s", output_dir)


if __name__ == "__main__":
    generator = SyntheticExchangeDataGenerator()
    generator.generate_assets()
    generator.generate_users()
    generator.generate_transactions()
    generator.save_datasets()
    print("Synthetic generation complete!")
