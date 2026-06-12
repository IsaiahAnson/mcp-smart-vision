"""Data analysis tools for MCP server."""

import csv
import json
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd


def analyze_csv(path: str, preview_rows: int = 10) -> Dict[str, Any]:
    """Load and analyze CSV files."""
    try:
        path_obj = Path(path).resolve()
        if not path_obj.exists():
            return {"success": False, "error": f"File does not exist: {path}"}
        
        df = pd.read_csv(str(path_obj))
        
        # Basic statistics
        stats = {}
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                stats[col] = {
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "std": float(df[col].std())
                }
        
        return {
            "success": True,
            "path": str(path_obj),
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "statistics": stats,
            "preview": df.head(preview_rows).to_dict(orient='records'),
            "missing_values": df.isnull().sum().to_dict()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def analyze_excel(path: str, sheet_name: str = None, preview_rows: int = 10) -> Dict[str, Any]:
    """Load and analyze Excel files."""
    try:
        path_obj = Path(path).resolve()
        if not path_obj.exists():
            return {"success": False, "error": f"File does not exist: {path}"}
        
        # Get all sheet names
        excel_file = pd.ExcelFile(str(path_obj))
        sheet_names = excel_file.sheet_names
        
        # Load specific sheet or first sheet
        if sheet_name:
            if sheet_name not in sheet_names:
                return {"success": False, "error": f"Sheet '{sheet_name}' not found"}
            df = pd.read_excel(str(path_obj), sheet_name=sheet_name)
        else:
            df = pd.read_excel(str(path_obj), sheet_name=0)
            sheet_name = sheet_names[0]
        
        # Basic statistics
        stats = {}
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                stats[col] = {
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "std": float(df[col].std())
                }
        
        return {
            "success": True,
            "path": str(path_obj),
            "sheets": sheet_names,
            "current_sheet": sheet_name,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "statistics": stats,
            "preview": df.head(preview_rows).to_dict(orient='records'),
            "missing_values": df.isnull().sum().to_dict()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def query_data(path: str, query: str, sheet_name: str = None) -> Dict[str, Any]:
    """Execute data queries on CSV/Excel files using pandas query syntax."""
    try:
        path_obj = Path(path).resolve()
        if not path_obj.exists():
            return {"success": False, "error": f"File does not exist: {path}"}
        
        # Load data
        if path_obj.suffix.lower() == '.csv':
            df = pd.read_csv(str(path_obj))
        elif path_obj.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(str(path_obj), sheet_name=sheet_name or 0)
        else:
            return {"success": False, "error": "Unsupported file format"}
        
        # Execute query
        result_df = df.query(query)
        
        return {
            "success": True,
            "path": str(path_obj),
            "query": query,
            "result_rows": len(result_df),
            "total_rows": len(df),
            "results": result_df.to_dict(orient='records')
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def merge_data(files: List[str], output_path: str, merge_type: str = "concat") -> Dict[str, Any]:
    """Merge multiple data files."""
    try:
        dataframes = []
        
        for file_path in files:
            path_obj = Path(file_path).resolve()
            if not path_obj.exists():
                return {"success": False, "error": f"File does not exist: {file_path}"}
            
            if path_obj.suffix.lower() == '.csv':
                df = pd.read_csv(str(path_obj))
            elif path_obj.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(str(path_obj))
            else:
                return {"success": False, "error": f"Unsupported file format: {file_path}"}
            
            dataframes.append(df)
        
        # Merge based on type
        if merge_type == "concat":
            merged_df = pd.concat(dataframes, ignore_index=True)
        else:
            return {"success": False, "error": f"Unsupported merge type: {merge_type}"}
        
        # Save output
        output_obj = Path(output_path).resolve()
        if output_obj.suffix.lower() == '.csv':
            merged_df.to_csv(str(output_obj), index=False)
        elif output_obj.suffix.lower() in ['.xlsx', '.xls']:
            merged_df.to_excel(str(output_obj), index=False)
        else:
            return {"success": False, "error": "Unsupported output format"}
        
        return {
            "success": True,
            "input_files": files,
            "output_path": str(output_obj),
            "total_rows": len(merged_df),
            "columns": len(merged_df.columns)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_data(input_path: str, output_path: str, sheet_name: str = None, 
                columns: List[str] = None, filter_query: str = None) -> Dict[str, Any]:
    """Export data to various formats with optional filtering."""
    try:
        input_obj = Path(input_path).resolve()
        if not input_obj.exists():
            return {"success": False, "error": f"File does not exist: {input_path}"}
        
        # Load data
        if input_obj.suffix.lower() == '.csv':
            df = pd.read_csv(str(input_obj))
        elif input_obj.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(str(input_obj), sheet_name=sheet_name or 0)
        else:
            return {"success": False, "error": "Unsupported input format"}
        
        # Apply filter if specified
        if filter_query:
            df = df.query(filter_query)
        
        # Select columns if specified
        if columns:
            df = df[columns]
        
        # Export
        output_obj = Path(output_path).resolve()
        output_obj.parent.mkdir(parents=True, exist_ok=True)
        
        if output_obj.suffix.lower() == '.csv':
            df.to_csv(str(output_obj), index=False)
        elif output_obj.suffix.lower() in ['.xlsx', '.xls']:
            df.to_excel(str(output_obj), index=False)
        elif output_obj.suffix.lower() == '.json':
            df.to_json(str(output_obj), orient='records', indent=2)
        else:
            return {"success": False, "error": "Unsupported output format"}
        
        return {
            "success": True,
            "input_path": str(input_obj),
            "output_path": str(output_obj),
            "rows_exported": len(df),
            "columns_exported": len(df.columns)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# Tool definitions for MCP server
DATA_TOOLS = [
    {
        "name": "analyze_csv",
        "description": "Analyze CSV file and get statistics",
        "function": analyze_csv,
        "parameters": {
            "path": {"type": "string", "required": True},
            "preview_rows": {"type": "integer", "required": False, "default": 10}
        }
    },
    {
        "name": "analyze_excel",
        "description": "Analyze Excel file and get statistics",
        "function": analyze_excel,
        "parameters": {
            "path": {"type": "string", "required": True},
            "sheet_name": {"type": "string", "required": False},
            "preview_rows": {"type": "integer", "required": False, "default": 10}
        }
    },
    {
        "name": "query_data",
        "description": "Query data file using pandas syntax",
        "function": query_data,
        "parameters": {
            "path": {"type": "string", "required": True},
            "query": {"type": "string", "required": True},
            "sheet_name": {"type": "string", "required": False}
        }
    },
    {
        "name": "merge_data",
        "description": "Merge multiple data files",
        "function": merge_data,
        "parameters": {
            "files": {"type": "array", "required": True},
            "output_path": {"type": "string", "required": True},
            "merge_type": {"type": "string", "required": False, "default": "concat"}
        }
    },
    {
        "name": "export_data",
        "description": "Export data to different format",
        "function": export_data,
        "parameters": {
            "input_path": {"type": "string", "required": True},
            "output_path": {"type": "string", "required": True},
            "sheet_name": {"type": "string", "required": False},
            "columns": {"type": "array", "required": False},
            "filter_query": {"type": "string", "required": False}
        }
    }
]
