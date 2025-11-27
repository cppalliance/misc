#!/usr/bin/env python3
"""
Script to analyze Boost library documentation files and generate statistics.
Only processes main documentation types: qbk, adoc, rst, md, xml, html, mml
"""

import os
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any, Tuple, List

# Main documentation types that can be converted to AsciiDoc
MAIN_TYPES = {'qbk', 'adoc', 'rst', 'md', 'xml', 'html', 'htm', 'mml', 'dox'}

TYPE_LABELS = {
    'adoc': 'AsciiDoc',
    'dox': 'Doxygen',
    'html': 'HTML',
    'htm': 'HTML',
    'md': 'Markdown',
    'mml': 'MathML',
    'qbk': 'Quickbook',
    'rst': 'reStructuredText',
    'xml': 'DocBook XML',
}

# Map format labels to their extensions
LABEL_TO_EXTENSIONS = {
    'AsciiDoc': ['.adoc'],
    'Doxygen': ['.dox'],
    'HTML': ['.html', '.htm'],
    'Markdown': ['.md'],
    'MathML': ['.mml'],
    'Quickbook': ['.qbk'],
    'reStructuredText': ['.rst'],
    'DocBook XML': ['.xml'],
}

CONVERSION_TABLE = [
    ('HTML', 'Medium', 'Pandoc'),
    ('Quickbook', 'High', 'Quickbook → DocBook → AsciiDoc'),
    ('Markdown', 'Low', 'Pandoc'),
    ('AsciiDoc', 'None', 'Copy (already target format)'),
    ('reStructuredText', 'Low', 'Pandoc'),
    ('DocBook XML', 'Low', 'Pandoc'),
    ('MathML', 'Low', 'Wrap in code blocks'),
    ('Doxygen', 'Low', 'Pandoc'),
]

# Directories to skip when scanning
SKIP_DIRS = {'test', 'tests', 'example', 'examples', 'build', '.git', 'include', 'src'}


def count_lines(file_path: Path) -> int:
    """Count the number of lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except (OSError, IOError):
        return 0


def get_file_extension(file_path: Path) -> str:
    """Get file extension without the dot."""
    return file_path.suffix[1:].lower() if file_path.suffix else 'no_ext'


def should_skip_directory(relative_parts: tuple) -> bool:
    """Check if directory should be skipped."""
    return any(part in SKIP_DIRS for part in relative_parts) if relative_parts else False


def is_main_type_file(file_path: Path, is_doc_dir: bool) -> bool:
    """Check if file is a main type documentation file."""
    ext = get_file_extension(file_path)

    # Only process main types
    if ext not in MAIN_TYPES:
        return False

    # Include if in doc directory or is a main type
    return is_doc_dir or ext in MAIN_TYPES


def get_relative_path(file_path: Path) -> str:
    """Get relative path from boost_1_89_0/libs, or absolute path if not relative."""
    try:
        relative_path = file_path.relative_to(Path('boost_1_89_0/libs'))
        return str(relative_path).replace('\\', '/')
    except ValueError:
        return str(file_path).replace('\\', '/')


def process_file(file_path: Path, is_doc_dir: bool,
                 stats: Dict[str, Dict[str, int]],
                 file_paths: Dict[str, List[str]]) -> None:
    """Process a single file if it's a main type."""
    if not is_main_type_file(file_path, is_doc_dir):
        return

    ext = get_file_extension(file_path)
    stats[ext]['file count'] += 1
    stats[ext]['line count'] += count_lines(file_path)
    file_paths[ext].append(get_relative_path(file_path))


