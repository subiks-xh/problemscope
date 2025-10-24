import os

print("Checking routes.py file...")
print("-" * 60)

file_path = "app/routes.py"

if os.path.exists(file_path):
    print(f"✅ File exists: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "PASSWORD RESET REQUEST SUBMITTED" in content:
        print("✅ Updated code found in routes.py")
    else:
        print("❌ Updated code NOT found - file not updated properly!")
    
    if "RESET REQUEST FUNCTION CALLED" in content:
        print("✅ Debug print statements found")
    else:
        print("❌ Debug print statements NOT found!")
        
    print(f"\nFile size: {len(content)} characters")
    print(f"File location: {os.path.abspath(file_path)}")
    
else:
    print(f"❌ File not found: {file_path}")

print("-" * 60)