#!/usr/bin/env python3
"""
API Contract Validation Script for CI/CD Pipeline

This script validates that frontend API calls match backend endpoints
and fails the build if mismatches are detected.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


class APIContractValidator:
    """Validates API contracts between frontend and backend."""

    def __init__(self):
        self.frontend_api_calls: Set[Tuple[str, str]] = set()  # (method, endpoint)
        self.backend_endpoints: Set[Tuple[str, str]] = set()  # (method, endpoint)
        self.mismatches: List[Dict] = []
        self.warnings: List[str] = []

    def extract_frontend_api_calls(self, frontend_dir: Path) -> None:
        """Extract API calls from frontend TypeScript/JavaScript files."""
        api_service_file = frontend_dir / "src" / "services" / "api.ts"
        
        if not api_service_file.exists():
            self.warnings.append(f"Frontend API service file not found: {api_service_file}")
            return

        content = api_service_file.read_text()
        
        # Extract API calls using regex patterns
        patterns = [
            # GET requests: api.get('/api/v1/...')
            (r"api\.get\(['\"]([^'\"]+)['\"]", "GET"),
            # POST requests: api.post('/api/v1/...')
            (r"api\.post\(['\"]([^'\"]+)['\"]", "POST"),
            # PUT requests: api.put('/api/v1/...')
            (r"api\.put\(['\"]([^'\"]+)['\"]", "PUT"),
            # DELETE requests: api.delete('/api/v1/...')
            (r"api\.delete\(['\"]([^'\"]+)['\"]", "DELETE"),
        ]
        
        for pattern, method in patterns:
            matches = re.findall(pattern, content)
            for endpoint in matches:
                if endpoint.startswith('/api/v1/'):
                    self.frontend_api_calls.add((method, endpoint))

    def extract_backend_endpoints(self, backend_dir: Path) -> None:
        """Extract API endpoints from backend Python files."""
        api_dir = backend_dir / "app" / "api"
        
        if not api_dir.exists():
            self.warnings.append(f"Backend API directory not found: {api_dir}")
            return

        # Find all Python API files
        api_files = list(api_dir.glob("*.py"))
        api_files = [f for f in api_files if f.name != "__init__.py"]

        for api_file in api_files:
            self._extract_endpoints_from_file(api_file)

    def _extract_endpoints_from_file(self, file_path: Path) -> None:
        """Extract endpoints from a single Python API file."""
        content = file_path.read_text()
        
        # Extract router decorators
        patterns = [
            (r"@router\.get\(['\"]([^'\"]*)['\"]", "GET"),
            (r"@router\.post\(['\"]([^'\"]*)['\"]", "POST"),
            (r"@router\.put\(['\"]([^'\"]*)['\"]", "PUT"),
            (r"@router\.delete\(['\"]([^'\"]*)['\"]", "DELETE"),
        ]
        
        # Determine the service prefix from filename
        service_name = file_path.stem
        if service_name in ["auth", "payment", "chat", "research", "user"]:
            prefix = f"/api/v1/{service_name}"
        else:
            prefix = "/api/v1"
        
        for pattern, method in patterns:
            matches = re.findall(pattern, content)
            for endpoint in matches:
                # Construct full endpoint path
                if endpoint.startswith("/"):
                    full_endpoint = f"{prefix}{endpoint}"
                else:
                    full_endpoint = f"{prefix}/{endpoint}"
                
                # Add both with and without trailing slash for root endpoints
                self.backend_endpoints.add((method, full_endpoint))
                if endpoint == "/" or endpoint == "":
                    # Also add without trailing slash
                    self.backend_endpoints.add((method, prefix))

    def validate_contracts(self) -> bool:
        """Validate that frontend calls match backend endpoints."""
        print("🔍 Validating API contracts...")
        print(f"Found {len(self.frontend_api_calls)} frontend API calls")
        print(f"Found {len(self.backend_endpoints)} backend endpoints")
        
        # Check for mismatches
        for method, endpoint in self.frontend_api_calls:
            if (method, endpoint) not in self.backend_endpoints:
                # Look for similar endpoints
                similar = self._find_similar_endpoints(method, endpoint)
                self.mismatches.append({
                    "type": "missing_backend",
                    "method": method,
                    "endpoint": endpoint,
                    "similar": similar
                })
        
        # Check for unused backend endpoints
        unused_endpoints = self.backend_endpoints - self.frontend_api_calls
        for method, endpoint in unused_endpoints:
            self.warnings.append(f"Unused backend endpoint: {method} {endpoint}")
        
        return len(self.mismatches) == 0

    def _find_similar_endpoints(self, method: str, endpoint: str) -> List[str]:
        """Find similar backend endpoints for suggestions."""
        similar = []
        endpoint_parts = endpoint.split('/')
        
        for backend_method, backend_endpoint in self.backend_endpoints:
            if backend_method == method:
                backend_parts = backend_endpoint.split('/')
                # Check if they share common parts
                common_parts = len(set(endpoint_parts) & set(backend_parts))
                if common_parts >= 3:  # At least api, v1, service
                    similar.append(backend_endpoint)
        
        return similar[:3]  # Return top 3 similar endpoints

    def print_results(self) -> None:
        """Print validation results."""
        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if self.mismatches:
            print("\n❌ API Contract Mismatches Found:")
            for mismatch in self.mismatches:
                print(f"  - {mismatch['method']} {mismatch['endpoint']}")
                if mismatch['similar']:
                    print(f"    Similar endpoints: {', '.join(mismatch['similar'])}")
                else:
                    print("    No similar endpoints found")
        else:
            print("\n✅ All API contracts are valid!")
        
        print(f"\nSummary:")
        print(f"  - Frontend API calls: {len(self.frontend_api_calls)}")
        print(f"  - Backend endpoints: {len(self.backend_endpoints)}")
        print(f"  - Mismatches: {len(self.mismatches)}")
        print(f"  - Warnings: {len(self.warnings)}")

    def generate_report(self, output_file: Path) -> None:
        """Generate a JSON report for CI/CD systems."""
        report = {
            "validation_passed": len(self.mismatches) == 0,
            "frontend_api_calls": list(self.frontend_api_calls),
            "backend_endpoints": list(self.backend_endpoints),
            "mismatches": self.mismatches,
            "warnings": self.warnings,
            "summary": {
                "frontend_calls_count": len(self.frontend_api_calls),
                "backend_endpoints_count": len(self.backend_endpoints),
                "mismatches_count": len(self.mismatches),
                "warnings_count": len(self.warnings)
            }
        }
        
        output_file.write_text(json.dumps(report, indent=2))
        print(f"📄 Report generated: {output_file}")


def main():
    """Main validation function."""
    print("🚀 Starting API Contract Validation")
    
    # Get project root directory
    project_root = Path(__file__).parent.parent
    frontend_dir = project_root / "frontend"
    backend_dir = project_root
    
    # Initialize validator
    validator = APIContractValidator()
    
    # Extract API calls and endpoints
    validator.extract_frontend_api_calls(frontend_dir)
    validator.extract_backend_endpoints(backend_dir)
    
    # Validate contracts
    is_valid = validator.validate_contracts()
    
    # Print results
    validator.print_results()
    
    # Generate report for CI/CD
    report_file = project_root / "api_contract_report.json"
    validator.generate_report(report_file)
    
    # Exit with appropriate code
    if is_valid:
        print("\n🎉 API contract validation passed!")
        sys.exit(0)
    else:
        print("\n💥 API contract validation failed!")
        print("Please fix the mismatches before deploying.")
        sys.exit(1)


if __name__ == "__main__":
    main()