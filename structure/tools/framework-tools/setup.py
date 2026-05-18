#!/usr/bin/env python3
"""

"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    """Read README.md for long description"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()

# Read requirements from requirements.txt
def read_requirements():
    """Read requirements.txt and return list of dependencies"""
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            # Filter out comments and empty lines
            return [
                line.strip() 
                for line in f 
                if line.strip() and not line.strip().startswith('#')
            ]
    return []

setup(
    version="3.0.0",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    
    # Package discovery - find all packages in tools/ and shared/
    packages=find_packages(include=[
        'tools.*',
        'shared.*',
        'config',
        'database_schemas',  # Legacy location - will be deprecated
    ]),
    
    # Include package data
    package_data={
        'tools.legacy_analyzer': ['*.md', '*.txt', '*.yaml'],
        'tools.migration_planner': ['*.md', '*.txt', '*.yaml'],
        'tools.database_analyzer': ['*.md', '*.txt', '*.yaml', '*.json'],
        'shared': ['*.yaml', '*.json'],
        'config': ['*.yaml', '*.json'],
    },
    
    # Include additional files
    include_package_data=True,
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Optional dependencies for development
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'pytest-mock>=3.11.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.5.0',
        ],
        'docs': [
            'sphinx>=4.0.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
        'analytics': [
            'pandas>=1.5.0',
            'numpy>=1.21.0',
            'matplotlib>=3.5.0',
            'seaborn>=0.11.0',
        ],
        'dashboard': [
            'flask>=3.0.0',
            'flask-session>=0.5.0',
            'python-magic>=0.4.27',
            'gunicorn>=21.0.0',
        ]
    },
    
    # Console scripts for tool access
    entry_points={
        'console_scripts': [
            
            # Legacy Analyzer tool
            'legacy-analyzer=tools.legacy_analyzer.__main__:main',
            
            
            
            # Migration Planner tool
            'migration-planner=tools.migration_planner.__main__:main',
            
            # Database Analyzer tool
            'database-analyzer=tools.database_analyzer.__main__:main',
            
        ],
    },
    
    # Classifiers for PyPI
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Database :: Database Engines/Servers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    
    # Keywords for discovery
    keywords=[
        "legacy", "cobol", "jcl", "analysis", "parsing"
    ],
    
    # Project URLs
    project_urls={
    },
    
    # Zip safe
    zip_safe=False,
)