# Integration Plan for Translated Documentation

## Current State

Every library contains documentation in the `doc` folder. The Weblate project creates translated documentation files in the same folder as the original files, with a language suffix (e.g., `_zh`, `_ja`).

## Integration Logic

### Approach 1:

- CI/CD Build Logic

  In `ci_boost_release.py`, after all documentation is converted to HTML and before generating the original index pages, code should be added to detect translated languages and reorganize files with language suffixes (e.g., `_zh`) by moving them to `doc/{language_code}/` and removing the suffix, and update hyperlinks in all HTML files to remove suffixes. Index pages should then be generated for all supported languages including the original and translated versions. Finally, all documentation including translated versions should be archived and saved to S3 as a single archive file.

- Website Display Logic

  When displaying documentation on the website, the user's preferred language should be detected using query parameters, cookies/session, Accept-Language header, optional IP geolocation, and website default settings. Based on the detected language, the URL for getting content from S3 should be changed to include the language code, such as `doc/{language_code}/html/`.

- Advantages

  - Clean separation of languages in folder structure
  - Simple URL structure for website routing
  - Less website code changes required
  - Clear organization makes it easy to add or remove languages

- Disadvantages

  - Requires processing all HTML files to update hyperlinks
  - More complex reorganization logic needed
  - Files are moved from original locations, which may affect existing references
  - Need to handle both root `doc/` and library-specific `libs/{library}/doc/` folders during reorganization

### Approach 2:

- CI/CD Build Logic

  In `ci_boost_release.py`, generate index pages for different languages and save them in the same folder structure as the original index files.

- Website Display Logic

  The documentation is displayed using URLs that include a language suffix in the filename, e.g. `/doc/libs/latest/libs/unordered/doc/html/unordered/intro_zh.html`. The language-specific content should be served by detecting the user's preferred language and serving the corresponding file with the appropriate suffix.

- Advantages

  - Minimal changes to existing file structure
  - No need to reorganize or move files
  - Original file locations remain unchanged
  - Less risk of breaking existing links or references

- Disadvantages

  - Requires complex logic for generating index files for each language
  - More complex URL routing logic needed on website to handle suffix-based file serving
  - Less clear organization for managing multiple languages
  - Index files need to reference translated files with suffixes, complicating link generation
