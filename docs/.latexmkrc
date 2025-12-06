# Use pdflatex
$pdf_mode = 1;

# Use biber for biblatex (use system biber)
$biber = 'biber --output-directory=build %O %S';
$bibtex_use = 2;

# Disable continuous preview mode for faster single builds
$preview_continuous_mode = 0;

# Suppress unnecessary output
$silent = 0;

# Output auxiliary files to build/ directory
$out_dir = 'build';
$aux_dir = 'build';

# Copy final PDF to pdf/ directory after build
$success_cmd = 'cp build/%R.pdf pdf/%R.pdf';

# Extra file extensions to clean
$clean_ext = 'bbl nav snm synctex.gz run.xml bcf fls';

# Max print line (prevent line wrapping in logs)
$max_repeat = 5;
