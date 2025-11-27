#!/usr/bin/env python3
"""
Convert Boost documentation sources to AsciiDoc format.

This script converts all main documentation types (qbk, rst, md, adoc, xml, html, mml)
from Boost libraries into a unified AsciiDoc format.
"""

import os
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Optional, Dict, Tuple

BOOST_LIBS = Path("boost_1_89_0/libs")
OUTPUT_ADOC = Path("converted_docs/adoc")


class ContentError(Exception):
    """Exception for content/format errors (e.g., missing doc_info)."""


def ensure_dir(path: Path) -> None:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def find_pandoc_path() -> Optional[str]:
    """Find Pandoc executable on Windows."""
    if os.name != 'nt':
        return None

    local_appdata = os.environ.get('LOCALAPPDATA', '')
    program_files = os.environ.get('ProgramFiles', '')
    program_files_x86 = os.environ.get('ProgramFiles(x86)', '')

    possible_paths = [
        Path(local_appdata) / 'Pandoc' / 'pandoc.exe',
        Path(program_files) / 'Pandoc' / 'pandoc.exe',
        Path(program_files_x86) / 'Pandoc' / 'pandoc.exe',
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)
    return None


def find_command_path(cmd: str) -> Optional[str]:
    """Find the full path to a command."""
    # First check PATH
    path = shutil.which(cmd)
    if path:
        return path

    # Check Windows-specific locations
    if cmd == 'pandoc':
        return find_pandoc_path()

    return None


def check_command_exists(cmd: str) -> bool:
    """Check if a command exists in PATH or common installation locations."""
    return find_command_path(cmd) is not None


def resolve_command_path(cmd: Sequence[str]) -> Sequence[str]:
    """Resolve command to absolute path if needed."""
    if not cmd:
        return cmd

    cmd_list = list(cmd)
    cmd_name = cmd_list[0]

    if not Path(cmd_name).is_absolute():
        full_path = find_command_path(cmd_name)
        if full_path:
            cmd_list[0] = full_path

    return cmd_list


def is_quickbook_command(cmd: Sequence[str]) -> bool:
    """Check if command is related to Quickbook."""
    cmd_str = ' '.join(str(c) for c in cmd).lower()
    return "quickbook" in cmd_str or ".qbk" in cmd_str


def has_file_error(error_str: str) -> bool:
    """Check if error is a file/path error."""
    file_error_patterns = [
        "file not found",
        "cannot find",
        "no such file",
        "parent directory not found",
        "cannot open",
        "access denied",
    ]
    return any(pattern in error_str.lower() for pattern in file_error_patterns)


def is_content_error(cmd: Sequence[str], error_str: str) -> bool:
    """Determine if error is a content/format error."""
    if not is_quickbook_command(cmd):
        return False

    # For Quickbook, if it's not a file error, it's likely a content error
    return not has_file_error(error_str)


def extract_error_message(error_str: str) -> str:
    """Extract meaningful error message from error string."""
    error_lines = [line.strip() for line in error_str.split('\n') if line.strip()]

    # Find first line with "error:" or "warning:"
    first_error = next(
        (
            line for line in error_lines
            if 'error:' in line.lower() or 'warning:' in line.lower()
        ),
        error_lines[0] if error_lines else error_str[:200]
    )
    return first_error


def run_command(cmd: Sequence[str], cwd: Path | None = None) -> None:
    """Run a command and provide helpful error messages if it fails."""
    cmd = resolve_command_path(cmd)

    try:
        subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
    except FileNotFoundError as e:
        cmd_name = cmd[0] if cmd else "unknown"
        raise FileNotFoundError(
            f"Command '{cmd_name}' not found. "
            "Please install it and ensure it's in your PATH.\n"
            "See require.md for installation instructions."
        ) from e
    except subprocess.CalledProcessError as e:
        error_msg = (e.stderr or '') + (e.stdout or '')
        if not error_msg:
            error_msg = 'Unknown error'
        error_str = str(error_msg)

        if is_content_error(cmd, error_str):
            first_error = extract_error_message(error_str)
            raise ContentError(f"Content error: {first_error}") from e

        # Tool/execution error
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\n"
            f"Return code: {e.returncode}\n"
            f"Error output: {error_msg[:500]}"
        ) from e


def read_text(path: Path) -> str:
    """Read text file content."""
    return path.read_text(encoding="utf-8", errors="ignore")


