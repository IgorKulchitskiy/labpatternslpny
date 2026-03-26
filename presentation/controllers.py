from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import Blueprint, Flask, jsonify, make_response, redirect, render_template, request, url_for

try:
    from flasgger import Swagger
except ModuleNotFoundError:
    Swagger = None


class TestScenarioWebController:

    AUTH_EMAIL = "igor@gmail.com"
    AUTH_PASSWORD = "1111"
    JWT_SECRET = "super-secret-jwt-key-for-labpatternslpny-2026"
    JWT_ALGORITHM = "HS256"
    JWT_EXP_MINUTES = 60
    JWT_COOKIE_NAME = "access_token"

    def __init__(self, service):
        self.service = service
        self.blueprint = Blueprint("scenarios", __name__)
        self.api_blueprint = Blueprint("scenarios_api", __name__)
        self._register_routes()
        self._register_api_routes()

    @staticmethod
    def _scenario_to_dict(scenario):
        return {
            "scenario_id": scenario.scenario_id,
            "name": scenario.name,
            "description": scenario.description,
            "priority": scenario.priority,
            "steps_count": len(scenario.steps),
            "results_count": len(scenario.results),
        }

    def _create_access_token(self, email: str):
        exp = datetime.now(timezone.utc) + timedelta(minutes=self.JWT_EXP_MINUTES)
        token_payload = {"sub": email, "exp": exp}
        return jwt.encode(token_payload, self.JWT_SECRET, algorithm=self.JWT_ALGORITHM)

    def _decode_access_token(self, token: str):
        try:
            return jwt.decode(token, self.JWT_SECRET, algorithms=[self.JWT_ALGORITHM])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None

    def _extract_token_from_request(self):
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            if token:
                return token

        cookie_token = request.cookies.get(self.JWT_COOKIE_NAME, "").strip()
        if cookie_token:
            return cookie_token

        return None

    def _register_routes(self):

      @self.blueprint.get("/login")
      def login_page():
        return render_template("login.html", error=None)

      @self.blueprint.post("/login")
      def login_submit():
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if email != self.AUTH_EMAIL or password != self.AUTH_PASSWORD:
          return render_template("login.html", error="Невірний логін або пароль"), 401

        token = self._create_access_token(email)
        response = make_response(redirect(url_for("scenarios.scenarios_page", login_success="1")))
        response.set_cookie(
          self.JWT_COOKIE_NAME,
          token,
          httponly=True,
          samesite="Lax",
          max_age=self.JWT_EXP_MINUTES * 60,
        )
        return response

      @self.blueprint.post("/logout")
      def logout_submit():
        response = make_response(redirect(url_for("scenarios.login_page")))
        response.delete_cookie(self.JWT_COOKIE_NAME)
        return response

      @self.blueprint.get("/")
      def index():
        return redirect(url_for("scenarios.login_page"))

      @self.blueprint.get("/scenarios")
      def scenarios_page():
        scenarios = self.service.list_scenarios()
        login_success = request.args.get("login_success") == "1"
        return render_template("scenarios_list.html", scenarios=scenarios, login_success=login_success)

      @self.blueprint.get("/scenarios/new")
      def create_page():
        return render_template("scenario_form.html", scenario=None, action="create")

      @self.blueprint.post("/scenarios")
      def create_scenario():
        self.service.create_scenario(
          name=request.form.get("name", "").strip(),
          description=request.form.get("description", "").strip(),
          priority=request.form.get("priority", "").strip(),
        )
        return redirect(url_for("scenarios.scenarios_page"))

      @self.blueprint.get("/scenarios/<int:scenario_id>/edit")
      def edit_page(scenario_id: int):
        scenario = self.service.get_scenario(scenario_id)
        if scenario is None:
          return redirect(url_for("scenarios.scenarios_page"))
        return render_template("scenario_form.html", scenario=scenario, action="edit")

      @self.blueprint.post("/scenarios/<int:scenario_id>/edit")
      def edit_scenario(scenario_id: int):
        self.service.update_scenario(
          scenario_id=scenario_id,
          name=request.form.get("name", "").strip(),
          description=request.form.get("description", "").strip(),
          priority=request.form.get("priority", "").strip(),
        )
        return redirect(url_for("scenarios.scenarios_page"))

      @self.blueprint.post("/scenarios/<int:scenario_id>/delete")
      def delete_scenario(scenario_id: int):
        self.service.delete_scenario(scenario_id)
        return redirect(url_for("scenarios.scenarios_page"))

    def _register_api_routes(self):

        def require_jwt_token(view_func):
            @wraps(view_func)
            def wrapper(*args, **kwargs):
                token = self._extract_token_from_request()
                if not token:
                    return jsonify({"message": "Token is required"}), 401

                if self._decode_access_token(token) is None:
                    return jsonify({"message": "Invalid token"}), 401

                return view_func(*args, **kwargs)

            return wrapper

        @self.api_blueprint.post("/api/login")
        def api_login():
            """
            Login and receive JWT token.
            ---
            tags:
              - Auth API
            consumes:
              - application/json
            parameters:
              - in: body
                name: body
                required: true
                schema:
                  type: object
                  required:
                    - email
                    - password
                  properties:
                    email:
                      type: string
                    password:
                      type: string
            responses:
              200:
                description: Token generated
              401:
                description: Invalid credentials
            """
            payload = request.get_json(silent=True) or {}
            email = str(payload.get("email", "")).strip()
            password = str(payload.get("password", "")).strip()

            if email != self.AUTH_EMAIL or password != self.AUTH_PASSWORD:
                print(f"[AUTH] Login failed for email={email}; status=401")
                return jsonify({"message": "Invalid email or password"}), 401

            token = self._create_access_token(email)
            print(f"[AUTH] Login successful for email={email}; status=200")
            return jsonify(
                {
                    "message": "Login successful",
                    "status": 200,
                    "access_token": token,
                    "token_type": "Bearer",
                }
            ), 200

        @self.api_blueprint.post("/api/login-status")
        def api_login_status():
            payload = request.get_json(silent=True) or {}
            email = str(payload.get("email", "")).strip()
            password = str(payload.get("password", "")).strip()

            if email != self.AUTH_EMAIL or password != self.AUTH_PASSWORD:
                print(f"[AUTH] Login status check failed for email={email}; status=401")
                return jsonify({"message": "Invalid email or password", "status": 401}), 401

            print(f"[AUTH] Login successful for email={email}; status=200")
            return jsonify({"message": "Login successful", "status": 200}), 200

        @self.api_blueprint.get("/api/scenarios")
        @require_jwt_token
        def api_list_scenarios():
            """
            Get all scenarios.
            ---
            tags:
              - Scenarios API
            security:
              - BearerAuth: []
            responses:
              200:
                description: List of test scenarios
            """
            scenarios = self.service.list_scenarios()
            data = [self._scenario_to_dict(scenario) for scenario in scenarios]
            return jsonify(data)

        @self.api_blueprint.get("/api/scenarios/<int:scenario_id>")
        @require_jwt_token
        def api_get_scenario(scenario_id: int):
            """
            Get scenario by ID.
            ---
            tags:
              - Scenarios API
            security:
              - BearerAuth: []
            parameters:
              - in: path
                name: scenario_id
                required: true
                type: integer
            responses:
              200:
                description: Scenario found
              404:
                description: Scenario not found
            """
            scenario = self.service.get_scenario(scenario_id)
            if scenario is None:
                return jsonify({"message": "Scenario not found"}), 404
            return jsonify(self._scenario_to_dict(scenario))

        @self.api_blueprint.post("/api/scenarios")
        @require_jwt_token
        def api_create_scenario():
            """
            Create a scenario.
            ---
            tags:
              - Scenarios API
            security:
              - BearerAuth: []
            consumes:
              - application/json
            parameters:
              - in: body
                name: body
                required: true
                schema:
                  type: object
                  required:
                    - name
                    - description
                    - priority
                  properties:
                    name:
                      type: string
                    description:
                      type: string
                    priority:
                      type: string
            responses:
              201:
                description: Scenario created
              400:
                description: Invalid payload
            """
            payload = request.get_json(silent=True) or {}
            name = str(payload.get("name", "")).strip()
            description = str(payload.get("description", "")).strip()
            priority = str(payload.get("priority", "")).strip()

            if not name or not description or not priority:
                return jsonify({"message": "Fields name, description, priority are required"}), 400

            scenario = self.service.create_scenario(name, description, priority)
            return jsonify(self._scenario_to_dict(scenario)), 201

        @self.api_blueprint.put("/api/scenarios/<int:scenario_id>")
        @require_jwt_token
        def api_update_scenario(scenario_id: int):
            """
            Update a scenario.
            ---
            tags:
              - Scenarios API
            security:
              - BearerAuth: []
            consumes:
              - application/json
            parameters:
              - in: path
                name: scenario_id
                required: true
                type: integer
              - in: body
                name: body
                required: true
                schema:
                  type: object
                  required:
                    - name
                    - description
                    - priority
                  properties:
                    name:
                      type: string
                    description:
                      type: string
                    priority:
                      type: string
            responses:
              200:
                description: Scenario updated
              400:
                description: Invalid payload
              404:
                description: Scenario not found
            """
            payload = request.get_json(silent=True) or {}
            name = str(payload.get("name", "")).strip()
            description = str(payload.get("description", "")).strip()
            priority = str(payload.get("priority", "")).strip()

            if not name or not description or not priority:
                return jsonify({"message": "Fields name, description, priority are required"}), 400

            scenario = self.service.update_scenario(scenario_id, name, description, priority)
            if scenario is None:
                return jsonify({"message": "Scenario not found"}), 404

            return jsonify(self._scenario_to_dict(scenario))

        @self.api_blueprint.delete("/api/scenarios/<int:scenario_id>")
        @require_jwt_token
        def api_delete_scenario(scenario_id: int):
            """
            Delete a scenario.
            ---
            tags:
              - Scenarios API
            security:
              - BearerAuth: []
            parameters:
              - in: path
                name: scenario_id
                required: true
                type: integer
            responses:
              200:
                description: Scenario deleted
              404:
                description: Scenario not found
            """
            deleted = self.service.delete_scenario(scenario_id)
            if not deleted:
                return jsonify({"message": "Scenario not found"}), 404
            return jsonify({"message": "Scenario deleted"})

    def create_app(self):
        app = Flask(__name__, template_folder="../templates", static_folder="../static")

        @app.before_request
        def require_authentication():
            path = request.path or ""

            if path == "/login" or path == "/api/login" or path == "/api/login-status":
                return None
            if path.startswith("/static/"):
                return None
            if path == "/apidocs" or path.startswith("/apidocs/"):
                return None
            if path == "/apispec_1.json" or path.startswith("/flasgger_static"):
                return None

            token = self._extract_token_from_request()
            payload = self._decode_access_token(token) if token else None
            if payload is not None:
                return None

            if path.startswith("/api/"):
                return jsonify({"message": "Unauthorized"}), 401

            return redirect(url_for("scenarios.login_page"))

        @app.get("/apidocs")
        def apidocs_redirect():
            if Swagger is None:
                return jsonify({"message": "Swagger is not available. Install flasgger to enable /apidocs/."}), 404
            return redirect(url_for("flasgger.apidocs"))

        if Swagger is not None:
            swagger_config = {
                "headers": [],
                "specs": [
                    {
                        "endpoint": "apispec_1",
                        "route": "/apispec_1.json",
                        "rule_filter": lambda rule: True,
                        "model_filter": lambda tag: True,
                    }
                ],
                "static_url_path": "/flasgger_static",
                "swagger_ui": True,
                "specs_route": "/apidocs/",
            }
            swagger_template = {
                "swagger": "2.0",
                "info": {
                    "title": "Lab 3 Scenarios API",
                    "description": "API для керування тест-сценаріями",
                    "version": "1.0.0",
                },
              "securityDefinitions": {
                "BearerAuth": {
                  "type": "apiKey",
                  "name": "Authorization",
                  "in": "header",
                  "description": "Введіть: Bearer <JWT_TOKEN>",
                }
              },
            }

            Swagger(app, config=swagger_config, template=swagger_template)

        app.register_blueprint(self.blueprint)
        app.register_blueprint(self.api_blueprint)
        return app
