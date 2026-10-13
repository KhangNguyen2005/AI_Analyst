import json
import logging
import os
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAnalysisSynthesizer:
    """Synthesize analysis from multiple bots using Google Gemini AI"""

    def __init__(self, api_key=None):
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        # Updated model: gemini-pro is deprecated, using gemini-2.5-flash (latest, free tier)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def synthesize_analysis(self, symbol, technical_analysis, sentiment_analysis,
                           ml_prediction, fundamental_analysis, price_info):
        """Synthesize all analysis types using Gemini"""
        try:
            prompt = f"""You are an expert financial analyst. Analyze the following data for {symbol} and provide a synthesized recommendation.

TECHNICAL ANALYSIS:
{json.dumps(technical_analysis, indent=2, default=str)}

SENTIMENT ANALYSIS:
{json.dumps(sentiment_analysis, indent=2, default=str)}

ML PREDICTION:
{json.dumps(ml_prediction, indent=2, default=str)}

FUNDAMENTAL ANALYSIS:
{json.dumps(fundamental_analysis, indent=2, default=str)}

PRICE INFO:
{json.dumps(price_info, indent=2, default=str)}

Please provide:
1. A synthesized signal (BUY, SELL, NEUTRAL)
2. Your confidence level (0-100%)
3. Key factors supporting your recommendation
4. Risk factors to consider
5. Price targets (next week, next month)
6. A brief summary for trading action

Format your response as a JSON object with the following structure:
{{
    "signal": "BUY|SELL|NEUTRAL",
    "confidence": 0-100,
    "reasoning": "explanation",
    "key_factors": ["factor1", "factor2", ...],
    "risk_factors": ["risk1", "risk2", ...],
    "price_targets": {{
        "1_week": value,
        "1_month": value
    }},
    "action_summary": "Brief summary"
}}"""

            response = self.model.generate_content(prompt)
            response_text = response.text

            # Extract JSON from response
            try:
                # Try to find JSON in the response
                import re
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = json.loads(response_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response
                result = {
                    "signal": "NEUTRAL",
                    "confidence": 50,
                    "reasoning": response_text,
                    "key_factors": [],
                    "risk_factors": [],
                    "price_targets": {},
                    "action_summary": "See reasoning"
                }

            result["symbol"] = symbol

            return result

        except Exception as e:
            logger.error(f"Error synthesizing analysis for {symbol}: {e}")
            return {
                "symbol": symbol,
                "signal": "NEUTRAL",
                "confidence": 0,
                "reasoning": f"Error: {e}",
                "key_factors": [],
                "risk_factors": ["Analysis error occurred"],
                "price_targets": {},
                "action_summary": "Unable to generate recommendation"
            }

    def get_detailed_report(self, symbol, all_analyses):
        """Generate a detailed investment report"""
        try:
            prompt = f"""Generate a comprehensive investment report for {symbol} based on these analyses:

{json.dumps(all_analyses, indent=2, default=str)}

Provide:
1. Executive Summary
2. Technical Analysis Interpretation
3. Sentiment Analysis Insights
4. ML Prediction Assessment
5. Fundamental Strength Assessment
6. Overall Recommendation
7. Entry/Exit Points
8. Risk Management Tips

Be concise but comprehensive."""

            response = self.model.generate_content(prompt)

            return {
                "symbol": symbol,
                "report": response.text,
                "timestamp": pd.Timestamp.now()
            }

        except Exception as e:
            logger.error(f"Error generating report for {symbol}: {e}")
            return {
                "symbol": symbol,
                "report": f"Error generating report: {e}",
                "timestamp": pd.Timestamp.now()
            }

    def identify_opportunities(self, analyses_dict):
        """Identify trading opportunities across multiple stocks"""
        try:
            prompt = f"""Analyze these stocks and identify the top trading opportunities:

{json.dumps(analyses_dict, indent=2, default=str)}

Provide:
1. Top 3 BUY opportunities with reasoning
2. Top 3 SELL opportunities with reasoning
3. Stocks to AVOID with explanations
4. Portfolio construction suggestions

Format as structured JSON."""

            response = self.model.generate_content(prompt)

            return response.text

        except Exception as e:
            logger.error(f"Error identifying opportunities: {e}")
            return f"Error: {e}"

import pandas as pd
