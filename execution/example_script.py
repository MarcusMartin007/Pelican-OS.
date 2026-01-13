import os
import sys

def main():
    print("This is an example deterministic script.")
    print(f"Arguments passed: {sys.argv[1:]}")
    
    # Simulate work
    output_dir = ".tmp"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(os.path.join(output_dir, "example_output.txt"), "w") as f:
        f.write("Execution complete.")

if __name__ == "__main__":
    main()
