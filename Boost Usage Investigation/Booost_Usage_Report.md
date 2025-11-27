# Boost Usage Analysis Report

Generated: 2025-11-26 21:58:43 UTC

## Overview

- **Total Repositories**: 37,693
- **Repositories Using System Boost**: 34,158
- **Repositories Using Boost**: 36,244
- **Total Boost Libraries**: 150
- **Total Boost Headers**: 15,172
- **Total Usage Records**: 3,002,447

**Note on Repository Counts**: "Repositories Using Boost" counts distinct repositories that depend on external/system Boost. This may be less than "Total Repositories" because repositories with vendored Boost bundle their own copy of Boost rather than using external Boost, so their Boost includes are filtered out during processing.

## Top Boost Libraries by Repository Count

| Library | Repository Count | Usage Count |
|---------|------------------|-------------|
| smart_ptr | 15,466 | 176,184 |
| thread | 14,681 | 146,810 |
| algorithm | 14,107 | 159,172 |
| filesystem | 13,312 | 158,729 |
| bind | 12,633 | 79,357 |
| lexical_cast | 12,127 | 50,775 |
| program_options | 11,469 | 45,196 |
| config | 10,984 | 111,196 |
| date_time | 10,610 | 52,899 |
| asio | 10,515 | 79,489 |
| function | 9,716 | 33,707 |
| test | 9,475 | 267,893 |
| foreach | 9,462 | 141,623 |
| variant | 8,138 | 26,048 |
| type_traits | 7,796 | 65,747 |
| tuple | 7,755 | 37,249 |
| iostreams | 7,481 | 39,899 |
| array | 7,437 | 16,170 |
| assign | 6,973 | 71,514 |
| interprocess | 6,791 | 38,211 |

## Top Boost Headers by Repository Count

| Header | Repository Count | Usage Count |
|--------|------------------|-------------|
| boost/shared_ptr.hpp | 12,922 | 94,079 |
| boost/bind.hpp | 12,518 | 75,975 |
| boost/algorithm/string.hpp | 12,482 | 52,930 |
| boost/filesystem.hpp | 12,437 | 90,094 |
| boost/lexical_cast.hpp | 12,123 | 50,582 |
| boost/thread.hpp | 10,986 | 49,006 |
| boost/asio.hpp | 9,891 | 27,879 |
| boost/function.hpp | 9,701 | 31,242 |
| boost/foreach.hpp | 9,460 | 141,563 |
| boost/thread/mutex.hpp | 9,404 | 28,677 |
| boost/test/unit_test.hpp | 8,962 | 231,622 |
| boost/version.hpp | 8,811 | 26,710 |
| boost/variant.hpp | 7,903 | 17,602 |
| boost/tuple/tuple.hpp | 7,703 | 26,313 |
| boost/date_time/posix_time/posix_time.hpp | 7,614 | 18,696 |
| boost/array.hpp | 7,437 | 16,170 |
| boost/filesystem/path.hpp | 7,314 | 19,900 |
| boost/config.hpp | 7,277 | 45,177 |
| boost/algorithm/string/predicate.hpp | 7,212 | 27,745 |
| boost/algorithm/string/replace.hpp | 7,099 | 23,281 |

## Boost Version Distribution (Top 10)

| Version | Usage Count |
|---------|-------------|
| 1.53.0 | 232 |
| 1.55 | 229 |
| 1.54 | 192 |
| 1.54.0 | 153 |
| 1.55.0 | 151 |
| 1.40.0 | 125 |
| 1.58.0 | 100 |
| 1.48.0 | 97 |
| 1.38 | 97 |
| 1.57.0 | 88 |

## Data Processing Procedure

This report is generated from BigQuery exports containing Boost-related files from GitHub repositories. The processing procedure consists of the following steps:

### 1. BigQuery Data Production

**The most important step**: Data is produced by executing `query.sql` in Google BigQuery against the `bigquery-public-data.github_repos` dataset. This query:

- Detects repositories containing Boost includes in C/C++ source files
- Identifies repositories with vendored Boost (containing `boost/` folder)
- Extracts Boost version information from multiple sources:
  - `boost/version.hpp` files (BOOST_VERSION macro)
  - CMake `find_package(Boost ...)` declarations
  - Conan `conanfile.txt` or `conanfile.py` references
  - vcpkg `vcpkg.json` manifest files
- Retrieves latest commit metadata for each repository
- Outputs results to CSV files (`bq-results-*`) exported to the data directory

The query produces CSV files with the following key fields:

- `repo_name`: GitHub repository identifier
- `path`: File path within the repository
- `file_content`: Full file content (for include extraction)
- `boost_version`: Detected Boost version (if found)
- `contains_vendored_boost`: Boolean indicating if repository has vendored Boost
- `last_commit_ts`: Timestamp of the most recent commit

### 2. Data Collection

- Scan all `bq-results-*` CSV files in the data directory (including subdirectories)
- Extract `#include <boost/...>` and `#include "boost/..."` directives from file contents
- Parse repository metadata from CSV fields

### 3. Version Detection

Boost version is determined in priority order:

1. From the `boost_version` field in the CSV (populated by `query.sql` from version detection sources)
2. If CSV field is empty, extracted from file paths containing patterns like:
   - `/boost_1_57_0/` → `1.57.0`
   - `/boost-1.70.0/` → `1.70.0`
   - `/boost1.76.0/` → `1.76.0`

**Note on Missing Version Information**: Some repositories may not have Boost version information available because:

- The repository uses system Boost installed via package managers (apt, yum, brew, etc.) without explicit version declarations in build files
- Version information is specified in documentation or README files rather than in machine-readable build configuration files
- The repository uses Boost headers directly without any dependency management system (CMake, Conan, vcpkg)
- The repository's build system doesn't explicitly declare Boost as a dependency
- Version information exists in files that are not scanned by the query (e.g., CI configuration files, Dockerfiles, or other non-standard locations)

### 4. Data Filtering

Usage records are excluded if:

- The file path contains `/boost` AND the repository has `contains_vendored_boost = true`

This ensures that vendored Boost headers within repository directories are not counted as external Boost usage.

### 5. Database Construction

A relational SQLite database is built with the following tables:

- **`boost_library`**: Unique Boost libraries
- **`boost_header`**: Headers mapped to their parent library
- **`repository`**: GitHub repositories with `affect_from_boost` flag (1 if using system Boost, 0 if vendored) and detected `boost_version`
- **`boost_usage`**: Individual usage records linking repositories to headers with file paths and commit timestamps
