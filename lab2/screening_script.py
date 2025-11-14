#!/usr/bin/env python3
"""
Article Screening Script for RCT Identification
Reads article metadata and identifies Randomized Controlled Trials (RCTs)
"""

import csv
import pandas as pd
import re
from typing import Dict, Tuple

# File paths
INPUT_CSV = "/workspaces/Comm2026/CustomisedSearch/output/article_metadata.csv"
OUTPUT_EXCEL = "/workspaces/Comm2026/Screening/screened_articles.xlsx"


class RCTScreener:
    """Class to screen articles and identify RCTs"""
    
    def __init__(self):
        self.rct_keywords = [
            r'\brandomized controlled trial\b',
            r'\brandomised controlled trial\b',
            r'\bRCT\b',
            r'\brandomly assigned\b',
            r'\brandomly allocated\b',
            r'\brandom allocation\b',
            r'\brandom assignment\b',
            r'\brandomization\b',
            r'\brandomisation\b',
            r'\bcontrol group\b.*\bintervention group\b',
            r'\bintervention group\b.*\bcontrol group\b',
            r'\bplacebo.*control\b',
            r'\bcontrol.*placebo\b',
            r'\bdouble.*blind\b',
            r'\bsingle.*blind\b',
            r'\btriple.*blind\b',
            r'\bblinded.*trial\b',
            r'\bparallel.*group\b',
            r'\bcrossover.*trial\b',
            r'\bcross-over.*trial\b',
            r'\brandomly\b.*\bcontrol\b',
            r'\bcontrol\b.*\brandomly\b'
        ]
        
        self.non_rct_keywords = [
            r'\bcohort study\b',
            r'\bcohort\b.*\bstudy\b',
            r'\bcross-sectional\b',
            r'\bcase.*control\b',
            r'\bcase.*study\b',
            r'\bobservational\b',
            r'\bprospective study\b',
            r'\bretrospective\b',
            r'\bsurvey\b',
            r'\bqualitative\b',
            r'\bmixed.*method\b',
            r'\bpilot study\b',
            r'\bfeasibility study\b',
            r'\breview\b',
            r'\bmeta.*analysis\b',
            r'\bsystematic review\b',
            r'\bliterature review\b',
            r'\bscoping review\b',
            r'\bnarrative review\b',
            r'\bdescriptive study\b',
            r'\bexploratory study\b'
        ]
    
    def is_rct(self, title: str, abstract: str) -> Tuple[bool, str]:
        """
        Determine if an article is an RCT based on title and abstract
        
        Returns:
            Tuple of (is_rct: bool, reason: str)
        """
        # Combine title and abstract for searching
        text = f"{title} {abstract}".lower()
        
        # Check for strong non-RCT indicators first
        for pattern in self.non_rct_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                match = re.search(pattern, text, re.IGNORECASE)
                matched_text = match.group(0) if match else pattern
                return False, f"Study design indicates non-RCT: mentions '{matched_text}'"
        
        # Check for RCT indicators
        rct_matches = []
        for pattern in self.rct_keywords:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                rct_matches.append(match.group(0))
        
        if rct_matches:
            reasons = ", ".join(set(rct_matches[:3]))  # Show up to 3 matches
            return True, f"RCT keywords found: {reasons}"
        
        # If no clear indicators found
        return False, "No clear RCT indicators found in title or abstract"
    
    def screen_articles(self):
        """Read CSV and screen articles for RCT identification"""
        print("="*60)
        print("Article Screening for RCT Identification")
        print("="*60)
        print()
        
        # Read the CSV file
        print(f"Reading articles from: {INPUT_CSV}")
        try:
            df = pd.read_csv(INPUT_CSV)
            print(f"Total articles to screen: {len(df)}")
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return
        
        # Initialize lists for RCT and non-RCT articles
        rct_articles = []
        non_rct_articles = []
        
        # Screen each article
        print("\nScreening articles...")
        for idx, row in df.iterrows():
            if (idx + 1) % 100 == 0:
                print(f"  Processed {idx + 1}/{len(df)} articles...")
            
            title = str(row.get('title', ''))
            abstract = str(row.get('abstract', ''))
            
            # Determine if RCT
            is_rct, reason = self.is_rct(title, abstract)
            
            # Create article dict with reason
            article_data = row.to_dict()
            article_data['screening_reason'] = reason
            
            if is_rct:
                rct_articles.append(article_data)
            else:
                non_rct_articles.append(article_data)
        
        print(f"\nScreening complete!")
        print(f"  RCT studies identified: {len(rct_articles)}")
        print(f"  Non-RCT studies: {len(non_rct_articles)}")
        
        # Convert to DataFrames
        rct_df = pd.DataFrame(rct_articles)
        non_rct_df = pd.DataFrame(non_rct_articles)
        
        # Reorder columns to put screening_reason after abstract
        if not rct_df.empty:
            cols = list(rct_df.columns)
            if 'screening_reason' in cols:
                cols.remove('screening_reason')
                # Insert after abstract if it exists
                if 'abstract' in cols:
                    abstract_idx = cols.index('abstract')
                    cols.insert(abstract_idx + 1, 'screening_reason')
                else:
                    cols.append('screening_reason')
                rct_df = rct_df[cols]
        
        if not non_rct_df.empty:
            cols = list(non_rct_df.columns)
            if 'screening_reason' in cols:
                cols.remove('screening_reason')
                if 'abstract' in cols:
                    abstract_idx = cols.index('abstract')
                    cols.insert(abstract_idx + 1, 'screening_reason')
                else:
                    cols.append('screening_reason')
                non_rct_df = non_rct_df[cols]
        
        # Save to Excel with two sheets
        print(f"\nSaving results to: {OUTPUT_EXCEL}")
        try:
            with pd.ExcelWriter(OUTPUT_EXCEL, engine='openpyxl') as writer:
                rct_df.to_excel(writer, sheet_name='RCT_Studies', index=False)
                non_rct_df.to_excel(writer, sheet_name='Non_RCT_Studies', index=False)
                
                # Auto-adjust column widths
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 100)  # Cap at 100
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print("Excel file created successfully!")
            print(f"\nSheet 1: 'RCT_Studies' - {len(rct_articles)} articles")
            print(f"Sheet 2: 'Non_RCT_Studies' - {len(non_rct_articles)} articles")
            
        except Exception as e:
            print(f"Error saving Excel file: {e}")
            return
        
        # Generate summary statistics
        self.generate_summary(rct_df, non_rct_df)
        
        print("\n" + "="*60)
        print("Screening completed successfully!")
        print("="*60)
    
    def generate_summary(self, rct_df: pd.DataFrame, non_rct_df: pd.DataFrame):
        """Generate summary statistics"""
        print("\n" + "="*60)
        print("SUMMARY STATISTICS")
        print("="*60)
        
        total = len(rct_df) + len(non_rct_df)
        rct_percentage = (len(rct_df) / total * 100) if total > 0 else 0
        
        print(f"\nTotal articles screened: {total}")
        print(f"RCT studies: {len(rct_df)} ({rct_percentage:.1f}%)")
        print(f"Non-RCT studies: {len(non_rct_df)} ({100-rct_percentage:.1f}%)")
        
        # RCT articles by year
        if not rct_df.empty and 'year' in rct_df.columns:
            print("\nRCT Studies by Year:")
            year_counts = rct_df['year'].value_counts().sort_index()
            for year, count in year_counts.items():
                print(f"  {year}: {count} studies")
        
        # Top journals with RCTs
        if not rct_df.empty and 'journal' in rct_df.columns:
            print("\nTop 10 Journals with RCT Studies:")
            journal_counts = rct_df['journal'].value_counts().head(10)
            for idx, (journal, count) in enumerate(journal_counts.items(), 1):
                print(f"  {idx}. {journal}: {count} studies")
        
        # Sample RCT reasons
        if not rct_df.empty and 'screening_reason' in rct_df.columns:
            print("\nSample RCT Identification Reasons:")
            sample_reasons = rct_df['screening_reason'].head(5)
            for idx, reason in enumerate(sample_reasons, 1):
                print(f"  {idx}. {reason}")


def main():
    """Main execution function"""
    screener = RCTScreener()
    screener.screen_articles()


if __name__ == "__main__":
    main()
