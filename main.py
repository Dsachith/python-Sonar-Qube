import os
import datetime
from typing import Dict, List
from analyzer.code_analyzer import analyze_flutter_project
from analyzer.visualization import generate_report
from utils.file_utils import get_flutter_project_files
from config.settings import OUTPUT_DIR

def main():
    flutter_project_path = input("Enter path to your Flutter project: ").strip()
    
    if not os.path.exists(flutter_project_path):
        print("Error: The specified path does not exist.")
        return
    
    # Get all Dart files in the project
    dart_files = get_flutter_project_files(flutter_project_path)
    
    if not dart_files:
        print("No Dart files found in the specified project.")
        return
    
    # Analyze the project
    analysis_results = analyze_flutter_project(dart_files)
    
    # Generate the report
    report_path = os.path.join(OUTPUT_DIR, "code_analysis_report.html")
    generate_report(analysis_results, report_path)
    
    print(f"Analysis complete. Report generated at: {report_path}")

if __name__ == "__main__":
    main()