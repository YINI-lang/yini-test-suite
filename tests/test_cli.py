# tests/test_cli.py
from yini_test.cli import DEFAULT_CASES_ROOT, build_parser


def test_build_parser() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "smoke",
            "--adapter",
            "python",
            "adapter.py",
            "--input",
            "{input}",
            "--mode",
            "{mode}",
        ]
    )

    assert parser.prog == "yini-test-suite"
    assert args.suite == "smoke"
    assert args.strict is False
    assert args.show_progress is False
    assert args.cases_root == DEFAULT_CASES_ROOT
    assert args.adapter == [
        "python",
        "adapter.py",
        "--input",
        "{input}",
        "--mode",
        "{mode}",
    ]


def test_build_parser_accepts_golden_suite() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "golden",
            "--adapter",
            "python",
            "adapter.py",
        ]
    )

    assert args.suite == "golden"
    assert args.strict is False
    assert args.all_modes is False


def test_build_parser_accepts_all_modes() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "all",
            "--all-modes",
            "--adapter",
            "python",
            "adapter.py",
        ]
    )

    assert args.suite == "all"
    assert args.all_modes is True
    assert args.strict is False


def test_build_parser_accepts_show_progress() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "smoke",
            "--show-progress",
            "--adapter",
            "python",
            "adapter.py",
        ]
    )

    assert args.show_progress is True


def test_build_parser_accepts_cases_root_override(tmp_path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "smoke",
            "--cases-root",
            str(tmp_path),
            "--adapter",
            "python",
            "adapter.py",
        ]
    )

    assert args.cases_root == tmp_path


def test_build_parser_help_starts_with_name_and_version() -> None:
    parser = build_parser()

    help_text = parser.format_help()
    help_lines = help_text.splitlines()

    assert help_lines[0] == "yini-test-suite 0.3.0b2"
    assert help_lines[1].startswith("usage:")
