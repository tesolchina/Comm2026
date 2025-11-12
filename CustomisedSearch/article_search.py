#!/usr/bin/env python3
"""
Article Search Script for Meta-Analysis
Searches Scopus and Semantic Scholar APIs for articles on AI-based digital mental health interventions for youth
"""

import requests
import csv
import json
import time
from datetime import datetime
from typing import List, Dict, Any
import os

# API Configuration
SCOPUS_API_KEY = "c250bb68fb176b5907c8296410568516"
SCOPUS_INSTTOKEN = "d45c2a5307a7d3fa145c5afe451a8a32"
SEMANTIC_API_KEY = "Rx2fP6Lcq833H9Dybfw3J38LfP0xYLaQ1T1f3BTc"

# Search Query from Meta Study Plan
SCOPUS_QUERY = (
    '( TITLE-ABS-KEY ( youth OR "young adult*" OR adolescent* OR teen* OR '
    '"college student*" OR "university student*" OR "emerging adult*" ) ) AND '
    '( TITLE-ABS-KEY ( "mental health" OR "mental disorder*" OR depress* OR anxiety OR '
    '"psychological distress" OR wellbeing OR "well-being" ) ) AND '
    '( TITLE-ABS-KEY ( digital OR e-health OR "electronic health" OR mhealth OR m-health OR '
    'mobile OR online OR "web-based" OR internet OR app OR smartphone OR "digital health" OR '
    '"digital intervention" OR "digital service" ) ) AND '
    '( TITLE-ABS-KEY ( "artificial intelligence" OR AI OR "machine learning" OR "deep learning" OR '
    '"natural language processing" OR NLP OR chatbot* OR "chat bot" OR "conversational agent" OR '
    '"intelligent system" OR "predictive model" OR "computer vision" OR "personalized intervention" ) )'
)

# Time range
START_YEAR = 2021
END_YEAR = 2026

# Output paths
OUTPUT_DIR = "/workspaces/Comm2026/CustomisedSearch/output"
CSV_FILE = os.path.join(OUTPUT_DIR, "article_metadata.csv")
REPORT_FILE = os.path.join(OUTPUT_DIR, "search_report.md")


