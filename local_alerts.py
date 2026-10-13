import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pandas as pd

from data_fetcher import DataFetcher

logger = logging.getLogger(__name__)


class LocalAlertEngine:
    """TradingView-free alert engine backed by yfinance data."""

    RULE_TYPES = {
        "analysis_signal",
        "price_above",
        "price_below",
        "rsi_above",
        "rsi_below",
        "sma_cross_above",
        "sma_cross_below",
    }

    def __init__(self, rules_path="local_alerts.json", events_path="local_alert_events.json"):
        self.rules_path = Path(rules_path)
        self.events_path = Path(events_path)
        self.rules = self.load_rules()
        self.events = self.load_events()

    def load_rules(self):
        if not self.rules_path.exists():
            return []

        try:
            with self.rules_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Error loading local alerts: {e}")
            return []

    def load_events(self):
        if not self.events_path.exists():
            return []

        try:
            with self.events_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Error loading local alert events: {e}")
            return []

    def save_rules(self):
        with self.rules_path.open("w", encoding="utf-8") as f:
            json.dump(self.rules, f, indent=2)

    def list_rules(self):
        return self.rules

    def list_events(self, limit=25):
        return self.events[-limit:]

    def add_rule(self, rule):
        normalized = self._normalize_rule(rule)
        self.rules.append(normalized)
        self.save_rules()
        return normalized

    def delete_rule(self, rule_id):
        original_count = len(self.rules)
        self.rules = [rule for rule in self.rules if rule.get("id") != rule_id]
        deleted = len(self.rules) != original_count
        if deleted:
            self.save_rules()
        return deleted

    def set_enabled(self, rule_id, enabled):
        for rule in self.rules:
            if rule.get("id") == rule_id:
                rule["enabled"] = bool(enabled)
                self.save_rules()
                return rule
        return None

    def scan(self, execute_callback=None, analysis_callback=None):
        events = []
        changed = False

        for rule in self.rules:
            if not rule.get("enabled", True):
                continue

            try:
                df = None
                analysis = None
                if rule["type"] == "analysis_signal":
                    if not analysis_callback:
                        raise ValueError("analysis_callback is required for analysis_signal alerts")
                    analysis = analysis_callback(rule["symbol"])
                else:
                    df = DataFetcher.fetch_stock_data(
                        rule["symbol"],
                        period=rule.get("period", "6mo"),
                        interval=rule.get("interval", "1d"),
                    )

                triggered, details = self.evaluate_rule(rule, df, analysis)
                rule["last_checked_at"] = datetime.now().isoformat()
                rule["last_value"] = details.get("value")
                changed = True

                if triggered and not self._in_cooldown(rule):
                    event = self._build_event(rule, details)
                    rule["last_triggered_at"] = event["triggered_at"]
                    changed = True

                    if execute_callback and rule.get("execute_trade", True) and event["signal"] in {"BUY", "SELL"}:
                        event["trade"] = execute_callback(
                            rule["symbol"],
                            event["signal"],
                            float(event.get("confidence", rule.get("confidence", 0.7))),
                        )

                    events.append(event)
                    self._record_event(event)
                    logger.info(
                        "Local alert triggered: %s %s via %s",
                        rule["symbol"],
                        event["signal"],
                        rule["type"],
                    )

            except Exception as e:
                rule["last_error"] = str(e)
                rule["last_checked_at"] = datetime.now().isoformat()
                changed = True
                logger.error(f"Error scanning local alert {rule.get('id')}: {e}")

        if changed:
            self.save_rules()

        return events

    def evaluate_rule(self, rule, df=None, analysis=None):
        if rule["type"] == "analysis_signal":
            return self._evaluate_analysis_signal(rule, analysis)

        if df is None or df.empty:
            return False, {"reason": "No market data"}

        close = self._numeric_series(df, "Close")
        if len(close) < 2:
            return False, {"reason": "Not enough data"}

        rule_type = rule["type"]

        if rule_type == "price_above":
            value = float(close.iloc[-1])
            threshold = float(rule["threshold"])
            return value > threshold, {"value": value, "threshold": threshold}

        if rule_type == "price_below":
            value = float(close.iloc[-1])
            threshold = float(rule["threshold"])
            return value < threshold, {"value": value, "threshold": threshold}

        if rule_type in {"rsi_above", "rsi_below"}:
            rsi = self._rsi(close, int(rule.get("rsi_window", 14)))
            value = float(rsi.iloc[-1])
            threshold = float(rule["threshold"])
            if pd.isna(value):
                return False, {"reason": "RSI not ready"}
            if rule_type == "rsi_above":
                return value > threshold, {"value": value, "threshold": threshold}
            return value < threshold, {"value": value, "threshold": threshold}

        if rule_type in {"sma_cross_above", "sma_cross_below"}:
            short_window = int(rule.get("short_window", 20))
            long_window = int(rule.get("long_window", 50))
            if len(close) < long_window + 1:
                return False, {"reason": "Not enough data for SMA windows"}

            short_sma = close.rolling(short_window).mean()
            long_sma = close.rolling(long_window).mean()
            previous_delta = short_sma.iloc[-2] - long_sma.iloc[-2]
            current_delta = short_sma.iloc[-1] - long_sma.iloc[-1]

            details = {
                "value": float(current_delta),
                "short_sma": float(short_sma.iloc[-1]),
                "long_sma": float(long_sma.iloc[-1]),
            }

            if pd.isna(previous_delta) or pd.isna(current_delta):
                return False, {"reason": "SMA not ready"}

            if rule_type == "sma_cross_above":
                return previous_delta <= 0 and current_delta > 0, details
            return previous_delta >= 0 and current_delta < 0, details

        return False, {"reason": f"Unsupported rule type: {rule_type}"}

    def _normalize_rule(self, rule):
        symbol = str(rule.get("symbol", "")).strip().upper()
        rule_type = str(rule.get("type", "")).strip()
        signal = str(rule.get("signal", "AUTO")).strip().upper()

        if not symbol:
            raise ValueError("symbol is required")
        if rule_type not in self.RULE_TYPES:
            raise ValueError(f"type must be one of: {', '.join(sorted(self.RULE_TYPES))}")
        if rule_type == "analysis_signal":
            if signal not in {"AUTO", "BUY", "SELL", "NEUTRAL"}:
                raise ValueError("analysis signal must be AUTO, BUY, SELL, or NEUTRAL")
        elif signal not in {"BUY", "SELL"}:
            raise ValueError("signal must be BUY or SELL")
        if rule_type in {"price_above", "price_below", "rsi_above", "rsi_below"}:
            float(rule["threshold"])

        normalized = {
            "id": rule.get("id") or uuid4().hex,
            "name": rule.get("name") or f"{symbol} {rule_type} {signal}",
            "symbol": symbol,
            "type": rule_type,
            "signal": signal,
            "confidence": float(rule.get("confidence", 0.7)),
            "enabled": bool(rule.get("enabled", True)),
            "execute_trade": bool(rule.get("execute_trade", rule_type != "analysis_signal")),
            "cooldown_minutes": int(rule.get("cooldown_minutes", 240)),
            "period": rule.get("period", "6mo"),
            "interval": rule.get("interval", "1d"),
            "created_at": rule.get("created_at") or datetime.now().isoformat(),
            "last_checked_at": rule.get("last_checked_at"),
            "last_triggered_at": rule.get("last_triggered_at"),
            "last_value": rule.get("last_value"),
        }

        optional_fields = [
            "threshold",
            "rsi_window",
            "short_window",
            "long_window",
            "min_confidence",
        ]
        for field in optional_fields:
            if field in rule:
                normalized[field] = rule[field]

        return normalized

    def _in_cooldown(self, rule):
        last_triggered = rule.get("last_triggered_at")
        if not last_triggered:
            return False

        cooldown = timedelta(minutes=int(rule.get("cooldown_minutes", 240)))
        try:
            triggered_at = datetime.fromisoformat(last_triggered)
            return datetime.now() - triggered_at < cooldown
        except ValueError:
            return False

    def _build_event(self, rule, details):
        signal = details.get("signal") or rule["signal"]
        confidence = details.get("confidence", rule.get("confidence", 0.7))
        return {
            "rule_id": rule["id"],
            "name": rule["name"],
            "symbol": rule["symbol"],
            "signal": signal,
            "confidence": float(confidence),
            "type": rule["type"],
            "details": details,
            "execute_trade": bool(rule.get("execute_trade", True)),
            "triggered_at": datetime.now().isoformat(),
        }

    def _record_event(self, event):
        self.events.append(event)
        self.events = self.events[-100:]
        with self.events_path.open("w", encoding="utf-8") as f:
            json.dump(self.events, f, indent=2, default=str)

    def _evaluate_analysis_signal(self, rule, analysis):
        if not analysis:
            return False, {"reason": "No analysis returned"}

        synthesized = analysis.get("synthesized", {})
        signal = str(synthesized.get("signal", "NEUTRAL")).upper()
        raw_confidence = float(synthesized.get("confidence", 0))
        min_confidence = float(rule.get("min_confidence", 65))
        target_signal = rule.get("signal", "AUTO")

        if signal not in {"BUY", "SELL", "NEUTRAL"}:
            signal = "NEUTRAL"

        matches_signal = target_signal == "AUTO" or signal == target_signal
        is_actionable = signal in {"BUY", "SELL"} and raw_confidence >= min_confidence

        return matches_signal and is_actionable, {
            "value": raw_confidence,
            "signal": signal,
            "confidence": raw_confidence / 100,
            "confidence_percent": raw_confidence,
            "min_confidence": min_confidence,
            "reasoning": synthesized.get("reasoning"),
            "action_summary": synthesized.get("action_summary"),
            "key_factors": synthesized.get("key_factors", []),
            "risk_factors": synthesized.get("risk_factors", []),
            "price_targets": synthesized.get("price_targets", {}),
        }

    @staticmethod
    def _numeric_series(df, column):
        series = df[column]
        if isinstance(series, pd.DataFrame):
            series = series.iloc[:, 0]
        return pd.to_numeric(series, errors="coerce").dropna()

    @staticmethod
    def _rsi(close, window=14):
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
