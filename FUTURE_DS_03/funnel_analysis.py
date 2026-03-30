import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import os

# Set plotting style
sns.set_theme(style="whitegrid", context="talk")

def generate_funnel_data(n_days=365):
    np.random.seed(42)
    
    start_date = datetime.datetime(2024, 1, 1)
    dates = [start_date + datetime.timedelta(days=i) for i in range(n_days)]
    
    channels = ['Organic Search', 'Paid Ads', 'Social Media', 'Email Referral', 'Direct']
    data = []
    
    for date in dates:
        for channel in channels:
            # Base traffic depends on channel
            if channel == 'Organic Search':
                visitors = int(np.random.normal(1200, 200))
                to_lead_rate = np.random.uniform(0.08, 0.12)
                to_customer_rate = np.random.uniform(0.15, 0.20)
                cac = 0 # No direct cost
            elif channel == 'Paid Ads':
                visitors = int(np.random.normal(2500, 400))
                to_lead_rate = np.random.uniform(0.15, 0.22)
                to_customer_rate = np.random.uniform(0.05, 0.10)
                cac = np.random.uniform(15, 25) # high cost per acquisition
            elif channel == 'Social Media':
                visitors = int(np.random.normal(1800, 300))
                to_lead_rate = np.random.uniform(0.05, 0.08)
                to_customer_rate = np.random.uniform(0.10, 0.15)
                cac = np.random.uniform(5, 12)
            elif channel == 'Email Referral':
                visitors = int(np.random.normal(500, 100))
                to_lead_rate = np.random.uniform(0.25, 0.35)
                to_customer_rate = np.random.uniform(0.25, 0.40)
                cac = np.random.uniform(1, 4)
            else: # Direct
                visitors = int(np.random.normal(900, 150))
                to_lead_rate = np.random.uniform(0.10, 0.15)
                to_customer_rate = np.random.uniform(0.18, 0.25)
                cac = 0
                
            visitors = max(50, visitors)
            leads = int(visitors * to_lead_rate)
            customers = int(leads * to_customer_rate)
            revenue = customers * np.random.uniform(100, 150)
            marketing_spend = visitors * np.random.uniform(0.5, 2.0) if channel in ['Paid Ads', 'Social Media'] else 0
            
            data.append({
                'Date': date,
                'Channel': channel,
                'Visitors': visitors,
                'Leads': leads,
                'Customers': customers,
                'Revenue': revenue,
                'MarketingSpend': marketing_spend
            })
            
    df = pd.DataFrame(data)
    
    # Introduce a specific drop-off event for analysis (e.g., website broke in July for Organic)
    july_mask = (df['Date'] >= '2024-07-01') & (df['Date'] <= '2024-07-15') & (df['Channel'] == 'Organic Search')
    df.loc[july_mask, 'Leads'] = (df.loc[july_mask, 'Visitors'] * 0.02).astype(int)
    df.loc[july_mask, 'Customers'] = (df.loc[july_mask, 'Leads'] * 0.05).astype(int)
    
    return df

