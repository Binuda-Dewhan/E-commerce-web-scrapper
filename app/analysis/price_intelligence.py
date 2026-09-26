import pandas as pd
from typing import Dict, Any

class PriceIntelligence:
    @staticmethod
    def analyze(products_df: pd.DataFrame, observations_df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyzes historical observations to compute price intelligence metrics per product.
        """
        if observations_df.empty or products_df.empty:
            return pd.DataFrame()
            
        # Ensure timestamp is datetime and sort by it
        obs_df = observations_df.copy()
        obs_df['scraped_at'] = pd.to_datetime(obs_df['scraped_at'])
        obs_sorted = obs_df.sort_values(by=['product_id', 'scraped_at'])
        
        results = []
        
        for pid, group in obs_sorted.groupby('product_id'):
            # Convert group back to dicts for easier processing
            obs_list = group.to_dict('records')
            
            latest = obs_list[-1]
            first = obs_list[0]
            
            prices = [o['current_price'] for o in obs_list if pd.notna(o['current_price'])]
            
            latest_price = latest.get('current_price')
            original_price = latest.get('original_price')
            
            # Price history metrics
            metrics = {
                'product_id': str(pid),
                'latest_price': latest_price,
                'first_observed_price': first.get('current_price'),
                'lowest_observed_price': min(prices) if prices else None,
                'highest_observed_price': max(prices) if prices else None,
                'observation_count': len(obs_list),
                'latest_observation_date': latest['scraped_at'].isoformat()
            }
            
            # Change from previous observation
            if len(obs_list) > 1:
                previous_price = obs_list[-2].get('current_price')
                if previous_price and latest_price:
                    metrics['previous_price'] = previous_price
                    metrics['price_change'] = latest_price - previous_price
                    metrics['price_change_pct'] = ((latest_price - previous_price) / previous_price) * 100
                else:
                    metrics['previous_price'] = None
                    metrics['price_change'] = None
                    metrics['price_change_pct'] = None
            else:
                metrics['previous_price'] = None
                metrics['price_change'] = None
                metrics['price_change_pct'] = None
                
            # Current discount
            if original_price and latest_price and original_price > latest_price:
                metrics['discount_amount'] = original_price - latest_price
                metrics['discount_pct'] = ((original_price - latest_price) / original_price) * 100
            else:
                metrics['discount_amount'] = 0.0
                metrics['discount_pct'] = 0.0
                
            # Latest ratings state
            metrics['latest_rating'] = latest.get('rating')
            metrics['latest_review_count'] = latest.get('review_count')
            metrics['latest_availability'] = latest.get('availability_status')
                
            results.append(metrics)
            
        analysis_df = pd.DataFrame(results)
        
        # Merge with product master to get full context
        products_df_copy = products_df.copy()
        products_df_copy['product_id'] = products_df_copy['product_id'].astype(str)
        final_df = pd.merge(products_df_copy, analysis_df, on='product_id', how='inner')
        return final_df