def copy_to(dest: Path, content: str) -> None:
    """Write content to destination file."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")


@dataclass
class DocumentConverter:
    """Base class for document converters."""
    extension: str

    def matches(self, path: Path) -> bool:
        """Check if path matches this converter's extension."""
        return path.suffix.lower().lstrip(".") == self.extension

    def convert(self, source: Path, adoc_dest: Path) -> None:
        """Convert source file to AsciiDoc."""
        raise NotImplementedError


class PandocConverter(DocumentConverter):
    """Base converter using Pandoc."""
    reader: str

    def pandoc(self, source: Path, dest: Path, to_format: str) -> None:
        """Run Pandoc conversion."""
        if not check_command_exists("pandoc"):
            raise FileNotFoundError(
                "pandoc command not found. Please install Pandoc.\n"
                "See require.md for installation instructions."
            )
        ensure_dir(dest.parent)
        run_command([
            "pandoc",
            "-f", self.reader,
            "-t", to_format,
            "-o", str(dest),
            str(source),
        ])

    def convert(self, source: Path, adoc_dest: Path) -> None:
        """Convert to AsciiDoc format."""
        self.pandoc(source, adoc_dest, "asciidoc")


class MarkdownConverter(PandocConverter):
    """Convert Markdown files."""
    extension = "md"
    reader = "gfm"


class RstConverter(PandocConverter):
    """Convert reStructuredText files."""
    extension = "rst"
    reader = "rst"


class AsciiDocConverter(DocumentConverter):
    """Copy AsciiDoc files (already in correct format)."""
    extension = "adoc"

    def convert(self, source: Path, adoc_dest: Path) -> None:
        """Copy AsciiDoc file."""
        ensure_dir(adoc_dest.parent)
        shutil.copy2(source, adoc_dest)


class DocBookConverter(PandocConverter):
    """Convert DocBook XML files."""
    extension = "xml"
    reader = "docbook"


class HtmlConverter(PandocConverter):
    """Convert HTML files."""
    extension = "html"
    reader = "html"

    def convert(self, source: Path, adoc_dest: Path) -> None:
        """Convert HTML to AsciiDoc."""
        self.pandoc(source, adoc_dest, "asciidoc")


class HtmConverter(PandocConverter):
    """Convert HTM files."""
    extension = "htm"
    reader = "html"

    def convert(self, source: Path, adoc_dest: Path) -> None:
        """Convert HTM to AsciiDoc."""
        self.pandoc(source, adoc_dest, "asciidoc")


class QuickbookConverter(DocumentConverter):
    """Convert Quickbook files."""
    extension = "qbk"

    def convert(self, source: Path, adoc_dest: Path) -> None:
        """Convert Quickbook to AsciiDoc via DocBook."""
        if not check_command_exists("quickbook"):
            raise FileNotFoundError(
                "quickbook command not found. Please install Boost.Quickbook.\n"
                "See require.md for installation instructions."
            )

        source_abs = source.resolve()
        source_dir = source_abs.parent
        tmp_docbook = source_dir / f"{source_abs.stem}.tmp.docbook.xml"
        ensure_dir(tmp_docbook.parent)

        source_str = str(source_abs).replace('\\', '/')
        output_str = str(tmp_docbook).replace('\\', '/')

        run_command([
            "quickbook",
            f"--output-file={output_str}",
            source_str,
        ], cwd=None)

        try:
            docbook_converter = DocBookConverter("xml")
            docbook_converter.convert(tmp_docbook, adoc_dest)
        finally:
            if tmp_docbook.exists():
                tmp_docbook.unlink()


class MathMLConverter(DocumentConverter):
    """Convert MathML files."""
    extension = "mml"

    def convert(self, source: Path, adoc_dest: Path) -> None:
        """Wrap MathML in AsciiDoc code block."""
        content = read_text(source)
        asciidoc_content = f"[source,xml]\n----\n{content}\n----\n"
        copy_to(adoc_dest, asciidoc_content)


class DoxygenConverter(PandocConverter):
    """Convert Doxygen files."""
    extension = "dox"
    reader = "markdown"

    def convert(self, source: Path, adoc_dest: Path) -> None:
        """Convert Doxygen to AsciiDoc."""
        self.pandoc(source, adoc_dest, "asciidoc")


CONVERTERS: List[DocumentConverter] = [
    QuickbookConverter("qbk"),
    RstConverter("rst"),
    MarkdownConverter("md"),
    AsciiDocConverter("adoc"),
    DocBookConverter("xml"),
    HtmlConverter("html"),
    HtmConverter("htm"),
    MathMLConverter("mml"),
    DoxygenConverter("dox"),
]


