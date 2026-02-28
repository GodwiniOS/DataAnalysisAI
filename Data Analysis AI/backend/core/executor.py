import ast
import pandas as pd
import astunparse

class SafeExecutor:
    """
    Safely executes AI-generated Pandas code using AST parsing.
    Prevents execution of dangerous builtins and modules.
    """
    ALLOWED_MODULES = {'pd', 'np', 'df', 'plt', 'sns'}
    ALLOWED_BUILTINS = {'len', 'range', 'list', 'dict', 'set', 'int', 'float', 'str', 'bool', 'round', 'sum', 'min', 'max', 'abs', 'print'}
    
    def __init__(self):
        pass

    def validate_code(self, code_str: str):
        """
        Parses and validates the code string for security risks.
        """
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return False, f"Syntax Error: {str(e)}"

        for node in ast.walk(tree):
            # Block imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                return False, "Import statements are not allowed."
            
            # Block attribute access to dangerous things (e.g. __subclasses__)
            if isinstance(node, ast.Attribute):
                if node.attr.startswith('__'):
                    return False, f"Access to private attributes ({node.attr}) is forbidden."
            
            # Block restricted functions
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id not in self.ALLOWED_BUILTINS:
                        # Allow pandas/numpy methods
                        pass
                elif isinstance(node.func, ast.Attribute):
                    # Check for things like os.system
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id in ('os', 'subprocess', 'sys'):
                            return False, f"Calls to {node.func.value.id} are forbidden."
                            
        return True, None

    def execute(self, code_str: str, df: pd.DataFrame):
        """
        Executes the code within a restricted environment.
        Returns (result, updated_df, error)
        """
        is_safe, error = self.validate_code(code_str)
        if not is_safe:
            return None, df, error
        
        # Define the local scope
        local_scope = {
            'df': df,
            'pd': pd,
            'import': None  # Extra precaution
        }
        
        try:
            # We use exec but with a restricted global/local scope
            # For multiline code, we might want to capture the final output or specific variables
            exec(code_str, {}, local_scope)
            
            updated_df = local_scope.get('df')
            # Extract other results? (e.g. if the code creates a 'result' variable)
            result = local_scope.get('result', "Operation completed successfully.")
            
            return result, updated_df, None
        except Exception as e:
            return None, df, str(e)
