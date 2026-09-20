import os
import re
import sys

def patch_file(path, replacements):
    if not os.path.exists(path):
        print(f"ERROR: File not found: {path}")
        sys.exit(1)
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    orig_content = content
    for target, replacement in replacements:
        if callable(target):
            content = target(content)
        elif target not in content:
            print(f"ERROR: Target text not found in {path}:\n{target}")
            sys.exit(1)
        else:
            content = content.replace(target, replacement, 1)
            print(f"Successfully replaced target in {path}")
            
    if content == orig_content:
        print(f"WARNING: No changes made to {path}")
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {path}")

def main():
    print("=== Applying Unlimited Accounts Patch for Telegram Desktop ===")
    
    # 1. Patch Telegram/SourceFiles/main/main_domain.h
    main_domain_h = "Telegram/SourceFiles/main/main_domain.h"
    def patch_domain_h(text):
        text, n1 = re.subn(r"static constexpr auto kMaxAccounts = \d+;", "static constexpr auto kMaxAccounts = 1000000;", text)
        text, n2 = re.subn(r"static constexpr auto kPremiumMaxAccounts = \d+;", "static constexpr auto kPremiumMaxAccounts = 1000000;", text)
        if n1 == 0 or n2 == 0:
            print("ERROR: Failed to regex replace kMaxAccounts or kPremiumMaxAccounts in main_domain.h")
            sys.exit(1)
        print("Patched kMaxAccounts & kPremiumMaxAccounts to 1000000 in main_domain.h")
        return text

    patch_file(main_domain_h, [(patch_domain_h, None)])

    # 2. Patch Telegram/SourceFiles/storage/storage_domain.cpp
    storage_domain_cpp = "Telegram/SourceFiles/storage/storage_domain.cpp"
    t1 = "if (count <= 0 || count > Main::Domain::kPremiumMaxAccounts) {"
    r1 = "if (count <= 0) {"

    t2 = "if (index >= 0\n\t\t\t&& index < Main::Domain::kPremiumMaxAccounts\n\t\t\t&& tried.emplace(index).second) {"
    r2 = "if (index >= 0\n\t\t\t&& tried.emplace(index).second) {"

    patch_file(storage_domain_cpp, [
        (t1, r1),
        (t2, r2),
    ])

    print("=== All Unlimited Accounts Patches Applied Successfully! ===")

if __name__ == "__main__":
    main()
