import os
from pathlib import Path
import sys

# Add current dir to python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from leakwatch.orchestration.pipeline import PipelineManager

def main():
    pm = PipelineManager()
    
    if len(sys.argv) > 1:
        img_path = Path(sys.argv[1])
        if not img_path.exists():
            print(f"Error: Could not find the specified image: {img_path}")
            return
    else:
        # Try the user-provided path first, then fallback to what we found
        paths_to_try = [
            Path("samples/image/sample_aadhar.png"),
            Path("samples/images/driver_licence.jpeg"),
            Path("samples/image/driver_lisence.jpeg")
        ]
        
        img_path = None
        for p in paths_to_try:
            if p.exists():
                img_path = p
                break
                
        if not img_path:
            print("Error: Could not find the sample image.")
            return

    print(f"Processing image: {img_path}")
    result = pm.process_image(img_path)
    
    print("-" * 50)
    print("PIPELINE RESULT")
    print("-" * 50)
    print(f"Output Image Path: {result.mitigated_output}")
    
    overlay_paths = [a for a in result.artifacts if str(a).endswith('.overlay.png')]
    overlay = overlay_paths[0] if overlay_paths else None
    print(f"Overlay Image Path: {overlay}")
    print(f"Audit Log Path: {getattr(result, 'audit_log', None)}")
    
    print("\nDetected Entities:")
    for ent in result.entities:
        print(f" - [{ent.label}] '{ent.text}' (Conf: {ent.confidence:.2f}) -> Location: {ent.bbox}")

if __name__ == '__main__':
    main()
