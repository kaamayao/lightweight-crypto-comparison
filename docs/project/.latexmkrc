# Use pdflatex
$pdf_mode = 1;

# Use biber instead of bibtex
$biber = "$ENV{HOME}/.local/bin/biber %O %S";
$bibtex_use = 2;

# Disable continuous preview mode for faster single builds
$preview_continuous_mode = 0;

# Suppress unnecessary output
$silent = 1;

# Extra file extensions to clean
$clean_ext = 'bbl nav snm synctex.gz run.xml bcf fls';

# Max print line (prevent line wrapping in logs)
$max_repeat = 5;
