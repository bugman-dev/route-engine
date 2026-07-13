"""Allow `python -m route_engine` after installing the package."""

from .cli import main

raise SystemExit(main())
