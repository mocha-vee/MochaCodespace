import os
import sys
import subprocess
import tempfile
import threading
import webbrowser
import re
from pathlib import Path

# Try PyQt6 first, fallback to PySide6
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTextEdit, QPlainTextEdit, QPushButton, QLabel, QComboBox,
        QFileDialog, QMessageBox, QInputDialog, QSplitter, QTreeWidget,
        QTreeWidgetItem, QTabWidget, QToolBar, QStatusBar, QMenuBar, QMenu,
        QCompleter, QListWidget
    )
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal as Signal, QThread, QStringListModel, QRect
    from PyQt6.QtGui import (QFont, QTextCharFormat, QColor, QTextCursor, QKeySequence, 
                             QAction, QSyntaxHighlighter, QPalette)
    USING_PYQT = True
except ImportError:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTextEdit, QPlainTextEdit, QPushButton, QLabel, QComboBox,
        QFileDialog, QMessageBox, QInputDialog, QSplitter, QTreeWidget,
        QTreeWidgetItem, QTabWidget, QToolBar, QStatusBar, QMenuBar, QMenu,
        QCompleter, QListWidget
    )
    from PySide6.QtCore import Qt, QTimer, Signal, QThread, QStringListModel, QRect
    from PySide6.QtGui import (QFont, QTextCharFormat, QColor, QTextCursor, QKeySequence,
                               QAction, QSyntaxHighlighter, QPalette)
    USING_PYQT = False


# Language configurations
LANG_CONFIG = {
    "PTX": {
        "ext": ".ptx",
        "sample": "examples/hello.ptx",
        "comment": "// ",
        "runner": "ptx"
    },
    "Python": {
        "ext": ".py",
        "sample": "examples/hello.py",
        "comment": "# ",
        "runner": lambda f: [sys.executable, str(f)]
    },
    "Java": {
        "ext": ".java",
        "sample": "examples/Hello.java",
        "comment": "// ",
        "runner": "java"
    },
    "C": {
        "ext": ".c",
        "sample": "examples/hello.c",
        "comment": "// ",
        "runner": "c"
    },
    "C++": {
        "ext": ".cpp",
        "sample": "examples/hello.cpp",
        "comment": "// ",
        "runner": "cpp"
    },
    "JavaScript": {
        "ext": ".js",
        "sample": "examples/hello.js",
        "comment": "// ",
        "runner": lambda f: ["node", str(f)]
    },
    "TypeScript": {
        "ext": ".ts",
        "sample": "examples/hello.ts",
        "comment": "// ",
        "runner": "typescript"
    },
    "Rust": {
        "ext": ".rs",
        "sample": "examples/hello.rs",
        "comment": "// ",
        "runner": "rust"
    },
    "Go": {
        "ext": ".go",
        "sample": "examples/hello.go",
        "comment": "// ",
        "runner": lambda f: ["go", "run", str(f)]
    },
    "C#": {
        "ext": ".cs",
        "sample": "examples/hello.cs",
        "comment": "// ",
        "runner": "csharp"
    },
    "Ruby": {
        "ext": ".rb",
        "sample": "examples/hello.rb",
        "comment": "# ",
        "runner": lambda f: ["ruby", str(f)]
    },
    "Kotlin": {
        "ext": ".kt",
        "sample": "examples/hello.kt",
        "comment": "// ",
        "runner": "kotlin"
    },
    "HTML": {
        "ext": ".html",
        "sample": "examples/index.html",
        "comment": "<!-- ",
        "runner": "browser"
    },
    "CSS": {
        "ext": ".css",
        "sample": "examples/styles.css",
        "comment": "/* ",
        "runner": "browser"
    },
    "Lua": {
        "ext": ".lua",
        "sample": "examples/hello.lua",
        "comment": "-- ",
        "runner": lambda f: ["lua", str(f)]
    },
    "Nix": {
        "ext": ".nix",
        "sample": "examples/shell.nix",
        "comment": "# ",
        "runner": "nix"
    }
}