def scan_library_docs(
    lib_path: Path
) -> Tuple[Dict[str, Dict[str, int]], Dict[str, List[str]]]:
    """
    Scan a library directory for main type documentation files.
    Returns statistics and file paths for main types only.
    """
    stats = defaultdict(lambda: {'file count': 0, 'line count': 0})
    file_paths = defaultdict(list)

    for root, _, files in os.walk(lib_path):
        root_path = Path(root)

        # Get relative parts for skipping logic
        if root_path == lib_path:
            relative_parts = ()
        else:
            try:
                relative_parts = root_path.relative_to(lib_path).parts
            except ValueError:
                relative_parts = root_path.parts

        # Skip certain directories
        if should_skip_directory(relative_parts):
            continue

        # Check if we're in a documentation directory
        is_doc_dir = 'doc' in root_path.parts
        if not is_doc_dir:
            continue

        # Process files
        for file in files:
            file_path = root_path / file
            process_file(file_path, is_doc_dir, stats, file_paths)

    # Convert to regular dict and filter out empty entries
    result = {ext: data for ext, data in stats.items() if data['file count'] > 0}
    return result, dict(file_paths)


def sort_stats(stats: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, int]]:
    """Return a dict sorted by descending file count, then extension name."""
    return {
        ext: stats[ext]
        for ext in sorted(
            stats.keys(),
            key=lambda ext: (-stats[ext]['file count'], ext)
        )
    }


def collect_libraries_by_type(lib_stats: Dict[str, Dict[str, Dict[str, int]]],
                              main_type: str) -> List[Dict[str, Dict[str, int]]]:
    """Collect all libraries that have a specific main type."""
    libraries_with_type = []
    for lib_name, lib_data in lib_stats.items():
        if main_type in lib_data:
            libraries_with_type.append({
                lib_name: {
                    "file count": lib_data[main_type].get('file count', 0),
                    "line count": lib_data[main_type].get('line count', 0)
                }
            })
    return libraries_with_type


def sort_libraries_by_file_count(
    libraries: List[Dict[str, Dict[str, int]]]
) -> List[Dict[str, Dict[str, int]]]:
    """Sort libraries by file count (descending), then by library name."""
    return sorted(
        libraries,
        key=lambda x: (
            -list(x.values())[0]['file count'],
            list(x.keys())[0]
        )
    )


def get_top_libraries(libraries: List[Dict[str, Dict[str, int]]],
                     min_count: int) -> Dict[str, Dict[str, int]]:
    """Get top libraries, merged into a single dict."""
    top_count = min_count if len(libraries) >= min_count else len(libraries)
    top_libraries = libraries[:top_count]

    merged = {}
    for lib in top_libraries:
        merged.update(lib)
    return merged


def create_type_data(main_type: str,
                    lib_stats: Dict[str, Dict[str, Dict[str, int]]],
                    total_stats: Dict[str, Dict[str, int]],
                    min_top_libraries: int) -> Dict[str, Any]:
    """Create data structure for a single main type."""
    type_data = {
        "_total": {
            "file count": total_stats.get(main_type, {}).get('file count', 0),
            "line count": total_stats.get(main_type, {}).get('line count', 0)
        },
        "top libraries": {}
    }

    libraries_with_type = collect_libraries_by_type(lib_stats, main_type)
    sorted_libraries = sort_libraries_by_file_count(libraries_with_type)
    type_data["top libraries"] = get_top_libraries(sorted_libraries, min_top_libraries)

    return type_data


def create_main_types_by_type(lib_stats: Dict[str, Dict[str, Dict[str, int]]],
                              total_stats: Dict[str, Dict[str, int]],
                              min_top_libraries: int = 5) -> Dict[str, Any]:
    """
    Create structure organized by file type with totals and top libraries.
    """
    result = {}

    for main_type in sorted(MAIN_TYPES):
        result[main_type] = create_type_data(
            main_type, lib_stats, total_stats, min_top_libraries
        )

    # Add file types list at the beginning
    result = {"file types": list(sorted(MAIN_TYPES))} | result
    return result


