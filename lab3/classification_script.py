#!/usr/bin/env python3
"""
AI Classification Script for RCT Studies
Classifies studies based on whether they use LLM AI tools or classical AI tools (non-LLMs)
"""

import pandas as pd
import re
from typing import Tuple, List

# File paths
INPUT_EXCEL = "/workspaces/Comm2026/Screening/screened_articles.xlsx"
OUTPUT_EXCEL = "/workspaces/Comm2026/classification/classified_articles.xlsx"


class AIClassifier:
    """Class to classify RCT studies by AI type"""
    
    def __init__(self):
        # LLM-related keywords
        self.llm_keywords = [
            r'\bLLM\b',
            r'\bLLMs\b',
            r'\blarge language model\b',
            r'\blarge language models\b',
            r'\bGPT\b',
            r'\bGPT-3\b',
            r'\bGPT-4\b',
            r'\bChatGPT\b',
            r'\bBERT\b',
            r'\bRoBERTa\b',
            r'\bT5\b',
            r'\btransformer\b.*\bmodel\b',
            r'\btransformer-based\b',
            r'\bgenerative.*model\b',
            r'\bpre-trained.*language\b',
            r'\bfoundation model\b',
            r'\bClaude\b',
            r'\bBard\b',
            r'\bLLaMA\b',
            r'\bPaLM\b',
            r'\bBloom\b',
            r'\bALERT\b',
            r'\bELECTRA\b',
            r'\bXLNet\b',
            r'\bDistilBERT\b',
            r'\bALBERT\b',
            r'\bconversational AI\b',
            r'\bdialog.*model\b',
            r'\bdialogue.*model\b',
            r'\bnatural language generation\b',
            r'\bNLG\b',
            r'\btext generation\b',
            r'\bGPT.*based\b',
            r'\bBERT.*based\b'
        ]
        
        # Classical AI keywords (non-LLM)
        self.classical_ai_keywords = [
            r'\bmachine learning\b',
            r'\bML\b',
            r'\bdeep learning\b',
            r'\bneural network\b',
            r'\bconvolutional neural network\b',
            r'\bCNN\b',
            r'\brecurrent neural network\b',
            r'\bRNN\b',
            r'\bLSTM\b',
            r'\bGRU\b',
            r'\brandom forest\b',
            r'\bsupport vector machine\b',
            r'\bSVM\b',
            r'\bdecision tree\b',
            r'\bk-means\b',
            r'\bclustering\b',
            r'\bclassification algorithm\b',
            r'\bregression model\b',
            r'\blogistic regression\b',
            r'\bnaive bayes\b',
            r'\bgradient boosting\b',
            r'\bXGBoost\b',
            r'\bAdaBoost\b',
            r'\bensemble method\b',
            r'\bpredictive model\b',
            r'\bprediction algorithm\b',
            r'\bfeature extraction\b',
            r'\bcomputer vision\b',
            r'\bimage recognition\b',
            r'\bsentiment analysis\b',
            r'\btext classification\b',
            r'\bNLP\b.*(?!.*LLM)(?!.*GPT)(?!.*BERT)',
            r'\bnatural language processing\b.*(?!.*LLM)(?!.*GPT)(?!.*BERT)',
            r'\breinforcement learning\b',
            r'\bunsupervised learning\b',
            r'\bsupervised learning\b'
        ]
        
        # Chatbot/conversational agent keywords (need to check if LLM-based)
        self.chatbot_keywords = [
            r'\bchatbot\b',
            r'\bchat bot\b',
            r'\bconversational agent\b',
            r'\bvirtual assistant\b',
            r'\bdigital assistant\b',
            r'\bdialog system\b',
            r'\bdialogue system\b'
        ]
    
    def classify_ai_type(self, title: str, abstract: str) -> Tuple[str, str, List[str]]:
        """
        Classify the type of AI used in the study
        
        Returns:
            Tuple of (category: str, ai_tools: str, identified_tools: List[str])
            category: 'LLM', 'Non-LLM', 'Both', or 'Unclear'
        """
        text = f"{title} {abstract}".lower()
        
        # Check for LLM indicators
        llm_matches = []
        for pattern in self.llm_keywords:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                matched_text = match.group(0)
                if matched_text not in llm_matches:
                    llm_matches.append(matched_text)
        
        # Check for classical AI indicators
        classical_matches = []
        for pattern in self.classical_ai_keywords:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                matched_text = match.group(0)
                if matched_text not in classical_matches:
                    classical_matches.append(matched_text)
        
        # Check for chatbot mentions
        chatbot_found = False
        for pattern in self.chatbot_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                chatbot_found = True
                break
        
        # Determine category
        has_llm = len(llm_matches) > 0
        has_classical = len(classical_matches) > 0
        
        # If chatbot is mentioned but no specific LLM indicators, check context
        if chatbot_found and not has_llm:
            # Check if there are NLP/conversational AI indicators that might suggest LLM
            nlp_patterns = [r'\bnatural language\b', r'\btext.*generation\b', r'\bconversation\b']
            nlp_found = any(re.search(p, text, re.IGNORECASE) for p in nlp_patterns)
            if nlp_found:
                # Likely conversational AI but unclear if LLM
                pass
        
        # Classify
        if has_llm and has_classical:
            category = 'Both'
            all_tools = llm_matches + classical_matches
            ai_tools = ', '.join(all_tools[:5])  # Limit to first 5
        elif has_llm:
            category = 'LLM'
            ai_tools = ', '.join(llm_matches[:5])
        elif has_classical:
            category = 'Non-LLM'
            ai_tools = ', '.join(classical_matches[:5])
        else:
            category = 'Unclear'
            ai_tools = 'No specific AI tools clearly identified'
        
        return category, ai_tools, llm_matches + classical_matches
    
    def classify_articles(self):
        """Read Excel and classify RCT articles by AI type"""
        print("="*60)
        print("AI Classification for RCT Studies")
        print("="*60)
        print()
        
        # Read the RCT studies from Excel
        print(f"Reading RCT studies from: {INPUT_EXCEL}")
        try:
            df = pd.read_excel(INPUT_EXCEL, sheet_name='RCT_Studies')
            print(f"Total RCT articles to classify: {len(df)}")
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return
        
        # Initialize lists for different categories
        llm_articles = []
        non_llm_articles = []
        both_articles = []
        unclear_articles = []
        
        # Classify each article
        print("\nClassifying articles...")
        for idx, row in df.iterrows():
            if (idx + 1) % 10 == 0:
                print(f"  Processed {idx + 1}/{len(df)} articles...")
            
            title = str(row.get('title', ''))
            abstract = str(row.get('abstract', ''))
            
            # Classify AI type
            category, ai_tools, identified_tools = self.classify_ai_type(title, abstract)
            
            # Create article dict with AI tools column
            article_data = row.to_dict()
            article_data['ai_tools_identified'] = ai_tools
            article_data['ai_category'] = category
            
            # Sort into appropriate list
            if category == 'LLM':
                llm_articles.append(article_data)
            elif category == 'Non-LLM':
                non_llm_articles.append(article_data)
            elif category == 'Both':
                both_articles.append(article_data)
                # Also add to both LLM and Non-LLM lists for separate sheets
                llm_articles.append(article_data.copy())
                non_llm_articles.append(article_data.copy())
            else:
                unclear_articles.append(article_data)
        
        print(f"\nClassification complete!")
        print(f"  LLM-based AI: {len([a for a in llm_articles if a.get('ai_category') != 'Both'])} studies")
        print(f"  Classical/Non-LLM AI: {len([a for a in non_llm_articles if a.get('ai_category') != 'Both'])} studies")
        print(f"  Both LLM and Non-LLM: {len(both_articles)} studies")
        print(f"  Unclear/No specific AI identified: {len(unclear_articles)} studies")
        
        # Convert to DataFrames
        llm_df = pd.DataFrame(llm_articles)
        non_llm_df = pd.DataFrame(non_llm_articles)
        
        # Reorder columns to put ai_tools_identified after abstract
        for df_to_reorder in [llm_df, non_llm_df]:
            if not df_to_reorder.empty:
                cols = list(df_to_reorder.columns)
                if 'ai_tools_identified' in cols:
                    cols.remove('ai_tools_identified')
                    if 'ai_category' in cols:
                        cols.remove('ai_category')
                    # Insert after abstract if it exists
                    if 'abstract' in cols:
                        abstract_idx = cols.index('abstract')
                        cols.insert(abstract_idx + 1, 'ai_category')
                        cols.insert(abstract_idx + 2, 'ai_tools_identified')
                    else:
                        cols.extend(['ai_category', 'ai_tools_identified'])
                    df_to_reorder = df_to_reorder[cols]
                    
                    # Update the reference
                    if df_to_reorder is llm_df:
                        llm_df = df_to_reorder
                    else:
                        non_llm_df = df_to_reorder
        
        # Convert unclear articles to DataFrame
        unclear_df = pd.DataFrame(unclear_articles)
        
        # Reorder columns for unclear_df
        if not unclear_df.empty:
            cols = list(unclear_df.columns)
            if 'ai_tools_identified' in cols:
                cols.remove('ai_tools_identified')
                if 'ai_category' in cols:
                    cols.remove('ai_category')
                # Insert after abstract if it exists
                if 'abstract' in cols:
                    abstract_idx = cols.index('abstract')
                    cols.insert(abstract_idx + 1, 'ai_category')
                    cols.insert(abstract_idx + 2, 'ai_tools_identified')
                else:
                    cols.extend(['ai_category', 'ai_tools_identified'])
                unclear_df = unclear_df[cols]
        
        # Save to Excel with three sheets
        print(f"\nSaving results to: {OUTPUT_EXCEL}")
        try:
            with pd.ExcelWriter(OUTPUT_EXCEL, engine='openpyxl') as writer:
                llm_df.to_excel(writer, sheet_name='LLM_AI_Studies', index=False)
                non_llm_df.to_excel(writer, sheet_name='Non_LLM_AI_Studies', index=False)
                unclear_df.to_excel(writer, sheet_name='Unclear_No_AI_Identified', index=False)
                
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
            print(f"\nSheet 1: 'LLM_AI_Studies' - {len(llm_df)} articles")
            print(f"Sheet 2: 'Non_LLM_AI_Studies' - {len(non_llm_df)} articles")
            print(f"Sheet 3: 'Unclear_No_AI_Identified' - {len(unclear_df)} articles")
            
        except Exception as e:
            print(f"Error saving Excel file: {e}")
            return
        
        # Generate summary statistics
        self.generate_summary(llm_df, non_llm_df, both_articles, unclear_articles)
        
        print("\n" + "="*60)
        print("Classification completed successfully!")
        print("="*60)
    
    def generate_summary(self, llm_df: pd.DataFrame, non_llm_df: pd.DataFrame, 
                        both_articles: List, unclear_articles: List):
        """Generate summary statistics"""
        print("\n" + "="*60)
        print("SUMMARY STATISTICS")
        print("="*60)
        
        total = len(llm_df) + len(non_llm_df) - len(both_articles)  # Subtract duplicates
        
        print(f"\nTotal RCT articles classified: {total + len(unclear_articles)}")
        print(f"LLM-based AI only: {len(llm_df) - len(both_articles)} studies")
        print(f"Classical/Non-LLM AI only: {len(non_llm_df) - len(both_articles)} studies")
        print(f"Both LLM and Non-LLM: {len(both_articles)} studies")
        print(f"Unclear/No specific AI: {len(unclear_articles)} studies")
        
        # Sample LLM tools
        if not llm_df.empty and 'ai_tools_identified' in llm_df.columns:
            print("\nSample LLM-based AI Tools Identified:")
            sample_tools = llm_df['ai_tools_identified'].head(10)
            for idx, tools in enumerate(sample_tools, 1):
                print(f"  {idx}. {tools}")
        
        # Sample Non-LLM tools
        if not non_llm_df.empty and 'ai_tools_identified' in non_llm_df.columns:
            print("\nSample Classical/Non-LLM AI Tools Identified:")
            sample_tools = non_llm_df['ai_tools_identified'].head(10)
            for idx, tools in enumerate(sample_tools, 1):
                print(f"  {idx}. {tools}")
        
        # Year distribution for LLM studies
        if not llm_df.empty and 'year' in llm_df.columns:
            print("\nLLM-based Studies by Year:")
            year_counts = llm_df['year'].value_counts().sort_index()
            for year, count in year_counts.items():
                print(f"  {year}: {count} studies")


def main():
    """Main execution function"""
    classifier = AIClassifier()
    classifier.classify_articles()


if __name__ == "__main__":
    main()
