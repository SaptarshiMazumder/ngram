import pandas as pd
from collections import defaultdict

# Step 1: Load the CSV file with proper encoding
def load_csv(file_path):
    # We are trying to read the CSV file using different encodings because Japanese text files
    # can be encoded in various ways. The most common encodings are listed below:
    encodings = ['shift_jis', 'euc_jp', 'iso2022_jp', 'cp932']
    
    # Loop through the list of encodings and try to load the file
    for enc in encodings:
        try:
            # Attempt to read the CSV file with the current encoding
            df = pd.read_csv(file_path, dtype=str, encoding=enc)
            print(f"Successfully loaded with encoding: {enc}")
            return df
        except UnicodeDecodeError:
            # If loading fails due to encoding issues, print a message and try the next encoding
            print(f"Failed with encoding: {enc}")
    
    # If none of the encodings work, raise an error indicating that the file could not be read
    raise ValueError("Unable to read the file with the provided encodings.")

# Step 2: Create 2-grams from the address components
def generate_2grams(text):
    # A 2-gram is a sequence of 2 consecutive characters in a string.
    # This function breaks down the given text into all possible 2-grams.
    # For example, the string "東京都" would produce ["東京", "京都"].
    
    return [text[i:i+2] for i in range(len(text) - 1)]

# Step 3: Build the inverted index
def build_inverted_index(df):
    # An inverted index is a data structure that maps content (in this case, 2-grams)
    # to the rows in which they appear in the DataFrame. This allows us to quickly
    # search for rows that contain specific 2-grams.
    
    index = defaultdict(list)  # defaultdict automatically creates a new list for each new key
    
    # Iterate over each row in the DataFrame
    for i, row in df.iterrows():
        # Combine all the relevant text-based columns into one long string.
        # We're excluding numerical codes and the postal code because the problem statement
        # specifies that those should not be part of the search.
        
        full_text = ''
        for col in ['都道府県', '都道府県カナ', '市区町村', '市区町村カナ', 
                    '町域', '町域カナ', '町域補足', '補足', 
                    '事業所名', '事業所名カナ', '事業所住所']:
            if col in df.columns:  # Only include columns that exist in the DataFrame
                full_text += str(row[col])  # Concatenate the column's value to the full text
        
        # Generate 2-grams from the combined text
        tokens = generate_2grams(full_text)
        
        # Add each 2-gram to the inverted index
        for token in tokens:
            index[token].append(i)  # Append the current row index to the list for this 2-gram
    
    return index

# Step 4: Search for rows that match the query based on 2-grams
def search_addresses(query, index, df):
    # This function searches for rows in the DataFrame that match the given query.
    # It does this by breaking the query into 2-grams and finding rows that contain
    # all of those 2-grams.
    
    # Generate 2-grams from the search query
    tokens = generate_2grams(query)
    if not tokens:
        return []  # If no tokens were generated (e.g., if the query is too short), return an empty list
    
    # Start with the set of all rows that contain the first 2-gram
    matched_indices = set(index[tokens[0]])
    
    # Narrow down the matches by intersecting with rows that contain the other 2-grams
    for token in tokens[1:]:
        current_indices = set(index[token])  # Get the set of indices for the current 2-gram
        matched_indices = matched_indices.intersection(current_indices)  # Keep only rows that match all 2-grams
    
    # Return the rows in the DataFrame that match the query
    return df.iloc[list(matched_indices)]

# Step 5: Display the search results
def display_results(results):
    # This function simply prints out the results of the search in a readable format.
    # It shows the postal code, prefecture, city/ward/town, and district/neighborhood.
    
    for _, row in results.iterrows():
        print(row['郵便番号'], row['都道府県'], row['市区町村'], row['町域'])

# Main function to load data, build the index, and perform a search
def main(file_path, search_query):
    df = load_csv(file_path)  # Step 1: Load the data from the CSV file
    index = build_inverted_index(df)  # Step 3: Build the inverted index from the DataFrame
    results = search_addresses(search_query, index, df)  # Step 4: Search the index for the query
    display_results(results)  # Step 5: Display the search results

# Example usage
file_path = r"C:\Users\googler\OneDrive\Desktop\linkers\ngram\zenkoku.csv"  # Replace with the actual file path, this is file path in my directory
search_query = '東京都'  # Example search query: "東京都"
main(file_path, search_query)
