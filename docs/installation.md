# Installation

GDX Aerospace is a monorepo managed with [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/Geopossib/gdxaerospace.git
cd gdxaerospace
uv sync
```

During development you can also install a single package with pip:

```bash
pip install -e packages/aerounits
pip install -e packages/aerocalc
```

Requires Python 3.11 or newer.
