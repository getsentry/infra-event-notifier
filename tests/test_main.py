from infra_event_notifier.main import parse_args


class TestCLI:
    def test_parse_dryrun(self):
        examples = [
            ["-n", "datadog"],
            ["--dry-run", "datadog"],
            ["datadog", "-n"],
            ["datadog", "--dry-run"],
            ["-n", "terragrunt", "--cli-args=foo", "--region-map=foo"],
            ["--dry-run", "terragrunt", "--cli-args=foo", "--region-map=foo"],
            ["terragrunt", "-n", "--cli-args=foo", "--region-map=foo"],
            ["terragrunt", "--dry-run", "--cli-args=foo", "--region-map=foo"],
        ]
        for example in examples:
            args = parse_args(example)
            assert args.dry_run

    def test_parse_datadog_no_dryrun(self):
        example = ["datadog"]
        args = parse_args(example)
        assert not args.dry_run

    def test_parse_terragrunt_no_dryrun(self):
        example = ["terragrunt", "--cli-args=foo", "--region-map=foo"]
        args = parse_args(example)
        assert not args.dry_run