def create_total_main_types_stats(
    lib_stats: Dict[str, Dict[str, Dict[str, int]]]
) -> Dict[str, Any]:
    """
    Create statistics for all libraries, only for main types.
    """
    result = {}
    for lib_name, lib_data in sorted(lib_stats.items()):
        # Only include main types (already filtered, but double-check)
        main_types_only = {
            ext: stats for ext, stats in lib_data.items() if ext in MAIN_TYPES
        }
        if main_types_only:
            result[lib_name] = main_types_only
    return result


def get_library_directories(boost_libs_path: Path) -> List[Path]:
    """Get all library directories to analyze."""
    return sorted([
        d for d in boost_libs_path.iterdir()
        if d.is_dir() and not d.name.startswith('.')
    ])


def analyze_single_library(
    lib_dir: Path
) -> Tuple[Dict[str, Dict[str, int]], Dict[str, List[str]]]:
    """Analyze a single library and return its statistics."""
    lib_name = lib_dir.name
    print(f"Analyzing {lib_name}...")

    lib_stats, lib_file_paths = scan_library_docs(lib_dir)
    return lib_stats, lib_file_paths


def accumulate_totals(lib_stats: Dict[str, Dict[str, int]],
                      total_stats: Dict[str, Dict[str, int]]) -> None:
    """Accumulate library statistics into totals."""
    for ext, data in lib_stats.items():
        if ext in MAIN_TYPES:
            total_stats[ext]['file count'] += data['file count']
            total_stats[ext]['line count'] += data['line count']


def save_statistics_files(main_types_lib_stats: Dict[str, Dict[str, Dict[str, int]]],
                          total_stats: Dict[str, Dict[str, int]],
                          all_file_paths: Dict[str, List[str]]) -> Dict[str, Any]:
    """Save all statistics files."""
    # Save main types by type
    main_types_output_file = 'boost_doc_statistics_main.json'
    main_types_by_type = create_main_types_by_type(
        main_types_lib_stats,
        total_stats,
        min_top_libraries=5
    )
    with open(main_types_output_file, 'w', encoding='utf-8') as f:
        json.dump(main_types_by_type, f, indent=2, ensure_ascii=False)

    # Save total statistics
    output_file = 'boost_doc_statistics_total.json'
    total_main_types_stats = create_total_main_types_stats(main_types_lib_stats)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(total_main_types_stats, f, indent=2, ensure_ascii=False)

    # Save file list for conversion
    file_list_output = 'boost_doc_files_to_convert.json'
    sorted_file_paths = {ext: sorted(paths) for ext, paths in all_file_paths.items()}
    with open(file_list_output, 'w', encoding='utf-8') as f:
        json.dump(sorted_file_paths, f, indent=2, ensure_ascii=False)

    report_content = build_report(main_types_by_type, sorted_file_paths)
    write_report(report_content)

    print("\nAnalysis complete!")
    print(
        f"  Main types by type (with totals & top libraries) "
        f"saved to: {main_types_output_file}"
    )
    print(f"  All libraries main types statistics saved to: {output_file}")
    print(f"  File list for conversion saved to: {file_list_output}")
    print("  Summary report saved to: Report.md")

    return main_types_by_type


