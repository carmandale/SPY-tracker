#!/usr/bin/env python3
"""
Prediction Evaluation Script for SPY TA Tracker

This script evaluates the accuracy of SPY price predictions by comparing them
against actual market prices. It can parse prediction files from the predictions/
directory and compute error metrics.

Usage:
    python eval_predictions.py --date YYYYMMDD [--output {text|csv|json}]
"""

import re
import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union

try:
    import pandas as pd
    import pytz
    import yfinance as yf
except ImportError:
    print("Required packages not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "pytz", "yfinance"])
    import pandas as pd
    import pytz
    import yfinance as yf


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Evaluate SPY price predictions")
    parser.add_argument(
        "--date", 
        type=str, 
        help="Date to evaluate in YYYYMMDD format"
    )
    parser.add_argument(
        "--output", 
        choices=["text", "csv", "json"], 
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--timezone", 
        choices=["ET", "CT", "both"], 
        default="both",
        help="Timezone to use for evaluation (default: both)"
    )
    parser.add_argument(
        "--file", 
        type=str,
        help="Path to specific comparison file (default: auto-detect from date)"
    )
    return parser.parse_args()


def parse_comparison_file(filepath: str) -> List[Dict]:
    """Parse a comparison markdown file and extract predictions."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith('|') and not line.startswith('|---') and 'Agent' not in line:
            parts = [p.strip() for p in line.strip('|').split('|')]
            if len(parts) >= 5:
                # Ensure we have at least 6 columns (agent, 4 times, notes)
                while len(parts) < 6:
                    parts.append('')
                rows.append({
                    'agent': parts[0],
                    'predictions': {
                        '8:30': parse_cell(parts[1]),
                        '12:00': parse_cell(parts[2]),
                        '2:00': parse_cell(parts[3]),
                        'Close': parse_cell(parts[4]),
                    },
                    'notes': parts[5]
                })
    
    return rows


def parse_cell(cell: str) -> Optional[float]:
    """Parse a price cell from the comparison table."""
    if not cell:
        return None
    
    # Replace various dash types and remove ~ and $
    cell = cell.replace('\u2014', '-').replace('\u2013', '-').replace('~', '').replace('$', '').strip()
    
    # Try to extract a range first (e.g., "637.50-638.00")
    m = re.search(r'([0-9]+\.?[0-9]*)\s*-\s*([0-9]+\.?[0-9]*)', cell)
    if m:
        a = float(m.group(1))
        b = float(m.group(2))
        return (a + b) / 2  # Return midpoint of range
    
    # Try to extract a single number
    m = re.search(r'([0-9]+\.?[0-9]*)', cell)
    if m:
        return float(m.group(1))
    
    return None


def get_actual_prices(date_str: str) -> Dict[str, Dict[str, Dict[str, Union[str, float]]]]:
    """Get actual SPY prices for the specified date."""
    # Parse date
    date_obj = datetime.strptime(date_str, '%Y%m%d')
    
    # Define timezone objects
    EDT = pytz.timezone('America/New_York')
    CDT = pytz.timezone('America/Chicago')
    
    # Fetch data from day before to day after to ensure we have all hours
    start = date_obj - timedelta(days=1)
    end = date_obj + timedelta(days=1)
    
    print(f"Fetching SPY minute data for {date_obj.strftime('%Y-%m-%d')}...")
    df = yf.download('SPY', start=start, end=end, interval='1m', prepost=True, progress=False)
    
    if df.empty:
        print("Error: No data retrieved from Yahoo Finance")
        sys.exit(1)
    
    # Ensure timezone awareness
    idx = df.index.tz_localize('UTC') if df.index.tz is None else df.index.tz_convert('UTC')
    df = df.set_index(idx)
    
    # Define checkpoint times in ET and CT
    et_times = {
        '8:30': datetime(date_obj.year, date_obj.month, date_obj.day, 8, 30, tzinfo=EDT).astimezone(timezone.utc),
        '12:00': datetime(date_obj.year, date_obj.month, date_obj.day, 12, 0, tzinfo=EDT).astimezone(timezone.utc),
        '2:00': datetime(date_obj.year, date_obj.month, date_obj.day, 14, 0, tzinfo=EDT).astimezone(timezone.utc),
        'Close': datetime(date_obj.year, date_obj.month, date_obj.day, 16, 0, tzinfo=EDT).astimezone(timezone.utc),
    }
    
    ct_times = {
        '8:30': datetime(date_obj.year, date_obj.month, date_obj.day, 8, 30, tzinfo=CDT).astimezone(timezone.utc),
        '12:00': datetime(date_obj.year, date_obj.month, date_obj.day, 12, 0, tzinfo=CDT).astimezone(timezone.utc),
        '2:00': datetime(date_obj.year, date_obj.month, date_obj.day, 14, 0, tzinfo=CDT).astimezone(timezone.utc),
        'Close': datetime(date_obj.year, date_obj.month, date_obj.day, 15, 0, tzinfo=CDT).astimezone(timezone.utc),
    }
    
    # Helper function to get nearest price
    def nearest_price(ts):
        idx = df.index.get_indexer([ts], method='nearest')
        i = idx[0]
        t = df.index[i]
        price = float(df['Close'].iloc[i])
        return t, price
    
    # Get actual prices for both timezones
    actuals = {'ET': {}, 'CT': {}}
    
    for k, ts in et_times.items():
        t, p = nearest_price(ts)
        actuals['ET'][k] = {'timestamp': t.isoformat(), 'price': p}
    
    for k, ts in ct_times.items():
        t, p = nearest_price(ts)
        actuals['CT'][k] = {'timestamp': t.isoformat(), 'price': p}
    
    return actuals


def evaluate_predictions(predictions: List[Dict], actuals: Dict) -> List[Dict]:
    """Evaluate predictions against actual prices."""
    results = []
    
    for pred in predictions:
        agent = pred['agent']
        pred_values = pred['predictions']
        notes = pred['notes']
        
        # Determine timezone hint from notes
        tz_hint = 'ET' if 'ET' in notes else ('CT' if ('CT' in notes or 'CDT' in notes) else None)
        
        # Compute errors for both timezones
        errors = {}
        for tz in ['ET', 'CT']:
            abs_errors = []
            count = 0
            
            for checkpoint, pred_value in pred_values.items():
                if pred_value is None:
                    continue
                
                actual_price = actuals[tz][checkpoint]['price']
                abs_error = abs(pred_value - actual_price)
                abs_errors.append(abs_error)
                count += 1
            
            if count > 0:
                mae = sum(abs_errors) / count
                errors[tz] = {
                    'mae': mae,
                    'abs_errors': abs_errors,
                    'count': count
                }
        
        # Determine best timezone based on MAE
        best_tz = None
        if errors:
            best_tz = min(errors.keys(), key=lambda k: errors[k]['mae'])
        
        results.append({
            'agent': agent,
            'errors': errors,
            'tz_hint': tz_hint,
            'best_tz': best_tz
        })
    
    # Sort by MAE of best timezone
    results.sort(key=lambda x: x['errors'].get(x['best_tz'], {}).get('mae', float('inf')))
    
    return results


def format_output(results: List[Dict], actuals: Dict, output_format: str) -> str:
    """Format evaluation results based on the specified output format."""
    if output_format == 'json':
        return json.dumps({
            'actuals': actuals,
            'results': results
        }, indent=2)
    
    elif output_format == 'csv':
        lines = ['agent,timezone,count,mae']
        for r in results:
            for tz, stats in r['errors'].items():
                lines.append(f"{r['agent']},{tz},{stats['count']},{stats['mae']:.2f}")
        return '\n'.join(lines)
    
    else:  # text
        lines = []
        
        # Actual prices
        lines.append("Actual SPY Prices:")
        for tz, checkpoints in actuals.items():
            prices_str = ', '.join([f"{k}={v['price']:.2f}" for k, v in checkpoints.items()])
            lines.append(f"  {tz}: {prices_str}")
        
        lines.append("\nPrediction Accuracy (sorted by MAE):")
        lines.append("=" * 60)
        
        for r in results:
            agent = r['agent']
            best_tz = r['best_tz']
            
            if best_tz and best_tz in r['errors']:
                mae = r['errors'][best_tz]['mae']
                count = r['errors'][best_tz]['count']
                
                # Add emoji based on MAE
                if mae < 2.0:
                    emoji = "🟢"  # Green for good
                elif mae < 4.0:
                    emoji = "🟡"  # Yellow for medium
                else:
                    emoji = "🔴"  # Red for poor
                
                lines.append(f"{emoji} {agent}: MAE ${mae:.2f} ({count} predictions, {best_tz})")
                
                # Add details for both timezones
                for tz, stats in r['errors'].items():
                    if tz != best_tz:
                        lines.append(f"    {tz}: MAE ${stats['mae']:.2f}")
            else:
                lines.append(f"⚠️ {agent}: No valid predictions")
        
        return '\n'.join(lines)


def main():
    """Main function."""
    args = parse_args()
    
    # Determine file path
    if args.file:
        filepath = args.file
    elif args.date:
        filepath = f"predictions/{args.date}/comparison_{args.date}.md"
    else:
        print("Error: Either --date or --file must be specified")
        sys.exit(1)
    
    # Check if file exists
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    # Parse comparison file
    predictions = parse_comparison_file(filepath)
    if not predictions:
        print(f"Error: No predictions found in {filepath}")
        sys.exit(1)
    
    # Get date from filepath if not provided
    if not args.date:
        match = re.search(r'(\d{6})\.md$', filepath)
        if match:
            args.date = match.group(1)
        else:
            print("Error: Could not determine date from filepath")
            sys.exit(1)
    
    # Get actual prices
    actuals = get_actual_prices(args.date)
    
    # Filter timezones if specified
    if args.timezone != 'both':
        actuals = {args.timezone: actuals[args.timezone]}
    
    # Evaluate predictions
    results = evaluate_predictions(predictions, actuals)
    
    # Format and print output
    output = format_output(results, actuals, args.output)
    print(output)


if __name__ == "__main__":
    main()

