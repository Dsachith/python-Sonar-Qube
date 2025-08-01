import re
from collections import defaultdict
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class CodeIssue:
    line_number: int
    issue_type: str
    description: str
    code_snippet: str

@dataclass
class FileAnalysis:
    file_path: str
    issues: List[CodeIssue]
    metrics: Dict[str, float]

def analyze_flutter_project(file_paths: List[str]) -> Dict[str, FileAnalysis]:
    results = {}
    
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()
        
        issues = []
        
        # Detect code duplication (simplified example)
        issues.extend(_detect_duplicate_code(content, file_path))
        
        # Detect unused imports
        issues.extend(_detect_unused_imports(content))
        
        # Detect long methods
        issues.extend(_detect_long_methods(content))
        
        # Detect dead code
        issues.extend(_detect_dead_code(content))
        
        # Detect potential bugs
        issues.extend(_detect_potential_bugs(content))
        
        # Calculate metrics
        metrics = _calculate_metrics(content, issues)
        
        results[file_path] = FileAnalysis(
            file_path=file_path,
            issues=issues,
            metrics=metrics
        )
    
    return results

def _detect_duplicate_code(content: List[str], file_path: str) -> List[CodeIssue]:
    # This is a simplified version - a real implementation would use more sophisticated techniques
    issues = []
    code_blocks = defaultdict(list)
    
    for i, line in enumerate(content):
        stripped = line.strip()
        if stripped and not stripped.startswith(('//', '/*', '*')):
            code_blocks[stripped].append(i + 1)  # +1 for 1-based line numbers
    
    for code, lines in code_blocks.items():
        if len(lines) > 1 and len(code) > 20:  # Arbitrary threshold
            for line in lines:
                issues.append(CodeIssue(
                    line_number=line,
                    issue_type="Duplication",
                    description=f"Duplicate code found (appears {len(lines)} times)",
                    code_snippet=code
                ))
    
    return issues

def _detect_unused_imports(content: List[str]) -> List[CodeIssue]:
    issues = []
    imports = []
    import_pattern = re.compile(r'^import\s+[\'"](.+?)[\'"]')
    
    # First pass: collect all imports
    for i, line in enumerate(content):
        match = import_pattern.match(line.strip())
        if match:
            imports.append((i + 1, match.group(1)))
    
    # Second pass: check if imports are used (simplified check)
    for line_num, import_stmt in imports:
        import_name = import_stmt.split('/')[-1].split('.')[0]
        used = False
        
        for line in content:
            if f"{import_name}." in line or f" {import_name}(" in line:
                used = True
                break
        
        if not used:
            issues.append(CodeIssue(
                line_number=line_num,
                issue_type="Unused Import",
                description=f"Unused import: {import_stmt}",
                code_snippet=content[line_num - 1].strip()
            ))
    
    return issues

def _detect_long_methods(content: List[str]) -> List[CodeIssue]:
    issues = []
    method_start = None
    brace_count = 0
    method_pattern = re.compile(r'^\s*(?:@[a-zA-Z]+\s+)*[a-zA-Z]+\s+[a-zA-Z]+\s*\([^)]*\)\s*[a-zA-Z]*\s*\{?')
    
    for i, line in enumerate(content):
        line_text = line.strip()
        
        # Detect method start
        if method_start is None and method_pattern.match(line_text):
            method_start = i + 1
            brace_count = 0
        
        # Count braces
        if method_start is not None:
            brace_count += line_text.count('{')
            brace_count -= line_text.count('}')
            
            # Method ended
            if brace_count <= 0 and method_start is not None:
                method_length = i + 1 - method_start
                if method_length > 20:  # Threshold for long method
                    issues.append(CodeIssue(
                        line_number=method_start,
                        issue_type="Long Method",
                        description=f"Method is too long ({method_length} lines)",
                        code_snippet=content[method_start - 1].strip()
                    ))
                method_start = None
    
    return issues

def _detect_dead_code(content: List[str]) -> List[CodeIssue]:
    issues = []
    private_method_pattern = re.compile(r'^\s*[_a-zA-Z]+\s+_[a-zA-Z]+\s*\([^)]*\)\s*\{?')
    
    for i, line in enumerate(content):
        line_text = line.strip()
        
        # Detect private methods
        if private_method_pattern.match(line_text):
            method_name = line_text.split('(')[0].split()[-1]
            
            # Check if method is called (simplified check)
            called = False
            for other_line in content:
                if f"{method_name}(" in other_line and other_line != line:
                    called = True
                    break
            
            if not called:
                issues.append(CodeIssue(
                    line_number=i + 1,
                    issue_type="Dead Code",
                    description=f"Private method '{method_name}' is never called",
                    code_snippet=line_text
                ))
    
    return issues

def _detect_potential_bugs(content: List[str]) -> List[CodeIssue]:
    issues = []
    null_check_pattern = re.compile(r'!\s*=\s*null')
    empty_catch_pattern = re.compile(r'catch\s*\([^)]*\)\s*\{\s*\}')
    
    for i, line in enumerate(content):
        line_text = line.strip()
        
        # Detect null checks without ?
        if null_check_pattern.search(line_text) and '?' not in line_text:
            issues.append(CodeIssue(
                line_number=i + 1,
                issue_type="Potential Bug",
                description="Null check without null-aware operator (?.)",
                code_snippet=line_text
            ))
        
        # Detect empty catch blocks
        if empty_catch_pattern.search(line_text):
            issues.append(CodeIssue(
                line_number=i + 1,
                issue_type="Potential Bug",
                description="Empty catch block - exceptions should be handled properly",
                code_snippet=line_text
            ))
    
    return issues

def _calculate_metrics(content: List[str], issues: List[CodeIssue]) -> Dict[str, float]:
    total_lines = len(content)
    code_lines = sum(1 for line in content if line.strip() and not line.strip().startswith(('//', '/*', '*')))
    comment_lines = sum(1 for line in content if line.strip().startswith(('//', '/*', '*')))
    
    issue_counts = defaultdict(int)
    for issue in issues:
        issue_counts[issue.issue_type] += 1
    
    metrics = {
        'total_lines': total_lines,
        'code_lines': code_lines,
        'comment_lines': comment_lines,
        'comment_density': comment_lines / code_lines * 100 if code_lines else 0,
    }
    
    # Add issue counts to metrics
    for issue_type, count in issue_counts.items():
        metrics[f'{issue_type.lower().replace(" ", "_")}_count'] = count
    
    return metrics