def load_file_list() -> Dict[str, List[str]]:
    """Load the file list generated by analyze_boost_docs.py."""
    file_list_path = Path('boost_doc_files_to_convert.json')
    if not file_list_path.exists():
        raise FileNotFoundError(
            f"File list not found: {file_list_path}\n"
            "Please run analyze_boost_docs.py first to generate the file list."
        )
    with open(file_list_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def is_fragment_file(file_path: Path) -> bool:
    """Check if a Quickbook file is a fragment."""
    if file_path.suffix.lower() != '.qbk':
        return False

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline().strip()
            if first_line.startswith('[section') or first_line.startswith('[/'):
                content_start = f.read(200)
                doc_info_indicators = [
                    '[library', '[article', '[book', '[chapter',
                    '[preface', '[reference'
                ]
                if not any(
                    indicator in content_start
                    for indicator in doc_info_indicators
                ):
                    return True
    except (OSError, IOError):
        pass
    return False


def find_files(extension: str, use_file_list: bool = True) -> Iterable[Path]:
    """Find files of a given extension."""
    if use_file_list:
        try:
            file_list = load_file_list()
            if extension in file_list:
                for rel_path in file_list[extension]:
                    file_path = BOOST_LIBS / rel_path
                    if file_path.exists():
                        yield file_path
            return
        except FileNotFoundError:
            print("⚠ File list not found, falling back to directory scanning...")

    # Fallback: scan directories
    for path in BOOST_LIBS.rglob(f"*.{extension}"):
        yield path


def check_tool(tool: str) -> bool:
    """Check if a tool exists and print status."""
    if check_command_exists(tool):
        print(f"✓ Found: {tool}")
        return True
    return False


def check_required_tools() -> None:
    """Check if all required tools are available."""
    required_tools = {
        "pandoc": (
            "Pandoc is required for most conversions. "
            "Install from https://pandoc.org/installing.html"
        ),
        "quickbook": (
            "Quickbook is required for converting .qbk files. "
            "Install Boost.Quickbook or build from Boost sources."
        ),
    }

    optional_tools = {}

    missing_required = []
    missing_optional = []

    for tool, message in required_tools.items():
        if not check_tool(tool):
            missing_required.append(f"  - {tool}: {message}")

    for tool, message in optional_tools.items():
        if not check_tool(tool):
            missing_optional.append(f"  - {tool}: {message}")

    if missing_optional:
        print("\n⚠ Optional tools not found (conversion will skip these file types):")
        print("\n".join(missing_optional))

    if missing_required:
        print("\n❌ ERROR: Missing required tools:")
        print("\n".join(missing_required))
        print("\nTroubleshooting:")
        print("  1. Ensure the tool is installed")
        print("  2. Restart your terminal/IDE after installation")
        print("  3. Verify the tool is in your system PATH")
        print("  4. Try running the tool directly (e.g., 'pandoc --version')")
        print("\nSee require.md for detailed installation instructions.")
        raise FileNotFoundError("Required tools are missing. Please install them first.")


def filter_available_converters() -> List[DocumentConverter]:
    """Filter converters based on available tools."""
    available = []
    for converter in CONVERTERS:
        # Quickbook is required, so it should already be checked in check_required_tools
        # Pandoc is also required, so it should already be checked
        # This function is mainly for consistency checks
        if isinstance(converter, PandocConverter):
            if not check_command_exists("pandoc"):
                print(f"⚠ Skipping {converter.extension} files (pandoc not available)")
                continue
        available.append(converter)
    return available


def handle_content_error(e: ContentError, source: Path,
                        content_errors: int, extension: str) -> None:
    """Handle content/format errors."""
    error_str = str(e)
    if "No doc_info block" in error_str or "doc_info" in error_str.lower():
        if content_errors <= 10:
            print(
                f"  ⚠ Skipped fragment/incomplete file: "
                f"{source.name} (missing doc_info)"
            )
        elif content_errors == 11:
            print(f"  ... (suppressing further content errors for {extension})")
    else:
        if content_errors <= 5:
            error_msg = error_str.split('\n', maxsplit=1)[0]
            print(f"  ⚠ Content error ({source.name}): {error_msg}")
        elif content_errors == 6:
            print(f"  ... (suppressing further content errors for {extension})")


def is_quickbook_content_error(extension: str, error_str: str) -> bool:
    """Check if RuntimeError is actually a Quickbook content error."""
    if extension != "qbk" or "Command failed" not in error_str:
        return False

    content_indicators = ["error:", "warning:", "error count", ".qbk:"]
    file_error_indicators = ["file not found", "cannot find", "no such file"]

    has_content = any(ind in error_str.lower() for ind in content_indicators)
    has_file_err = any(ind in error_str.lower() for ind in file_error_indicators)

    return has_content and not has_file_err


def handle_tool_error(e: Exception, source: Path, extension: str,
                     content_errors: int, tool_errors: int) -> Tuple[int, int]:
    """Handle tool/execution errors."""
    error_str = str(e)
    is_quickbook_content = is_quickbook_content_error(extension, error_str)

    if is_quickbook_content:
        content_errors += 1
        if content_errors <= 10:
            error_lines = error_str.split('\n')
            qbk_error = next(
                (
                    line for line in error_lines
                    if '.qbk:' in line or 'error:' in line.lower()
                ),
                None
            )
            if qbk_error:
                print(f"  ⚠ Content error ({source.name}): {qbk_error.strip()[:100]}")
            else:
                print(f"  ⚠ Content error ({source.name}): Quickbook syntax/format issue")
        elif content_errors == 11:
            print(f"  ... (suppressing further content errors for {extension})")
        return content_errors, tool_errors
    else:
        tool_errors += 1
        if tool_errors <= 3:
            error_msg = error_str.split('\n', maxsplit=1)[0]
            print(f"  ⚠ Tool error ({source.name}): {error_msg}")
        elif tool_errors == 4:
            print(f"  ... (suppressing further tool errors for {extension})")
        return content_errors, tool_errors


def convert_single_file(source: Path, converter: DocumentConverter,
                       adoc_dest: Path) -> bool:
    """Convert a single file. Returns True if successful."""
    if adoc_dest.exists():
        return False

    try:
        converter.convert(source, adoc_dest)
        return True
    except ContentError:
        raise
    except (FileNotFoundError, RuntimeError):
        raise
    except (OSError, IOError, ValueError, KeyError, AttributeError) as e:
        # Unexpected errors from file operations or converter issues
        error_msg = str(e).split('\n', maxsplit=1)[0]
        raise ContentError(f"Unexpected error: {error_msg}") from e


def process_converter(converter: DocumentConverter) -> None:
    """Process all files for a converter."""
    print(f"Processing {converter.extension} files...")
    count = 0
    skipped = 0
    content_errors = 0
    tool_errors = 0

    for source in find_files(converter.extension, use_file_list=True):
        # Skip fragment files early
        if converter.extension == "qbk" and is_fragment_file(source):
            content_errors += 1
            skipped += 1
            if content_errors <= 10:
                print(
                    f"  ⚠ Skipped fragment file: "
                    f"{source.name} (no doc_info block)"
                )
            elif content_errors == 11:
                print(
                    f"  ... (suppressing further fragment file skips "
                    f"for {converter.extension})"
                )
            continue

        relative = source.relative_to(BOOST_LIBS)
        adoc_dest = OUTPUT_ADOC / converter.extension / relative.with_suffix(".adoc")

        try:
            if convert_single_file(source, converter, adoc_dest):
                count += 1
                if count % 100 == 0:
                    print(f"  Converted {count} {converter.extension} files...")
        except ContentError as e:
            content_errors += 1
            skipped += 1
            handle_content_error(e, source, content_errors, converter.extension)
        except (FileNotFoundError, RuntimeError) as e:
            skipped += 1
            content_errors, tool_errors = handle_tool_error(
                e, source, converter.extension, content_errors, tool_errors
            )

    # Print summary
    if skipped > 0:
        summary_parts = [f"{count} converted"]
        if content_errors > 0:
            summary_parts.append(f"{content_errors} content errors")
        if tool_errors > 0:
            summary_parts.append(f"{tool_errors} tool errors")
        print(f"  Completed {converter.extension}: {', '.join(summary_parts)}\n")
    else:
        print(f"  Completed {converter.extension}: {count} files converted\n")


def convert_all() -> None:
    """Main conversion function."""
    print("Checking for required tools...")
    check_required_tools()

    file_list_path = Path('boost_doc_files_to_convert.json')
    if file_list_path.exists():
        print("\n✓ Using file list from analyze_boost_docs.py")
    else:
        print("\n⚠ File list not found - will scan directories directly")
        print("  (Run analyze_boost_docs.py first for better performance)")

    print("\nStarting conversion...\n")
    ensure_dir(OUTPUT_ADOC)

    available_converters = filter_available_converters()
    if not available_converters:
        print("No converters available. Please install required tools.")
        return

    for converter in available_converters:
        process_converter(converter)


if __name__ == "__main__":
    convert_all()
