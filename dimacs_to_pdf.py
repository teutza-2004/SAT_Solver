#!/usr/bin/env python3
import argparse
import os
import subprocess
import tempfile
import shutil

import dimacs_parser
import helpers

TEMPLATE = r"""
\documentclass{article}
\usepackage{amsmath}  % For enhanced math functionality
\usepackage{breqn}    % For automatic equation wrapping
\usepackage[margin=1in]{geometry}  % Adjust the page margins

\begin{document}

% Start the equation wrapped using dmath from breqn
\begin{dmath}
<FORMULA>
\end{dmath}

\end{document}
"""


def build_pdf(latex_code: str, pdf_path: str) -> None:
    with tempfile.TemporaryDirectory() as tempdir:
        latex_path = os.path.join(tempdir, "main.tex")
        with open(latex_path, "w") as f:
            f.write(latex_code)

        subprocess.run(["pdflatex",
                        "-output-directory", tempdir,
                        "-jobname", "temp",
                        latex_path])
        shutil.move(os.path.join(tempdir, "temp.pdf"), pdf_path)


def main() -> None:
    argparser = argparse.ArgumentParser(description="Convert a DIMACS file to "
                                                    "a PDF")
    argparser.add_argument("input", help="File containing an input formula "
                                         "in DIMACS format")
    argparser.add_argument("output", help="Output PDF file")
    argparser.add_argument("--logdir", type=str,
                           help="Name of the log directory (by default no "
                           "logs are saved)")
    argparser.add_argument("--loglevel", type=str, default="INFO",
                           help="Lowest log level for which to record "
                           "messages (default: %(default)s)")
    argparser.add_argument("--logquiet", action="store_true",
                           help="Suppress printing to stderr")

    args = argparser.parse_args()
    logger = helpers.setup_logging(args.logdir, args.logquiet, args.loglevel)

    parser = dimacs_parser.FormulaParser(logger=logger)
    parser.set_path(args.input)
    phi = parser.parse()
    assert phi is not None, "No formula was parsed!"

    latex_code = TEMPLATE.replace("<FORMULA>", phi.to_latex())
    build_pdf(latex_code, args.output)


if __name__ == "__main__":
    main()
