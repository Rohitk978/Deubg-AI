import re

def detect_language(code: str):

    code = code.lower()

    # C
    if "#include" in code and "stdio.h" in code:
        return "C"

    # C++
    if "#include" in code and ("iostream" in code or "std::" in code):
        return "C++"

    # Python
    if re.search(r"\bdef\b", code) or "print(" in code:
        return "Python"

    # Java
    if "public static void main" in code or "system.out.println" in code:
        return "Java"

    # JavaScript
    if "console.log" in code or "function(" in code:
        return "JavaScript"

    # TypeScript
    if ": string" in code or ": number" in code:
        return "TypeScript"

    # Go
    if "package main" in code and "func main()" in code:
        return "Go"

    # Rust
    if "fn main()" in code and "println!" in code:
        return "Rust"

    # C#
    if "using system" in code and "namespace" in code:
        return "C#"

    # PHP
    if "<?php" in code:
        return "PHP"

    # SQL
    if "select " in code and "from " in code:
        return "SQL"

    return "Unknown"