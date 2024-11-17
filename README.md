# Tool Pre-Selection Experiments

This project tests tool pre-selection using vector embeddings and HyDE.

# Paper

The paper can be found in the `paper` folder, at [tool-pre-selection-using-embeddings.pdf](paper/tool-pre-selection-using-embeddings.pdf).

## Installation

To install dependencies:

```bash
bun install
```

This additionally installs `ollama` which is used to generate the embeddings, and to generate the test data.
It requires the download of the `nomic-embed-text` model and the `qwen2.5-coder:32b` model.

## Usage

Basic run with default settings:
```bash
bun run index.ts
```

### Available Parameters

You can customize the experiment with these command line arguments:

- `--tools=<number>` - Number of tools to use (default: 100)
- `--queries=<number>` - Number of test queries to generate (default: 400)
- `--hyde=<boolean>` - Enable/disable Hypothetical Document Embeddings (default: true)

Examples:
```bash
# Run with 150 tools and 75 queries
bun run index.ts --tools=150 --queries=75

# Disable HyDE
bun run index.ts --hyde=false

# Combine multiple parameters
bun run index.ts --tools=200 --queries=100 --hyde=false
```

## Performance

The repository includes pre-generated test data in:
- `test-runs/default/tools.json`: A curated set of tools with their descriptions
- `test-runs/default/test-queries.json`: A collection of test queries with expected tool matches

Using these cached datasets, the system consistently achieves:
- >97% accuracy with HyDE enabled (default)
- >94% accuracy with HyDE disabled

These results have been validated across multiple runs using different configurations. Even in the case where there's multiple tools with relatively similar descriptions, like the tools and queries in this repository.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