# Keywords and autocomplete suggestions for each language
LANGUAGE_KEYWORDS = {
    "PTX": [
        "AL2P", "ALD", "AST", "B2R", "BFE", "BFI", "BMMA", "BMOV", "BMSK", "BREV",
        "BRK", "CCTL", "CCTLL", "CCTLT", "CONT", "CS2R", "CSET", "CSETP", "DADD",
        "DEPBAR", "DFMA", "DMMA", "DMNMX", "DMUL", "DSET", "DSETP", "F2F", "F2FP",
        "F2I", "F2IP", "FADD", "FADD32I", "FCHK", "FCMP", "FFMA", "FFMA32I", "FLO",
        "FMNMX", "FMUL", "FMUL32I", "FRND", "FSEL", "FSET", "FSETP", "FSWZADD",
        "GETCRSPTR", "GETLMEMBASE", "HADD2", "HFMA2", "HMMA", "HMNMX2", "HMUL2",
        "HSET2", "HSETP2", "I2F", "I2FP", "I2I", "I2IP", "IABS", "IADD", "IADD3",
        "IADD32I", "ICMP", "IDE", "IDP", "IMAD", "IMAD32I", "IMADSP", "IMMA", "IMNMX",
        "IMUL", "IMUL32I", "IPA", "ISBERD", "ISBEWR", "ISCADD", "ISCADD32I", "ISET", "ISETP",
        "JCAL", "LDC", "LDGDEPBAR", "LDGSTS", "LEA", "LEPC", "LONGJMP", "LOP", "LOP3",
        "LOP32I", "MATCH", "MOV", "MOV32I", "MOVM", "MUFU", "NOP", "OUT", "P2R", "PCNT",
        "PEXIT", "PIXLD", "PLONGJMP", "PLOP3", "POPC", "PRMT", "PSET", "PSETP", "QSPC",
        "R2B", "R2P", "R2UR", "RAM", "REDUX", "RRO", "RTT", "S2R", "S2UR", "SAM", "SEL",
        "SETCRSPTR", "SETLMEMBASE", "SGXT", "SHF", "SHFL", "SHL", "SHR", "STP", "TLD4S",
        "TLDS", "TMML", "TXA", "TXD", "TXQ", "UBREV", "UFLO", "UIADD3", "UIMAD", "UISETP",
        "ULDC", "ULEA", "ULOP3", "UMOV", "UP2UR", "UPLOP3", "UPOPC", "UPRMT", "USEL",
        "USGXT", "USHF", "VABSDIFF", "VABSDIFF4", "VADD", "VMAD", "VMNMX", "VOTE", "VOTEU",
        "VSET", "VSETP", "VSHL", "VSHR", "XMAD"
    ],
    "Python": [
        "and", "as", "assert", "async", "await", "break", "class", "continue",
        "def", "del", "elif", "else", "except", "False", "finally", "for",
        "from", "global", "if", "import", "in", "is", "lambda", "None",
        "nonlocal", "not", "or", "pass", "raise", "return", "True", "try",
        "while", "with", "yield", "print", "len", "range", "str", "int",
        "float", "list", "dict", "set", "tuple", "open", "self", "__init__"
    ],
    "Java": [
        "abstract", "assert", "boolean", "break", "byte", "case", "catch",
        "char", "class", "const", "continue", "default", "do", "double",
        "else", "enum", "extends", "final", "finally", "float", "for",
        "if", "implements", "import", "instanceof", "int", "interface",
        "long", "native", "new", "package", "private", "protected", "public",
        "return", "short", "static", "strictfp", "super", "switch", "synchronized",
        "this", "throw", "throws", "transient", "try", "void", "volatile", "while",
        "String", "System", "out", "println", "main", "args"
    ],
    "C": [
        "auto", "break", "case", "char", "const", "continue", "default", "do",
        "double", "else", "enum", "extern", "float", "for", "goto", "if",
        "int", "long", "register", "return", "short", "signed", "sizeof",
        "static", "struct", "switch", "typedef", "union", "unsigned", "void",
        "volatile", "while", "printf", "scanf", "malloc", "free", "NULL",
        "include", "define", "stdio", "stdlib", "string"
    ],
    "C++": [
        "alignas", "alignof", "and", "and_eq", "asm", "auto", "bitand", "bitor",
        "bool", "break", "case", "catch", "char", "class", "const", "constexpr",
        "continue", "decltype", "default", "delete", "do", "double", "dynamic_cast",
        "else", "enum", "explicit", "export", "extern", "false", "float", "for",
        "friend", "goto", "if", "inline", "int", "long", "mutable", "namespace",
        "new", "noexcept", "not", "nullptr", "operator", "or", "private", "protected",
        "public", "return", "short", "signed", "sizeof", "static", "struct", "switch",
        "template", "this", "throw", "true", "try", "typedef", "typeid", "typename",
        "union", "unsigned", "using", "virtual", "void", "volatile", "while",
        "cout", "cin", "endl", "string", "vector", "iostream", "std"
    ],
    "JavaScript": [
        "async", "await", "break", "case", "catch", "class", "const", "continue",
        "debugger", "default", "delete", "do", "else", "export", "extends", "false",
        "finally", "for", "function", "if", "import", "in", "instanceof", "let",
        "new", "null", "return", "super", "switch", "this", "throw", "true",
        "try", "typeof", "var", "void", "while", "with", "yield",
        "console", "log", "document", "window", "Array", "Object", "String",
        "Number", "Boolean", "Math", "Date", "JSON", "Promise", "setTimeout"
    ],
    "TypeScript": [
        "abstract", "any", "as", "async", "await", "boolean", "break", "case",
        "catch", "class", "const", "continue", "debugger", "declare", "default",
        "delete", "do", "else", "enum", "export", "extends", "false", "finally",
        "for", "from", "function", "if", "implements", "import", "in", "instanceof",
        "interface", "is", "keyof", "let", "module", "namespace", "never", "new",
        "null", "number", "of", "package", "private", "protected", "public",
        "readonly", "require", "return", "static", "string", "super", "switch",
        "symbol", "this", "throw", "true", "try", "type", "typeof", "undefined",
        "unique", "unknown", "var", "void", "while", "with", "yield"
    ],
    "Rust": [
        "as", "async", "await", "break", "const", "continue", "crate", "dyn",
        "else", "enum", "extern", "false", "fn", "for", "if", "impl", "in",
        "let", "loop", "match", "mod", "move", "mut", "pub", "ref", "return",
        "self", "Self", "static", "struct", "super", "trait", "true", "type",
        "unsafe", "use", "where", "while", "String", "Vec", "Option", "Result",
        "println", "print", "format", "panic", "unwrap", "expect"
    ],
    "Go": [
        "break", "case", "chan", "const", "continue", "default", "defer", "else",
        "fallthrough", "for", "func", "go", "goto", "if", "import", "interface",
        "map", "package", "range", "return", "select", "struct", "switch", "type",
        "var", "fmt", "Println", "Printf", "Sprintf", "main", "string", "int",
        "bool", "float64", "error", "nil", "true", "false", "make", "len", "append"
    ],
    "Ruby": [
        "alias", "and", "begin", "break", "case", "class", "def", "defined",
        "do", "else", "elsif", "end", "ensure", "false", "for", "if", "in",
        "module", "next", "nil", "not", "or", "redo", "rescue", "retry",
        "return", "self", "super", "then", "true", "undef", "unless", "until",
        "when", "while", "yield", "puts", "print", "gets", "attr_accessor",
        "attr_reader", "attr_writer", "initialize", "new", "require"
    ],
    "HTML": [
        "html", "head", "title", "body", "div", "span", "p", "a", "img",
        "ul", "ol", "li", "table", "tr", "td", "th", "form", "input",
        "button", "select", "option", "textarea", "label", "h1", "h2",
        "h3", "h4", "h5", "h6", "header", "footer", "nav", "section",
        "article", "aside", "main", "script", "style", "link", "meta",
        "br", "hr", "strong", "em", "code", "pre"
    ],
    "CSS": [
        "color", "background", "background-color", "font-family", "font-size",
        "font-weight", "margin", "padding", "border", "width", "height",
        "display", "position", "top", "left", "right", "bottom", "flex",
        "grid", "justify-content", "align-items", "text-align", "cursor",
        "transition", "transform", "opacity", "z-index", "overflow", "box-shadow"
    ]
}

