#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from donordash import create_app

if __name__ == "__main__":
    app = create_app()
    # port = int(app.config["PORT"])
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