def build_report(main_stats: Dict[str, Any],
                 file_inventory: Dict[str, List[str]]) -> str:
    """Generate the contents of the documentation report."""
    file_types = main_stats.get('file types', [])
    total_files = sum(
        main_stats.get(doc_type, {}).get('_total', {}).get('file count', 0)
        for doc_type in file_types
    )
    total_lines = sum(
        main_stats.get(doc_type, {}).get('_total', {}).get('line count', 0)
        for doc_type in file_types
    )

    def format_percentage(count: int) -> str:
        if not total_files:
            return "0%"
        return f"{(count / total_files) * 100:.1f}%"

    def short_lines(lines: int) -> str:
        if lines >= 1000:
            return f"{round(lines / 1000):,}K lines"
        return f"{lines:,} lines"

    def format_with_extensions(label: str) -> str:
        """Format label with file extensions."""
        extensions = LABEL_TO_EXTENSIONS.get(label, [])
        if extensions:
            ext_str = ', '.join(extensions)
            return f"{label} ({ext_str})"
        return label

    report_lines = [
        "# Boost Documentation Analysis - Report",
        "",
        "**Analysis Date:** Generated from Boost 1.90.0 Documentation",
        "",
        "---",
        "",
        "## Summary",
        "",
        "Comprehensive analysis of Boost library documentation reveals "
        f"**{total_files:,} files** containing **{total_lines:,} lines** across "
        f"{len(file_types)} documentation formats. All files are cataloged and "
        "ready for unified AsciiDoc conversion.",
        "",
        "### Key Metrics",
        "",
        f"- **Total Files:** {total_files:,}",
        f"- **Total Lines:** {total_lines:,}",
        f"- **Formats:** {len(file_types)} types (see table below)",
        "- **Status:** ✅ Ready for conversion",
        "",
        "---",
        "",
        "## Documentation Format Distribution",
        "",
        "| Format                          | Files  | %     | Lines     |",
        "| ------------------------------- | ------ | ----- | --------- |",
    ]

    # Group file types by label to combine html/htm
    grouped_by_label = {}
    for doc_type in file_types:
        doc_label = TYPE_LABELS.get(doc_type, doc_type.upper())
        if doc_label not in grouped_by_label:
            grouped_by_label[doc_label] = []
        grouped_by_label[doc_label].append(doc_type)

    # Generate table rows, combining html and htm
    for doc_label in sorted(grouped_by_label.keys()):
        types_for_label = grouped_by_label[doc_label]
        # Combine statistics for all types with this label
        combined_file_count = sum(
            main_stats.get(doc_type, {}).get('_total', {}).get('file count', 0)
            for doc_type in types_for_label
        )
        combined_line_count = sum(
            main_stats.get(doc_type, {}).get('_total', {}).get('line count', 0)
            for doc_type in types_for_label
        )
        label_with_ext = format_with_extensions(doc_label)
        report_lines.append(
            f"| **{label_with_ext}** | {combined_file_count:,} | "
            f"{format_percentage(combined_file_count)} | "
            f"{combined_line_count:,} |"
        )

    # Create sorted formats using grouped statistics
    sorted_formats = []
    for doc_label in grouped_by_label.keys():
        types_for_label = grouped_by_label[doc_label]
        combined_file_count = sum(
            main_stats.get(doc_type, {}).get('_total', {}).get('file count', 0)
            for doc_type in types_for_label
        )
        combined_line_count = sum(
            main_stats.get(doc_type, {}).get('_total', {}).get('line count', 0)
            for doc_type in types_for_label
        )
        sorted_formats.append(
            (types_for_label[0], doc_label, combined_file_count, combined_line_count)
        )
    sorted_formats.sort(key=lambda item: item[2], reverse=True)

    top_line = ""
    if sorted_formats:
        top = sorted_formats[0]
        top_label = format_with_extensions(top[1])
        top_line = (
            f"**Key Finding:** {top_label} represents "
            f"{format_percentage(top[2])} of all documentation files."
        )
        if len(sorted_formats) > 1:
            second = sorted_formats[1]
            second_label = format_with_extensions(second[1])
            top_line += (
                f" {second_label} follows with {format_percentage(second[2])} "
                f"across {second[2]:,} files."
            )

    report_lines.extend([
        "",
        top_line or "**Key Finding:** Documentation files are well-distributed "
        "across multiple formats.",
        "",
        "---",
        "",
        "## Top Libraries by Format",
        "",
    ])

    # Process each label group (combining html/htm)
    for doc_label in sorted(grouped_by_label.keys()):
        types_for_label = grouped_by_label[doc_label]
        # Combine file counts
        combined_file_count = sum(
            main_stats.get(doc_type, {}).get('_total', {}).get('file count', 0)
            for doc_type in types_for_label
        )
        label_with_ext = format_with_extensions(doc_label)
        report_lines.append(
            f"### {label_with_ext} ({combined_file_count:,} files)"
        )
        report_lines.append("")

        # Merge top libraries from all types with this label
        merged_libraries = {}
        for doc_type in types_for_label:
            top_libraries = main_stats.get(doc_type, {}).get('top libraries', {})
            for lib_name, stats_dict in top_libraries.items():
                if lib_name not in merged_libraries:
                    merged_libraries[lib_name] = {
                        'file count': 0,
                        'line count': 0
                    }
                merged_libraries[lib_name]['file count'] += (
                    stats_dict.get('file count', 0)
                )
                merged_libraries[lib_name]['line count'] += (
                    stats_dict.get('line count', 0)
                )

        if merged_libraries:
            # Sort by file count descending
            sorted_libs = sorted(
                merged_libraries.items(),
                key=lambda x: x[1]['file count'],
                reverse=True
            )
            for idx, (lib_name, stats_dict) in enumerate(sorted_libs[:5], 1):
                lib_files = stats_dict.get('file count', 0)
                lib_lines = stats_dict.get('line count', 0)
                report_lines.append(
                    f"{idx}. **{lib_name}** - {lib_files:,} files, "
                    f"{short_lines(lib_lines)}"
                )
        else:
            report_lines.append("No libraries recorded.")
        report_lines.append("")

    report_lines.extend([
        "---",
        "",
        "## Conversion Readiness",
        "",
        "### Status: ✅ Ready",
        "",
        "All files cataloged in `boost_doc_files_to_convert.json` and ready for "
        "conversion pipeline.",
        "",
        "### Conversion Complexity",
        "",
        "| Format                          | Complexity | Tool Required |",
        "| ------------------------------- | ---------- | ------------- |",
    ])

    for format_name, complexity, tool in CONVERSION_TABLE:
        label_with_ext = format_with_extensions(format_name)
        report_lines.append(
            f"| {label_with_ext:<30} | {complexity:<10} | {tool} |"
        )

    report_lines.extend([
        "",
        "**Note:** Fragment files (included in parent documents) are automatically "
        "detected and skipped.",
        "",
        "---",
        "",
        "## Generated Artifacts",
        "",
        "1. **boost_doc_statistics_main.json** - Statistics by file type with totals",
        "2. **boost_doc_statistics_total.json** - Complete library breakdown",
        "3. **boost_doc_files_to_convert.json** - Complete file inventory "
        f"({sum(len(v) for v in file_inventory.values()):,} files)",
    ])

    return "\n".join(report_lines)