# Sample code templates
SAMPLE_CODE = {
    "PTX": """
@P0 IMAD32I.U32.U32 R0, R0, 0x0, R0;
@P0 FADD32I R0, R0, 0;
@P0 LD.U8 R0, [R0];
""",
    "Python": """#!/usr/bin/env python3
\"\"\"
Simple Python Hello World
\"\"\"

def main():
    print("Hello from Mocha Codespace!")
    print("Python version:", end=" ")
    import sys
    print(sys.version.split()[0])

if __name__ == "__main__":
    main()
""",
    
    "Java": """public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello from Mocha Codespace!");
        System.out.println("Java version: " + System.getProperty("java.version"));
    }
}
""",
    
    "C": """#include <stdio.h>

int main() {
    printf("Hello from  Mocha Codespace!\\n");
    printf("Compiled with C\\n");
    return 0;
}
""",
    
    "C++": """#include <iostream>
#include <string>

int main() {
    std::cout << "Hello from Mocha Codespace!" << std::endl;
    std::cout << "C++ version: " << __cplusplus << std::endl;
    return 0;
}
""",
    
    "JavaScript": """// Hello World in JavaScript
console.log("Hello from Mocha Codespace!");
console.log("Node version:", process.version);

// Example function
function greet(name) {
    return `Hello, ${name}!`;
}

console.log(greet("Developer"));
""",
    
    "TypeScript": """// Hello World in TypeScript
function greet(name: string): string {
    return `Hello, ${name}!`;
}

console.log("Hello from Mocha Codespace!");
console.log(greet("Developer"));

// Example interface
interface Person {
    name: string;
    age: number;
}

const user: Person = {
    name: "Developer",
    age: 25
};

console.log(`User: ${user.name}, Age: ${user.age}`);
""",
    
    "Rust": """// Hello World in Rust
fn main() {
    println!("Hello from Mocha Codespace!");
    println!("Rust is awesome!");
    
    // Example variables
    let name = "Developer";
    let version = "1.0";
    
    println!("Welcome, {}! Version: {}", name, version);
}
""",
    
    "Go": """package main

import (
    "fmt"
    "runtime"
)

func main() {
    fmt.Println("Hello from Mocha Codespace!")
    fmt.Printf("Go version: %s\\n", runtime.Version())
    
    // Example function
    greet("Developer")
}

func greet(name string) {
    fmt.Printf("Hello, %s!\\n", name)
}
""",
    
    "C#": """using System;

class Program
{
    static void Main()
    {
        Console.WriteLine("Hello from Mocha Codespace!");
        Console.WriteLine($"C# version: {Environment.Version}");
        
        // Example method
        string greeting = Greet("Developer");
        Console.WriteLine(greeting);
    }
    
    static string Greet(string name)
    {
        return $"Hello, {name}!";
    }
}
""",
    
    "Ruby": """# Hello World in Ruby
puts "Hello from Mocha Codespace!"
puts "Ruby version: #{RUBY_VERSION}"

# Example method
def greet(name)
  "Hello, #{name}!"
end

puts greet("Developer")

# Example class
class Person
  attr_accessor :name, :age
  
  def initialize(name, age)
    @name = name
    @age = age
  end
  
  def introduce
    "I'm #{@name}, #{@age} years old"
  end
end

person = Person.new("Developer", 25)
puts person.introduce
""",
    
    "Kotlin": """// Hello World in Kotlin
fun main() {
    println("Hello from Mocha Codespace!")
    println("Kotlin is running!")
    
    // Example function
    val greeting = greet("Developer")
    println(greeting)
    
    // Example class
    val person = Person("Developer", 25)
    println(person.introduce())
}

fun greet(name: String): String {
    return "Hello, $name!"
}

class Person(val name: String, val age: Int) {
    fun introduce(): String {
        return "I'm $name, $age years old"
    }
}
""",
    
    "HTML": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hello from Mocha Codespace</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        h1 {
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Hello from Mocha Codespace! 🚀</h1>
        <p>Welcome to your HTML page created in Mocha Codespace.</p>
        <p>Edit this file and press Run to see changes in your browser!</p>
    </div>
</body>
</html>
""",
    
    "CSS": """/* Mocha Codespace - Sample Stylesheet */

:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --text-color: #333;
    --bg-color: #f5f5f5;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: var(--bg-color);
    color: var(--text-color);
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

h1, h2, h3 {
    color: var(--primary-color);
    margin-bottom: 1rem;
}

button {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
    transition: transform 0.2s;
}

button:hover {
    transform: scale(1.05);
}
""",
    
    "Lua": """-- Hello World in Lua
print("Hello from Mocha Codespace!")
print("Lua version: " .. _VERSION)

-- Example function
function greet(name)
    return "Hello, " .. name .. "!"
end

print(greet("Developer"))

-- Example table (Lua's main data structure)
local person = {
    name = "Developer",
    age = 25,
    introduce = function(self)
        return "I'm " .. self.name .. ", " .. self.age .. " years old"
    end
}

print(person:introduce())
""",
    
    "Nix": """# Mocha Codespace - Nix Shell Environment
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "mochacode-dev-env";
  
  buildInputs = with pkgs; [
    # Development tools
    gcc
    python3
    nodejs
    
    # Add your dependencies here
  ];
  
  shellHook = ''
    echo "Hello from Mocha Codespace!"
    echo "Nix development environment loaded"
    echo "Available tools: gcc, python3, nodejs"
  '';
}
"""
}


class SyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for multiple languages"""
    
    def __init__(self, parent, language="Python"):
        super().__init__(parent)
        self.language = language
        self.setup_rules()
        
    def setup_rules(self):
        """Setup highlighting rules based on language"""
        self.rules = []
        
        # Mocha theme colors
        keyword_color = QColor("#8b4513")      # Saddle brown
        string_color = QColor("#6b8e23")       # Olive drab
        comment_color = QColor("#a0826d")      # Light brown
        number_color = QColor("#cd853f")       # Peru
        function_color = QColor("#704241")     # Dark mocha
        
        # Keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(keyword_color)
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        # Get keywords for language
        keywords = LANGUAGE_KEYWORDS.get(self.language, [])
        for word in keywords:
            pattern = f"\\b{word}\\b"
            self.rules.append((re.compile(pattern), keyword_format))
        
        # String format (single and double quotes)
        string_format = QTextCharFormat()
        string_format.setForeground(string_color)
        self.rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.rules.append((re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))
        
        # Number format
        number_format = QTextCharFormat()
        number_format.setForeground(number_color)
        self.rules.append((re.compile(r'\b\d+\.?\d*\b'), number_format))
        
        # Function/method format
        function_format = QTextCharFormat()
        function_format.setForeground(function_color)
        function_format.setFontItalic(True)
        self.rules.append((re.compile(r'\b[A-Za-z_][A-Za-z0-9_]*(?=\()'), function_format))
        
        # Comment format (language-specific)
        comment_format = QTextCharFormat()
        comment_format.setForeground(comment_color)
        comment_format.setFontItalic(True)
        
        if self.language in ["Python", "Ruby", "Nix"]:
            self.rules.append((re.compile(r'#[^\n]*'), comment_format))
        elif self.language == "Lua":
            self.rules.append((re.compile(r'--[^\n]*'), comment_format))
        elif self.language in ["C", "C++", "Java", "JavaScript", "TypeScript", "Rust", "Go", "C#", "Kotlin"]:
            self.rules.append((re.compile(r'//[^\n]*'), comment_format))
            self.rules.append((re.compile(r'/\*.*?\*/', re.DOTALL), comment_format))
        elif self.language == "HTML":
            self.rules.append((re.compile(r'<!--.*?-->', re.DOTALL), comment_format))
        elif self.language == "CSS":
            self.rules.append((re.compile(r'/\*.*?\*/', re.DOTALL), comment_format))
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text"""
        for pattern, format_style in self.rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format_style)
    
    def set_language(self, language):
        """Change the highlighting language"""
        self.language = language
        self.setup_rules()
        self.rehighlight()


class RunnerThread(QThread):
    """Thread for running code without blocking UI"""
    output = Signal(str)
    finished = Signal()
    
    def __init__(self, command, cwd):
        super().__init__()
        self.command = command
        self.cwd = cwd
        
    def run(self):
        try:
            process = subprocess.Popen(
                self.command,
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=60)
            
            if stdout:
                self.output.emit(stdout)
            if stderr:
                self.output.emit(stderr)
                
        except subprocess.TimeoutExpired:
            self.output.emit("\n[Execution timeout after 60 seconds]\n")
        except Exception as e:
            self.output.emit(f"\n[Error: {str(e)}]\n")
        finally:
            self.finished.emit()


class CodeEditor(QPlainTextEdit):
    """Enhanced code editor with syntax highlighting and autocompletion"""
    
    def __init__(self, parent=None, language="Python"):
        super().__init__(parent)
        self.language = language
        self.setup_editor()
        self.setup_autocomplete()
        self.highlighter = SyntaxHighlighter(self.document(), language)
        
    def setup_editor(self):
        # Set JetBrains Mono font (fallback to other monospace fonts)
        font = QFont("JetBrains Mono", 11)
        if not font.exactMatch():
            font = QFont("Fira Code", 11)
        if not font.exactMatch():
            font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # Mocha theme colors - soft pastels
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #f5ebe0;
                color: #704241;
                selection-background-color: #e3d5ca;
                border: none;
                padding: 8px;
            }
        """)
        
        # Tab settings
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)
    
    def setup_autocomplete(self):
        """Setup autocompletion"""
        self.completer = QCompleter()
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        
        # Style the completer popup
        self.completer.popup().setStyleSheet("""
            QListView {
                background-color: #f5ebe0;
                color: #704241;
                border: 2px solid #d5bdaf;
                border-radius: 6px;
                padding: 4px;
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                selection-background-color: #e3d5ca;
            }
            QListView::item {
                padding: 6px;
                border-radius: 4px;
            }
            QListView::item:selected {
                background-color: #d5bdaf;
            }
        """)
        
        self.completer.activated.connect(self.insert_completion)
        self.update_completer_model()
    
    def update_completer_model(self):
        """Update completer with keywords for current language"""
        keywords = LANGUAGE_KEYWORDS.get(self.language, [])
        # Add words from current document
        text = self.toPlainText()
        words = set(re.findall(r'\b[A-Za-z_][A-Za-z0-9_]{2,}\b', text))
        all_completions = sorted(set(keywords) | words)
        
        model = QStringListModel(all_completions)
        self.completer.setModel(model)
    
    def insert_completion(self, completion):
        """Insert the selected completion"""
        cursor = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        cursor.movePosition(QTextCursor.MoveOperation.Left)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfWord)
        cursor.insertText(completion[-extra:])
        self.setTextCursor(cursor)
    
    def text_under_cursor(self):
        """Get the word under cursor for autocompletion"""
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        return cursor.selectedText()
    
    def keyPressEvent(self, event):
        # Handle completer shortcuts
        if self.completer.popup().isVisible():
            if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Escape, 
                               Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
                event.ignore()
                return
        
        # Auto-indent on Enter
        if event.key() == Qt.Key.Key_Return:
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()
            
            # Get indentation of current line
            indent = len(text) - len(text.lstrip())
            
            # Check if line ends with opening brace/colon
            stripped = text.rstrip()
            if stripped.endswith((':', '{', '(')):
                indent += 4
                
            super().keyPressEvent(event)
            self.insertPlainText(' ' * indent)
            return
            
        # Tab key inserts spaces
        elif event.key() == Qt.Key.Key_Tab:
            self.insertPlainText(' ' * 4)
            return
        
        # Handle normal key press
        super().keyPressEvent(event)
        
        # Show completer on Ctrl+Space or after typing
        completion_prefix = self.text_under_cursor()
        
        if event.key() == Qt.Key.Key_Space and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Force show completer
            self.update_completer_model()
            self.completer.setCompletionPrefix("")
            rect = self.cursorRect()
            rect.setWidth(self.completer.popup().sizeHintForColumn(0) + 
                         self.completer.popup().verticalScrollBar().sizeHint().width())
            self.completer.complete(rect)
        elif len(completion_prefix) >= 2 and event.text().isalnum():
            # Auto-show completer after 2 characters
            self.update_completer_model()
            self.completer.setCompletionPrefix(completion_prefix)
            
            if self.completer.completionCount() > 0:
                rect = self.cursorRect()
                rect.setWidth(self.completer.popup().sizeHintForColumn(0) + 
                             self.completer.popup().verticalScrollBar().sizeHint().width())
                self.completer.complete(rect)
    
    def set_language(self, language):
        """Change the editor language"""
        self.language = language
        self.highlighter.set_language(language)
        self.update_completer_model()