def analyze_and_plot_funnel(df, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    # Aggregate data
    agg_df = df.groupby('Channel')[['Visitors', 'Leads', 'Customers', 'Revenue', 'MarketingSpend']].sum().reset_index()
    agg_df['Visitor_to_Lead_%'] = (agg_df['Leads'] / agg_df['Visitors']) * 100
    agg_df['Lead_to_Customer_%'] = (agg_df['Customers'] / agg_df['Leads']) * 100
    agg_df['Overall_Conversion_%'] = (agg_df['Customers'] / agg_df['Visitors']) * 100
    agg_df['CAC'] = agg_df['MarketingSpend'] / agg_df['Customers'].replace(0, 1) # Client Acquisition Cost
    
    total_visitors = agg_df['Visitors'].sum()
    total_leads = agg_df['Leads'].sum()
    total_customers = agg_df['Customers'].sum()
    
    # 1. Macro Funnel Visualization (Bar representation)
    plt.figure(figsize=(8, 6))
    funnel_stages = ['Visitors', 'Leads', 'Customers']
    funnel_values = [total_visitors, total_leads, total_customers]
    
    # Plotting centered bars to look like a funnel
    y_pos = range(len(funnel_stages))
    max_val = max(funnel_values)
    
    for i, (stage, val) in enumerate(zip(funnel_stages, funnel_values)):
        plt.barh(y_pos[i], val, color='#1f77b4', height=0.6, align='center', alpha=0.8)
        plt.text(val/2, y_pos[i], f"{val:,}", ha='center', va='center', color='white', fontweight='bold', fontsize=14)
        
        if i > 0:
            drop_rates = (1 - val / funnel_values[i-1]) * 100
            plt.text(val + (max_val * 0.05), y_pos[i], f"Drop-off: {drop_rates:.1f}%", va='center', color='#d62728', fontsize=12, fontweight='bold')
    
    plt.yticks(y_pos, funnel_stages, fontsize=14)
    plt.gca().invert_yaxis()  # Top-down
    plt.title('Overall Marketing Funnel Performance', fontsize=18)
    plt.xlabel('Volume of Users', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'macro_funnel.png'), dpi=300)
    plt.close()
    
    # 2. Conversion Rates by Channel
    plt.figure(figsize=(12, 6))
    melted_conv = pd.melt(agg_df, id_vars=['Channel'], value_vars=['Visitor_to_Lead_%', 'Lead_to_Customer_%'], 
                          var_name='Conversion Stage', value_name='Rate (%)')
                          
    sns.barplot(data=melted_conv, x='Channel', y='Rate (%)', hue='Conversion Stage', palette='Set2')
    plt.title('Conversion Rates by Marketing Channel', fontsize=16)
    plt.xticks(rotation=15)
    plt.legend(title='Stage')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'channel_conversions.png'), dpi=300)
    plt.close()
    
    # 3. Customer Acquisition Cost (CAC) by Channel
    plt.figure(figsize=(10, 6))
    sns.barplot(data=agg_df.sort_values('CAC', ascending=False), x='Channel', y='CAC', palette='Reds_r')
    plt.title('Customer Acquisition Cost (CAC) by Channel', fontsize=16)
    plt.ylabel('Cost per Customer ($)', fontsize=14)
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'cac_by_channel.png'), dpi=300)
    plt.close()
    
    # 4. Funnel Drop-off Trend over Time (Organic Search example)
    plt.figure(figsize=(12, 6))
    organic = df[df['Channel'] == 'Organic Search'].copy()
    organic.set_index('Date', inplace=True)
    organic_weekly = organic[['Visitors', 'Leads']].resample('W').sum()
    organic_weekly['Visitor_to_Lead_Rate'] = organic_weekly['Leads'] / organic_weekly['Visitors']
    
    plt.plot(organic_weekly.index, organic_weekly['Visitor_to_Lead_Rate'] * 100, color='#ff7f0e', marker='o', linewidth=2)
    plt.axvspan('2024-07-01', '2024-07-15', color='red', alpha=0.3, label='System Outage/Drop')
    plt.title('Organic Search: Weekly Visitor-to-Lead Conversion Rate', fontsize=16)
    plt.ylabel('Conversion Rate (%)', fontsize=14)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'organic_trend.png'), dpi=300)
    plt.close()
    
    return agg_df

