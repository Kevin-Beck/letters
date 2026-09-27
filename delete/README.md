# Safe to delete

Everything in this folder can be deleted. A better copy of each file is kept
elsewhere in the project.

- `scans/`: extra scans of pages that already have a scan in `../scans/`.
  Each file is named after the page it duplicates. For example,
  `1942-07-02_tom-to-mother_p01_dup1.jpg` is a second scan of
  `../scans/1942-07-02_tom-to-mother_p01.jpg`. The copy kept in `../scans/`
  is the one with the highest resolution. `../rename_log.csv` gives each
  duplicate's original filename and folder.
- `old-drafts/`: early transcriptions and an index from the `TBF0defective`
  folder. They were replaced by the complete versions in `../transcriptions/`.

Nothing else in the project refers to these files, so deleting the folder
won't break anything. The project is in git, so a deleted file can always be
recovered from the history.
