  import sys
  import os

  # Add the analyzer service to Python path
  sys.path.insert(0, r"C:\Users\umang\Documents\GitHub\PDFy\services\analyzer")

  from app.services.fast_scan import run_fast_scan

  def main():
      if len(sys.argv) < 2:
          print("Usage: python tui.py <pdf_file>")
          sys.exit(1)

      file_path = sys.argv[1]
      if not os.path.exists(file_path):
          print(f"Error: File '{file_path}' not found")
          sys.exit(1)

      try:
          with open(file_path, "rb") as f:
              pdf_bytes = f.read()
      except Exception as e:
          print(f"Error reading file: {e}")
          sys.exit(1)

      try:
          result = run_fast_scan(pdf_bytes, os.path.basename(file_path))

          print("=" * 50)
          print("PDF Malware Analysis Results")
          print("=" * 50)
          print(f"File: {result.file_name}")
          print(f"SHA256: {result.sha256}")
          print(f"Keyword Hits: {', '.join(result.keyword_hits) if result.keyword_hits else 'None'}")
          print(f"URLs Found: {', '.join(result.iocs.urls) if result.iocs.urls else 'None'}")
          print(f"IPs Found: {', '.join(result.iocs.ips) if result.iocs.ips else 'None'}")
          print(f"Verdict: {result.summary.verdict}")
          print(f"Score: {result.summary.score}/100")
          print(f"Confidence: {result.summary.confidence}")
          print("=" * 50)
      except Exception as e:
          print(f"Error during analysis: {e}")
          sys.exit(1)

  if __name__ == "__main__":
      main()