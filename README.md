# Execution example

### pdf2md with matker and gpt-4

Setup with docker

```
docker build -t matker-local -f Dockerfile .
```

```
docker run --gpus=all --rm -it -v $(pwd):/work -w /work matker-local
```
Execution

1. ocr with matker
    ```
    marker_single /path/to/file.pdf /path/to/output/folder --batch_multiplier 2 --langs Japanese
    ```
2. re-formatter with gpt-4-turbo
    ```
    python3 scripts/gpt_formatter.py /path/to/output/folder
    ```

