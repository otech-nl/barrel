from app import app
import barrel
import controllers, do  # noqa: F401
import models
import os

########################################

barrel.rest.enable(app, [models.Group, models.Role])

########################################

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # for compatibility with Scalingo
    app.run(host="0.0.0.0", port=port, threaded=True)

########################################
