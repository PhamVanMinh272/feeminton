import os

from flask import Blueprint
from flask import render_template_string, send_from_directory, current_app

swagger_bp = Blueprint("swagger_bp", __name__)


@swagger_bp.route("/")
def swagger_ui():
    html = """
        <!-- templates/swagger_ui.html -->
    <!DOCTYPE html>
    <html>
    <head>
      <title>Swagger UI</title>
      <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.19.5/swagger-ui.css" >
      <style>
        .topbar {
          display: none;
        }
      </style>
    </head>
    <body>
      <div id="swagger-ui"></div>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.19.5/swagger-ui-bundle.js"></script>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.19.5/swagger-ui-standalone-preset.js"></script>
      <script>
        window.onload = function() {
          const ui = SwaggerUIBundle({
            url: "{{ url_for('swagger_bp.get_spec') }}",
            dom_id: '#swagger-ui',
            presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
            plugins: [
            SwaggerUIBundle.plugins.DownloadUrl
            ],
            layout: "StandaloneLayout"
          });
          window.ui = ui
        };
      </script>
    </body>
    </html>
    """
    return render_template_string(html)


@swagger_bp.route("/spec", methods=["GET"])
def get_spec():
    # 1. Compute the absolute path to your 'app/swagger' folder
    spec_dir = os.path.join(current_app.root_path, "src", "swagger")

    # 2. Serve the file by filename
    return send_from_directory(
        spec_dir, "openapi_spec.json", mimetype="application/x-yaml"
    )
