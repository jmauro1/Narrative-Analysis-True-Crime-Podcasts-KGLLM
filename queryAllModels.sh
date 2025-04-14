#!/bin/bash

# Function to display usage instructions
usage() {
    echo "Usage: $0 --data <Data> --root <Root> --query <QueryFile> --text <TextFile1> [--text <TextFile2> ...]"
    exit 1
}

# Check if the correct number of arguments is provided
if [ "$#" -lt 6 ]; then
    usage
fi

# Initialize variables
DATA_DIR=""
ROOT_DIR=""
QUERY_FILE=""
TEXT_FILES=()

# Parse labeled inputs
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --data)
            DATA_DIR="$2"
            shift 2
            ;;
        --root)
            ROOT_DIR="$2"
            shift 2
            ;;
        --query)
            QUERY_FILE="$2"
            shift 2
            ;;
        --text)
            TEXT_FILES+=("$2")
            shift 2
            ;;
        *)
            echo "Unknown parameter passed: $1"
            usage
            ;;
    esac
done

# Check if required parameters are set
if [[ -z "$DATA_DIR" || -z "$ROOT_DIR" || -z "$QUERY_FILE" || ${#TEXT_FILES[@]} -eq 0 ]]; then
    usage
fi
TIMESTAMP=$(date "+%Y%m%d%H%M%S")
OUTPUT_CSV="${ROOT_DIR}/Query Results: ${TIMESTAMP}.csv"

# Ensure the QUERY_FILE exists
if [ ! -f "$QUERY_FILE" ]; then
    echo "Query file not found!"
    exit 1
fi

# Create or overwrite the output CSV file
echo "Query,GraphRAG_Local_Output,GraphRAG_Global_Output,NaiveRAG_Output,NaiveLLM_Output" > "$OUTPUT_CSV"

# Read the query file line by line
while IFS= read -r query; do
    echo "Processing query: $query"
    
    # Run the graphrag.query module with local search
    graphrag_local_output=$(python -m graphrag.query --data "$DATA_DIR" --root "$ROOT_DIR" --method "local" "$query" 2>&1)
    echo "GraphRAG local output: $graphrag_local_output"

    # Run the graphrag.query module with global search
    graphrag_global_output=$(python -m graphrag.query --data "$DATA_DIR" --root "$ROOT_DIR" --method "global" "$query" 2>&1)
    echo "GraphRAG global output: $graphrag_global_output"
    
    # Run the naiveRAG.py script
    naiveRAG_output=$(python naiveRAG.py "$query" "${TEXT_FILES[@]}" 2>&1)
    echo "NaiveRAG output: $naiveRAG_output"
    
    # Run the naiveLLM.py script
    naiveLLM_output=$(python naiveLLM.py "$query" 2>&1)
    echo "NaiveLLM output: $naiveLLM_output"
    
    # Escape double quotes in outputs for CSV compatibility
    query_escaped=$(echo "$query" | sed 's/"/""/g')
    graphrag_local_output_escaped=$(echo "$graphrag_local_output" | sed 's/"/""/g')
    graphrag_global_output_escaped=$(echo "$graphrag_global_output" | sed 's/"/""/g')
    naiveRAG_output_escaped=$(echo "$naiveRAG_output" | sed 's/"/""/g')
    naiveLLM_output_escaped=$(echo "$naiveLLM_output" | sed 's/"/""/g')
    
    # Append the results to the CSV file
    echo "\"$query_escaped\",\"$graphrag_local_output_escaped\",\"$graphrag_global_output_escaped\",\"$naiveRAG_output_escaped\",\"$naiveLLM_output_escaped\"" >> "$OUTPUT_CSV"
done < "$QUERY_FILE"

echo "All queries processed. Results saved in $OUTPUT_CSV"
