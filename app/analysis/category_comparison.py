import pandas as pd

class CategoryComparison:
    @staticmethod
    def compare(analysis_df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes category-level metrics and ranks products within their category.
        Requires the output of PriceIntelligence.analyze()
        """
        if analysis_df.empty:
            return analysis_df
            
        result_df = analysis_df.copy()
        
        # Calculate category averages
        cat_metrics = result_df.groupby('category').agg(
            category_average_price=('latest_price', 'mean'),
            category_median_price=('latest_price', 'median'),
            category_average_rating=('latest_rating', 'mean')
        ).reset_index()
        
        # Merge back
        result_df = pd.merge(result_df, cat_metrics, on='category', how='left')
        
        # Compute differences
        result_df['price_vs_category_avg'] = result_df['latest_price'] - result_df['category_average_price']
        
        # Safe percentage calculation
        def calc_pct(row):
            if pd.notna(row['category_average_price']) and row['category_average_price'] > 0:
                return (row['price_vs_category_avg'] / row['category_average_price']) * 100
            return None
            
        result_df['price_vs_category_avg_pct'] = result_df.apply(calc_pct, axis=1)
        
        result_df['rating_vs_category_avg'] = result_df['latest_rating'] - result_df['category_average_rating']
        
        # Price rank within category (1 = lowest price)
        result_df['price_rank_in_category'] = result_df.groupby('category')['latest_price'].rank(method='min', ascending=True)
        
        return result_df
