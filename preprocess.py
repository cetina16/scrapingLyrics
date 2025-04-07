import pandas as pd
import sys
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Redirect output to a file
class DualLogger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = DualLogger("output_preprocess.txt")

# Ensure consistent language detection results
DetectorFactory.seed = 0

file = "lyrics_translations.csv"
print(f"Reading input file: {file}")

try:
    df = pd.read_csv(file)
    print(f"Initial data shape: {df.shape}")

    # Drop rows with "No translation found"
    for col in df.columns:
        if "translation" in col.lower():
            df = df[df[col] != "No translation found"]
    print(f"After removing rows with 'No translation found': {df.shape}")

    text_col = "text"
    translation_col = "translation"

    # Split into lines
    df["text_lines"] = df[text_col].astype(str).apply(lambda x: x.split("\n"))
    df["translation_lines"] = df[translation_col].astype(str).apply(lambda x: x.split("\n"))
    print("Split lyrics and translations into lines.")

    # Keep only rows with matching line counts
    df = df[df["text_lines"].str.len() == df["translation_lines"].str.len()]
    print(f"After filtering line mismatches: {df.shape}")

    # Language detection
    def is_english(text):
        try:
            return detect(text) == "en"
        except LangDetectException:
            return False

    df = df[df[translation_col].apply(is_english)]
    print(f"After filtering non-English translations: {df.shape}")

    # Drop temporary line columns
    df = df.drop(columns=["text_lines", "translation_lines"])

    # Save to new file
    output_file = "processed_lyrics_translations-b4.csv"
    df.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")
    print(f"Final row count: {len(df)}")

except FileNotFoundError as e:
    print(f"Error: {e}. Please ensure the CSV file exists in the current directory.")