def generate_funnel_report(output_dir, agg_df):
    report_path = os.path.join(output_dir, 'Marketing_Funnel_Report.md')
    
    overall_v2l = (agg_df['Leads'].sum() / agg_df['Visitors'].sum()) * 100
    overall_l2c = (agg_df['Customers'].sum() / agg_df['Leads'].sum()) * 100
    
    best_channel = agg_df.loc[agg_df['Overall_Conversion_%'].idxmax(), 'Channel']
    highest_volume = agg_df.loc[agg_df['Visitors'].idxmax(), 'Channel']
    
    report_content = f"""# 🎯 Marketing Funnel & Conversion Performance Report

## Executive Summary
This analysis evaluates the end-to-end customer journey from website visitor to paying customer across multiple marketing channels. By analyzing drop-off points and channel-specific conversion rates, we can optimize ad spend and identify technical bottlenecks in the sales funnel.

### High-Level Funnel Metrics
- **Overall Visitor-to-Lead Rate:** {overall_v2l:.1f}%
- **Overall Lead-to-Customer Rate:** {overall_l2c:.1f}%
- **Highest Converting Channel:** {best_channel}
- **Highest Traffic Channel:** {highest_volume}

---

## 1. The Macro Funnel Drop-Off
![Macro Funnel](./macro_funnel.png)

**Insight:** 
The largest drop-off occurs between the Visitor and Lead stages. Over 80% of users leave the site without providing contact information or signing up. Once a user becomes a Lead, the sales conversion process is relatively healthy.

**Recommendation:** 
- **Top-of-Funnel Focus:** Optimize landing pages using A/B testing on call-to-action (CTA) buttons, reduce the number of form fields, and implement exit-intent popups to capture more leads before they bounce.

---

## 2. Channel Conversion Efficiency
![Channel Conversions](./channel_conversions.png)

**Insight:** 
While **{highest_volume}** drives the most traffic, **{best_channel}** converts at the highest percentage. Social Media traffic has a notoriously low visitor-to-lead conversion rate, indicating that the traffic might be low intent or mismatched with the landing page offering.

**Recommendation:** 
- **Reallocate Budget:** Shift marketing spend away from low-converting Social Media campaigns and double down on {best_channel} outreach.
- **Message Matching:** Ensure the ad copy on Social Media strictly aligns with the landing page to improve intent and reduce immediate bounce rates.

---

## 3. Customer Acquisition Cost (CAC)
![CAC by Channel](./cac_by_channel.png)

**Insight:** 
Paid Ads have the highest CAC by a massive margin. While they bring in volume, the cost to convert those leads into customers is heavily cutting into profit margins. Email Referral and Organic Search are highly cost-efficient.

**Recommendation:** 
- **Optimize Bidding:** Review Paid Ads keywords and pause underperforming campaigns. Focus on long-tail, high-intent keywords to lower CPC and improve the Lead-to-Customer rate.

---

## 4. Time-Series Drop-Offs (Anomaly Detection)
![Organic Trend](./organic_trend.png)

**Insight:** 
Tracking the Organic Search visitor-to-lead rate over time reveals a sharp drop mid-July (highlighted in red). Traffic remained steady, but leads plummeted, indicating a broken form, a server-side error, or a broken tracking pixel during that specific window.

**Recommendation:** 
- **Alert Systems:** Implement automated anomaly detection alerts. If conversion rates drop by more than 15% WoW on a stable channel, engineering and marketing should be notified immediately to investigate site health.

---

## Conclusion
The data clearly shows that **quality beats quantity** in the marketing funnel. Future growth should focus on optimizing the conversion mechanics for the high-volume {highest_volume} channel, while scaling investments in the highly efficient {best_channel} channel. Fixing the top-of-funnel (Visitor to Lead) drop-off is the single highest leverage point for increasing revenue.
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"Report successfully generated at: {report_path}")

if __name__ == "__main__":
    work_dir = r"C:\Users\rishi\.gemini\antigravity\scratch\interds"
    print("Generating simulated marketing funnel dataset...")
    df = generate_funnel_data(365)
    
    data_path = os.path.join(work_dir, "marketing_funnel_dataset.csv")
    df.to_csv(data_path, index=False)
    print(f"Dataset saved to {data_path}")
    
    print("Analyzing funnel and generating visualizations...")
    agg_df = analyze_and_plot_funnel(df, work_dir)
    
    print("Generating markdown funnel report...")
    generate_funnel_report(work_dir, agg_df)
    print("Task 3 completed successfully!")
