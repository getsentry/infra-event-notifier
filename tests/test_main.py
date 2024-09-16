from infra_event_notifier.main import parse_args


class TestCLI:
    def test_parse_dryrun(self):
        examples = [
            ["-n", "datadog"],
            ["--dry-run", "datadog"],
            ["datadog", "-n"],
            ["datadog", "--dry-run"],
            ["-n", "terragrunt"],
            ["--dry-run", "terragrunt"],
            ["terragrunt", "-n"],
            ["terragrunt", "--dry-run"],
        ]
        for example in examples:
            args = parse_args(example)
            assert args.dry_run

    def test_parse_datadog_no_dryrun(self):
        example = ["datadog"]
        args = parse_args(example)
        assert not args.dry_run

    def test_parse_terragrunt_no_dryrun(self):
        example = ["terragrunt"]
        args = parse_args(example)
        assert not args.dry_run