class ArticleSearcher:
    """Class to handle article searching from multiple APIs"""
    
    def __init__(self):
        self.articles = []
        self.scopus_results = 0
        self.semantic_results = 0
        self.duplicates_removed = 0
        
    def search_scopus(self) -> List[Dict[str, Any]]:
        """Search Scopus API for articles"""
        print("Searching Scopus API...")
        
        url = "https://api.elsevier.com/content/search/scopus"
        headers = {
            "X-ELS-APIKey": SCOPUS_API_KEY,
            "X-ELS-Insttoken": SCOPUS_INSTTOKEN,
            "Accept": "application/json"
        }
        
        all_results = []
        start = 0
        count = 25  # Results per request
        
        while True:
            params = {
                "query": SCOPUS_QUERY,
                "date": f"{START_YEAR}-{END_YEAR}",
                "start": start,
                "count": count,
                "view": "COMPLETE"
            }
            
            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Extract results
                search_results = data.get("search-results", {})
                entries = search_results.get("entry", [])
                
                if not entries:
                    break
                
                for entry in entries:
                    article = self._parse_scopus_entry(entry)
                    if article:
                        all_results.append(article)
                
                # Check if there are more results
                total_results = int(search_results.get("opensearch:totalResults", 0))
                print(f"  Retrieved {len(all_results)} of {total_results} results...")
                
                if start + count >= total_results:
                    break
                
                start += count
                time.sleep(1)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                print(f"Error searching Scopus: {e}")
                break
        
        self.scopus_results = len(all_results)
        print(f"Found {self.scopus_results} articles from Scopus")
        return all_results
    
    def _parse_scopus_entry(self, entry: Dict) -> Dict[str, Any]:
        """Parse a Scopus API entry into a standardized format"""
        try:
            # Extract DOI
            doi = entry.get("prism:doi", "")
            
            # Extract authors
            authors = entry.get("dc:creator", "")
            
            # Extract publication info
            title = entry.get("dc:title", "")
            journal = entry.get("prism:publicationName", "")
            year = entry.get("prism:coverDate", "")[:4] if entry.get("prism:coverDate") else ""
            abstract = entry.get("dc:description", "")
            citations = entry.get("citedby-count", "0")
            
            # Scopus specific fields
            scopus_id = entry.get("dc:identifier", "").replace("SCOPUS_ID:", "")
            eid = entry.get("eid", "")
            
            return {
                "source": "Scopus",
                "title": title,
                "authors": authors,
                "year": year,
                "journal": journal,
                "abstract": abstract,
                "doi": doi,
                "citations": citations,
                "scopus_id": scopus_id,
                "eid": eid,
                "url": f"https://www.scopus.com/record/display.uri?eid={eid}" if eid else ""
            }
        except Exception as e:
            print(f"Error parsing Scopus entry: {e}")
            return None
    
    def search_semantic_scholar(self) -> List[Dict[str, Any]]:
        """Search Semantic Scholar API for articles"""
        print("Searching Semantic Scholar API...")
        
        # Convert Scopus query to Semantic Scholar query
        # Semantic Scholar uses simpler keyword-based search
        search_terms = [
            "youth mental health AI",
            "adolescent depression artificial intelligence",
            "young adult anxiety machine learning",
            "teen wellbeing chatbot",
            "digital mental health intervention AI",
            "mHealth mental health NLP",
            "college student mental health predictive model"
        ]
        
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        headers = {
            "x-api-key": SEMANTIC_API_KEY
        }
        
        all_results = []
        seen_ids = set()
        
        for term in search_terms:
            print(f"  Searching for: {term}")
            offset = 0
            limit = 100
            
            for _ in range(3):  # Limit to 3 pages per search term
                params = {
                    "query": term,
                    "year": f"{START_YEAR}-{END_YEAR}",
                    "offset": offset,
                    "limit": limit,
                    "fields": "title,authors,year,abstract,citationCount,publicationDate,journal,doi,url,publicationTypes"
                }
                
                try:
                    response = requests.get(url, headers=headers, params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    papers = data.get("data", [])
                    if not papers:
                        break
                    
                    for paper in papers:
                        paper_id = paper.get("paperId")
                        if paper_id and paper_id not in seen_ids:
                            article = self._parse_semantic_entry(paper)
                            if article:
                                all_results.append(article)
                                seen_ids.add(paper_id)
                    
                    offset += limit
                    time.sleep(1)  # Rate limiting
                    
                except requests.exceptions.RequestException as e:
                    print(f"Error searching Semantic Scholar: {e}")
                    break
        
        self.semantic_results = len(all_results)
        print(f"Found {self.semantic_results} articles from Semantic Scholar")
        return all_results
    
    def _parse_semantic_entry(self, entry: Dict) -> Dict[str, Any]:
        """Parse a Semantic Scholar API entry into a standardized format"""
        try:
            # Extract authors
            authors_list = entry.get("authors", [])
            authors = ", ".join([author.get("name", "") for author in authors_list])
            
            # Extract publication info
            title = entry.get("title", "")
            year = str(entry.get("year", ""))
            abstract = entry.get("abstract", "")
            citations = str(entry.get("citationCount", "0"))
            doi = entry.get("doi", "")
            url = entry.get("url", "")
            
            # Journal info
            journal_info = entry.get("journal", {})
            journal = journal_info.get("name", "") if journal_info else ""
            
            return {
                "source": "Semantic Scholar",
                "title": title,
                "authors": authors,
                "year": year,
                "journal": journal,
                "abstract": abstract,
                "doi": doi,
                "citations": citations,
                "scopus_id": "",
                "eid": "",
                "url": url
            }
        except Exception as e:
            print(f"Error parsing Semantic Scholar entry: {e}")
            return None
    
    def remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate articles based on DOI and title similarity"""
        print("Removing duplicates...")
        
        unique_articles = []
        seen_dois = set()
        seen_titles = set()
        
        for article in articles:
            doi = article.get("doi", "").lower().strip()
            title = article.get("title", "").lower().strip()
            
            # Check DOI first (most reliable)
            if doi and doi in seen_dois:
                self.duplicates_removed += 1
                continue
            
            # Check title (normalize for comparison)
            title_normalized = "".join(c for c in title if c.isalnum() or c.isspace())
            if title_normalized and title_normalized in seen_titles:
                self.duplicates_removed += 1
                continue
            
            # Add to unique list
            unique_articles.append(article)
            if doi:
                seen_dois.add(doi)
            if title_normalized:
                seen_titles.add(title_normalized)
        
        print(f"Removed {self.duplicates_removed} duplicates")
        return unique_articles
    
    def save_to_csv(self, articles: List[Dict[str, Any]]):
        """Save articles to CSV file"""
        print(f"Saving {len(articles)} articles to CSV...")
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        fieldnames = [
            "title", "authors", "year", "journal", "abstract", 
            "doi", "citations", "source", "scopus_id", "eid", "url"
        ]
        
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(articles)
        
        print(f"CSV saved to: {CSV_FILE}")
    
    def generate_report(self, articles: List[Dict[str, Any]]):
        """Generate a markdown report of the search process"""
        print("Generating report...")
        
        report = f"""# Article Search Report

## Search Date
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Search Parameters

### Time Range
{START_YEAR} - {END_YEAR}

### Research Question
AI-based digital mental health interventions for youth (18-25 years old)

### Scopus Query
```
{SCOPUS_QUERY}
```

### Semantic Scholar Search Terms
- youth mental health AI
- adolescent depression artificial intelligence
- young adult anxiety machine learning
- teen wellbeing chatbot
- digital mental health intervention AI
- mHealth mental health NLP
- college student mental health predictive model

## Search Results

### Summary Statistics
- **Total articles found (before deduplication):** {self.scopus_results + self.semantic_results}
- **Scopus results:** {self.scopus_results}
- **Semantic Scholar results:** {self.semantic_results}
- **Duplicates removed:** {self.duplicates_removed}
- **Final unique articles:** {len(articles)}

### Articles by Year
"""
        
        # Count articles by year
        year_counts = {}
        for article in articles:
            year = article.get("year", "Unknown")
            year_counts[year] = year_counts.get(year, 0) + 1
        
        for year in sorted(year_counts.keys()):
            report += f"- {year}: {year_counts[year]} articles\n"
        
        report += f"""
### Articles by Source
- Scopus: {sum(1 for a in articles if a.get('source') == 'Scopus')} articles
- Semantic Scholar: {sum(1 for a in articles if a.get('source') == 'Semantic Scholar')} articles

## Inclusion Criteria (PICOS)

### Population
- Age range: 18-25 years old
- Clinical, subclinical, or nonclinical populations

### Intervention
- Digital mental health technologies with AI components
- AI chatbots
- Large Language Models (LLMs)

### Control/Comparison
- Traditional mental health interventions
- Non-AI digital mental health interventions

### Outcomes
- Measurements evaluating anxiety, stress, and depression

### Study Design
- Quantitative studies
- Mixed-method studies
- Intervention studies
- Original research in English

## Next Steps

1. **Manual Screening:** Review the exported CSV file to apply inclusion/exclusion criteria
2. **Full-Text Review:** Obtain and review full-text articles for eligible studies
3. **Data Extraction:** Extract relevant data for meta-analysis
4. **Quality Assessment:** Assess the quality of included studies

## Output Files

- **CSV File:** `{CSV_FILE}`
- **Report File:** `{REPORT_FILE}`

## Notes

- Articles were retrieved from Scopus and Semantic Scholar APIs
- Duplicates were removed based on DOI and title matching
- Further manual screening is required to apply all inclusion criteria
- Some articles may not meet all PICOS criteria and will need to be excluded during manual review
"""
        
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"Report saved to: {REPORT_FILE}")


def main():
    """Main execution function"""
    print("="*60)
    print("Article Search for Meta-Analysis")
    print("AI-based Digital Mental Health Interventions for Youth")
    print("="*60)
    print()
    
    searcher = ArticleSearcher()
    
    # Search both APIs
    scopus_articles = searcher.search_scopus()
    semantic_articles = searcher.search_semantic_scholar()
    
    # Combine results
    all_articles = scopus_articles + semantic_articles
    print(f"\nTotal articles before deduplication: {len(all_articles)}")
    
    # Remove duplicates
    unique_articles = searcher.remove_duplicates(all_articles)
    print(f"Total unique articles: {len(unique_articles)}")
    
    # Save results
    searcher.save_to_csv(unique_articles)
    searcher.generate_report(unique_articles)
    
    print("\n" + "="*60)
    print("Search completed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()
