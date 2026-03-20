from flask import Blueprint, Flask, jsonify, redirect, render_template, request, url_for

try:
  from flasgger import Swagger
except ModuleNotFoundError:
  Swagger = None


class TestScenarioWebController:

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

    def _register_routes(self):

        @self.blueprint.get("/")
        def index():
            scenarios = self.service.list_scenarios()
            return render_template("scenarios_list.html", scenarios=scenarios)

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
            return redirect(url_for("scenarios.index"))

        @self.blueprint.get("/scenarios/<int:scenario_id>/edit")
        def edit_page(scenario_id: int):
            scenario = self.service.get_scenario(scenario_id)
            if scenario is None:
                return redirect(url_for("scenarios.index"))
            return render_template("scenario_form.html", scenario=scenario, action="edit")

        @self.blueprint.post("/scenarios/<int:scenario_id>/edit")
        def edit_scenario(scenario_id: int):
            self.service.update_scenario(
                scenario_id=scenario_id,
                name=request.form.get("name", "").strip(),
                description=request.form.get("description", "").strip(),
                priority=request.form.get("priority", "").strip(),
            )
            return redirect(url_for("scenarios.index"))

        @self.blueprint.post("/scenarios/<int:scenario_id>/delete")
        def delete_scenario(scenario_id: int):
            self.service.delete_scenario(scenario_id)
            return redirect(url_for("scenarios.index"))

    def _register_api_routes(self):

        @self.api_blueprint.get("/api/scenarios")
        def api_list_scenarios():
            """
            Get all scenarios.
            ---
            tags:
              - Scenarios API
            responses:
              200:
                description: List of test scenarios
            """
            scenarios = self.service.list_scenarios()
            data = [self._scenario_to_dict(scenario) for scenario in scenarios]
            return jsonify(data)

        @self.api_blueprint.get("/api/scenarios/<int:scenario_id>")
        def api_get_scenario(scenario_id: int):
            """
            Get scenario by ID.
            ---
            tags:
              - Scenarios API
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
        def api_create_scenario():
            """
            Create a scenario.
            ---
            tags:
              - Scenarios API
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
        def api_update_scenario(scenario_id: int):
            """
            Update a scenario.
            ---
            tags:
              - Scenarios API
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
        def api_delete_scenario(scenario_id: int):
            """
            Delete a scenario.
            ---
            tags:
              - Scenarios API
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
            }

            Swagger(app, config=swagger_config, template=swagger_template)

        app.register_blueprint(self.blueprint)
        app.register_blueprint(self.api_blueprint)
        return app