from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def write_latex_table(
    path: Path,
    caption: str,
    headers: list[str],
    rows: list[list[str]],
    extra_body: str,
) -> None:
    cols = "l" + "c" * (len(headers) - 1)
    header_line = " & ".join(f"\\textbf{{{h}}}" for h in headers)
    body = "\n".join(" & ".join(row) + r" \\" for row in rows)
    path.write_text(
        "\\begin{table}[h]\n"
        "\\centering\n"
        f"\\caption{{{caption}}}\n"
        f"\\begin{{tabular}}{{{cols}}}\n"
        "\\hline\n"
        f"{header_line} \\\\\n"
        "\\hline\n"
        f"{body}\n"
        f"{extra_body}"
        "\\hline\n"
        "\\end{tabular}\n"
        "\\end{table}\n",
    )
