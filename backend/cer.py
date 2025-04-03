
# function that already exists (i didn't write it myself)
def levenshtein_distance(hyp: str, ref: str) -> int:
    """Calculate the Levenshtein distance between two strings"""
    m = len(hyp)
    n = len(ref)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
        
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if hyp[i-1] == ref[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,     # Deletion
                dp[i][j-1] + 1,     # Insertion
                dp[i-1][j-1] + cost  # Substitution
            )
    return dp[m][n]

def calculate_cer(data):
    """Calculate CER for each row and overall CER"""
    total_errors = 0
    total_chars = 0
    
    for row in data:
        key = row[0]
        hyp = row[1]
        ref = row[2]
        
        # Convert to strings and handle N/A
        hyp_str = str(hyp).strip() if hyp != 'N/A' else ''
        ref_str = str(ref).strip() if ref != 'N/A' else ''
        
        # Handle empty reference cases
        if not ref_str:
            cer = 1.0 if hyp_str else 0.0
            row.append(cer)
            total_errors += len(hyp_str)
            continue
        
        # Calculate Levenshtein distance
        distance = levenshtein_distance(hyp_str, ref_str)
        cer = distance / len(ref_str)
        
        # "row" is an array of 3 objects, but this should make it 4 with key, hyptext, reftext, and now cer
        row.append(cer)
        total_errors += distance
        total_chars += len(ref_str)
    
    # Calculate overall CER
    overall_cer = total_errors / total_chars if total_chars > 0 else 0.0
    
    # returns modified comparison data + overall cer
    return {"result": data, "cer": overall_cer}



# # Example usage
# data = [
#     ['first_name', 'John', 'John'],
#     ['last_name', 'Doe', 'Doe'],
#     ['address', 'N/A', '123 Sigma Street'],
#     ['city', 'Toronto', 'Toronto'],
#     ['email_address', 'johndoe@gmail.com', 'johndoe@gmail.com'],
#     ['form_year', 'N/A', 2024],
#     ['form_type', 'N/A', 'T1'],
#     ['form_description', 'N/A', 'Income Tax and Benefit Return'],
#     ['social_insurance_number', '876543210', '876543210'],
#     ['SIN', 'N/A', '876543210'],
#     ['net_income', 'N/A', '800500'],
#     ['total_income', 'N/A', '69420']
# ]

# cer_results = calculate_cer(data)

# # Print results
# print("Per-field CER:")
# for result in cer_results['results']:
#     print(f"{result['key']}: {result['cer'] * 100:.2f}%")

# print(f"\nOverall CER: {cer_results['overall_cer'] * 100:.2f}%")

