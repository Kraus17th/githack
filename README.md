# githack

Rebuild source code from an exposed `.git` folder while preserving the original directory structure.

Useful for security assessments: once source is recovered, you can audit it for file uploads, SQL injection, and other web vulnerabilities.

## How it works

1. Parse `.git/index` to collect file names and SHA-1 hashes
2. Download the corresponding objects from `.git/objects/`
3. Decompress with zlib and write files back to disk

## Install

```bash
pipx install git+https://github.com/YOUR_USERNAME/githack.git
```

Update:

```bash
pipx upgrade githack
```

## Usage

```bash
githack http://www.example.com/.git/
```

Without installing:

```bash
python githack.py http://www.example.com/.git/
```

## Credits

Git index parser based on [gin](https://github.com/sbp/gin) by sbp.

Fork of [LiJieJie's githack](https://github.com/lijiejie/GitHack).