class EditorTab(QWidget):
    """Individual editor tab"""
    
    def __init__(self, language="Python", filepath=None):
        super().__init__()
        self.language = language
        self.filepath = Path(filepath) if filepath else None
        self.setup_ui()
        self.load_content()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Editor
        self.editor = CodeEditor(language=self.language)
        layout.addWidget(self.editor)
        
    def load_content(self):
        if self.filepath and self.filepath.exists():
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.editor.setPlainText(f.read())
        else:
            # Load sample code
            self.editor.setPlainText(SAMPLE_CODE.get(self.language, ""))
            
    def get_content(self):
        return self.editor.toPlainText()
        
    def save(self, filepath=None):
        if filepath:
            self.filepath = Path(filepath)
            
        if not self.filepath:
            return False
            
        # Ensure correct extension
        config = LANG_CONFIG.get(self.language, {})
        ext = config.get("ext", "")
        if ext and self.filepath.suffix != ext:
            self.filepath = self.filepath.with_suffix(ext)
            
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(self.get_content())
            return True
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save file:\n{str(e)}")
            return False


class MochaCodespace(QMainWindow):
    """Main IDE window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mocha Codespace")
        self.setGeometry(100, 100, 1200, 800)
        
        self.workspace_path = None
        self.runner_thread = None
        
        self.setup_ui()
        self.create_menus()
        self.create_toolbar()
        self.create_statusbar()
        self.setup_shortcuts()
        
        # Create initial tab
        self.new_file()
        
    def setup_ui(self):
        # Apply Mocha color scheme to main window
        self.setStyleSheet("""
            QMainWindow {
                background-color: #faf7f2;
            }
            QMenuBar {
                background-color: #f5ebe0;
                color: #704241;
                font-family: 'JetBrains Mono', 'Segoe UI', sans-serif;
                padding: 4px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #e3d5ca;
            }
            QMenu {
                background-color: #f5ebe0;
                color: #704241;
                border: 1px solid #d5bdaf;
                border-radius: 6px;
            }
            QMenu::item {
                padding: 8px 24px;
            }
            QMenu::item:selected {
                background-color: #e3d5ca;
                border-radius: 4px;
            }
            QToolBar {
                background-color: #f5ebe0;
                border: none;
                padding: 6px;
                spacing: 4px;
            }
            QPushButton, QToolButton {
                background-color: #e3d5ca;
                color: #704241;
                border: 1px solid #d5bdaf;
                border-radius: 6px;
                padding: 6px 12px;
                font-family: 'JetBrains Mono', 'Segoe UI', sans-serif;
                font-size: 10pt;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #d5bdaf;
            }
            QPushButton:pressed, QToolButton:pressed {
                background-color: #c9ada7;
            }
            QComboBox {
                background-color: #f5ebe0;
                color: #704241;
                border: 1px solid #d5bdaf;
                border-radius: 6px;
                padding: 6px 12px;
                font-family: 'JetBrains Mono', 'Segoe UI', sans-serif;
                min-width: 120px;
            }
            QComboBox:hover {
                border: 1px solid #c9ada7;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #f5ebe0;
                color: #704241;
                selection-background-color: #e3d5ca;
                border: 1px solid #d5bdaf;
                border-radius: 6px;
            }
            QTabWidget::pane {
                border: 1px solid #e3d5ca;
                background-color: #f5ebe0;
                border-radius: 6px;
                top: -1px;
            }
            QTabBar::tab {
                background-color: #e3d5ca;
                color: #704241;
                border: 1px solid #d5bdaf;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 2px;
                font-family: 'JetBrains Mono', 'Segoe UI', sans-serif;
            }
            QTabBar::tab:selected {
                background-color: #f5ebe0;
                border-bottom: 1px solid #f5ebe0;
            }
            QTabBar::tab:hover:!selected {
                background-color: #d5bdaf;
            }
            QTreeWidget {
                background-color: #faf7f2;
                color: #704241;
                border: 1px solid #e3d5ca;
                border-radius: 6px;
                font-family: 'JetBrains Mono', 'Segoe UI', sans-serif;
                padding: 4px;
            }
            QTreeWidget::item {
                padding: 6px;
                border-radius: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #e3d5ca;
            }
            QTreeWidget::item:hover {
                background-color: #f5ebe0;
            }
            QLabel {
                color: #704241;
                font-family: 'JetBrains Mono', 'Segoe UI', sans-serif;
                padding: 2px;
            }
            QStatusBar {
                background-color: #f5ebe0;
                color: #704241;
                border-top: 1px solid #e3d5ca;
                font-family: 'JetBrains Mono', 'Segoe UI', sans-serif;
            }
            QTextEdit {
                border: 1px solid #e3d5ca;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        
        # Central widget with splitter
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Main splitter (workspace tree | editor area)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.main_splitter)
        
        # Workspace tree (hidden initially)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("📁 Workspace")
        self.tree_widget.itemDoubleClicked.connect(self.on_tree_double_click)
        self.tree_widget.hide()
        
        # Right side: editor + console
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        
        # Tab widget for editor tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        right_layout.addWidget(self.tab_widget)
        
        # Console output
        console_label = QLabel("💻 Console Output:")
        console_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 11pt;
                padding: 4px;
            }
        """)
        right_layout.addWidget(console_label)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(200)
        self.console.setStyleSheet("""
            QTextEdit {
                background-color: #faf7f2;
                color: #704241;
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                font-size: 10pt;
                border: 1px solid #e3d5ca;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        right_layout.addWidget(self.console)
        
        self.main_splitter.addWidget(right_widget)
        
    def create_menus(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("&Find", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self.find_text)
        edit_menu.addAction(find_action)
        
        # Run menu
        run_menu = menubar.addMenu("&Run")
        
        run_action = QAction("&Run", self)
        run_action.setShortcut(Qt.Key.Key_F5)
        run_action.triggered.connect(self.run_code)
        run_menu.addAction(run_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(toolbar.iconSize() * 1.2)
        self.addToolBar(toolbar)
        
        # File operations
        toolbar.addAction("📄 New", self.new_file)
        toolbar.addAction("📂 Open", self.open_file)
        toolbar.addAction("💾 Save", self.save_file)
        toolbar.addSeparator()
        
        # Language selector
        lang_label = QLabel(" 🔤 Language: ")
        lang_label.setStyleSheet("font-weight: bold;")
        toolbar.addWidget(lang_label)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(list(LANG_CONFIG.keys()))
        self.lang_combo.currentTextChanged.connect(self.on_language_changed)
        toolbar.addWidget(self.lang_combo)
        
        toolbar.addSeparator()
        
        # Run button
        toolbar.addAction("▶️ Run", self.run_code)
        
        toolbar.addSeparator()
        
        # Workspace
        toolbar.addAction("📁 Open Workspace", self.open_workspace)
        toolbar.addAction("❌ Close Workspace", self.close_workspace)
        
    def create_statusbar(self):
        status_label = QLabel("✨ Welcome to Version 0.2!")
        self.statusBar().addPermanentWidget(status_label)
        self.statusBar().showMessage("Ready")
        
    def setup_shortcuts(self):
        pass  # Already handled in create_menus
        
    def new_file(self):
        language = self.lang_combo.currentText()
        tab = EditorTab(language=language)
        
        config = LANG_CONFIG.get(language, {})
        title = f"untitled{config.get('ext', '')}"
        
        idx = self.tab_widget.addTab(tab, title)
        self.tab_widget.setCurrentIndex(idx)
        self.statusBar().showMessage(f"New {language} file created")
        
    def open_file(self, filepath=None):
        if not filepath:
            filepath, _ = QFileDialog.getOpenFileName(
                self,
                "Open File",
                "",
                "All Files (*);;Python (*.py);;Java (*.java);;C (*.c);;C++ (*.cpp);;JavaScript (*.js)"
            )
            
        if not filepath:
            return
            
        filepath = Path(filepath)
        
        # Detect language from extension
        ext = filepath.suffix.lower()
        language = "Python"  # default
        for lang, config in LANG_CONFIG.items():
            if config.get("ext") == ext:
                language = lang
                break
                
        tab = EditorTab(language=language, filepath=filepath)
        idx = self.tab_widget.addTab(tab, filepath.name)
        self.tab_widget.setCurrentIndex(idx)
        self.statusBar().showMessage(f"Opened {filepath}")
        
    def save_file(self):
        tab = self.get_current_tab()
        if not tab:
            return
            
        if not tab.filepath:
            return self.save_file_as()
            
        if tab.save():
            self.tab_widget.setTabText(
                self.tab_widget.currentIndex(),
                tab.filepath.name
            )
            self.statusBar().showMessage(f"Saved {tab.filepath}")
            self.console.append(f"Saved: {tab.filepath}\n")
            
    def save_file_as(self):
        tab = self.get_current_tab()
        if not tab:
            return
            
        config = LANG_CONFIG.get(tab.language, {})
        ext = config.get("ext", "")
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            f"untitled{ext}",
            f"All Files (*);;{tab.language} (*{ext})"
        )
        
        if filepath and tab.save(filepath):
            self.tab_widget.setTabText(
                self.tab_widget.currentIndex(),
                tab.filepath.name
            )
            self.statusBar().showMessage(f"Saved as {tab.filepath}")
            self.console.append(f"Saved as: {tab.filepath}\n")
            
    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            QMessageBox.information(self, "Close Tab", "Cannot close the last tab")
            
    def get_current_tab(self):
        widget = self.tab_widget.currentWidget()
        return widget if isinstance(widget, EditorTab) else None
        
    def on_language_changed(self, language):
        tab = self.get_current_tab()
        if tab and not tab.filepath:
            tab.language = language
            tab.editor.set_language(language)
            tab.load_content()
            
    def undo(self):
        tab = self.get_current_tab()
        if tab:
            tab.editor.undo()
            
    def redo(self):
        tab = self.get_current_tab()
        if tab:
            tab.editor.redo()
            
    def find_text(self):
        tab = self.get_current_tab()
        if not tab:
            return
            
        text, ok = QInputDialog.getText(self, "Find", "Text to find:")
        if ok and text:
            if not tab.editor.find(text):
                QMessageBox.information(self, "Find", "Text not found")
                
    def run_code(self):
        tab = self.get_current_tab()
        if not tab:
            return
            
        # Save file first
        if not tab.filepath:
            reply = QMessageBox.question(
                self,
                "Save File",
                "File must be saved before running. Save now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.save_file_as()
            else:
                return
                
        if not tab.filepath:
            return
            
        self.console.clear()
        self.console.append(f"Running {tab.filepath.name} ({tab.language})...\n")
        self.statusBar().showMessage("Running...")
        
        # Get runner configuration
        config = LANG_CONFIG.get(tab.language, {})
        runner = config.get("runner")
        
        if runner == "browser":
            webbrowser.open(str(tab.filepath.resolve().as_uri()))
            self.console.append(f"Opened {tab.filepath.name} in browser\n")
            self.statusBar().showMessage("Ready")
            return
            
        # Compile/run based on language
        command = self.get_run_command(tab.filepath, tab.language, runner)
        
        if not command:
            self.console.append(f"Cannot run {tab.language} files (compiler/interpreter not found)\n")
            self.statusBar().showMessage("Ready")
            return
            
        # Run in thread
        self.runner_thread = RunnerThread(command, str(tab.filepath.parent))
        self.runner_thread.output.connect(self.console.append)
        self.runner_thread.finished.connect(lambda: self.statusBar().showMessage("Ready"))
        self.runner_thread.start()
        
    def get_run_command(self, filepath, language, runner):
        """Generate command to run the code"""
        
        if callable(runner):
            return runner(filepath)
            
        # Special cases that need compilation
        if runner == "java":
            # Compile Java
            compile_cmd = ["javac", str(filepath)]
            try:
                result = subprocess.run(
                    compile_cmd, 
                    check=True, 
                    cwd=str(filepath.parent),
                    capture_output=True,
                    text=True
                )
                if result.stderr:
                    self.console.append(result.stderr)
            except subprocess.CalledProcessError as e:
                self.console.append(f"Compilation failed:\n{e.stderr}\n")
                return None
            except FileNotFoundError:
                self.console.append("Java compiler (javac) not found in PATH\n")
                return None
                
            # Run compiled class
            classname = filepath.stem
            return ["java", classname]
            
        elif runner == "c":
            # Compile C
            exe = filepath.with_suffix(".out")
            compile_cmd = ["gcc", str(filepath), "-o", str(exe)]
            try:
                result = subprocess.run(
                    compile_cmd,
                    check=True,
                    cwd=str(filepath.parent),
                    capture_output=True,
                    text=True
                )
                if result.stderr:
                    self.console.append(result.stderr)
            except subprocess.CalledProcessError as e:
                self.console.append(f"Compilation failed:\n{e.stderr}\n")
                return None
            except FileNotFoundError:
                self.console.append("C compiler (gcc) not found in PATH\n")
                return None
            return [str(exe)]
            
        elif runner == "cpp":
            # Compile C++
            exe = filepath.with_suffix(".out")
            compile_cmd = ["g++", str(filepath), "-o", str(exe)]
            try:
                result = subprocess.run(
                    compile_cmd,
                    check=True,
                    cwd=str(filepath.parent),
                    capture_output=True,
                    text=True
                )
                if result.stderr:
                    self.console.append(result.stderr)
            except subprocess.CalledProcessError as e:
                self.console.append(f"Compilation failed:\n{e.stderr}\n")
                return None
            except FileNotFoundError:
                self.console.append("C++ compiler (g++) not found in PATH\n")
                return None
            return [str(exe)]
            
        elif runner == "rust":
            # Compile Rust
            exe = filepath.with_suffix(".out")
            compile_cmd = ["rustc", str(filepath), "-o", str(exe)]
            try:
                result = subprocess.run(
                    compile_cmd,
                    check=True,
                    cwd=str(filepath.parent),
                    capture_output=True,
                    text=True
                )
                if result.stderr:
                    self.console.append(result.stderr)
            except subprocess.CalledProcessError as e:
                self.console.append(f"Compilation failed:\n{e.stderr}\n")
                return None
            except FileNotFoundError:
                self.console.append("Rust compiler (rustc) not found in PATH\n")
                return None
            return [str(exe)]
            
        elif runner == "typescript":
            # Compile TypeScript
            js_file = filepath.with_suffix(".js")
            compile_cmd = ["tsc", str(filepath)]
            try:
                result = subprocess.run(
                    compile_cmd,
                    check=True,
                    cwd=str(filepath.parent),
                    capture_output=True,
                    text=True
                )
                if result.stderr:
                    self.console.append(result.stderr)
            except subprocess.CalledProcessError as e:
                self.console.append(f"Compilation failed:\n{e.stderr}\n")
                return None
            except FileNotFoundError:
                self.console.append("TypeScript compiler (tsc) not found in PATH\n")
                return None
                
            # Run with Node
            try:
                subprocess.run(["node", "--version"], check=True, capture_output=True)
                return ["node", str(js_file)]
            except (subprocess.CalledProcessError, FileNotFoundError):
                webbrowser.open(str(js_file.resolve().as_uri()))
                self.console.append("Node not found - opened compiled JS in browser\n")
                return None
                
        elif runner == "kotlin":
            # Compile Kotlin
            jar_file = filepath.parent / "output.jar"
            compile_cmd = ["kotlinc", str(filepath), "-include-runtime", "-d", str(jar_file)]
            try:
                result = subprocess.run(
                    compile_cmd,
                    check=True,
                    cwd=str(filepath.parent),
                    capture_output=True,
                    text=True
                )
                if result.stderr:
                    self.console.append(result.stderr)
            except subprocess.CalledProcessError as e:
                self.console.append(f"Compilation failed:\n{e.stderr}\n")
                return None
            except FileNotFoundError:
                self.console.append("Kotlin compiler (kotlinc) not found in PATH\n")
                return None
            return ["java", "-jar", str(jar_file)]
            
        elif runner == "csharp":
            # Run with dotnet
            try:
                subprocess.run(["dotnet", "--version"], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.console.append(".NET SDK not found in PATH\n")
                return None
                
            # Check if project exists
            proj_dir = filepath.parent
            if not (proj_dir / "project.csproj").exists():
                # Create new console project
                subprocess.run(
                    ["dotnet", "new", "console", "-o", "."],
                    cwd=str(proj_dir),
                    capture_output=True
                )
            return ["dotnet", "run"]
            
        elif runner == "nix":
            try:
                subprocess.run(["nix", "--version"], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.console.append("Nix not found in PATH\n")
                return None
                
            if filepath.name == "flake.nix":
                return ["nix", "develop", "."]
            else:
                return ["nix-shell", str(filepath)]
                
        return None
        
    def open_workspace(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Workspace")
        if not folder:
            return
            
        self.workspace_path = Path(folder)
        
        # Show tree widget
        if not self.tree_widget.isVisible():
            self.main_splitter.insertWidget(0, self.tree_widget)
            self.tree_widget.show()
            self.main_splitter.setSizes([250, 950])
            
        # Populate tree
        self.tree_widget.clear()
        self.populate_tree(self.workspace_path, None)
        self.statusBar().showMessage(f"Opened workspace: {self.workspace_path}")
        
    def populate_tree(self, path, parent, max_depth=3, current_depth=0):
        """Recursively populate workspace tree"""
        if current_depth > max_depth:
            return
            
        try:
            entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except PermissionError:
            return
            
        for entry in entries:
            # Skip hidden files and common ignore patterns
            if entry.name.startswith('.'):
                continue
            if entry.name in ('__pycache__', 'node_modules', 'target', 'build', 'dist'):
                continue
                
            display_name = entry.name + ("/" if entry.is_dir() else "")
            
            if parent is None:
                item = QTreeWidgetItem(self.tree_widget, [display_name])
            else:
                item = QTreeWidgetItem(parent, [display_name])
                
            item.setData(0, Qt.ItemDataRole.UserRole, str(entry))
            
            if entry.is_dir():
                self.populate_tree(entry, item, max_depth, current_depth + 1)
                
    def on_tree_double_click(self, item, column):
        filepath = item.data(0, Qt.ItemDataRole.UserRole)
        if filepath:
            path = Path(filepath)
            if path.is_file():
                self.open_file(str(path))
                
    def close_workspace(self):
        if self.workspace_path:
            self.tree_widget.hide()
            self.workspace_path = None
            self.statusBar().showMessage("Workspace closed")
            
    def show_about(self):
        QMessageBox.about(
            self,
            "About Mocha Codespace",
            """<h2>Mocha Codespace 0.2</h2>
            <p>A modern, beginner-friendly IDE built with PyQt6/PySide6</p>
            <p><b>Features:</b></p>
            <ul>
                <li>✨ Syntax highlighting for all supported languages</li>
                <li>🔤 Smart autocompletion (Ctrl+Space)</li>
                <li>📝 Auto-indentation</li>
                <li>🎨 Beautiful Mocha color theme</li>
            </ul>
            <p><b>Supported Languages:</b></p>
            <ul>
                <li>NVIDIA PTX</li>
                <li>Python</li>
                <li>Java</li>
                <li>C / C++</li>
                <li>JavaScript / TypeScript</li>
                <li>Rust</li>
                <li>Go</li>
                <li>C#</li>
                <li>Ruby</li>
                <li>Kotlin</li>
                <li>HTML / CSS</li>
                <li>Lua</li>
                <li>Nix</li>
            </ul>
            <p>Created with ♥ by Camila Rose</p>
            <p>PyQt6/PySide6 Version</p>
            """
        )


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = MochaCodespace()
    window.show()
    
    sys.exit(app.exec() if USING_PYQT else app.exec())


if __name__ == "__main__":
    main()
