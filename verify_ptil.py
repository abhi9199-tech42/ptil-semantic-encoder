""" 
PTIL (Pre-Tokenization Intelligence Layer) Verification Test 
============================================================ 
Run this: python verify_ptil.py 
""" 

import subprocess 
import sys 
from pathlib import Path 

def find_ptil(): 
    """Find PTIL project""" 
    # First check if we are already in the project root
    # A standard PTIL project root should have a 'ptil' subdirectory (the package)
    if (Path.cwd() / 'ptil').exists() and (Path.cwd() / 'ptil').is_dir():
        return Path.cwd()

    names = [ 
        'ptil', 'PTIL', 
        'Pre-Tokenization Intelligence Layer', 
        'ptil_engine', 
        'PromptShield' 
    ] 
    
    for base in [Path.cwd(), Path.cwd().parent]: 
        for name in names: 
            path = base / name 
            if path.exists(): 
                return path 
    return None 

def check_demos(project_dir): 
    """Check for demo scripts""" 
    examples_dir = project_dir / 'examples' 
    if not examples_dir.exists(): 
        return [] 
    
    demos = list(examples_dir.glob('*.py')) 
    return demos 

def run_basic_test(project_dir): 
    """Try to run basic_usage.py demo""" 
    examples_dir = project_dir / 'examples' 
    basic_demo = examples_dir / 'basic_usage.py' 
    
    if not basic_demo.exists(): 
        return -1, "basic_usage.py not found", "" 
    
    try: 
        result = subprocess.run( 
            [sys.executable, str(basic_demo)], 
            capture_output=True, 
            text=True, 
            timeout=10, 
            cwd=project_dir 
        ) 
        return result.returncode, result.stdout, result.stderr 
    except subprocess.TimeoutExpired: 
        return -1, "TIMEOUT", "" 
    except Exception as e: 
        return -1, "", str(e) 

def test_ptil_import(project_dir): 
    """Test PTIL import and basic encoding""" 
    sys.path.insert(0, str(project_dir)) 
    
    try: 
        from ptil import PTILEncoder 
        
        encoder = PTILEncoder() 
        
        # Test basic compression 
        test_text = "The quick brown fox jumps over the lazy dog" 
        csc = encoder.encode(test_text) 
        
        # Check if csc is valid (list of CSC objects or similar structure)
        # Adjust check based on actual return type of encode
        if csc: 
            return True, f"✅ Encoded to CSC: {csc}" 
        else: 
            return False, f"❌ Invalid CSC output: {csc}" 
            
    except ImportError as e: 
        return False, f"❌ Cannot import PTIL: {e}" 
    except Exception as e: 
        return False, f"❌ Encoding failed: {e}" 

def run_pytest(project_dir): 
    """Run pytest if tests exist""" 
    tests_dir = project_dir / 'tests' 
    
    if not tests_dir.exists(): 
        return -1, "No tests/ directory", "" 
    
    import os 
    os.chdir(project_dir) 
    
    try: 
        # using python -m pytest to use the same python environment
        result = subprocess.run( 
            [sys.executable, '-m', 'pytest', 'tests/', '-v'], 
            capture_output=True, 
            text=True, 
            timeout=300 
        ) 
        return result.returncode, result.stdout, result.stderr 
    except Exception as e: 
        return -1, "", f"pytest failed to run: {str(e)}" 

def main(): 
    print("=" * 70) 
    print("PTIL VERIFICATION TEST") 
    print("=" * 70) 
    
    # Find project 
    print("\n[1/5] Finding PTIL...") 
    project_dir = find_ptil() 
    
    if not project_dir: 
        # If we are in the root already
        if (Path.cwd() / 'ptil').exists():
            project_dir = Path.cwd()
        else:
            print("❌ PTIL not found") 
            print("Searched: ptil, PTIL, ptil_engine, PromptShield") 
            return 
    
    print(f"✅ Found: {project_dir}") 
    
    # Check for demos 
    print("\n[2/5] Checking for demo scripts...") 
    demos = check_demos(project_dir) 
    
    if demos: 
        print(f"✅ Found {len(demos)} demos:") 
        for demo in demos[:5]: 
            print(f"   - {demo.name}") 
    else: 
        print("⚠️  No demo scripts found in examples/") 
    
    # Run basic demo 
    print("\n[3/5] Running basic_usage.py...") 
    print("-" * 70) 
    
    returncode, stdout, stderr = run_basic_test(project_dir) 
    
    if returncode == 0: 
        print(stdout[:500])  # First 500 chars 
        print("-" * 70) 
        print("✅ Demo ran successfully") 
        demo_ok = True 
    elif returncode == -1: 
        print(stdout) 
        print("-" * 70) 
        print("⚠️  Demo not available or failed") 
        demo_ok = False 
    else: 
        print(stdout[:500]) 
        print("ERRORS:", stderr[:500]) 
        print("-" * 70) 
        print(f"❌ Demo failed (code {returncode})") 
        demo_ok = False 
    
    # Test import 
    print("\n[4/5] Testing PTIL import & encoding...") 
    import_ok, import_msg = test_ptil_import(project_dir) 
    print(import_msg) 
    
    # Run tests 
    print("\n[5/5] Running pytest (if available)...") 
    print("-" * 70) 
    
    test_code, test_out, test_err = run_pytest(project_dir) 
    
    if test_code == 0: 
        print(test_out[:500]) 
        print("-" * 70) 
        print("✅ Tests passed") 
        test_ok = True 
    elif test_code == -1: 
        print(test_out) 
        print("ERRORS:", test_err)
        print("-" * 70) 
        print("⚠️  No tests or pytest unavailable") 
        test_ok = False 
    else: 
        print(test_out[:500]) 
        print("-" * 70) 
        print(f"❌ Tests failed") 
        test_ok = False 
    
    # Summary 
    print("\n" + "=" * 70) 
    print("SUMMARY") 
    print("=" * 70) 
    print(f"Project: {project_dir.name}") 
    print(f"Demos: {len(demos)} found") 
    print(f"Demo ran: {'YES' if demo_ok else 'NO'}") 
    print(f"Import works: {'YES' if import_ok else 'NO'}") 
    print(f"Tests: {'PASS' if test_ok else 'FAIL/NOT RUN'}") 
    
    if import_ok and (demo_ok or test_ok): 
        print("\n🎉 VERDICT: PTIL IS WORKING") 
    else: 
        print("\n❌ VERDICT: PTIL HAS ISSUES") 
    
    print("=" * 70) 

if __name__ == "__main__": 
    main()