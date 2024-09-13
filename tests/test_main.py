from infra_event_notifier.main import parse_args


class TestCLI:
    def test_parse_dryrun(self):
        examples = [
            ["-n", "datadog"],
            ["--dry-run", "datadog"],
            ["datadog", "-n"],
            ["datadog", "--dry-run"],
        ]
        for example in examples:
            args = parse_args(example)
            assert args.dry_run

    def test_parse_no_dryrun(self):
        example = ["datadog"]
        args = parse_args(example)
        assert not args.dry_run
