# Boost Documentation Analysis - Report

Generated from Boost 1.90.0 Documentation

---

## Summary

Analysis of Boost library documentation reveals **7,669 files** containing **1,634,676 lines** across 9 documentation formats. All files are cataloged and ready for unified AsciiDoc conversion.

### Key Metrics

- **Total Files:** 7,669
- **Total Lines:** 1,634,676
- **Formats:** 9 types (see table below)
- **Status:** Ready to start pilot conversion for each format

---

## Documentation Format Distribution

| Format                          | Files  | %     | Lines     |
| ------------------------------- | ------ | ----- | --------- |
| **AsciiDoc (.adoc)** | 462 | 6.0% | 93,397 |
| **DocBook XML (.xml)** | 223 | 2.9% | 90,505 |
| **Doxygen (.dox)** | 10 | 0.1% | 1,969 |
| **HTML (.html, .htm)** | 3,993 | 52.1% | 787,021 |
| **Markdown (.md)** | 9 | 0.1% | 1,407 |
| **MathML (.mml)** | 352 | 4.6% | 26,341 |
| **Quickbook (.qbk)** | 2,411 | 31.4% | 593,592 |
| **reStructuredText (.rst)** | 209 | 2.7% | 40,444 |

**Key Finding:** HTML (.html, .htm) represents 52.1% of all documentation files. Quickbook (.qbk) follows with 31.4% across 2,411 files.

---

## Top Libraries by Format

### AsciiDoc (.adoc) (462 files)

1. **cobalt** - 80 files, 5K lines
2. **unordered** - 52 files, 23K lines
3. **json** - 32 files, 3K lines
4. **hash2** - 30 files, 4K lines
5. **uuid** - 28 files, 2K lines

### DocBook XML (.xml) (223 files)

1. **proto** - 64 files, 18K lines
2. **safe_numerics** - 35 files, 9K lines
3. **signals2** - 24 files, 4K lines
4. **variant** - 21 files, 5K lines
5. **concept_check** - 12 files, 2K lines

### Doxygen (.dox) (10 files)

1. **program_options** - 5 files, 379 lines
2. **asio** - 2 files, 756 lines
3. **nowide** - 2 files, 553 lines
4. **gil** - 1 files, 281 lines

### HTML (.html, .htm) (3,993 files)

1. **outcome** - 528 files, 26K lines
2. **preprocessor** - 524 files, 32K lines
3. **math** - 499 files, 177K lines
4. **mpl** - 266 files, 29K lines
5. **icl** - 255 files, 42K lines

### Markdown (.md) (9 files)

1. **gil** - 1 files, 34 lines
2. **histogram** - 1 files, 9 lines
3. **json** - 1 files, 11 lines
4. **leaf** - 1 files, 538 lines
5. **mysql** - 1 files, 49 lines

### MathML (.mml) (352 files)

1. **math** - 349 files, 26K lines
2. **multiprecision** - 3 files, 359 lines

### Quickbook (.qbk) (2,411 files)

1. **math** - 256 files, 55K lines
2. **metaparse** - 206 files, 17K lines
3. **geometry** - 176 files, 8K lines
4. **type_traits** - 161 files, 9K lines
5. **spirit** - 155 files, 32K lines

### reStructuredText (.rst) (209 files)

1. **iterator** - 74 files, 7K lines
2. **gil** - 48 files, 6K lines
3. **graph_parallel** - 37 files, 7K lines
4. **ptr_container** - 26 files, 5K lines
5. **python** - 15 files, 2K lines

---

## Conversion Readiness

All files cataloged in `boost_doc_files_to_convert.json` and ready for conversion pilot.

### Conversion Complexity

| Format                          | Complexity | Tool Required |
| ------------------------------- | ---------- | ------------- |
| HTML (.html, .htm)             | Medium     | Pandoc |
| Quickbook (.qbk)               | High       | Quickbook → DocBook → AsciiDoc |
| Markdown (.md)                 | Low        | Pandoc |
| AsciiDoc (.adoc)               | None       | None |
| reStructuredText (.rst)        | Low        | Pandoc |
| DocBook XML (.xml)             | Low        | Pandoc |
| MathML (.mml)                  | Low        | Wrap in code blocks |
| Doxygen (.dox)                 | Low        | Pandoc |

**Note:** Fragment files (included in parent documents) are automatically detected and skipped.

---

## Generated Artifacts

1. **boost_doc_statistics_main.json** - Statistics by file type with totals
2. **boost_doc_statistics_total.json** - Complete library breakdown
3. **boost_doc_files_to_convert.json** - Complete file inventory (7,669 files)
