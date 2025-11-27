# Boost Documentation Conversion to AsciiDoc

## Overview

The project consists of two main scripts:

1. **`analyze_boost_docs.py`** - Analyzes Boost documentation files and generates statistics
2. **`convert_to_adoc.py`** - Converts all documentation files to AsciiDoc format

## Requirements

### Essential Tools

- **Python 3.10+**
- **Pandoc** - For converting most formats to AsciiDoc
- **Quickbook** - Required for converting Quickbook (.qbk) files

### Quick Installation

```bash
# Install Pandoc (required)
# Windows: Download from https://pandoc.org/installing.html
# Or: choco install pandoc

# Install Quickbook (required for .qbk files)
# Build from Boost sources
```

## Usage

### Step 1: Analyze Documentation

First, run the analysis script to generate statistics and file lists:

```bash
python analyze_boost_docs.py
```

This will generate:

- `boost_doc_statistics_main.json` - Statistics organized by file type with totals and top libraries
- `boost_doc_statistics_total.json` - All libraries with main types statistics
- `boost_doc_files_to_convert.json` - List of files to convert (used by conversion script)

## Statistics Files

### `boost_doc_statistics_main.json`

Organized by file type with totals and top libraries:

```json
{
  "html": {
    "_total": {
      "file count": 14099,
      "line count": 4479024
    },
    "top libraries": [
      {"beast": {"file count": 1508, "line count": 177412}},
      ...
    ]
  },
  ...
}
```

### `boost_doc_statistics_total.json`

All libraries with main types only:

```json
{
  "algorithm": {
    "html": {"file count": 160, "line count": 17317},
    "qbk": {"file count": 22, "line count": 2200},
    ...
  },
  ...
}
```

### Step 2: Convert to AsciiDoc

Run the conversion script to convert all files to AsciiDoc:

```bash
python convert_to_adoc.py
```

The script will:

- Use the file list from `analyze_boost_docs.py`
- Convert all main documentation types to AsciiDoc
- Skip fragment files (they're included in parent documents)
- Output files to `converted_docs/adoc/`

## Output Structure

```
converted_docs/
  └── adoc/
      ├── qbk/          # Converted from Quickbook
      ├── rst/          # Converted from reStructuredText
      ├── md/           # Converted from Markdown
      ├── adoc/         # Copied AsciiDoc files
      ├── xml/          # Converted from DocBook XML
      ├── html/         # Converted from HTML
      └── mml/          # Converted from MathML
```

Each subdirectory maintains the original library structure:

```
adoc/qbk/algorithm/doc/algorithm.adoc
adoc/html/algorithm/doc/algorithm.adoc
```

## Main Documentation Types

The following file types are considered "main types" and can be converted:

- **qbk** - Quickbook (Boost documentation format)
- **rst** - reStructuredText
- **md** - Markdown
- **adoc** - AsciiDoc (copied as-is)
- **xml** - DocBook XML
- **html** - HTML
- **mml** - MathML

## Fragment Files

Quickbook fragment files (files without `doc_info` blocks) are automatically skipped because:

1. They are included in parent documents via `[include filename.qbk]`
2. Their content is already converted as part of the parent document
3. Converting them standalone would cause errors

The script detects fragment files by checking if they start with `[section` instead of a doc_info block (`[library`, `[article`, etc.).

## Troubleshooting

### "Pandoc not found"

- Install Pandoc from https://pandoc.org/installing.html
- Restart your terminal/IDE after installation
- Verify with: `pandoc --version`

### "Quickbook not found"

- Quickbook is required for converting .qbk files
- Build from Boost sources
- The conversion will fail if Quickbook is not available

### "File list not found"

- Run `analyze_boost_docs.py` first to generate the file list
- The conversion script will fall back to directory scanning if the file list is missing

### Fragment file errors

- Fragment files are automatically skipped
- This is expected behavior - they're included in parent documents
- No action needed

## Project Structure

```
InvestigateBoost/
├── analyze_boost_docs.py          # Analysis script
├── convert_to_adoc.py              # Conversion script
├── README.md                       # This file
├── boost_1_89_0/                   # Boost source directory
│   └── libs/                       # Boost libraries
├── converted_docs/                 # Output directory
│   └── adoc/                       # Converted AsciiDoc files
└── boost_doc_statistics_*.json     # Statistics files
```

## License

This project is for analyzing and converting Boost documentation. Boost libraries are distributed under the Boost Software License.
