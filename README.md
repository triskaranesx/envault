# envault

> A CLI tool for encrypting and versioning `.env` files with team-sharing support.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) for isolated installs:

```bash
pipx install envault
```

---

## Usage

**Initialize envault in your project:**
```bash
envault init
```

**Encrypt your `.env` file:**
```bash
envault lock --file .env
```

**Decrypt and restore a `.env` file:**
```bash
envault unlock --file .env.vault
```

**Push an encrypted version for your team:**
```bash
envault push --message "add stripe keys"
```

**Pull the latest version:**
```bash
envault pull
```

> Encrypted `.env.vault` files are safe to commit to version control. Share the decryption key with teammates via your preferred secure channel.

---

## How It Works

1. `envault lock` encrypts your `.env` using AES-256 and saves a `.env.vault` file
2. Version history is tracked locally in `.envault/history`
3. Team members run `envault unlock` with the shared key to restore the original file

---

## License

This project is licensed under the [MIT License](LICENSE).