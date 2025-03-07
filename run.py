#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from donordash import app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"App Config SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")  # Debug output
    app.run(host="0.0.0.0", port=port)