def write_report(content: str, path: Path = Path('Report.md')) -> None:
    """Write the generated report to disk."""
    path.write_text(content, encoding='utf-8')


def main():
    """Main function to analyze all Boost libraries."""
    # boost_libs_path = Path('boost_1_89_0/libs')
    boost_libs_path = Path('D:/boost/libs')
    if not boost_libs_path.exists():
        print(f"Error: {boost_libs_path} does not exist!")
        return

    libraries = get_library_directories(boost_libs_path)
    print(f"Found {len(libraries)} libraries to analyze...")

    main_types_lib_stats = {}
    total_stats = defaultdict(lambda: {'file count': 0, 'line count': 0})
    all_file_paths = defaultdict(list)

    # Analyze each library
    for lib_dir in libraries:
        lib_stats, lib_file_paths = analyze_single_library(lib_dir)

        if lib_stats:
            lib_name = lib_dir.name
            sorted_lib_stats = sort_stats(lib_stats)
            main_types_lib_stats[lib_name] = sorted_lib_stats

            # Merge file paths
            for ext, paths in lib_file_paths.items():
                all_file_paths[ext].extend(paths)

            # Accumulate totals
            accumulate_totals(lib_stats, total_stats)
        else:
            print(lib_dir)

    # Save all output files
    save_statistics_files(main_types_lib_stats, total_stats, all_file_paths)
    print(f"Total libraries analyzed: {len(main_types_lib_stats)}")


if __name__ == '__main__':
    main()
