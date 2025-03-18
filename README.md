# Rules Check

It is a CLI tool to analyze _a firewall_ security policies.

Rules Checker started as a tool to detect overlapping firewall rules, known as shadowing. During development, it evolved
into a straightforward framework that allows to define different checks very easily.

## Installation

You can install _Rules Check_ using `pip`, `poetry` or `pipx`:

```sh
pip install rules_check
poetry add rules_check
pipx install rules_check
```

## Usage

Once installed, you can run it using `rulescheck` or `rc` command:

```sh
rc --help
```

To see an example how does it works, run:

```sh
rc run-example
```

To check your own firewall rules:

```sh
rc run --security-rules policies.json
```

## Contribution & Development

If you'd like to contribute, follow these steps:

```sh
git clone https://github.com/Kanguros/rules_check
cd rules_check
poetry install --with=dev
pre-commit install --install-hooks
pre-commit run --all-files
```

Feel free to open issues or submit pull requests!
